# OPT-In Family Services Data Quality and Outcomes Dashboard

Polished work sample for a data liaison / research analyst role supporting community-based family support programs.

This project demonstrates how program and administrative referral data can be cleaned, validated, analyzed, visualized, and translated into actionable findings for non-technical stakeholders. The fictional program context is modeled after a multi-state prevention initiative serving families screened out from a child protective services hotline and connected to community-based support.

Important: all data in this repository is synthetic. It does not contain real family, child welfare, hotline, service provider, or confidential information.

## Project Objectives

- Generate a realistic synthetic referral dataset with intentional data quality issues.
- Clean and validate referral, outreach, service, flexible fund, follow-up, and outcome fields.
- Calculate operational KPIs relevant to family support implementation monitoring.
- Produce charts and dashboard specifications suitable for Power BI or Tableau.
- Write stakeholder-ready summaries that translate data findings into program action.

## Repository Structure

```text
optin-family-services-data-dashboard/
├── README.md
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── optin_analysis.ipynb
├── src/
│   ├── generate_sample_data.py
│   ├── clean_validate_data.py
│   └── analysis.py
├── reports/
│   ├── executive_summary.md
│   └── data_quality_report.md
├── dashboard/
│   └── dashboard_mockup.md
├── visuals/
├── requirements.txt
└── .gitignore
```

## Synthetic Data Fields

The generated dataset includes 774 raw rows, including intentional duplicate family IDs. The cleaned analytic file contains one validated record per family referral.

Key fields:

- `family_id`
- `site_state`
- `referral_date`
- `referral_source`
- `outreach_attempts`
- `engagement_status`
- `service_type`
- `flexible_funds_amount`
- `case_review_flag`
- `follow_up_completed`
- `outcome_status`

## Data Quality Scenarios

The raw dataset intentionally includes issues commonly found in administrative program data:

- Missing values in site, follow-up, service, and flexible fund fields.
- Duplicate `family_id` records.
- Inconsistent state names and abbreviations.
- Invalid referral dates.
- Outlier and negative flexible fund amounts.

The cleaning script standardizes states, removes invalid dates, deduplicates family IDs, fills appropriate missing values, caps extreme fund amounts for reporting, and produces a structured data quality summary.

## KPIs

The project calculates:

- Total referrals
- Engagement rate
- Outreach completion rate
- Follow-up completion rate
- Average outreach attempts
- Case review rate
- Flexible funds distribution by site
- Service type breakdown
- Outcome status by site

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate synthetic raw data:

```bash
python src/generate_sample_data.py
```

Clean and validate the data:

```bash
python src/clean_validate_data.py
```

Calculate KPIs and generate charts:

```bash
python src/analysis.py
```

## Outputs

- Raw synthetic data: `data/raw/optin_referrals_raw.csv`
- Clean analytic file: `data/processed/optin_referrals_clean.csv`
- Data quality summary: `data/processed/data_quality_summary.json`
- KPI summary: `data/processed/kpi_summary.json`
- Visuals: `visuals/*.png`
- Stakeholder reports: `reports/*.md`
- Dashboard design mockup: `dashboard/dashboard_mockup.md`

## Work Sample Relevance

This project is designed to reflect responsibilities common to a data liaison role:

- Translating program operations into measurable indicators.
- Improving data reliability before analysis.
- Communicating data limitations clearly.
- Supporting program staff with practical, decision-oriented reporting.
- Building repeatable workflows that can be adapted across sites.

## Notes for Reviewers

The focus is not predictive modeling. The focus is operational data stewardship: understanding referral pathways, service engagement, follow-up completion, flexible fund use, and site-level variation well enough to support program learning and continuous improvement.
