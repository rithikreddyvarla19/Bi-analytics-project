from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data"


def _read_silver(name: str) -> pd.DataFrame:
    return pd.read_parquet(DATA_ROOT / "silver" / name)


def _write(df: pd.DataFrame, name: str, partition_col: str | None = None) -> None:
    target = DATA_ROOT / "gold" / name
    target.mkdir(parents=True, exist_ok=True)
    if partition_col and partition_col in df.columns:
        df.to_parquet(target, index=False, partition_cols=[partition_col])
    else:
        df.to_parquet(target / f"{name}.parquet", index=False)


def run_pandas() -> None:
    customers = _read_silver("customers")
    products = _read_silver("products")
    orders = _read_silver("orders")
    payments = _read_silver("payments")
    returns = _read_silver("returns")
    inventory = _read_silver("inventory_snapshots")
    clickstream = _read_silver("clickstream_events")

    dim_customers = customers[["customer_id", "first_name", "last_name", "email", "region", "channel_preference", "created_at", "is_active"]]
    dim_products = products[["product_id", "sku", "product_name", "category", "base_price", "is_active"]]

    dim_region = orders[["region"]].dropna().drop_duplicates().rename(columns={"region": "region_name"}).reset_index(drop=True)
    dim_region["region_id"] = dim_region.index.map(lambda i: f"REG-{i + 1:02d}")

    dim_channel = orders[["channel"]].dropna().drop_duplicates().rename(columns={"channel": "channel_name"}).reset_index(drop=True)
    dim_channel["channel_id"] = dim_channel.index.map(lambda i: f"CH-{i + 1:02d}")

    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
    dim_date = pd.DataFrame({"date_key": orders["order_date"].dropna().dt.date.unique()})
    dim_date["date_key"] = pd.to_datetime(dim_date["date_key"])
    dim_date["year"] = dim_date["date_key"].dt.year
    dim_date["month"] = dim_date["date_key"].dt.month
    dim_date["day"] = dim_date["date_key"].dt.day
    dim_date["week_of_year"] = dim_date["date_key"].dt.isocalendar().week.astype(int)

    fact_orders = orders[
        ["order_id", "order_line_id", "order_date", "customer_id", "product_id", "region", "channel", "quantity", "line_amount"]
    ].rename(columns={"quantity": "item_quantity", "line_amount": "order_amount"})
    fact_orders["order_status"] = "placed"
    fact_orders["order_date"] = fact_orders["order_date"].dt.date.astype(str)

    fact_payments = payments[["payment_id", "order_id", "payment_date", "payment_method", "payment_status", "payment_amount"]]
    fact_returns = returns[["return_id", "order_id", "return_date", "return_reason", "refund_amount"]] if not returns.empty else pd.DataFrame(columns=["return_id", "order_id", "return_date", "return_reason", "refund_amount"])
    fact_web_events = clickstream[["event_id", "event_ts", "event_date", "session_id", "customer_id", "product_id", "event_type", "channel", "region"]]
    fact_inventory = inventory[["snapshot_date", "product_id", "region", "on_hand_qty", "reorder_point"]]

    daily_sales = (
        fact_orders.groupby(["order_date", "region", "channel"], as_index=False)
        .agg(gross_sales=("order_amount", "sum"), orders=("order_id", "nunique"), units_sold=("item_quantity", "sum"))
        .rename(columns={"order_date": "sales_date"})
    )

    conversion = pd.pivot_table(
        fact_web_events,
        index=["event_date", "channel"],
        columns="event_type",
        values="event_id",
        aggfunc="count",
        fill_value=0,
    ).reset_index()

    fact_inventory["is_stockout"] = (fact_inventory["on_hand_qty"] <= 0).astype(int)
    inventory_stockout = (
        fact_inventory.groupby(["snapshot_date", "region"], as_index=False)
        .agg(stockout_products=("is_stockout", "sum"), tracked_products=("product_id", "nunique"))
    )

    _write(dim_customers, "dim_customers")
    _write(dim_products, "dim_products")
    _write(dim_region, "dim_region")
    _write(dim_channel, "dim_channel")
    _write(dim_date, "dim_date")
    _write(fact_orders, "fact_orders", "order_date")
    _write(fact_payments, "fact_payments", "payment_date")
    _write(fact_returns, "fact_returns", "return_date")
    _write(fact_web_events, "fact_web_events", "event_date")
    _write(fact_inventory.drop(columns=["is_stockout"]), "fact_inventory", "snapshot_date")
    _write(daily_sales, "daily_sales", "sales_date")
    _write(conversion, "conversion_funnel_proxy", "event_date")
    _write(inventory_stockout, "inventory_stockout_trends", "snapshot_date")


