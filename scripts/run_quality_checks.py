from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

try:
    from common import DATA_ROOT, OUTPUT_ROOT, configure_logging, ensure_dir
except ModuleNotFoundError:
    from scripts.common import DATA_ROOT, OUTPUT_ROOT, configure_logging, ensure_dir

logger = configure_logging("quality_checks")


def _result(dataset: str, expectation: str, success: bool, unexpected_percent: float = 0.0) -> dict[str, object]:
    return {
        "dataset": dataset,
        "expectation": expectation,
        "success": bool(success),
        "unexpected_percent": round(float(unexpected_percent), 4),
    }


def non_null_check(df: pd.DataFrame, dataset: str, column: str) -> dict[str, object]:
    nulls = df[column].isna().sum() if column in df.columns else len(df)
    unexpected_percent = (nulls / max(len(df), 1)) * 100
    return _result(dataset, f"non_null_{column}", nulls == 0, unexpected_percent)


def unique_check(df: pd.DataFrame, dataset: str, column: str) -> dict[str, object]:
    duplicated = df[column].duplicated().sum() if column in df.columns else len(df)
    unexpected_percent = (duplicated / max(len(df), 1)) * 100
    return _result(dataset, f"unique_{column}", duplicated == 0, unexpected_percent)


def positive_check(df: pd.DataFrame, dataset: str, column: str, strict: bool = False) -> dict[str, object]:
    if column not in df.columns:
        return _result(dataset, f"{column}_exists", False, 100)
    invalid = (df[column] <= 0).sum() if strict else (df[column] < 0).sum()
    unexpected_percent = (invalid / max(len(df), 1)) * 100
    comparator = "positive" if strict else "non_negative"
    return _result(dataset, f"{column}_{comparator}", invalid == 0, unexpected_percent)


def run_checks(df: pd.DataFrame, dataset: str) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []

    keys = {
        "fact_orders": ["order_id", "order_line_id"],
        "fact_payments": ["payment_id", "order_id"],
        "fact_returns": ["return_id", "order_id"],
        "fact_web_events": ["event_id"],
        "fact_inventory": ["product_id", "snapshot_date"],
    }

    for key in keys.get(dataset, []):
        results.append(non_null_check(df, dataset, key))
    unique_keys = {
        "fact_orders": "order_line_id",
        "fact_payments": "payment_id",
        "fact_returns": "return_id",
        "fact_web_events": "event_id",
    }
    if dataset in unique_keys:
        results.append(unique_check(df, dataset, unique_keys[dataset]))

    if "order_amount" in df.columns:
        results.append(positive_check(df, dataset, "order_amount", strict=False))
    if "item_quantity" in df.columns:
        results.append(positive_check(df, dataset, "item_quantity", strict=True))
    if "refund_amount" in df.columns:
        results.append(positive_check(df, dataset, "refund_amount", strict=False))
    if "on_hand_qty" in df.columns:
        results.append(positive_check(df, dataset, "on_hand_qty", strict=False))

    return results


def main() -> None:
    warehouse_root = DATA_ROOT / "warehouse"
    ensure_dir(OUTPUT_ROOT / "quality")
    ensure_dir(OUTPUT_ROOT / "observability")

    table_names = [
        "fact_orders",
        "fact_payments",
        "fact_returns",
        "fact_web_events",
        "fact_inventory",
        "dim_customers",
        "dim_products",
        "dim_date",
        "dim_region",
        "dim_channel",
    ]

    report_rows: list[dict[str, object]] = []
    row_counts: list[dict[str, object]] = []

    for table in table_names:
        csv_path = warehouse_root / f"{table}.csv"
        if not csv_path.exists():
            logger.warning("Skipping quality for missing table: %s", table)
            continue

        df = pd.read_csv(csv_path)
        row_counts.append({"dataset": table, "row_count": int(len(df))})
        report_rows.extend(run_checks(df, table))

    fact_orders_path = warehouse_root / "fact_orders.csv"
    fact_returns_path = warehouse_root / "fact_returns.csv"
    if fact_orders_path.exists() and fact_returns_path.exists():
        fact_orders = pd.read_csv(fact_orders_path)
        fact_returns = pd.read_csv(fact_returns_path)
        return_rate = fact_returns["order_id"].nunique() / max(fact_orders["order_id"].nunique(), 1)
        report_rows.append(
            _result("global", "refund_rate_below_threshold_0.25", return_rate <= 0.25, max(return_rate - 0.25, 0) * 100)
        )

    quality_df = pd.DataFrame(report_rows)
    counts_df = pd.DataFrame(row_counts)

    quality_df.to_csv(OUTPUT_ROOT / "quality" / "data_quality_report.csv", index=False)
    counts_df.to_csv(OUTPUT_ROOT / "observability" / "stage_row_counts.csv", index=False)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checks_total": int(len(quality_df)),
        "checks_passed": int(quality_df["success"].sum()) if not quality_df.empty else 0,
        "checks_failed": int((~quality_df["success"]).sum()) if not quality_df.empty else 0,
    }
    (OUTPUT_ROOT / "quality" / "quality_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.info("Quality checks completed: %s", summary)


if __name__ == "__main__":
    main()

