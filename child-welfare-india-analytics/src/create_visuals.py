"""Create portfolio-ready charts for the child welfare analytics project."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "child_welfare_cases_clean.csv"
VISUALS_DIR = PROJECT_ROOT / "visuals"

sns.set_theme(style="whitegrid", context="notebook")
PALETTE = [
    "#2f6f73",
    "#8f5b3f",
    "#4f6fb0",
    "#c97b2b",
    "#6b5b95",
    "#3d7c47",
    "#b64f58",
    "#607d8b",
    "#9c6f2e",
    "#557a95",
]


def save_chart(filename: str) -> None:
    path = VISUALS_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()


def barplot(data: pd.DataFrame, x: str, y: str, title: str, filename: str, rotation: int = 35) -> None:
    plt.figure(figsize=(10, 6))
    palette = PALETTE[: data[x].nunique()]
    sns.barplot(data=data, x=x, y=y, palette=palette, hue=x, legend=False)
    plt.title(title, fontsize=14, weight="bold")
    plt.xlabel("")
    plt.ylabel(y.replace("_", " ").title())
    plt.xticks(rotation=rotation, ha="right")
    save_chart(filename)


def main() -> None:
    VISUALS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROCESSED_PATH, parse_dates=["referral_date"])
    df["referral_month"] = pd.to_datetime(df["referral_month"])

    monthly = df.groupby("referral_month").size().reset_index(name="cases")
    plt.figure(figsize=(11, 6))
    sns.lineplot(data=monthly, x="referral_month", y="cases", marker="o", color="#2f6f73")
    plt.title("Monthly Case Trends", fontsize=14, weight="bold")
    plt.xlabel("Referral Month")
    plt.ylabel("Cases")
    save_chart("monthly_case_trends.png")

    state_volume = df["state"].value_counts().reset_index()
    state_volume.columns = ["state", "cases"]
    barplot(state_volume, "state", "cases", "State-wise Case Volume", "state_wise_case_volume.png")

    referral = df["referral_source"].value_counts().reset_index()
    referral.columns = ["referral_source", "cases"]
    barplot(referral, "referral_source", "cases", "Referral Source Breakdown", "referral_source_breakdown.png")

    risk_order = ["Low", "Medium", "High", "Critical"]
    risk = df["risk_level"].value_counts().reindex(risk_order).reset_index()
    risk.columns = ["risk_level", "cases"]
    barplot(risk, "risk_level", "cases", "Risk-level Distribution", "risk_level_distribution.png", rotation=0)

    follow_up = df.assign(completed=df["follow_up_status"].eq("Completed")).groupby("state")["completed"].mean().mul(100).reset_index()
    follow_up.columns = ["state", "completion_rate"]
    follow_up = follow_up.sort_values("completion_rate", ascending=False)
    barplot(follow_up, "state", "completion_rate", "Follow-up Completion Rate by State", "follow_up_completion_rate.png")

    response = df.groupby("state")["days_to_first_contact"].mean().reset_index().sort_values("days_to_first_contact")
    barplot(response, "state", "days_to_first_contact", "Average Response Time by State", "average_response_time_by_state.png")

    services = df["service_provided"].value_counts().reset_index()
    services.columns = ["service_provided", "cases"]
    barplot(services, "service_provided", "cases", "Service Type Utilization", "service_type_utilization.png")

    outcomes = df["outcome_category"].value_counts(normalize=True).mul(100).reset_index()
    outcomes.columns = ["outcome_category", "percentage"]
    barplot(outcomes, "outcome_category", "percentage", "Outcome Category Comparison", "outcome_category_comparison.png")

    plt.figure(figsize=(11, 6))
    sns.boxplot(data=df, x="state", y="support_amount_inr", palette=PALETTE, hue="state", legend=False)
    plt.title("Support Amount Distribution by State", fontsize=14, weight="bold")
    plt.xlabel("")
    plt.ylabel("Support Amount (INR)")
    plt.xticks(rotation=35, ha="right")
    save_chart("support_amount_distribution_by_state.png")

    print(f"Saved charts to {VISUALS_DIR}")


if __name__ == "__main__":
    main()
