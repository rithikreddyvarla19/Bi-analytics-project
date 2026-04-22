from __future__ import annotations

from pathlib import Path

import pandas as pd


def _load_processed(processed_dir: Path) -> dict[str, pd.DataFrame]:
    return {
        "fact_sales": pd.read_csv(processed_dir / "fact_sales.csv"),
        "dim_customers": pd.read_csv(processed_dir / "dim_customers.csv", parse_dates=["signup_date"]),
        "dim_products": pd.read_csv(processed_dir / "dim_products.csv"),
        "dim_date": pd.read_csv(processed_dir / "dim_date.csv", parse_dates=["date"]),
        "dim_region": pd.read_csv(processed_dir / "dim_region.csv"),
    }


def create_kpi_outputs(processed_dir: Path, output_dir: Path, dashboard_export_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    dashboard_export_dir.mkdir(parents=True, exist_ok=True)
    data = _load_processed(processed_dir)

    fact = data["fact_sales"]
    dim_date = data["dim_date"]
    dim_products = data["dim_products"]
    dim_customers = data["dim_customers"]
    dim_region = data["dim_region"]

    sales = fact.merge(dim_date[["date_key", "date", "year", "month"]], on="date_key", how="left")
    sales["month_start"] = sales["date"].dt.to_period("M").dt.to_timestamp()

    order_level = sales.groupby("order_id", as_index=False).agg(order_revenue=("recognized_revenue", "sum"))
    customer_orders = sales.groupby("customer_key", as_index=False).agg(order_count=("order_id", "nunique"))

    total_revenue = float(sales["recognized_revenue"].sum())
    total_orders = int(sales["order_id"].nunique())
    average_order_value = float(order_level["order_revenue"].mean())
    repeat_purchase_rate = float((customer_orders["order_count"] >= 2).mean() * 100)
    refund_rate = float((sales["refunded_amount"].sum() / sales["net_revenue"].sum()) * 100)

    monthly = (
        sales.groupby("month_start", as_index=False)
        .agg(
            monthly_revenue=("recognized_revenue", "sum"),
            monthly_orders=("order_id", "nunique"),
            monthly_customers=("customer_key", "nunique"),
        )
        .sort_values("month_start")
    )
    monthly["monthly_growth_pct"] = monthly["monthly_revenue"].pct_change() * 100
    monthly["monthly_aov"] = monthly["monthly_revenue"] / monthly["monthly_orders"]

    product_perf = (
        sales.merge(dim_products[["product_key", "product_name", "category"]], on="product_key", how="left")
        .groupby(["category", "product_name"], as_index=False)
        .agg(
            revenue=("recognized_revenue", "sum"),
            units_sold=("quantity", "sum"),
            refunded=("refunded_amount", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )

    region_perf = (
        sales.merge(dim_customers[["customer_key", "region_key"]], on="customer_key", how="left")
        .merge(dim_region[["region_key", "region_name"]], on="region_key", how="left")
        .groupby("region_name", as_index=False)
        .agg(
            revenue=("recognized_revenue", "sum"),
            profit=("profit_amount", "sum"),
            orders=("order_id", "nunique"),
            refunded=("refunded_amount", "sum"),
        )
    )
    region_perf["refund_rate_pct"] = (region_perf["refunded"] / region_perf["revenue"]).fillna(0) * 100

    clv_proxy = (
        sales.groupby("customer_key", as_index=False)
        .agg(total_revenue=("recognized_revenue", "sum"), total_orders=("order_id", "nunique"))
        .merge(dim_customers[["customer_key", "loyalty_tier", "region_key"]], on="customer_key", how="left")
        .merge(dim_region[["region_key", "region_name"]], on="region_key", how="left")
        .sort_values("total_revenue", ascending=False)
    )

    kpi_summary = pd.DataFrame(
        [
            {"kpi_name": "total_revenue", "kpi_value": round(total_revenue, 2)},
            {"kpi_name": "total_orders", "kpi_value": total_orders},
            {"kpi_name": "average_order_value", "kpi_value": round(average_order_value, 2)},
            {"kpi_name": "monthly_growth_latest_pct", "kpi_value": round(float(monthly["monthly_growth_pct"].iloc[-1]), 2)},
            {"kpi_name": "repeat_purchase_rate_pct", "kpi_value": round(repeat_purchase_rate, 2)},
            {"kpi_name": "refund_rate_pct", "kpi_value": round(refund_rate, 2)},
        ]
    )

    kpi_summary.to_csv(output_dir / "kpi_summary.csv", index=False)
    monthly.to_csv(output_dir / "monthly_kpi_trend.csv", index=False)
    product_perf.to_csv(output_dir / "product_category_performance.csv", index=False)
    region_perf.to_csv(output_dir / "regional_performance.csv", index=False)
    clv_proxy.to_csv(output_dir / "customer_ltv_proxy.csv", index=False)

    executive_dashboard = monthly.merge(
        region_perf[["region_name", "revenue"]].rename(columns={"revenue": "region_revenue_total"}),
        how="cross",
    )
    customer_dashboard = clv_proxy.head(500)
    product_dashboard = product_perf
    region_dashboard = region_perf.merge(
        monthly[["month_start", "monthly_revenue", "monthly_growth_pct"]], how="cross"
    )

    executive_dashboard.to_csv(dashboard_export_dir / "executive_dashboard_dataset.csv", index=False)
    customer_dashboard.to_csv(dashboard_export_dir / "customer_insights_dataset.csv", index=False)
    product_dashboard.to_csv(dashboard_export_dir / "product_performance_dataset.csv", index=False)
    region_dashboard.to_csv(dashboard_export_dir / "regional_trends_dataset.csv", index=False)

    excel_path = output_dir / "bi_dashboard_pack.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        kpi_summary.to_excel(writer, sheet_name="kpi_summary", index=False)
        monthly.to_excel(writer, sheet_name="monthly_trend", index=False)
        product_perf.to_excel(writer, sheet_name="product_perf", index=False)
        region_perf.to_excel(writer, sheet_name="region_perf", index=False)
        clv_proxy.to_excel(writer, sheet_name="customer_ltv_proxy", index=False)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    create_kpi_outputs(
        processed_dir=project_root / "data" / "processed",
        output_dir=project_root / "outputs",
        dashboard_export_dir=project_root / "dashboard_spec" / "datasets",
    )
    print("KPI and dashboard-ready datasets generated in outputs and dashboard_spec/datasets")
