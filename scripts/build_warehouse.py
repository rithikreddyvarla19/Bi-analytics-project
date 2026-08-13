from __future__ import annotations

import os

import pandas as pd
from sqlalchemy import create_engine

try:
    from common import DATA_ROOT, configure_logging, ensure_dir
except ModuleNotFoundError:
    from scripts.common import DATA_ROOT, configure_logging, ensure_dir

logger = configure_logging("build_warehouse")
WAREHOUSE_ROOT = DATA_ROOT / "warehouse"


def read_gold(name: str) -> pd.DataFrame:
    path = DATA_ROOT / "gold" / name
    if not path.exists():
        raise FileNotFoundError(f"Gold dataset missing: {path}")
    return pd.read_parquet(path)


def build_core_tables() -> dict[str, pd.DataFrame]:
    fact_orders = read_gold("fact_orders")
    fact_payments = read_gold("fact_payments")
    fact_returns = read_gold("fact_returns")
    fact_web_events = read_gold("fact_web_events")
    fact_inventory = read_gold("fact_inventory")
    dim_customers = read_gold("dim_customers")
    dim_products = read_gold("dim_products")
    dim_date = read_gold("dim_date")
    dim_region = read_gold("dim_region")
    dim_channel = read_gold("dim_channel")

    return {
        "fact_orders": fact_orders,
        "fact_payments": fact_payments,
        "fact_returns": fact_returns,
        "fact_web_events": fact_web_events,
        "fact_inventory": fact_inventory,
        "dim_customers": dim_customers,
        "dim_products": dim_products,
        "dim_date": dim_date,
        "dim_region": dim_region,
        "dim_channel": dim_channel,
    }


def write_csv_tables(tables: dict[str, pd.DataFrame]) -> None:
    ensure_dir(WAREHOUSE_ROOT)
    for name, frame in tables.items():
        out = WAREHOUSE_ROOT / f"{name}.csv"
        frame.to_csv(out, index=False)
        logger.info("Wrote warehouse table %s (%s rows)", name, len(frame))


def load_to_postgres_if_available(tables: dict[str, pd.DataFrame]) -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "retail_warehouse")
    user = os.getenv("POSTGRES_USER", "retail")
    password = os.getenv("POSTGRES_PASSWORD", "retail")

    connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    try:
        engine = create_engine(connection_string)
        with engine.begin() as conn:
            for name, frame in tables.items():
                frame.to_sql(name, conn, if_exists="replace", index=False)
        logger.info("Loaded %s warehouse tables into PostgreSQL", len(tables))
        return "loaded"
    except Exception as exc:  # noqa: BLE001
        logger.warning("PostgreSQL load skipped: %s", exc)
        return "skipped"


def main() -> None:
    tables = build_core_tables()
    write_csv_tables(tables)
    load_to_postgres_if_available(tables)


if __name__ == "__main__":
    main()
