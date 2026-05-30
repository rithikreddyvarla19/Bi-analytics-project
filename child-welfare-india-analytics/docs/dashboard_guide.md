# Dashboard Guide

## Dashboard Objective

The dashboard should help program and operations stakeholders monitor child welfare support service demand, risk, responsiveness, follow-up completion, service utilization, outcomes, and data quality.

The dashboard is based entirely on synthetic data.

## Intended Users

- Program directors
- Operations managers
- Monitoring and evaluation teams
- Data analysts
- Partner coordination teams
- Public-sector analytics reviewers

## Recommended Pages

### Page 1: Executive Overview

Purpose: Provide a high-level view of service demand and performance.

Recommended components:

- KPI strip: total cases, high-risk percentage, average days to first contact, follow-up completion rate, closure rate.
- Monthly case trend line chart.
- State-wise case volume bar chart.
- Risk-level distribution chart.
- Outcome category comparison.

Primary decisions supported:

- Is demand increasing or decreasing?
- Which states have higher case volume?
- What share of cases are high or critical risk?
- Are outcomes trending toward stabilization or ongoing support needs?

### Page 2: Operations Monitoring

Purpose: Help teams identify workflow bottlenecks and follow-up gaps.

Recommended components:

- Average response time by state.
- Follow-up completion rate by state.
- Referral source breakdown.
- Case status distribution.
- Table for cases exceeding first-contact targets.

Primary decisions supported:

- Where should operations teams focus follow-up improvement?
- Which referral channels may require stronger coordination?
- Are response times consistent across states?

### Page 3: Service and Outcome Review

Purpose: Support program evaluation and service planning.

Recommended components:

- Service type utilization.
- Outcome distribution.
- Support amount distribution by state.
- Closure rate by risk level.
- Service mix by case type.

Primary decisions supported:

- Which services are used most often?
- Are support resources distributed consistently?
- Which outcomes require deeper review?

### Page 4: Data Quality Monitor

Purpose: Make data reliability visible to reporting users.

Recommended components:

- Duplicate case IDs removed.
- Invalid dates removed.
- Missing districts retained as `Unknown District`.
- Inconsistent state spellings standardized.
- Inconsistent case status labels standardized.
- Validation pass/fail summary.

Primary decisions supported:

- Is the dataset reliable enough for recurring reporting?
- Which source fields require stronger validation controls?
- Are data quality issues improving over time?

## Global Filters

Recommended filters:

- Date range
- State
- District
- Referral source
- Risk level
- Case type
- Service provided
- Case status

## Visual Design Guidance

- Use a professional, restrained palette with clear contrast.
- Avoid excessive decorative elements.
- Keep KPI cards concise and definition-backed.
- Use tooltips for KPI definitions.
- Show synthetic-data notice in the footer.
- Use consistent state and risk-level ordering.
- Make high-risk and critical categories visually distinct.

## KPI Tooltip Text

| KPI | Suggested tooltip |
|---|---|
| Total cases | Count of unique clean synthetic case records. |
| High-risk case percentage | Share of cases marked High or Critical. |
| Average days to first contact | Mean number of days from referral to first contact. |
| Follow-up completion rate | Share of cases with follow-up status marked Completed. |
| Closure rate | Share of cases with case status marked Closed. |

## Dashboard Caveats

- The dataset is synthetic and should not be used for real-world inference.
- High-level averages should be segmented by risk level before operational targets are set.
- Closure is a workflow status and does not automatically mean a positive outcome.
- Outcome metrics depend on follow-up quality and documentation completeness.
