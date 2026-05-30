# Data Quality Report

## Purpose

This report documents the intentional data quality issues included in the synthetic OPT-In referral dataset and explains how they were addressed before analysis. The goal is to model the type of data stewardship needed when administrative data from multiple program sites is used for stakeholder reporting.

## Issues Detected

The raw dataset includes common administrative data issues:

- 24 duplicate `family_id` values.
- 10 missing `site_state` values.
- 202 missing `service_type` values.
- 18 missing `follow_up_completed` values.
- 13 missing `flexible_funds_amount` values.
- Inconsistent state names, including abbreviations and capitalization differences.
- 12 invalid referral dates that cannot be parsed into valid calendar dates.
- 8 flexible fund amounts above the reporting threshold and 1 negative fund amount.

## Cleaning Decisions

- State names were standardized to full state names.
- Invalid referral dates were removed because they cannot support time-series reporting.
- Duplicate family IDs were deduplicated after sorting by family ID, referral date, and follow-up completion.
- Missing service types were set to `No service recorded` to preserve transparency.
- Missing follow-up values were treated as `False` for operational reporting.
- Missing flexible fund amounts were set to `$0` when no amount was recorded.
- Negative flexible fund amounts were set to `$0`.
- Flexible fund amounts above `$1,500` were capped for reporting and flagged using `fund_amount_capped_flag`.

## Cleaning Results

- Input rows: 774
- Rows removed for invalid dates: 12
- Rows removed as duplicate family IDs after date cleaning: 23
- Final analytic rows: 739
- Records requiring case review: 106
- Records with capped fund amounts: 8

## Validation Checks

The cleaning script produces `data/processed/data_quality_summary.json`, which includes:

- Input and output row counts.
- Duplicate family IDs detected and removed.
- Missing values by field.
- Invalid dates detected and removed.
- Fund outliers detected and capped.
- Validation flags for uniqueness, valid dates, non-negative funds, engagement status values, and outcome status values.

## Reporting Implications

The cleaned dataset is suitable for descriptive program monitoring. However, the quality report should accompany any dashboard review because data entry completeness affects interpretation. For example, low follow-up completion may reflect either program workflow gaps or incomplete documentation. A data liaison should use these findings to support site-level troubleshooting before drawing firm conclusions about program performance.

## Recommended Data Governance Improvements

- Create a shared data dictionary across participating sites.
- Use controlled dropdown values for state, service type, engagement status, follow-up completion, and outcome status.
- Add validation rules to prevent invalid referral dates and negative fund amounts.
- Review duplicate family IDs monthly to distinguish true duplicate records from repeat referrals.
- Add a required case note or reason field when flexible fund amounts exceed a locally defined threshold.

## Confidentiality Note

This report uses only synthetic data created for a job-application work sample. It contains no real family, child welfare, hotline, provider, or confidential information.
