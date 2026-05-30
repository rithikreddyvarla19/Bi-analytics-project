"""Clean and validate synthetic OPT-In referral data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "optin_referrals_raw.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "optin_referrals_clean.csv"
QUALITY_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "data_quality_summary.json"

STATE_MAP = {
    "illinois": "Illinois",
    "il": "Illinois",
    "ill.": "Illinois",
    "new york": "New York",
    "ny": "New York",
    "n.y.": "New York",
    "ohio": "Ohio",
    "oh": "Ohio",
    "texas": "Texas",
    "tx": "Texas",
    "washington": "Washington",
    "wa": "Washington",
    "wash.": "Washington",
}

VALID_ENGAGEMENT = {"Engaged", "Unable to contact", "Declined", "Pending outreach"}
VALID_OUTCOMES = {
    "Needs met",
    "Connected to ongoing service",
    "No response after outreach",
    "Family declined services",
    "Still active",
}


def _standardize_state(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    return STATE_MAP.get(str(value).strip().lower(), str(value).strip().title())


def _to_bool_series(series: pd.Series) -> pd.Series:
    mapped = (
        series.astype("string")
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False})
    )
    return mapped.where(mapped.notna(), False).astype(bool)


def clean_and_validate(raw_path: Path = RAW_DATA_PATH) -> tuple[pd.DataFrame, dict]:
    """Return cleaned data and a structured data quality summary."""
    df = pd.read_csv(raw_path)
    original_rows = len(df)

    quality = {
        "input_rows": int(original_rows),
        "duplicate_family_ids_detected": int(df.duplicated("family_id").sum()),
        "missing_values_by_field": {
            column: int(count) for column, count in df.isna().sum().to_dict().items()
        },
    }

    df["site_state_original"] = df["site_state"]
    df["site_state"] = df["site_state"].apply(_standardize_state)

    df["referral_date_raw"] = df["referral_date"]
    df["referral_date"] = pd.to_datetime(df["referral_date"], errors="coerce")
    invalid_date_mask = df["referral_date"].isna()
    quality["invalid_referral_dates_detected"] = int(invalid_date_mask.sum())
    df = df.loc[~invalid_date_mask].copy()

    df["flexible_funds_amount_raw"] = df["flexible_funds_amount"]
    df["flexible_funds_amount"] = pd.to_numeric(
        df["flexible_funds_amount"], errors="coerce"
    )
    quality["missing_flexible_funds_detected"] = int(
        df["flexible_funds_amount"].isna().sum()
    )
    quality["negative_fund_amounts_detected"] = int((df["flexible_funds_amount"] < 0).sum())
    quality["fund_outliers_over_1500_detected"] = int(
        (df["flexible_funds_amount"] > 1500).sum()
    )

    df["flexible_funds_amount"] = df["flexible_funds_amount"].fillna(0)
    df.loc[df["flexible_funds_amount"] < 0, "flexible_funds_amount"] = 0
    df["fund_amount_capped_flag"] = df["flexible_funds_amount"] > 1500
    df.loc[df["fund_amount_capped_flag"], "flexible_funds_amount"] = 1500

    df["outreach_attempts"] = pd.to_numeric(df["outreach_attempts"], errors="coerce").fillna(0)
    df["outreach_attempts"] = df["outreach_attempts"].clip(lower=0, upper=8).astype(int)

    df["case_review_flag"] = _to_bool_series(df["case_review_flag"])
    df["follow_up_completed"] = _to_bool_series(df["follow_up_completed"])
    df["service_type"] = df["service_type"].fillna("No service recorded")
    df["site_state"] = df["site_state"].fillna("Unknown")

    df["engagement_status_valid"] = df["engagement_status"].isin(VALID_ENGAGEMENT)
    df["outcome_status_valid"] = df["outcome_status"].isin(VALID_OUTCOMES)

    df = df.sort_values(
        ["family_id", "referral_date", "follow_up_completed"],
        ascending=[True, True, False],
    )
    df["duplicate_family_id_flag"] = df.duplicated("family_id", keep="first")
    deduped = df.loc[~df["duplicate_family_id_flag"]].copy()

    quality["rows_removed_invalid_dates"] = int(invalid_date_mask.sum())
    quality["rows_removed_duplicate_family_ids"] = int(df["duplicate_family_id_flag"].sum())
    quality["output_rows"] = int(len(deduped))
    quality["standardized_states"] = sorted(deduped["site_state"].dropna().unique().tolist())
    quality["records_requiring_case_review"] = int(deduped["case_review_flag"].sum())
    quality["records_with_capped_fund_amounts"] = int(deduped["fund_amount_capped_flag"].sum())
    quality["validation_checks"] = {
        "family_id_unique": bool(deduped["family_id"].is_unique),
        "no_invalid_referral_dates": bool(deduped["referral_date"].notna().all()),
        "no_negative_fund_amounts": bool((deduped["flexible_funds_amount"] >= 0).all()),
        "engagement_values_valid": bool(deduped["engagement_status_valid"].all()),
        "outcome_values_valid": bool(deduped["outcome_status_valid"].all()),
    }

    deduped["referral_date"] = deduped["referral_date"].dt.strftime("%Y-%m-%d")
    return deduped, quality


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=RAW_DATA_PATH)
    parser.add_argument("--output", type=Path, default=PROCESSED_DATA_PATH)
    parser.add_argument("--quality-output", type=Path, default=QUALITY_SUMMARY_PATH)
    args = parser.parse_args()

    cleaned, quality = clean_and_validate(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(args.output, index=False)
    args.quality_output.write_text(json.dumps(quality, indent=2), encoding="utf-8")

    print(f"Wrote {len(cleaned):,} cleaned records to {args.output}")
    print(f"Wrote data quality summary to {args.quality_output}")


if __name__ == "__main__":
    main()
