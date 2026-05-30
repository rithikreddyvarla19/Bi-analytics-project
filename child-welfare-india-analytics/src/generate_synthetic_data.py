"""Generate synthetic child welfare support service records for India.

All records are artificial and are intended for analytics portfolio use only.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "synthetic_child_welfare_cases_raw.csv"

RNG = np.random.default_rng(42)

STATE_DISTRICTS = {
    "Telangana": ["Hyderabad", "Rangareddy", "Warangal", "Nizamabad", "Karimnagar"],
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Kurnool"],
    "Karnataka": ["Bengaluru Urban", "Mysuru", "Mangaluru", "Belagavi", "Dharwad"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi"],
    "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Siliguri", "Asansol"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Prayagraj"],
}

STATE_VARIANTS = {
    "Telangana": ["Telangana", "telangana", "Telengana"],
    "Andhra Pradesh": ["Andhra Pradesh", "Andhra pradesh", "AP"],
    "Karnataka": ["Karnataka", "karnataka", "Karnatka"],
    "Tamil Nadu": ["Tamil Nadu", "Tamil nadu", "TN"],
    "Maharashtra": ["Maharashtra", "maharashtra", "Maharahstra"],
    "Delhi": ["Delhi", "NCT Delhi", "delhi"],
    "West Bengal": ["West Bengal", "west bengal", "WB"],
    "Kerala": ["Kerala", "kerala", "Keralam"],
    "Rajasthan": ["Rajasthan", "rajasthan", "Rajastan"],
    "Uttar Pradesh": ["Uttar Pradesh", "UP", "Uttar pradesh"],
}

REFERRAL_SOURCES = [
    "Childline/Helpline",
    "School",
    "Community Worker",
    "Healthcare Facility",
    "Police",
    "NGO Partner",
    "Self/Family",
]
AGE_GROUPS = ["0-5", "6-10", "11-14", "15-17"]
CASE_TYPES = [
    "Education Support",
    "Health/Nutrition",
    "Protection Concern",
    "Family Reintegration",
    "Mental Health Support",
    "Emergency Shelter",
]
RISK_LEVELS = ["Low", "Medium", "High", "Critical"]
SERVICES = [
    "Counseling",
    "Education Kit",
    "Nutrition Support",
    "Medical Referral",
    "Shelter Referral",
    "Legal Aid Referral",
    "Family Counseling",
    "Cash Support",
]
FOLLOW_UP_STATUSES = ["Completed", "Pending", "In Progress", "Unable to Contact"]
CASE_STATUSES = ["Open", "Closed", "Referred", "Escalated"]
STATUS_VARIANTS = ["open", "OPEN", "closed", "Closed ", "reffered", "Escalate", "In-progress"]
OUTCOMES = [
    "Stabilized",
    "Improved Access to Services",
    "Ongoing Support Needed",
    "Referred to Specialist Agency",
    "Unable to Verify Outcome",
]


def weighted_choice(values: list[str], probabilities: list[float], size: int) -> np.ndarray:
    return RNG.choice(values, size=size, p=np.array(probabilities) / np.sum(probabilities))


def generate_records(n: int = 10_000) -> pd.DataFrame:
    states = list(STATE_DISTRICTS)
    state_probabilities = [0.09, 0.09, 0.11, 0.10, 0.13, 0.08, 0.10, 0.07, 0.10, 0.13]
    canonical_states = weighted_choice(states, state_probabilities, n)

    raw_states = [
        RNG.choice(STATE_VARIANTS[state], p=[0.84, 0.10, 0.06])
        for state in canonical_states
    ]
    districts = [RNG.choice(STATE_DISTRICTS[state]) for state in canonical_states]

    start_date = np.datetime64("2023-01-01")
    end_date = np.datetime64("2025-12-31")
    day_offsets = RNG.integers(0, (end_date - start_date).astype(int) + 1, size=n)
    referral_dates = pd.to_datetime(start_date + day_offsets.astype("timedelta64[D]"))

    risk = weighted_choice(RISK_LEVELS, [0.34, 0.38, 0.21, 0.07], n)
    first_contact = []
    support_amounts = []
    for risk_level in risk:
        if risk_level == "Critical":
            first_contact.append(max(0, int(RNG.normal(1.5, 1.2))))
            support_amounts.append(max(500, RNG.normal(8500, 2500)))
        elif risk_level == "High":
            first_contact.append(max(0, int(RNG.normal(3.0, 2.0))))
            support_amounts.append(max(300, RNG.normal(6200, 2200)))
        elif risk_level == "Medium":
            first_contact.append(max(0, int(RNG.normal(5.0, 3.0))))
            support_amounts.append(max(200, RNG.normal(4200, 1700)))
        else:
            first_contact.append(max(0, int(RNG.normal(7.0, 4.0))))
            support_amounts.append(max(100, RNG.normal(2500, 1200)))

    df = pd.DataFrame(
        {
            "case_id": [f"CWI-{i:06d}" for i in range(1, n + 1)],
            "state": raw_states,
            "district": districts,
            "referral_date": referral_dates.strftime("%Y-%m-%d"),
            "referral_source": weighted_choice(
                REFERRAL_SOURCES, [0.20, 0.18, 0.17, 0.12, 0.11, 0.14, 0.08], n
            ),
            "child_age_group": weighted_choice(AGE_GROUPS, [0.20, 0.27, 0.29, 0.24], n),
            "case_type": weighted_choice(CASE_TYPES, [0.21, 0.18, 0.20, 0.12, 0.16, 0.13], n),
            "risk_level": risk,
            "outreach_attempts": RNG.poisson(lam=2.2, size=n) + 1,
            "service_provided": weighted_choice(SERVICES, [0.18, 0.15, 0.16, 0.14, 0.09, 0.08, 0.13, 0.07], n),
            "follow_up_status": weighted_choice(FOLLOW_UP_STATUSES, [0.58, 0.17, 0.19, 0.06], n),
            "case_status": weighted_choice(CASE_STATUSES, [0.31, 0.49, 0.13, 0.07], n),
            "support_amount_inr": np.round(support_amounts, 0).astype(int),
            "days_to_first_contact": first_contact,
            "outcome_category": weighted_choice(OUTCOMES, [0.29, 0.24, 0.22, 0.17, 0.08], n),
        }
    )

    return introduce_quality_issues(df)


def introduce_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    dirty = df.copy()

    duplicate_idx = RNG.choice(dirty.index[200:], size=140, replace=False)
    source_idx = RNG.choice(dirty.index[:9000], size=140, replace=False)
    dirty.loc[duplicate_idx, "case_id"] = dirty.loc[source_idx, "case_id"].to_numpy()

    missing_district_idx = RNG.choice(dirty.index, size=280, replace=False)
    dirty.loc[missing_district_idx, "district"] = np.nan

    invalid_date_idx = RNG.choice(dirty.index, size=90, replace=False)
    invalid_values = RNG.choice(["2025-02-30", "not_available", "13/41/2024", ""], size=90)
    dirty.loc[invalid_date_idx, "referral_date"] = invalid_values

    outlier_idx = RNG.choice(dirty.index, size=55, replace=False)
    dirty.loc[outlier_idx, "support_amount_inr"] = RNG.choice(
        [0, 75_000, 95_000, 125_000, -500], size=55
    )

    bad_status_idx = RNG.choice(dirty.index, size=220, replace=False)
    dirty.loc[bad_status_idx, "case_status"] = RNG.choice(STATUS_VARIANTS, size=220)

    return dirty.sample(frac=1, random_state=42).reset_index(drop=True)


def main() -> None:
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generate_records()
    df.to_csv(RAW_PATH, index=False)
    print(f"Generated {len(df):,} synthetic records at {RAW_PATH}")


if __name__ == "__main__":
    main()
