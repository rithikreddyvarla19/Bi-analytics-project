# KPI Definitions

## KPI Design Principles

The KPIs in this project are designed for program monitoring, operational review, and stakeholder reporting. They balance simplicity with interpretability so non-technical stakeholders can quickly understand service demand, risk, responsiveness, follow-up, and outcomes.

## Summary KPI Table

| KPI | Formula | Interpretation |
|---|---|---|
| Total cases | Count of clean records | Overall case volume after cleaning and validation. |
| Cases by state | Count of records grouped by `state` | Geographic distribution of demand. |
| Cases by referral source | Count of records grouped by `referral_source` | Intake channel distribution. |
| High-risk case percentage | `High` or `Critical` risk cases / total cases * 100 | Share of cases requiring closer prioritization. |
| Average days to first contact | Mean of `days_to_first_contact` | Average response timeliness. |
| Follow-up completion rate | Completed follow-ups / total cases * 100 | Continuity of support after initial service. |
| Service utilization by type | Count of records grouped by `service_provided` | Relative use of service categories. |
| Outcome category distribution | Count by outcome / total cases * 100 | Recorded outcome mix. |
| Support amount distribution by state | Count, mean, median, min, max by state | Financial support variation by geography. |
| Closure rate by risk level | Closed cases / cases in risk level * 100 | Workflow closure performance by risk category. |

## Detailed Definitions

### Total Cases

**Definition:** Number of unique analysis-ready case records after cleaning.

**Formula:** `count(case_id)`

**Current result:** 9,771

**Use:** Top-line demand indicator for leadership and operational planning.

### Cases by State

**Definition:** Count of clean cases grouped by state.

**Formula:** `count(case_id) by state`

**Use:** Identifies geographic concentration of demand and supports resource allocation discussions.

### Cases by Referral Source

**Definition:** Count of cases by intake channel.

**Formula:** `count(case_id) by referral_source`

**Use:** Shows which channels are driving referrals and where partnership management may matter most.

### High-risk Case Percentage

**Definition:** Share of cases classified as `High` or `Critical` risk.

**Formula:** `(count(risk_level in ['High', 'Critical']) / count(case_id)) * 100`

**Current result:** 28.47%

**Use:** Helps teams monitor prioritization burden and escalation workload.

### Average Days to First Contact

**Definition:** Average number of days between referral and first contact.

**Formula:** `mean(days_to_first_contact)`

**Current result:** 4.56 days

**Use:** Measures responsiveness. In production, this should be reviewed by risk level because urgent cases require faster contact.

### Follow-up Completion Rate

**Definition:** Share of cases with follow-up marked as completed.

**Formula:** `(count(follow_up_status == 'Completed') / count(case_id)) * 100`

**Current result:** 58.44%

**Use:** Measures continuity after service delivery. A low rate may indicate capacity constraints, engagement barriers, or documentation gaps.

### Service Utilization by Type

**Definition:** Count of cases by primary service provided.

**Formula:** `count(case_id) by service_provided`

**Use:** Supports planning for staffing, partner capacity, supplies, and referral pathways.

### Outcome Category Distribution

**Definition:** Percentage distribution of recorded outcomes.

**Formula:** `(count(case_id) by outcome_category / total cases) * 100`

**Use:** Provides a program evaluation signal, but should be interpreted alongside follow-up completeness and outcome verification practices.

### Support Amount Distribution by State

**Definition:** Summary statistics for synthetic support amounts by state.

**Formula:** `count, mean, median, min, max of support_amount_inr by state`

**Use:** Helps detect variation in financial support patterns and potential outliers.

### Closure Rate by Risk Level

**Definition:** Percentage of cases closed within each risk level.

**Formula:** `(count(case_status == 'Closed') / count(case_id within risk_level)) * 100`

**Use:** Supports workflow management. It should not be interpreted as success by itself because closure quality depends on case context and outcome verification.

## Interpretation Guardrails

- These KPIs are calculated from synthetic data only.
- KPI values do not represent real program performance.
- Closure rate is an operational workflow measure, not a standalone outcome measure.
- Outcome category distribution depends on follow-up quality.
- Average response time should be segmented by risk level before operational targets are set.

## Suggested Production Enhancements

If this were implemented in a real environment, recommended enhancements would include:

- SLA compliance by risk level.
- Follow-up aging buckets.
- Open case backlog.
- Repeat referral indicator.
- District-level drilldowns.
- Service-to-outcome pathway analysis.
- Caseworker or partner workload metrics.
- Data quality score by source system.
