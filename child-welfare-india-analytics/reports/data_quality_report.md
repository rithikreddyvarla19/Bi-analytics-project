# Data Quality Report

## Scope

This report documents the quality checks applied to the synthetic child welfare support services dataset. The raw dataset contains 10,000 records. After cleaning, the processed dataset contains 9,771 records.

**Data notice:** This project uses synthetic data only. No real child, family, NGO, or government records are included.

## Issues Identified and Actions Taken

| Data quality issue | Records affected before cleaning | Records remaining after cleaning | Action taken |
|---|---:|---:|---|
| Duplicate case IDs | 139 | 0 | Dropped duplicate `case_id` records, keeping the first observed record. |
| Missing district values | 276 | 276 | Imputed missing districts as `Unknown District` so geography gaps remain visible in reporting. |
| Inconsistent state spellings | 1,595 | 0 | Standardized spelling, capitalization, and abbreviations to canonical state names. |
| Invalid referral dates | 90 | 0 | Removed records with invalid or missing referral dates. |
| Inconsistent case status labels | 187 | 0 | Mapped misspellings, whitespace, capitalization, and alternate labels to standard case statuses. |
| Outlier support amounts | 56 | 0 | Capped negative and extreme support amounts to a non-negative range with an upper cap of INR 11,049. |

## Validation Results

The final processed dataset passed the following checks:

- `case_id` is unique.
- All state values are in the expected ten-state reference list.
- Referral dates are valid and fall between January 1, 2023 and December 31, 2025.
- Support amounts are non-negative.
- Case status values are standardized to `Open`, `Closed`, `Referred`, and `Escalated`.

## Cleaning Approach

The cleaning process balances analytical usability with transparency. Records with invalid dates were removed because monthly trend and response-time reporting depend on valid referral dates. Duplicate case IDs were removed to avoid overstating volume. Missing districts were retained as `Unknown District` rather than dropped, because missing geography is itself an operational data quality signal.

Support amount outliers were capped instead of removed. This preserves case records while reducing the influence of unrealistic synthetic values on state-level distribution analysis.

## Recommended Data Governance Controls

- Enforce unique case IDs at the point of data entry.
- Use dropdowns or reference tables for state, district, case status, risk level, service type, and outcome category.
- Apply date validation before records are accepted into reporting tables.
- Flag missing districts for follow-up rather than silently excluding them.
- Create automated monthly data quality checks and publish a short exception report alongside KPI dashboards.
