from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

try:
    from common import DATA_ROOT, configure_logging, ensure_dir
except ModuleNotFoundError:
    from scripts.common import DATA_ROOT, configure_logging, ensure_dir

logger = configure_logging("ingest_to_bronze")

RAW_DATASETS = [
    "customers",
    "products",
    "orders",
    "payments",
    "returns",
    "inventory_snapshots",
    "clickstream_events",
]


def ingest_dataset(raw_root: Path, bronze_root: Path, dataset: str, ingest_date: str) -> int:
    source = raw_root / f"{dataset}.csv"
    if not source.exists():
        raise FileNotFoundError(f"Missing raw source: {source}")

    df = pd.read_csv(source)
    df["ingest_ts_utc"] = datetime.now(timezone.utc).isoformat()
    df["ingest_date"] = ingest_date

    target = bronze_root / f"domain={dataset}" / f"ingest_date={ingest_date}"
    ensure_dir(target)
    output_file = target / f"{dataset}.parquet"
    df.to_parquet(output_file, index=False)

    logger.info("Ingested %s rows from %s into %s", len(df), source.name, output_file)
    return len(df)


def main() -> None:
    raw_root = DATA_ROOT / "raw"
    bronze_root = DATA_ROOT / "bronze"
    ingest_date = datetime.utcnow().strftime("%Y-%m-%d")

    counts = {}
    for dataset in RAW_DATASETS:
        counts[dataset] = ingest_dataset(raw_root, bronze_root, dataset, ingest_date)

    counts_df = pd.DataFrame(
        [{"dataset": k, "row_count": v, "ingest_date": ingest_date} for k, v in counts.items()]
    )
    ensure_dir(DATA_ROOT / "warehouse")
    counts_df.to_csv(DATA_ROOT / "warehouse" / "bronze_ingestion_counts.csv", index=False)
    logger.info("Bronze ingestion complete for %s datasets", len(RAW_DATASETS))


if __name__ == "__main__":
    main()
