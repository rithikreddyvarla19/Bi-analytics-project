from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_sql_marts_present():
    marts = [
        "daily_sales.sql",
        "customer_lifetime_value_proxy.sql",
        "repeat_purchase_metrics.sql",
        "refund_return_rate.sql",
        "inventory_stockout_trends.sql",
        "conversion_funnel_proxy.sql",
        "top_products_categories.sql",
        "regional_revenue_performance.sql",
    ]
    for name in marts:
        assert (ROOT / "sql" / "marts" / name).exists()