def run_spark() -> None:
    from pyspark.sql import SparkSession, functions as F

    spark = (
        SparkSession.builder.appName("silver-to-gold")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    def read(name: str):
        return spark.read.parquet(str(DATA_ROOT / "silver" / name))

    def write(df, name: str, partition_col: str | None = None):
        writer = df.write.mode("overwrite")
        if partition_col:
            writer = writer.partitionBy(partition_col)
        writer.parquet(str(DATA_ROOT / "gold" / name))

    customers = read("customers")
    products = read("products")
    orders = read("orders")
    payments = read("payments")
    returns = read("returns")
    inventory = read("inventory_snapshots")
    clickstream = read("clickstream_events")

    dim_customers = customers.select("customer_id", "first_name", "last_name", "email", "region", "channel_preference", "created_at", "is_active")
    dim_products = products.select("product_id", "sku", "product_name", "category", "base_price", "is_active")
    dim_region = orders.select("region").dropna().dropDuplicates().withColumnRenamed("region", "region_name")
    dim_region = dim_region.withColumn("region_id", F.concat(F.lit("REG-"), F.lpad(F.monotonically_increasing_id() % 100, 2, "0")))
    dim_channel = orders.select("channel").dropna().dropDuplicates().withColumnRenamed("channel", "channel_name")
    dim_channel = dim_channel.withColumn("channel_id", F.concat(F.lit("CH-"), F.lpad(F.monotonically_increasing_id() % 100, 2, "0")))

    dim_date = (
        orders.select(F.to_date("order_date").alias("date_key"))
        .dropDuplicates(["date_key"])
        .withColumn("year", F.year("date_key"))
        .withColumn("month", F.month("date_key"))
        .withColumn("day", F.dayofmonth("date_key"))
        .withColumn("week_of_year", F.weekofyear("date_key"))
    )

    fact_orders = orders.select(
        "order_id", "order_line_id", "order_date", "customer_id", "product_id", "region", "channel",
        F.col("quantity").alias("item_quantity"), F.col("line_amount").alias("order_amount")
    ).withColumn("order_status", F.lit("placed"))

    fact_payments = payments.select("payment_id", "order_id", "payment_date", "payment_method", "payment_status", "payment_amount")
    fact_returns = returns.select("return_id", "order_id", "return_date", "return_reason", "refund_amount")
    fact_web_events = clickstream.select("event_id", "event_ts", "event_date", "session_id", "customer_id", "product_id", "event_type", "channel", "region")
    fact_inventory = inventory.select("snapshot_date", "product_id", "region", "on_hand_qty", "reorder_point")

    daily_sales = (
        fact_orders.groupBy("order_date", "region", "channel")
        .agg(F.round(F.sum("order_amount"), 2).alias("gross_sales"), F.countDistinct("order_id").alias("orders"), F.sum("item_quantity").alias("units_sold"))
        .withColumnRenamed("order_date", "sales_date")
    )

    conversion = (
        clickstream.groupBy("event_date", "channel")
        .pivot("event_type", ["page_view", "product_view", "add_to_cart", "checkout_start", "purchase"])
        .count().fillna(0)
    )

    inventory_stockout = (
        fact_inventory.withColumn("is_stockout", F.when(F.col("on_hand_qty") <= 0, 1).otherwise(0))
        .groupBy("snapshot_date", "region")
        .agg(F.sum("is_stockout").alias("stockout_products"), F.countDistinct("product_id").alias("tracked_products"))
    )

    write(dim_customers, "dim_customers")
    write(dim_products, "dim_products")
    write(dim_region, "dim_region")
    write(dim_channel, "dim_channel")
    write(dim_date, "dim_date")
    write(fact_orders, "fact_orders", "order_date")
    write(fact_payments, "fact_payments", "payment_date")
    write(fact_returns, "fact_returns", "return_date")
    write(fact_web_events, "fact_web_events", "event_date")
    write(fact_inventory, "fact_inventory", "snapshot_date")
    write(daily_sales, "daily_sales", "sales_date")
    write(conversion, "conversion_funnel_proxy", "event_date")
    write(inventory_stockout, "inventory_stockout_trends", "snapshot_date")

    spark.stop()


def main() -> None:
    try:
        run_spark()
    except Exception:
        run_pandas()


if __name__ == "__main__":
    main()
