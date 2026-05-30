"""Calculate KPI metrics for the synthetic child welfare analytics project."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "child_welfare_cases_clean.csv"
KPI_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "kpi_summary.json"
KPI_TABLE_PATH = PROJECT_ROOT / "data" / "processed" / "kpi_summary_table.csv"


def pct(series: pd.Series) -> float:
    return round(float(series.mean() * 100), 2)


def calculate_kpis(df: pd.DataFrame) -> dict[str, object]:
    total_cases = int(len(df))
    high_risk_mask = df["risk_level"].isin(["High", "Critical"])
    completed_follow_up_mask = df["follow_up_status"].eq("Completed")
    closed_mask = df["case_status"].eq("Closed")

    return {
        "total_cases": total_cases,
        "cases_by_state": df["state"].value_counts().sort_index().to_dict(),
        "cases_by_referral_source": df["referral_source"].value_counts().to_dict(),
        "high_risk_case_percentage": pct(high_risk_mask),
        "average_days_to_first_contact": round(float(df["days_to_first_contact"].mean()), 2),
        "follow_up_completion_rate": pct(completed_follow_up_mask),
        "service_utilization_by_type": df["service_provided"].value_counts().to_dict(),
        "outcome_category_distribution": df["outcome_category"].value_counts(normalize=True).mul(100).round(2).to_dict(),
        "support_amount_distribution_by_state": df.groupby("state")["support_amount_inr"]
        .agg(["count", "mean", "median", "min", "max"])
        .round(2)
        .to_dict(orient="index"),
        "closure_rate_by_risk_level": df.groupby("risk_level")["case_status"]
        .apply(lambda status: round(float(status.eq("Closed").mean() * 100), 2))
        .to_dict(),
        "overall_closure_rate": pct(closed_mask),
    }


def flatten_kpis(kpis: dict[str, object]) -> pd.DataFrame:
    rows = [
        {"metric": "Total cases", "value": kpis["total_cases"]},
        {"metric": "High-risk case percentage", "value": f"{kpis['high_risk_case_percentage']}%"},
        {"metric": "Average days to first contact", "value": kpis["average_days_to_first_contact"]},
        {"metric": "Follow-up completion rate", "value": f"{kpis['follow_up_completion_rate']}%"},
        {"metric": "Overall closure rate", "value": f"{kpis['overall_closure_rate']}%"},
    ]
    return pd.DataFrame(rows)


def main() -> None:
    df = pd.read_csv(PROCESSED_PATH, parse_dates=["referral_date"])
    kpis = calculate_kpis(df)
    KPI_JSON_PATH.write_text(json.dumps(kpis, indent=2), encoding="utf-8")
    flatten_kpis(kpis).to_csv(KPI_TABLE_PATH, index=False)
    print(f"Saved KPI summary to {KPI_JSON_PATH}")


if __name__ == "__main__":
    main()
