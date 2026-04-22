from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class DataConfig:
    seed: int = 42
    n_customers: int = 5000
    n_products: int = 180
    n_orders: int = 12000


def _region_catalog() -> list[dict[str, str]]:
    return [
        {"region_code": "NE", "region_name": "Northeast", "country": "USA"},
        {"region_code": "SE", "region_name": "Southeast", "country": "USA"},
        {"region_code": "MW", "region_name": "Midwest", "country": "USA"},
        {"region_code": "SW", "region_name": "Southwest", "country": "USA"},
        {"region_code": "W", "region_name": "West", "country": "USA"},
        {"region_code": "P", "region_name": "Pacific", "country": "USA"},
    ]


def generate_customers(config: DataConfig, rng: np.random.Generator) -> pd.DataFrame:
    regions = pd.DataFrame(_region_catalog())
    signup_dates = pd.to_datetime("2022-01-01") + pd.to_timedelta(
        rng.integers(0, 1150, size=config.n_customers), unit="D"
    )
    customer_df = pd.DataFrame(
        {
            "customer_id": np.arange(1, config.n_customers + 1),
            "first_name": [f"Customer{i}" for i in range(1, config.n_customers + 1)],
            "last_name": [f"LN{i}" for i in range(1, config.n_customers + 1)],
            "email": [f"customer{i}@shopmail.com" for i in range(1, config.n_customers + 1)],
            "signup_date": signup_dates,
            "region_code": rng.choice(regions["region_code"], size=config.n_customers),
            "loyalty_tier": rng.choice(["Bronze", "Silver", "Gold"], p=[0.5, 0.35, 0.15], size=config.n_customers),
        }
    )
    missing_region_idx = rng.choice(customer_df.index, size=40, replace=False)
    missing_email_idx = rng.choice(customer_df.index, size=35, replace=False)
    customer_df.loc[missing_region_idx, "region_code"] = np.nan
    customer_df.loc[missing_email_idx, "email"] = np.nan

    duplicate_rows = customer_df.sample(20, random_state=config.seed)
    return pd.concat([customer_df, duplicate_rows], ignore_index=True)


def generate_products(config: DataConfig, rng: np.random.Generator) -> pd.DataFrame:
    categories = {
        "Electronics": ["Audio", "Mobile", "Accessories"],
        "Home": ["Kitchen", "Decor", "Furniture"],
        "Fashion": ["Apparel", "Shoes", "Bags"],
        "Beauty": ["Skincare", "Haircare", "Makeup"],
        "Sports": ["Outdoor", "Fitness", "Athleisure"],
    }
    records: list[dict[str, object]] = []
    product_id = 1
    for category, subcats in categories.items():
        for _ in range(config.n_products // len(categories)):
            subcat = rng.choice(subcats)
            base_cost = rng.uniform(5, 200)
            margin = rng.uniform(1.2, 2.0)
            list_price = round(base_cost * margin, 2)
            records.append(
                {
                    "product_id": product_id,
                    "product_name": f"{category[:3].upper()}-{subcat[:3].upper()}-{product_id:04d}",
                    "category": category,
                    "subcategory": subcat,
                    "brand": rng.choice(["North Peak", "Urban Fox", "Nova", "Wildly", "Core"]),
                    "unit_cost": round(base_cost, 2),
                    "list_price": list_price,
                }
            )
            product_id += 1
    products = pd.DataFrame(records)
    missing_brand_idx = rng.choice(products.index, size=8, replace=False)
    products.loc[missing_brand_idx, "brand"] = np.nan
    return products


def generate_orders(
    config: DataConfig, customers: pd.DataFrame, products: pd.DataFrame, rng: np.random.Generator
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    customer_ids = customers["customer_id"].drop_duplicates().values
    order_dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(
        rng.integers(0, 730, size=config.n_orders), unit="D"
    )
    status = rng.choice(["Delivered", "Cancelled"], p=[0.93, 0.07], size=config.n_orders)
    orders = pd.DataFrame(
        {
            "order_id": np.arange(1, config.n_orders + 1),
            "customer_id": rng.choice(customer_ids, size=config.n_orders),
            "order_date": order_dates,
            "order_status": status,
            "payment_method": rng.choice(
                ["Credit Card", "Debit Card", "PayPal", "Wallet"], p=[0.45, 0.27, 0.18, 0.1], size=config.n_orders
            ),
        }
    )

    item_records: list[dict[str, object]] = []
    item_id = 1
    for row in orders.itertuples(index=False):
        line_count = int(rng.integers(1, 5))
        chosen_products = rng.choice(products["product_id"], size=line_count)
        for line_num, product_id in enumerate(chosen_products, start=1):
            product_row = products.loc[products["product_id"] == product_id].iloc[0]
            quantity = int(rng.integers(1, 4))
            discount_rate = float(rng.choice([0, 0.05, 0.1, 0.15], p=[0.58, 0.2, 0.16, 0.06]))
            unit_price = float(product_row["list_price"]) * rng.uniform(0.9, 1.05)
            item_records.append(
                {
                    "order_item_id": item_id,
                    "order_id": int(row.order_id),
                    "line_number": line_num,
                    "product_id": int(product_id),
                    "quantity": quantity,
                    "unit_price": round(unit_price, 2),
                    "discount_rate": round(discount_rate, 2),
                    "unit_cost": float(product_row["unit_cost"]),
                }
            )
            item_id += 1
    order_items = pd.DataFrame(item_records)

    delivered_items = order_items.merge(orders[["order_id", "order_date", "order_status"]], on="order_id", how="left")
    delivered_items = delivered_items[delivered_items["order_status"] == "Delivered"]
    return_candidates = delivered_items.sample(frac=0.08, random_state=config.seed)
    returns = return_candidates[["order_item_id", "order_id", "product_id", "quantity"]].copy()
    returns["returned_qty"] = returns["quantity"].clip(upper=1)
    returns["return_reason"] = rng.choice(
        ["Damaged", "Wrong Size", "Not Needed", "Late Delivery"], size=len(returns), p=[0.35, 0.25, 0.25, 0.15]
    )
    returns["return_date"] = pd.to_datetime(delivered_items["order_date"].sample(n=len(returns), random_state=7).values) + pd.to_timedelta(
        rng.integers(3, 40, size=len(returns)), unit="D"
    )
    returns = returns.drop(columns=["quantity"]).reset_index(drop=True)

    duplicate_orders = orders.sample(25, random_state=config.seed)
    orders = pd.concat([orders, duplicate_orders], ignore_index=True)
    return orders, order_items, returns


def generate_all(output_dir: Path, config: DataConfig) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(config.seed)

    customers = generate_customers(config, rng)
    products = generate_products(config, rng)
    orders, order_items, returns = generate_orders(config, customers, products, rng)
    regions = pd.DataFrame(_region_catalog())

    customers.to_csv(output_dir / "customers_raw.csv", index=False)
    products.to_csv(output_dir / "products_raw.csv", index=False)
    orders.to_csv(output_dir / "orders_raw.csv", index=False)
    order_items.to_csv(output_dir / "order_items_raw.csv", index=False)
    returns.to_csv(output_dir / "returns_raw.csv", index=False)
    regions.to_csv(output_dir / "regions_raw.csv", index=False)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_all(root / "data" / "raw", DataConfig())
    print("Raw ecommerce data generated in data/raw")
