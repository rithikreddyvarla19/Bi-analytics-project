"""Clean and validate synthetic child welfare support service data."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "synthetic_child_welfare_cases_raw.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "child_welfare_cases_clean.csv"
QUALITY_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "data_quality_summary.json"
QUALITY_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "data_quality_issues.csv"

STATE_MAP = {
    "telangana": "Telangana",
    "telengana": "Telangana",
    "andhra pradesh": "Andhra Pradesh",
    "andhra pradesh": "Andhra Pradesh",
    "ap": "Andhra Pradesh",
    "karnataka": "Karnataka",
    "karnatka": "Karnataka",
    "tamil nadu": "Tamil Nadu",
    "tamil nadu": "Tamil Nadu",
    "tn": "Tamil Nadu",
    "maharashtra": "Maharashtra",
    "maharahstra": "Maharashtra",
    "delhi": "Delhi",
    "nct delhi": "Delhi",
    "west bengal": "West Bengal",
    "wb": "West Bengal",
    "kerala": "Kerala",
    "keralam": "Kerala",
    "rajasthan": "Rajasthan",
    "rajastan": "Rajasthan",
    "uttar pradesh": "Uttar Pradesh",
    "up": "Uttar Pradesh",
}

STATUS_MAP = {
    "open": "Open",
    "closed": "Closed",
    "closed ": "Closed",
    "referred": "Referred",
    "reffered": "Referred",
    "escalated": "Escalated",
    "escalate": "Escalated",
    "in-progress": "Open",
}

EXPECTED_STATES = {
    "Telangana",
    "Andhra Pradesh",
    "Karnataka",
    "Tamil Nadu",
    "Maharashtra",
    "Delhi",
    "West Bengal",
    "Kerala",
    "Rajasthan",
    "Uttar Pradesh",
}


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def issue_record(issue: str, before: int, after: int, action: str) -> dict[str, object]:
    return {
        "issue": issue,
        "records_affected_before_cleaning": int(before),
        "records_remaining_after_cleaning": int(after),
        "action_taken": action,
    }


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, object]], dict[str, object]]:
    quality_issues: list[dict[str, object]] = []
    cleaned = df.copy()
    initial_rows = len(cleaned)

    duplicate_before = cleaned.duplicated("case_id").sum()
    cleaned = cleaned.sort_values("case_id").drop_duplicates("case_id", keep="first")
    duplicate_after = cleaned.duplicated("case_id").sum()
    quality_issues.append(
        issue_record(
            "Duplicate case IDs",
            duplicate_before,
            duplicate_after,
            "Dropped duplicate case_id records, keeping the first observed record.",
        )
    )

    missing_district_before = cleaned["district"].isna().sum() + (cleaned["district"].astype(str).str.strip() == "").sum()
    cleaned["district"] = cleaned["district"].fillna("Unknown District").replace("", "Unknown District")
    missing_district_after = (cleaned["district"] == "Unknown District").sum()
    quality_issues.append(
        issue_record(
            "Missing district values",
            missing_district_before,
            missing_district_after,
            "Imputed missing districts as Unknown District for transparent reporting.",
        )
    )

    state_before = cleaned["state"].map(
        lambda value: STATE_MAP.get(normalize_text(value).lower(), normalize_text(value)) != normalize_text(value)
    ).sum()
    cleaned["state"] = cleaned["state"].map(lambda value: STATE_MAP.get(normalize_text(value).lower(), normalize_text(value)))
    state_after = (~cleaned["state"].isin(EXPECTED_STATES)).sum()
    quality_issues.append(
        issue_record(
            "Inconsistent state spellings",
            state_before,
            state_after,
            "Standardized state spelling and abbreviations to canonical state names.",
        )
    )

    parsed_dates = pd.to_datetime(cleaned["referral_date"], errors="coerce", format="mixed")
    invalid_dates_before = parsed_dates.isna().sum()
    cleaned["referral_date"] = parsed_dates
    cleaned = cleaned.dropna(subset=["referral_date"])
    invalid_dates_after = cleaned["referral_date"].isna().sum()
    quality_issues.append(
        issue_record(
            "Invalid referral dates",
            invalid_dates_before,
            invalid_dates_after,
            "Removed records with invalid or missing referral dates.",
        )
    )

    status_before = cleaned["case_status"].map(
        lambda value: STATUS_MAP.get(normalize_text(value).lower(), normalize_text(value).title()) != normalize_text(value)
    ).sum()
    cleaned["case_status"] = cleaned["case_status"].map(
        lambda value: STATUS_MAP.get(normalize_text(value).lower(), normalize_text(value).title())
    )
    status_after = (~cleaned["case_status"].isin(["Open", "Closed", "Referred", "Escalated"])).sum()
    quality_issues.append(
        issue_record(
            "Inconsistent case status labels",
            status_before,
            status_after,
            "Mapped common misspellings, whitespace, and capitalization variants to standard labels.",
        )
    )

    amount = pd.to_numeric(cleaned["support_amount_inr"], errors="coerce")
    outlier_mask = (amount < 0) | (amount > amount.quantile(0.995))
    outliers_before = outlier_mask.sum()
    cap_value = amount[~outlier_mask].quantile(0.99)
    cleaned["support_amount_inr"] = amount.clip(lower=0, upper=cap_value).round(0).astype(int)
    outliers_after = ((cleaned["support_amount_inr"] < 0) | (cleaned["support_amount_inr"] > cap_value)).sum()
    quality_issues.append(
        issue_record(
            "Outlier support amounts",
            outliers_before,
            outliers_after,
            f"Capped negative and extreme support amounts to a non-negative range with an upper cap of INR {cap_value:,.0f}.",
        )
    )

    cleaned["days_to_first_contact"] = pd.to_numeric(cleaned["days_to_first_contact"], errors="coerce")
    cleaned["days_to_first_contact"] = cleaned["days_to_first_contact"].clip(lower=0, upper=60)
    cleaned["outreach_attempts"] = pd.to_numeric(cleaned["outreach_attempts"], errors="coerce").fillna(0).astype(int)
    cleaned["referral_month"] = cleaned["referral_date"].dt.to_period("M").astype(str)
    cleaned["data_is_synthetic"] = True

    summary = {
        "initial_rows": int(initial_rows),
        "clean_rows": int(len(cleaned)),
        "rows_removed": int(initial_rows - len(cleaned)),
        "duplicate_case_ids_removed": int(duplicate_before),
        "invalid_dates_removed": int(invalid_dates_before),
        "missing_districts_flagged_unknown": int(missing_district_after),
        "synthetic_data_notice": "This dataset is fully synthetic and contains no real child, family, NGO, or government records.",
    }

    return cleaned.reset_index(drop=True), quality_issues, summary


def validate_clean_data(df: pd.DataFrame) -> dict[str, object]:
    return {
        "unique_case_id": bool(df["case_id"].is_unique),
        "states_in_expected_list": bool(df["state"].isin(EXPECTED_STATES).all()),
        "referral_dates_valid": bool(df["referral_date"].notna().all()),
        "support_amount_non_negative": bool((df["support_amount_inr"] >= 0).all()),
        "case_status_values": sorted(df["case_status"].dropna().unique().tolist()),
        "date_range": {
            "min": str(df["referral_date"].min().date()),
            "max": str(df["referral_date"].max().date()),
        },
    }


def main() -> None:
    df = pd.read_csv(RAW_PATH)
    cleaned, issues, summary = clean_data(df)
    validation = validate_clean_data(cleaned)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(PROCESSED_PATH, index=False)
    pd.DataFrame(issues).to_csv(QUALITY_CSV_PATH, index=False)
    QUALITY_JSON_PATH.write_text(
        json.dumps({"summary": summary, "validation": validation, "issues": issues}, indent=2),
        encoding="utf-8",
    )
    print(f"Saved clean dataset with {len(cleaned):,} records to {PROCESSED_PATH}")
    print(f"Saved data quality summary to {QUALITY_JSON_PATH}")


if __name__ == "__main__":
    main()
