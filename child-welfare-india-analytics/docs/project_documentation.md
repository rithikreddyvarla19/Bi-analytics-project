# Project Documentation

## Project Title

Child Welfare Support Services Analytics - India

## Purpose

This project is an end-to-end analytics portfolio case study built around a fully synthetic child welfare support services dataset. It demonstrates how a data analyst can move from raw operational records to cleaned data, validated outputs, KPI reporting, charts, dashboard planning, and stakeholder recommendations.

The project is designed for public-sector analytics, social-impact analytics, program evaluation, nonprofit operations, and data reporting roles.

## Data Ethics Statement

All records in this repository are synthetic. The dataset does not include real child, family, NGO, school, healthcare, police, or government records. The project should not be used to infer actual child welfare conditions or program performance in India.

The synthetic data is intentionally realistic enough to support analytics practice, while avoiding any personally identifiable information or sensitive case narratives.

## Business Scenario

A child welfare support program receives referrals from several channels, including helplines, schools, community workers, healthcare facilities, police, NGO partners, and families. Program managers need to understand:

- Where case demand is concentrated.
- Which referral sources generate the most cases.
- What share of cases are high or critical risk.
- How quickly teams make first contact.
- Whether follow-up is being completed.
- Which services are used most often.
- What outcomes are being recorded.
- Whether data quality is strong enough for routine reporting.

This project simulates that environment through a controlled dataset and a reproducible Python workflow.

## End-to-End Workflow

1. Generate a synthetic raw dataset with 10,000 records.
2. Inject realistic data quality issues into the raw dataset.
3. Clean and standardize records.
4. Validate the processed dataset.
5. Calculate KPIs for program performance and operational review.
6. Create visualizations for dashboarding and stakeholder communication.
7. Produce written reports for technical and non-technical audiences.
8. Document methodology, formulas, assumptions, and limitations.

## Project Components

### Data

- `data/raw/synthetic_child_welfare_cases_raw.csv`: synthetic source dataset with intentional quality issues.
- `data/processed/child_welfare_cases_clean.csv`: cleaned analysis-ready dataset.
- `data/processed/data_quality_summary.json`: structured data quality and validation summary.
- `data/processed/data_quality_issues.csv`: tabular quality issue log.
- `data/processed/kpi_summary.json`: KPI output used for reporting.
- `data/processed/kpi_summary_table.csv`: compact KPI table.

### Source Code

- `src/generate_synthetic_data.py`: creates synthetic data and injects quality issues.
- `src/clean_validate_data.py`: standardizes fields, removes invalid records, handles outliers, and validates output.
- `src/kpi_metrics.py`: calculates core KPI metrics.
- `src/create_visuals.py`: creates chart images for dashboard and reporting use.

### Notebooks

- `notebooks/01_data_cleaning.ipynb`: data profiling and cleaning review.
- `notebooks/02_eda.ipynb`: exploratory analysis of trends and distributions.
- `notebooks/03_kpi_reporting.ipynb`: KPI reporting and interpretation.

### Reports

- `reports/executive_summary.md`: concise leadership summary.
- `reports/data_quality_report.md`: quality issues, fixes, and governance recommendations.
- `reports/stakeholder_report.md`: operational findings and recommendations.

### Dashboard Planning

- `dashboard/dashboard_wireframe.md`: recommended dashboard pages, filters, metrics, and layout.
- `docs/dashboard_guide.md`: expanded dashboard design and usage guidance.

## Core Results

The raw dataset contains 10,000 synthetic records. After cleaning, the processed dataset contains 9,771 records.

Headline KPIs:

- Total clean cases: 9,771
- High or critical risk cases: 28.47%
- Average days to first contact: 4.56 days
- Follow-up completion rate: 58.44%
- Overall closure rate: 48.85%
- Most common referral source: Childline/Helpline
- Most used service type: Counseling

## Value Demonstrated

This project demonstrates both technical and stakeholder-facing analytics skills:

- Building synthetic data for a sensitive domain.
- Designing intentional data quality issues for cleaning practice.
- Creating repeatable Python data workflows.
- Validating data before reporting.
- Translating operational data into KPIs.
- Producing dashboard-ready visuals.
- Writing polished executive and stakeholder reports.
- Explaining limitations and ethical boundaries clearly.

## Intended Review Path

For a hiring manager or reviewer, the recommended review order is:

1. Read `README.md`.
2. Review `reports/executive_summary.md`.
3. Skim `docs/data_dictionary.md` and `docs/kpi_definitions.md`.
4. Open charts in `visuals/`.
5. Review scripts in `src/`.
6. Open notebooks for exploratory workflow details.
