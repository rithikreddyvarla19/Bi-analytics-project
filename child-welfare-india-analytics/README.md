# Child Welfare Support Services Analytics - India

## Project Overview

This portfolio project demonstrates an end-to-end public-sector analytics workflow for child welfare support services across selected Indian states. It uses a fully synthetic dataset of 10,000 case records to show how an analyst can generate controlled test data, identify data quality issues, clean and validate records, calculate operational KPIs, create reporting visuals, and translate findings into stakeholder-ready recommendations.

**Important data notice:** All data in this repository is synthetic. It does not contain real child, family, NGO, school, healthcare, police, or government records.

## Business Context

Child welfare support programs often coordinate referrals from helplines, schools, community workers, healthcare providers, police, NGO partners, and families. Program teams need timely visibility into demand, risk levels, service utilization, follow-up completion, response time, and outcomes. This project simulates that reporting environment and provides an analytics foundation suitable for executive briefings, operational review, and dashboard planning.

## Repository Structure

```text
child-welfare-india-analytics/
|-- README.md
|-- requirements.txt
|-- data/
|   |-- raw/
|   `-- processed/
|-- docs/
|   |-- project_documentation.md
|   |-- data_dictionary.md
|   |-- methodology.md
|   |-- kpi_definitions.md
|   |-- technical_runbook.md
|   |-- dashboard_guide.md
|   `-- portfolio_presentation_guide.md
|-- notebooks/
|   |-- 01_data_cleaning.ipynb
|   |-- 02_eda.ipynb
|   `-- 03_kpi_reporting.ipynb
|-- src/
|   |-- generate_synthetic_data.py
|   |-- clean_validate_data.py
|   |-- kpi_metrics.py
|   `-- create_visuals.py
|-- reports/
|   |-- executive_summary.md
|   |-- stakeholder_report.md
|   `-- data_quality_report.md
|-- dashboard/
|   `-- dashboard_wireframe.md
`-- visuals/
```

## Dataset

The raw dataset contains 10,000 synthetic referral/case records across Telangana, Andhra Pradesh, Karnataka, Tamil Nadu, Maharashtra, Delhi, West Bengal, Kerala, Rajasthan, and Uttar Pradesh.

Fields include:

- `case_id`
- `state`
- `district`
- `referral_date`
- `referral_source`
- `child_age_group`
- `case_type`
- `risk_level`
- `outreach_attempts`
- `service_provided`
- `follow_up_status`
- `case_status`
- `support_amount_inr`
- `days_to_first_contact`
- `outcome_category`

The raw data intentionally includes realistic quality issues: duplicate case IDs, missing districts, inconsistent state spellings, invalid dates, support amount outliers, and inconsistent case status labels.

## KPI Highlights

After cleaning and validation, the processed dataset contains 9,771 analysis-ready records.

- Total clean cases: 9,771
- High or critical risk cases: 28.47%
- Average days to first contact: 4.56 days
- Follow-up completion rate: 58.44%
- Overall closure rate: 48.85%
- Largest clean case volumes: Maharashtra, Uttar Pradesh, Karnataka, and West Bengal
- Most common referral source: Childline/Helpline
- Most used service type: Counseling

## Visual Outputs

The project creates PNG charts in `visuals/`:

- Monthly case trends
- State-wise case volume
- Referral source breakdown
- Risk-level distribution
- Follow-up completion rate by state
- Average response time by state
- Service type utilization
- Outcome category comparison
- Support amount distribution by state

## How to Run

```bash
pip install -r requirements.txt
python src/generate_synthetic_data.py
python src/clean_validate_data.py
python src/kpi_metrics.py
python src/create_visuals.py
```

## Analytical Workflow

1. **Synthetic data generation:** Creates controlled, realistic case records and intentionally injects known data quality issues.
2. **Cleaning and validation:** Standardizes labels, resolves duplicates, handles missing districts, removes invalid dates, and caps extreme support amount outliers.
3. **KPI reporting:** Calculates program indicators for volume, timeliness, follow-up, utilization, outcomes, and closure.
4. **Visualization:** Produces chart-ready outputs for dashboard and stakeholder communication.
5. **Reporting:** Converts metrics into executive-facing insights, data quality documentation, and program recommendations.

## Skills Demonstrated

- Data cleaning and validation
- Synthetic data generation
- KPI design and reporting
- Program evaluation analytics
- Public-sector and social-impact analytics
- Dashboard planning
- Stakeholder communication
- Python, pandas, matplotlib, seaborn, and Jupyter

## Portfolio Positioning

This project is designed as a professional work sample for analytics, data analyst, public-sector analytics, social-impact analytics, program evaluation, and reporting roles. It emphasizes not only technical execution, but also the ability to explain data quality, operational performance, and program recommendations to non-technical stakeholders.

## Detailed Documentation

The `docs/` folder contains expanded documentation for reviewers and hiring teams:

- `project_documentation.md`: complete project narrative and end-to-end workflow
- `data_dictionary.md`: field-level definitions, expected values, and cleaning rules
- `methodology.md`: synthetic data design, quality checks, and analytical assumptions
- `kpi_definitions.md`: KPI formulas, interpretation notes, and limitations
- `technical_runbook.md`: setup, execution, outputs, troubleshooting, and reproducibility
- `dashboard_guide.md`: dashboard audience, page layout, filters, and design guidance
- `portfolio_presentation_guide.md`: how to present the project in interviews and applications
