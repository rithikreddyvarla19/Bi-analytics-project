from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

try:
    from common import DATA_ROOT, configure_logging, ensure_dir
except ModuleNotFoundError:
    from scripts.common import DATA_ROOT, configure_logging, ensure_dir

fake = Faker()
logger = configure_logging("generate_data")

REGIONS = ["Northeast", "Southeast", "Midwest", "West"]
CHANNELS = ["web", "mobile", "store", "marketplace"]
CATEGORIES = ["Apparel", "Electronics", "Home", "Beauty", "Sports"]
PAYMENT_METHODS = ["card", "wallet", "bank_transfer", "gift_card"]
EVENT_TYPES = ["page_view", "product_view", "add_to_cart", "checkout_start", "purchase"]


def _date_range(days: int) -> pd.DatetimeIndex:
    end = datetime.now(UTC).date()
    start = end - timedelta(days=days - 1)
    return pd.date_range(start, end, freq="D")


def generate_customers(n_customers: int) -> pd.DataFrame:
    customers = []
    for i in range(1, n_customers + 1):
        created_at = fake.date_time_between(start_date="-2y", end_date="now")
        customers.append(
            {
                "customer_id": f"CUST{i:06d}",
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": f"customer{i}@example.com",
                "region": np.random.choice(REGIONS),
                "channel_preference": np.random.choice(CHANNELS),
                "created_at": created_at,
                "is_active": np.random.choice([True, True, True, False]),
            }
        )
    return pd.DataFrame(customers)


def generate_products(n_products: int) -> pd.DataFrame:
    products = []
    for i in range(1, n_products + 1):
        category = np.random.choice(CATEGORIES)
        price = round(np.random.uniform(8, 500), 2)
        products.append(
            {
                "product_id": f"PROD{i:06d}",
                "sku": f"SKU-{i:06d}",
                "product_name": f"{category} Item {i}",
                "category": category,
                "base_price": price,
                "is_active": np.random.choice([True, True, True, False]),
            }
        )
    return pd.DataFrame(products)


