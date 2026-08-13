from __future__ import annotations


import pandas as pd

try:
    from common import DATA_ROOT, OUTPUT_ROOT, configure_logging, ensure_dir
except ModuleNotFoundError:
    from scripts.common import DATA_ROOT, OUTPUT_ROOT, configure_logging, ensure_dir

logger = configure_logging("export_kpis")


def read_table(name: str) -> pd.DataFrame:
    csv_path = DATA_ROOT / "warehouse" / f"{name}.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return pd.read_parquet(DATA_ROOT / "gold" / name)


def main() -> None:
    ensure_dir(OUTPUT_ROOT / "kpis")

    fact_orders = read_table("fact_orders")
    fact_payments = read_table("fact_payments")
    fact_returns = read_table("fact_returns")
    fact_web_events = read_table("fact_web_events")
    dim_products = read_table("dim_products")

    fact_orders["order_date"] = pd.to_datetime(fact_orders["order_date"])
    fact_payments["payment_date"] = pd.to_datetime(fact_payments["payment_date"])

    daily_sales = (
        fact_orders.groupby(fact_orders["order_date"].dt.date)
        .agg(revenue=("order_amount", "sum"), orders=("order_id", "nunique"))
        .reset_index()
        .rename(columns={"order_date": "sales_date"})
    )

    customer_ltv = (
        fact_orders.groupby("customer_id")
        .agg(total_revenue=("order_amount", "sum"), total_orders=("order_id", "nunique"))
        .reset_index()
    )
    customer_ltv["ltv_proxy"] = customer_ltv["total_revenue"]

    repeat_purchase = (
        fact_orders.groupby("customer_id")["order_id"].nunique().reset_index(name="order_count")
    )
    repeat_purchase["is_repeat"] = repeat_purchase["order_count"] > 1
    repeat_metrics = pd.DataFrame(
        [
            {
                "repeat_customer_rate": round(repeat_purchase["is_repeat"].mean(), 4),
                "customers": int(repeat_purchase.shape[0]),
            }
        ]
    )

    return_rate = pd.DataFrame(
        [
            {
                "orders": int(fact_orders["order_id"].nunique()),
                "returns": int(fact_returns["order_id"].nunique())
                if "order_id" in fact_returns
                else 0,
                "return_rate": round(
                    (
                        fact_returns["order_id"].nunique()
                        / max(fact_orders["order_id"].nunique(), 1)
                    ),
                    4,
                )
                if "order_id" in fact_returns
                else 0.0,
            }
        ]
    )

    conversion = (
        fact_web_events.groupby(["event_date", "event_type"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
        if "event_date" in fact_web_events
        else pd.DataFrame()
    )

    top_products = (
        fact_orders.groupby("product_id")
        .agg(revenue=("order_amount", "sum"), orders=("order_id", "nunique"))
        .reset_index()
    )
    top_products = top_products.merge(
        dim_products[["product_id", "product_name", "category"]], on="product_id", how="left"
    )
    top_products = top_products.sort_values("revenue", ascending=False).head(25)

    regional_revenue = (
        fact_orders.groupby("region")
        .agg(revenue=("order_amount", "sum"), orders=("order_id", "nunique"))
        .reset_index()
    )

    artifacts = {
        "daily_sales.csv": daily_sales,
        "customer_ltv_proxy.csv": customer_ltv,
        "repeat_purchase_metrics.csv": repeat_metrics,
        "refund_return_rate.csv": return_rate,
        "conversion_funnel_proxy.csv": conversion,
        "top_products.csv": top_products,
        "regional_revenue_performance.csv": regional_revenue,
    }

    for name, frame in artifacts.items():
        output_path = OUTPUT_ROOT / "kpis" / name
        frame.to_csv(output_path, index=False)
        logger.info("Generated KPI artifact %s (%s rows)", name, len(frame))


if __name__ == "__main__":
    main()
