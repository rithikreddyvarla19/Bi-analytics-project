# Methodology

## Analytical Objective

The objective is to simulate a realistic child welfare support services analytics workflow using synthetic data. The methodology covers data generation, quality issue injection, cleaning, validation, KPI calculation, visualization, and reporting.

## Synthetic Data Design

The dataset is generated through `src/generate_synthetic_data.py`. It creates 10,000 synthetic case records across ten Indian states:

- Telangana
- Andhra Pradesh
- Karnataka
- Tamil Nadu
- Maharashtra
- Delhi
- West Bengal
- Kerala
- Rajasthan
- Uttar Pradesh

The generation process uses weighted random sampling to make the data feel operationally plausible. For example:

- Larger states have slightly higher synthetic case volumes.
- Referral sources are distributed across helplines, schools, community workers, healthcare facilities, police, NGO partners, and families.
- Risk levels are weighted so low and medium cases are common, while high and critical cases remain operationally significant.
- Support amounts and response times vary by risk level.

## Intentional Data Quality Issues

To demonstrate cleaning and validation skills, the raw dataset intentionally includes:

- Duplicate case IDs.
- Missing districts.
- State spelling variants and abbreviations.
- Invalid date values.
- Negative and extreme support amount outliers.
- Inconsistent case status labels.

These issues are common in real operational data environments, especially when records are collected across multiple intake channels or partner systems.

## Cleaning Methodology

The cleaning process is implemented in `src/clean_validate_data.py`.

### Deduplication

Duplicate `case_id` values are removed by keeping the first observed record. This prevents inflated case counts and ensures case-level metrics are based on unique records.

### Geographic Standardization

State spellings, capitalization differences, and abbreviations are mapped to canonical state names. Missing districts are retained as `Unknown District` rather than dropped, because missing geography is a meaningful data quality signal.

### Date Validation

Referral dates are parsed into valid date values. Records with invalid or missing referral dates are removed because time-series analysis and response-time KPIs depend on valid dates.

### Status Standardization

Case status labels are mapped to a consistent workflow vocabulary:

- `Open`
- `Closed`
- `Referred`
- `Escalated`

### Outlier Treatment

Support amounts are converted to numeric values, constrained to non-negative values, and capped at a high-end threshold. This keeps records in the dataset while preventing unrealistic synthetic outliers from distorting averages and boxplots.

## Validation Methodology

The validation step checks:

- Case IDs are unique.
- States match the expected reference list.
- Referral dates are valid.
- Support amounts are non-negative.
- Case status values are standardized.
- The reporting date range is as expected.

Validation outputs are stored in `data/processed/data_quality_summary.json`.

## KPI Methodology

KPI calculations are implemented in `src/kpi_metrics.py`. The metrics are designed to support operational review and program evaluation:

- Total cases
- Cases by state
- Cases by referral source
- High-risk case percentage
- Average days to first contact
- Follow-up completion rate
- Service utilization by type
- Outcome category distribution
- Support amount distribution by state
- Closure rate by risk level

## Visualization Methodology

Visuals are created through `src/create_visuals.py`. Charts are saved as PNG files in `visuals/` and are intended for dashboard mockups, reports, and portfolio presentation.

The visual layer focuses on:

- Trends over time.
- Geographic comparisons.
- Referral and service channel breakdowns.
- Risk profile.
- Follow-up performance.
- Response-time variation.
- Outcome distribution.

## Assumptions

- Each record represents one synthetic case referral.
- `case_id` should be unique after cleaning.
- `High` and `Critical` risk levels are grouped for the high-risk percentage KPI.
- `Completed` is the only status counted as follow-up completion.
- `Closed` is the only status counted as case closure.
- Missing districts are not removed because retaining them supports data governance reporting.

## Limitations

This methodology is designed for portfolio demonstration. The dataset is not real, and the findings are not evidence about actual services, states, districts, children, or organizations.

In a production environment, the methodology would require:

- Formal data governance approval.
- Privacy review.
- Role-based access controls.
- Audit logging.
- Source system reconciliation.
- Stakeholder validation of KPI definitions.
- Routine quality assurance and monitoring.