def generate_orders(
    customers: pd.DataFrame, products: pd.DataFrame, n_orders: int, days: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dates = _date_range(days)
    orders = []
    payments = []
    returns = []
    inventory = []

    product_ids = products["product_id"].tolist()
    customer_ids = customers["customer_id"].tolist()

    for d in dates:
        for product_id in np.random.choice(
            product_ids, size=min(len(product_ids), 120), replace=False
        ):
            inventory.append(
                {
                    "snapshot_date": d,
                    "product_id": product_id,
                    "on_hand_qty": int(np.random.randint(0, 240)),
                    "reorder_point": int(np.random.randint(15, 70)),
                    "region": np.random.choice(REGIONS),
                }
            )

    for i in range(1, n_orders + 1):
        order_ts = np.random.choice(dates) + pd.Timedelta(hours=np.random.randint(0, 24))
        customer_id = np.random.choice(customer_ids)
        order_id = f"ORD{i:07d}"
        num_lines = int(np.random.randint(1, 5))
        line_products = np.random.choice(product_ids, size=num_lines, replace=False)
        total_amount = 0.0

        for product_id in line_products:
            base_price = float(
                products.loc[products["product_id"] == product_id, "base_price"].iloc[0]
            )
            quantity = int(np.random.randint(1, 4))
            discount_rate = float(
                np.random.choice([0.0, 0.05, 0.1, 0.15], p=[0.5, 0.25, 0.2, 0.05])
            )
            unit_price = round(base_price * (1 - discount_rate), 2)
            line_amount = round(unit_price * quantity, 2)
            total_amount += line_amount
            orders.append(
                {
                    "order_id": order_id,
                    "order_line_id": f"{order_id}-L{quantity}{product_id[-3:]}",
                    "order_ts": order_ts,
                    "customer_id": customer_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "line_amount": line_amount,
                    "region": np.random.choice(REGIONS),
                    "channel": np.random.choice(CHANNELS),
                }
            )

        payment_status = np.random.choice(
            ["completed", "completed", "failed", "refunded"], p=[0.78, 0.15, 0.03, 0.04]
        )
        payments.append(
            {
                "payment_id": f"PAY{i:07d}",
                "order_id": order_id,
                "payment_ts": order_ts + pd.Timedelta(minutes=np.random.randint(1, 60)),
                "payment_method": np.random.choice(PAYMENT_METHODS),
                "payment_status": payment_status,
                "payment_amount": round(total_amount, 2),
            }
        )

        if np.random.random() < 0.09:
            returns.append(
                {
                    "return_id": f"RET{i:07d}",
                    "order_id": order_id,
                    "return_ts": order_ts + pd.Timedelta(days=np.random.randint(1, 28)),
                    "return_reason": np.random.choice(
                        ["damaged", "wrong_size", "late_delivery", "not_as_described"]
                    ),
                    "refund_amount": round(total_amount * np.random.uniform(0.2, 1.0), 2),
                }
            )

    return (
        pd.DataFrame(orders),
        pd.DataFrame(payments),
        pd.DataFrame(returns),
        pd.DataFrame(inventory),
    )


def generate_clickstream(
    customers: pd.DataFrame, products: pd.DataFrame, n_events: int, days: int
) -> pd.DataFrame:
    dates = _date_range(days)
    records = []
    customer_ids = customers["customer_id"].tolist()
    product_ids = products["product_id"].tolist()

    for i in range(1, n_events + 1):
        event_ts = np.random.choice(dates) + pd.Timedelta(
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60),
            seconds=np.random.randint(0, 60),
        )
        records.append(
            {
                "event_id": f"EVT{i:09d}",
                "event_ts": event_ts,
                "session_id": f"SESS{np.random.randint(1, n_events // 8 + 1):08d}",
                "customer_id": np.random.choice(
                    customer_ids + [None],
                    p=[*(np.repeat(0.9 / len(customer_ids), len(customer_ids))), 0.1],
                ),
                "product_id": np.random.choice(product_ids),
                "event_type": np.random.choice(EVENT_TYPES, p=[0.45, 0.25, 0.15, 0.1, 0.05]),
                "page_url": np.random.choice(
                    ["/home", "/search", "/product", "/cart", "/checkout"]
                ),
                "channel": np.random.choice(["web", "mobile"], p=[0.65, 0.35]),
                "region": np.random.choice(REGIONS),
            }
        )
    return pd.DataFrame(records)


def save_raw_data(raw_root: Path, data_frames: dict[str, pd.DataFrame]) -> None:
    ensure_dir(raw_root)
    for name, frame in data_frames.items():
        frame.to_csv(raw_root / f"{name}.csv", index=False)
        logger.info("Wrote %s rows to %s", len(frame), raw_root / f"{name}.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic retail datasets")
    parser.add_argument("--customers", type=int, default=500)
    parser.add_argument("--products", type=int, default=250)
    parser.add_argument("--orders", type=int, default=4000)
    parser.add_argument("--clickstream-events", type=int, default=25000)
    parser.add_argument("--days", type=int, default=90)
    args = parser.parse_args()

    raw_root = DATA_ROOT / "raw"
    customers = generate_customers(args.customers)
    products = generate_products(args.products)
    orders, payments, returns, inventory = generate_orders(
        customers, products, args.orders, args.days
    )
    clickstream = generate_clickstream(customers, products, args.clickstream_events, args.days)

    save_raw_data(
        raw_root,
        {
            "customers": customers,
            "products": products,
            "orders": orders,
            "payments": payments,
            "returns": returns,
            "inventory_snapshots": inventory,
            "clickstream_events": clickstream,
        },
    )
    logger.info("Synthetic retail raw data generation completed")


if __name__ == "__main__":
    main()
