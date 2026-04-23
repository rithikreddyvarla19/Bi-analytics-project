from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data"


def _latest_bronze_file(domain: str) -> Path:
    matches = sorted((DATA_ROOT / "bronze" / f"domain={domain}").rglob("*.parquet"))
    if not matches:
        raise FileNotFoundError(f"No bronze parquet found for {domain}")
    return matches[-1]


def _write_pandas(df: pd.DataFrame, name: str, partition_col: str | None = None) -> None:
    target = DATA_ROOT / "silver" / name
    target.mkdir(parents=True, exist_ok=True)
    if partition_col and partition_col in df.columns:
        df.to_parquet(target, index=False, partition_cols=[partition_col])
    else:
        df.to_parquet(target / f"{name}.parquet", index=False)


def run_pandas() -> None:
    customers = pd.read_parquet(_latest_bronze_file("customers")).drop_duplicates(subset=["customer_id"])
    customers["email"] = customers["email"].astype(str).str.lower()
    customers["created_at"] = pd.to_datetime(customers["created_at"], errors="coerce")

    products = pd.read_parquet(_latest_bronze_file("products")).drop_duplicates(subset=["product_id"])
    products["base_price"] = pd.to_numeric(products["base_price"], errors="coerce")
    products = products[(products["base_price"] > 0) & products["product_id"].notna()]

    orders = pd.read_parquet(_latest_bronze_file("orders")).drop_duplicates(subset=["order_line_id"])
    orders["order_ts"] = pd.to_datetime(orders["order_ts"], errors="coerce")
    orders["order_date"] = orders["order_ts"].dt.date.astype(str)
    orders["quantity"] = pd.to_numeric(orders["quantity"], errors="coerce").fillna(0).astype(int)
    orders["line_amount"] = pd.to_numeric(orders["line_amount"], errors="coerce").fillna(0.0)
    orders = orders[(orders["order_id"].notna()) & (orders["quantity"] > 0) & (orders["line_amount"] >= 0)]

    payments = pd.read_parquet(_latest_bronze_file("payments")).drop_duplicates(subset=["payment_id"])
    payments["payment_ts"] = pd.to_datetime(payments["payment_ts"], errors="coerce")
    payments["payment_date"] = payments["payment_ts"].dt.date.astype(str)

    returns = pd.read_parquet(_latest_bronze_file("returns")).drop_duplicates(subset=["return_id"])
    if not returns.empty:
        returns["return_ts"] = pd.to_datetime(returns["return_ts"], errors="coerce")
        returns["return_date"] = returns["return_ts"].dt.date.astype(str)

    inventory = pd.read_parquet(_latest_bronze_file("inventory_snapshots")).drop_duplicates(
        subset=["snapshot_date", "product_id", "region"]
    )
    inventory["snapshot_date"] = pd.to_datetime(inventory["snapshot_date"], errors="coerce").dt.date.astype(str)

    clickstream = pd.read_parquet(_latest_bronze_file("clickstream_events")).drop_duplicates(subset=["event_id"])
    clickstream["event_ts"] = pd.to_datetime(clickstream["event_ts"], errors="coerce")
    clickstream["event_date"] = clickstream["event_ts"].dt.date.astype(str)

    _write_pandas(customers, "customers")
    _write_pandas(products, "products")
    _write_pandas(orders, "orders", "order_date")
    _write_pandas(payments, "payments", "payment_date")
    _write_pandas(returns, "returns", "return_date")
    _write_pandas(inventory, "inventory_snapshots", "snapshot_date")
    _write_pandas(clickstream, "clickstream_events", "event_date")


def run_spark() -> None:
    from pyspark.sql import SparkSession, functions as F

    spark = (
        SparkSession.builder.appName("bronze-to-silver")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    def read_domain(domain: str):
        return spark.read.parquet(str(DATA_ROOT / "bronze" / f"domain={domain}" / "*"))

    def write(df, name: str, partition_col: str | None = None):
        writer = df.write.mode("overwrite")
        if partition_col:
            writer = writer.partitionBy(partition_col)
        writer.parquet(str(DATA_ROOT / "silver" / name))

    customers = (
        read_domain("customers")
        .dropDuplicates(["customer_id"])
        .withColumn("created_at", F.to_timestamp("created_at"))
        .withColumn("email", F.lower(F.col("email")))
        .filter(F.col("customer_id").isNotNull())
    )
    products = (
        read_domain("products")
        .dropDuplicates(["product_id"])
        .withColumn("base_price", F.col("base_price").cast("double"))
        .filter((F.col("base_price") > 0) & F.col("product_id").isNotNull())
    )
    orders = (
        read_domain("orders")
        .withColumn("order_ts", F.to_timestamp("order_ts"))
        .withColumn("order_date", F.to_date("order_ts"))
        .withColumn("quantity", F.col("quantity").cast("int"))
        .withColumn("line_amount", F.col("line_amount").cast("double"))
        .dropDuplicates(["order_line_id"])
        .filter((F.col("order_id").isNotNull()) & (F.col("quantity") > 0) & (F.col("line_amount") >= 0))
    )
    payments = (
        read_domain("payments")
        .withColumn("payment_ts", F.to_timestamp("payment_ts"))
        .withColumn("payment_date", F.to_date("payment_ts"))
        .withColumn("payment_amount", F.col("payment_amount").cast("double"))
        .dropDuplicates(["payment_id"])
        .filter(F.col("order_id").isNotNull())
    )
    returns = (
        read_domain("returns")
        .withColumn("return_ts", F.to_timestamp("return_ts"))
        .withColumn("return_date", F.to_date("return_ts"))
        .withColumn("refund_amount", F.col("refund_amount").cast("double"))
        .dropDuplicates(["return_id"])
        .filter(F.col("order_id").isNotNull())
    )
    inventory = (
        read_domain("inventory_snapshots")
        .withColumn("snapshot_date", F.to_date("snapshot_date"))
        .withColumn("on_hand_qty", F.col("on_hand_qty").cast("int"))
        .withColumn("reorder_point", F.col("reorder_point").cast("int"))
        .dropDuplicates(["snapshot_date", "product_id", "region"])
        .filter(F.col("product_id").isNotNull())
    )
    clickstream = (
        read_domain("clickstream_events")
        .withColumn("event_ts", F.to_timestamp("event_ts"))
        .withColumn("event_date", F.to_date("event_ts"))
        .dropDuplicates(["event_id"])
        .filter(F.col("event_id").isNotNull())
    )

    write(customers, "customers")
    write(products, "products")
    write(orders, "orders", "order_date")
    write(payments, "payments", "payment_date")
    write(returns, "returns", "return_date")
    write(inventory, "inventory_snapshots", "snapshot_date")
    write(clickstream, "clickstream_events", "event_date")

    spark.stop()


def main() -> None:
    try:
        run_spark()
    except Exception:
        run_pandas()


if __name__ == "__main__":
    main()
