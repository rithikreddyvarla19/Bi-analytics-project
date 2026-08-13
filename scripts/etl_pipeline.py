from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _load_raw(raw_dir: Path) -> dict[str, pd.DataFrame]:
    return {
        "customers": pd.read_csv(raw_dir / "customers_raw.csv", parse_dates=["signup_date"]),
        "products": pd.read_csv(raw_dir / "products_raw.csv"),
        "orders": pd.read_csv(raw_dir / "orders_raw.csv", parse_dates=["order_date"]),
        "order_items": pd.read_csv(raw_dir / "order_items_raw.csv"),
        "returns": pd.read_csv(raw_dir / "returns_raw.csv", parse_dates=["return_date"]),
        "regions": pd.read_csv(raw_dir / "regions_raw.csv"),
    }


def _data_quality_report(
    raw: dict[str, pd.DataFrame], cleaned: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for name, raw_df in raw.items():
        clean_df = cleaned[name]
        records.append(
            {
                "table_name": name,
                "raw_rows": len(raw_df),
                "clean_rows": len(clean_df),
                "duplicate_rows_removed": int(raw_df.duplicated().sum()),
                "raw_null_cells": int(raw_df.isna().sum().sum()),
                "clean_null_cells": int(clean_df.isna().sum().sum()),
            }
        )
    return pd.DataFrame(records)


def clean_data(raw: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    customers = raw["customers"].drop_duplicates(subset=["customer_id"]).copy()
    customers["region_code"] = customers["region_code"].fillna("UNK")
    customers["email"] = np.where(
        customers["email"].isna(),
        customers["customer_id"].apply(lambda value: f"missing_{value}@shopmail.com"),
        customers["email"],
    )

    products = raw["products"].drop_duplicates(subset=["product_id"]).copy()
    products["brand"] = products["brand"].fillna("Unknown")
    products = products[products["list_price"] > 0]

    orders = raw["orders"].drop_duplicates(subset=["order_id"]).copy()
    orders = orders[orders["customer_id"].isin(customers["customer_id"])]
    orders["order_status"] = orders["order_status"].fillna("Delivered")

    order_items = raw["order_items"].drop_duplicates(subset=["order_item_id"]).copy()
    order_items = order_items[
        order_items["order_id"].isin(orders["order_id"])
        & order_items["product_id"].isin(products["product_id"])
    ].copy()
    order_items["quantity"] = order_items["quantity"].clip(lower=1)
    order_items["discount_rate"] = order_items["discount_rate"].clip(lower=0, upper=0.4)

    returns = raw["returns"].drop_duplicates(subset=["order_item_id"]).copy()
    returns = returns[returns["order_item_id"].isin(order_items["order_item_id"])]
    returns["returned_qty"] = returns["returned_qty"].clip(lower=0)

    regions = raw["regions"].drop_duplicates(subset=["region_code"]).copy()
    if not (regions["region_code"] == "UNK").any():
        regions = pd.concat(
            [
                regions,
                pd.DataFrame([{"region_code": "UNK", "region_name": "Unknown", "country": "USA"}]),
            ],
            ignore_index=True,
        )

    return {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "returns": returns,
        "regions": regions,
    }


def build_star_schema(cleaned: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    customers = cleaned["customers"]
    products = cleaned["products"]
    orders = cleaned["orders"]
    order_items = cleaned["order_items"]
    returns = cleaned["returns"]
    regions = cleaned["regions"]

    dim_region = regions.sort_values("region_code").reset_index(drop=True).copy()
    dim_region["region_key"] = np.arange(1, len(dim_region) + 1)
    region_map = dim_region.set_index("region_code")["region_key"].to_dict()

    dim_customers = customers.copy()
    dim_customers["region_key"] = dim_customers["region_code"].map(region_map)
    dim_customers["customer_key"] = np.arange(1, len(dim_customers) + 1)
    dim_customers = dim_customers[
        [
            "customer_key",
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "signup_date",
            "loyalty_tier",
            "region_key",
        ]
    ]
    customer_key_map = dim_customers.set_index("customer_id")["customer_key"].to_dict()

    dim_products = products.copy()
    dim_products["product_key"] = np.arange(1, len(dim_products) + 1)
    dim_products = dim_products[
        [
            "product_key",
            "product_id",
            "product_name",
            "category",
            "subcategory",
            "brand",
            "unit_cost",
            "list_price",
        ]
    ]
    product_key_map = dim_products.set_index("product_id")["product_key"].to_dict()

    min_date = orders["order_date"].min()
    max_date = orders["order_date"].max()
    date_range = pd.date_range(min_date, max_date, freq="D")
    dim_date = pd.DataFrame({"date": date_range})
    dim_date["date_key"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["quarter"] = "Q" + dim_date["date"].dt.quarter.astype(str)
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["month_name"] = dim_date["date"].dt.strftime("%b")
    dim_date["week_of_year"] = dim_date["date"].dt.isocalendar().week.astype(int)
    dim_date["day"] = dim_date["date"].dt.day
    dim_date["weekday_name"] = dim_date["date"].dt.strftime("%A")
    date_key_map = dim_date.set_index("date")["date_key"].to_dict()

    order_header = orders[["order_id", "customer_id", "order_date", "order_status"]].copy()
    fact = order_items.merge(order_header, on="order_id", how="left")
    fact = fact[fact["order_status"] != "Cancelled"].copy()

    return_lookup = returns[["order_item_id", "returned_qty"]].copy()
    fact = fact.merge(return_lookup, on="order_item_id", how="left")
    fact["returned_qty"] = fact["returned_qty"].fillna(0).astype(int)

    fact["customer_key"] = fact["customer_id"].map(customer_key_map)
    fact["product_key"] = fact["product_id"].map(product_key_map)
    fact["date_key"] = fact["order_date"].dt.normalize().map(date_key_map)
    fact["date_key"] = fact["date_key"].astype(int)

    fact["gross_revenue"] = fact["quantity"] * fact["unit_price"]
    fact["discount_amount"] = fact["gross_revenue"] * fact["discount_rate"]
    fact["net_revenue"] = fact["gross_revenue"] - fact["discount_amount"]
    fact["refunded_amount"] = fact["returned_qty"] * (
        fact["unit_price"] * (1 - fact["discount_rate"])
    )
    fact["recognized_revenue"] = fact["net_revenue"] - fact["refunded_amount"]
    fact["cogs_amount"] = fact["quantity"] * fact["unit_cost"]
    fact["profit_amount"] = fact["recognized_revenue"] - fact["cogs_amount"]

    fact_sales = fact[
        [
            "order_item_id",
            "order_id",
            "line_number",
            "date_key",
            "customer_key",
            "product_key",
            "quantity",
            "returned_qty",
            "unit_price",
            "discount_rate",
            "gross_revenue",
            "discount_amount",
            "net_revenue",
            "refunded_amount",
            "recognized_revenue",
            "cogs_amount",
            "profit_amount",
        ]
    ].copy()

    return {
        "dim_region": dim_region[["region_key", "region_code", "region_name", "country"]],
        "dim_customers": dim_customers,
        "dim_products": dim_products,
        "dim_date": dim_date[
            [
                "date_key",
                "date",
                "year",
                "quarter",
                "month",
                "month_name",
                "week_of_year",
                "day",
                "weekday_name",
            ]
        ],
        "fact_sales": fact_sales,
    }


def save_outputs(
    raw: dict[str, pd.DataFrame],
    cleaned: dict[str, pd.DataFrame],
    star_schema: dict[str, pd.DataFrame],
    processed_dir: Path,
    outputs_dir: Path,
) -> None:
    processed_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    for name, df in cleaned.items():
        df.to_csv(processed_dir / f"{name}_clean.csv", index=False)

    for table_name, df in star_schema.items():
        df.to_csv(processed_dir / f"{table_name}.csv", index=False)

    quality = _data_quality_report(raw=raw, cleaned=cleaned)
    quality.to_csv(outputs_dir / "data_quality_report.csv", index=False)


def run_pipeline(project_root: Path) -> None:
    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    outputs_dir = project_root / "outputs"

    raw = _load_raw(raw_dir)
    cleaned = clean_data(raw)
    star = build_star_schema(cleaned)
    save_outputs(raw, cleaned, star, processed_dir, outputs_dir)
    print("ETL pipeline complete. Processed tables are available in data/processed")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    run_pipeline(root)
