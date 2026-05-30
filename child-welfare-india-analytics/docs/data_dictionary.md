# Data Dictionary

## Dataset Overview

The project uses synthetic case-level records representing child welfare support service referrals across selected Indian states. The raw dataset contains intentional quality issues. The processed dataset is cleaned and analysis-ready.

## Data Files

| File | Description |
|---|---|
| `data/raw/synthetic_child_welfare_cases_raw.csv` | Raw synthetic dataset with 10,000 records and intentional data quality issues. |
| `data/processed/child_welfare_cases_clean.csv` | Cleaned dataset after deduplication, standardization, invalid date removal, and outlier handling. |
| `data/processed/data_quality_issues.csv` | Summary of issues found and actions taken. |
| `data/processed/kpi_summary.json` | KPI outputs in structured JSON format. |

## Field Definitions

| Field | Type | Description | Example values |
|---|---|---|---|
| `case_id` | String | Synthetic unique case identifier after cleaning. | `CWI-000001` |
| `state` | String | Indian state or territory where the case is associated. | `Telangana`, `Maharashtra`, `Delhi` |
| `district` | String | District associated with the case. Missing raw values are retained as `Unknown District` after cleaning. | `Hyderabad`, `Pune`, `Unknown District` |
| `referral_date` | Date | Date the case was referred. Invalid raw dates are removed during cleaning. | `2024-08-14` |
| `referral_source` | String | Channel through which the case entered the support workflow. | `Childline/Helpline`, `School`, `NGO Partner` |
| `child_age_group` | String | Synthetic age band. Does not identify any individual. | `0-5`, `6-10`, `11-14`, `15-17` |
| `case_type` | String | Primary support need or referral category. | `Education Support`, `Health/Nutrition`, `Protection Concern` |
| `risk_level` | String | Operational risk prioritization category. | `Low`, `Medium`, `High`, `Critical` |
| `outreach_attempts` | Integer | Number of attempted contacts or outreach events. | `1`, `3`, `5` |
| `service_provided` | String | Main service recorded for the case. | `Counseling`, `Nutrition Support`, `Medical Referral` |
| `follow_up_status` | String | Status of post-service follow-up. | `Completed`, `Pending`, `In Progress`, `Unable to Contact` |
| `case_status` | String | Current workflow status after standardization. | `Open`, `Closed`, `Referred`, `Escalated` |
| `support_amount_inr` | Integer | Synthetic support amount in Indian rupees. Extreme values are capped in the clean dataset. | `2500`, `6200`, `11049` |
| `days_to_first_contact` | Numeric | Days from referral to first contact. Values are clipped to a reasonable analytical range. | `0`, `4`, `9` |
| `outcome_category` | String | Recorded outcome category. | `Stabilized`, `Ongoing Support Needed` |
| `referral_month` | String | Month derived from `referral_date` for trend reporting. Present in processed data. | `2025-04` |
| `data_is_synthetic` | Boolean | Flag confirming records are synthetic. Present in processed data. | `True` |

## Expected State Values

The cleaned dataset standardizes all state values to:

- Andhra Pradesh
- Delhi
- Karnataka
- Kerala
- Maharashtra
- Rajasthan
- Tamil Nadu
- Telangana
- Uttar Pradesh
- West Bengal

## Expected Case Status Values

The cleaned dataset standardizes case status to:

- `Open`
- `Closed`
- `Referred`
- `Escalated`

## Intentional Raw Data Quality Issues

The raw dataset includes:

- Duplicate case IDs.
- Missing district values.
- Inconsistent state spellings and abbreviations.
- Invalid referral dates.
- Negative or extreme support amounts.
- Inconsistent case status labels.

## Cleaning Rules

| Issue | Cleaning rule |
|---|---|
| Duplicate `case_id` | Drop duplicates and keep first observed record. |
| Missing `district` | Replace missing values with `Unknown District`. |
| Inconsistent `state` | Map spelling variants and abbreviations to canonical state names. |
| Invalid `referral_date` | Remove records with invalid or missing dates. |
| Inconsistent `case_status` | Map variants to standard workflow labels. |
| Outlier `support_amount_inr` | Clip negative values to zero and cap extreme high values. |
| `days_to_first_contact` | Clip to a reasonable non-negative analytical range. |

## Data Limitations

The dataset is synthetic and is not suitable for real-world child welfare inference. Values, distributions, geography, case types, outcomes, and support amounts were generated for analytics demonstration only.
