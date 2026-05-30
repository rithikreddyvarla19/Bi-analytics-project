"""Calculate OPT-In KPIs and generate stakeholder-ready visuals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "optin_referrals_clean.csv"
KPI_PATH = PROJECT_ROOT / "data" / "processed" / "kpi_summary.json"
VISUALS_DIR = PROJECT_ROOT / "visuals"


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate program monitoring KPIs for reporting."""
    engaged = df["engagement_status"].eq("Engaged")
    outreach_completed = df["outreach_attempts"].ge(2)

    kpis = {
        "total_referrals": int(len(df)),
        "engagement_rate": round(float(engaged.mean()), 3),
        "outreach_completion_rate": round(float(outreach_completed.mean()), 3),
        "follow_up_completion_rate": round(float(df["follow_up_completed"].mean()), 3),
        "average_outreach_attempts": round(float(df["outreach_attempts"].mean()), 2),
        "case_review_rate": round(float(df["case_review_flag"].mean()), 3),
        "total_flexible_funds": round(float(df["flexible_funds_amount"].sum()), 2),
        "average_flexible_funds_per_referral": round(
            float(df["flexible_funds_amount"].mean()), 2
        ),
        "flexible_funds_distribution_by_site": {
            site: round(float(amount), 2)
            for site, amount in df.groupby("site_state")["flexible_funds_amount"]
            .sum()
            .sort_values(ascending=False)
            .to_dict()
            .items()
        },
        "service_type_breakdown": {
            service: int(count)
            for service, count in df["service_type"].value_counts().to_dict().items()
        },
        "outcome_status_by_site": {
            site: outcomes
            for site, outcomes in pd.crosstab(
                df["site_state"], df["outcome_status"]
            ).to_dict(orient="index").items()
        },
    }
    return kpis


def save_bar_chart(series: pd.Series, title: str, xlabel: str, ylabel: str, path: Path) -> None:
    """Save a clean horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(9, 5.5))
    series.sort_values().plot(kind="barh", ax=ax, color="#2F6F73")
    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def create_visuals(df: pd.DataFrame, visuals_dir: Path = VISUALS_DIR) -> None:
    """Create chart assets for the dashboard mockup and reports."""
    visuals_dir.mkdir(parents=True, exist_ok=True)

    engagement_by_site = (
        df.assign(engaged=df["engagement_status"].eq("Engaged"))
        .groupby("site_state")["engaged"]
        .mean()
        .mul(100)
        .round(1)
    )
    save_bar_chart(
        engagement_by_site,
        "Engagement Rate by Site",
        "Engagement rate (%)",
        "Site",
        visuals_dir / "engagement_rate_by_site.png",
    )

    funds_by_site = df.groupby("site_state")["flexible_funds_amount"].sum().round(0)
    save_bar_chart(
        funds_by_site,
        "Flexible Funds Distributed by Site",
        "Funds distributed ($)",
        "Site",
        visuals_dir / "flexible_funds_by_site.png",
    )

    service_breakdown = df["service_type"].value_counts()
    save_bar_chart(
        service_breakdown,
        "Service Type Breakdown",
        "Referrals",
        "Service type",
        visuals_dir / "service_type_breakdown.png",
    )

    outcome_by_site = pd.crosstab(df["site_state"], df["outcome_status"])
    fig, ax = plt.subplots(figsize=(10, 6))
    outcome_by_site.plot(kind="bar", stacked=True, ax=ax, colormap="tab20c")
    ax.set_title("Outcome Status by Site", fontsize=14, pad=12)
    ax.set_xlabel("Site")
    ax.set_ylabel("Referrals")
    ax.legend(title="Outcome", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(visuals_dir / "outcome_status_by_site.png", dpi=160)
    plt.close(fig)

    monthly_referrals = (
        pd.to_datetime(df["referral_date"])
        .dt.to_period("M")
        .value_counts()
        .sort_index()
    )
    monthly_referrals.index = monthly_referrals.index.astype(str)
    fig, ax = plt.subplots(figsize=(10, 5))
    monthly_referrals.plot(kind="line", marker="o", ax=ax, color="#5B5F97")
    ax.set_title("Monthly Referral Volume", fontsize=14, pad=12)
    ax.set_xlabel("Referral month")
    ax.set_ylabel("Referrals")
    ax.grid(alpha=0.25)
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    fig.savefig(visuals_dir / "monthly_referral_volume.png", dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=PROCESSED_DATA_PATH)
    parser.add_argument("--kpi-output", type=Path, default=KPI_PATH)
    parser.add_argument("--visuals-dir", type=Path, default=VISUALS_DIR)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    kpis = calculate_kpis(df)
    args.kpi_output.write_text(json.dumps(kpis, indent=2), encoding="utf-8")
    create_visuals(df, args.visuals_dir)

    print(f"Wrote KPI summary to {args.kpi_output}")
    print(f"Wrote visuals to {args.visuals_dir}")


if __name__ == "__main__":
    main()
