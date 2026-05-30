# Dashboard Wireframe

## Dashboard Title

Child Welfare Support Services Analytics - India

## Audience

Program leadership, operations managers, monitoring and evaluation staff, and partner coordination teams.

## Global Filters

- Date range
- State
- District
- Referral source
- Risk level
- Case type
- Service provided
- Case status

## Top KPI Strip

| KPI | Definition |
|---|---|
| Total cases | Count of unique clean case records |
| High-risk case percentage | Share of cases with `High` or `Critical` risk level |
| Average days to first contact | Mean days between referral and first contact |
| Follow-up completion rate | Share of cases with completed follow-up |
| Closure rate | Share of cases with `Closed` status |

## Page 1: Executive Overview

Recommended layout:

1. KPI strip across the top.
2. Monthly case trend line chart.
3. State-wise case volume bar chart.
4. Risk-level distribution chart.
5. Outcome category comparison chart.

Primary questions answered:

- Is case volume increasing or decreasing?
- Which states have the highest service demand?
- What share of cases require higher-priority response?
- What outcomes are being recorded most often?

## Page 2: Operations Monitoring

Recommended layout:

1. Average response time by state.
2. Follow-up completion rate by state.
3. Referral source breakdown.
4. Open, referred, escalated, and closed case counts.
5. Table of cases exceeding first-contact target, grouped by risk level.

Primary questions answered:

- Where is response time slower?
- Which states or referral sources have lower follow-up completion?
- Are high-risk and critical cases moving through the workflow quickly enough?

## Page 3: Service and Outcome Review

Recommended layout:

1. Service type utilization bar chart.
2. Support amount distribution by state.
3. Outcome category comparison.
4. Closure rate by risk level.
5. Service mix by case type.

Primary questions answered:

- Which services are most commonly provided?
- Are support amounts distributed consistently across states?
- How do outcomes vary by service, risk level, and geography?

## Suggested Dashboard Design Notes

- Use a restrained, professional color palette with clear contrast.
- Use state and risk-level filters on every page.
- Display synthetic-data notice in the dashboard footer.
- Keep definitions visible through tooltip text or a data dictionary panel.
- Include a data quality tile showing duplicate IDs removed, invalid dates removed, and missing districts retained as `Unknown District`.
