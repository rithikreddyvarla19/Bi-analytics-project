"""Generate synthetic OPT-In family services referral data.

The data produced by this script is fully synthetic and intentionally includes
known data quality issues for cleaning, validation, and reporting practice.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "optin_referrals_raw.csv"


def generate_sample_data(record_count: int = 750, seed: int = 42) -> pd.DataFrame:
    """Create synthetic referral records with realistic quality issues."""
    if record_count < 500 or record_count > 1000:
        raise ValueError("record_count must be between 500 and 1,000")

    rng = np.random.default_rng(seed)

    states_clean = ["Illinois", "New York", "Ohio", "Texas", "Washington"]
    state_variants = {
        "Illinois": ["Illinois", "IL", "illinois", "Ill."],
        "New York": ["New York", "NY", "new york", "N.Y."],
        "Ohio": ["Ohio", "OH", "ohio"],
        "Texas": ["Texas", "TX", "texas"],
        "Washington": ["Washington", "WA", "washington", "Wash."],
    }
    referral_sources = [
        "CPS hotline screened-out",
        "Community partner",
        "School",
        "Health provider",
        "Self-referral",
        "Family resource center",
    ]
    service_types = [
        "Concrete supports",
        "Parent coaching",
        "Mental health referral",
        "Housing navigation",
        "Benefits enrollment",
        "Child care support",
        "Legal aid referral",
    ]
    engagement_statuses = ["Engaged", "Unable to contact", "Declined", "Pending outreach"]
    outcome_statuses = [
        "Needs met",
        "Connected to ongoing service",
        "No response after outreach",
        "Family declined services",
        "Still active",
    ]

    start_date = pd.Timestamp("2025-01-01")
    referral_dates = start_date + pd.to_timedelta(
        rng.integers(0, 365, size=record_count), unit="D"
    )

    base_states = rng.choice(
        states_clean,
        size=record_count,
        p=[0.24, 0.18, 0.17, 0.22, 0.19],
    )
    site_states = [rng.choice(state_variants[state]) for state in base_states]

    outreach_attempts = rng.poisson(lam=2.3, size=record_count)
    outreach_attempts = np.clip(outreach_attempts, 0, 8)

    engagement_status = rng.choice(
        engagement_statuses,
        size=record_count,
        p=[0.58, 0.18, 0.12, 0.12],
    )
    follow_up_completed = [
        rng.choice([True, False], p=[0.77, 0.23])
        if status in {"Engaged", "Declined"}
        else rng.choice([True, False], p=[0.22, 0.78])
        for status in engagement_status
    ]
    case_review_flag = [
        rng.choice([True, False], p=[0.28, 0.72])
        if attempts >= 4 or status == "Pending outreach"
        else rng.choice([True, False], p=[0.08, 0.92])
        for attempts, status in zip(outreach_attempts, engagement_status)
    ]

    service_type = [
        rng.choice(service_types)
        if status == "Engaged"
        else rng.choice(service_types + [None], p=[0.06] * len(service_types) + [0.58])
        for status in engagement_status
    ]

    funds = []
    for service in service_type:
        if service is None:
            funds.append(0.0)
            continue
        if service in {"Concrete supports", "Housing navigation", "Child care support"}:
            funds.append(round(float(rng.gamma(shape=2.1, scale=145)), 2))
        else:
            funds.append(round(float(rng.gamma(shape=1.5, scale=65)), 2))

    outcome_status = []
    for status, follow_up in zip(engagement_status, follow_up_completed):
        if status == "Engaged" and follow_up:
            outcome_status.append(
                rng.choice(
                    ["Needs met", "Connected to ongoing service", "Still active"],
                    p=[0.43, 0.37, 0.20],
                )
            )
        elif status == "Declined":
            outcome_status.append("Family declined services")
        elif status == "Unable to contact":
            outcome_status.append("No response after outreach")
        else:
            outcome_status.append(rng.choice(["Still active", "No response after outreach"]))

    df = pd.DataFrame(
        {
            "family_id": [f"FAM-{100000 + i}" for i in range(record_count)],
            "site_state": site_states,
            "referral_date": referral_dates.strftime("%Y-%m-%d"),
            "referral_source": rng.choice(referral_sources, size=record_count),
            "outreach_attempts": outreach_attempts,
            "engagement_status": engagement_status,
            "service_type": service_type,
            "flexible_funds_amount": funds,
            "case_review_flag": case_review_flag,
            "follow_up_completed": follow_up_completed,
            "outcome_status": outcome_status,
        }
    )

    # Intentional data quality issues.
    duplicate_rows = df.sample(n=24, random_state=seed).copy()
    duplicate_rows["referral_source"] = rng.choice(referral_sources, size=len(duplicate_rows))
    df = pd.concat([df, duplicate_rows], ignore_index=True)

    missing_service_idx = rng.choice(df.index, size=22, replace=False)
    df.loc[missing_service_idx, "service_type"] = np.nan

    df["follow_up_completed"] = df["follow_up_completed"].astype("object")
    missing_follow_up_idx = rng.choice(df.index, size=18, replace=False)
    df.loc[missing_follow_up_idx, "follow_up_completed"] = np.nan

    missing_state_idx = rng.choice(df.index, size=10, replace=False)
    df.loc[missing_state_idx, "site_state"] = np.nan

    invalid_date_idx = rng.choice(df.index, size=12, replace=False)
    invalid_dates = ["2025-02-30", "not available", "13/15/2025", "2026-99-01"]
    df.loc[invalid_date_idx, "referral_date"] = rng.choice(
        invalid_dates, size=len(invalid_date_idx)
    )

    outlier_idx = rng.choice(df.index, size=9, replace=False)
    df.loc[outlier_idx, "flexible_funds_amount"] = rng.choice(
        [2500, 3750, 5000, -125], size=len(outlier_idx)
    )

    missing_funds_idx = rng.choice(df.index, size=13, replace=False)
    df.loc[missing_funds_idx, "flexible_funds_amount"] = np.nan

    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=750)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=RAW_DATA_PATH)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df = generate_sample_data(record_count=args.records, seed=args.seed)
    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df):,} synthetic records to {args.output}")


if __name__ == "__main__":
    main()
