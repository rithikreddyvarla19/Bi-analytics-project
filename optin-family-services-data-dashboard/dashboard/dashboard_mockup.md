# Dashboard Mockup

## OPT-In Family Services Data Quality and Outcomes Dashboard

Audience: program leadership, site managers, data liaisons, implementation partners, and non-technical stakeholders.

Platform fit: Power BI or Tableau.

## Page 1: Program Overview

Top KPI cards:

- Total referrals
- Engagement rate
- Outreach completion rate
- Follow-up completion rate
- Average outreach attempts
- Total flexible funds distributed

Primary visuals:

- Monthly referral volume line chart.
- Engagement rate by site horizontal bar chart.
- Referral source breakdown.
- Engagement status breakdown.

Recommended filters:

- Site/state
- Referral month
- Referral source
- Engagement status
- Case review flag

## Page 2: Outreach and Engagement

Purpose: help site teams identify where referral-to-contact workflows are strong or need support.

Visuals:

- Outreach attempts distribution.
- Engagement rate by site.
- Follow-up completion by engagement status.
- Case review flag count by site.

Suggested interaction:

- Selecting a site filters all outreach and follow-up metrics.
- Selecting `Pending outreach` or `Unable to contact` highlights records that may need staff review.

## Page 3: Services and Flexible Funds

Purpose: monitor what supports families receive and whether flexible funds are distributed consistently.

Visuals:

- Flexible funds distributed by site.
- Service type breakdown.
- Average flexible funds per referral by service type.
- Table of records with capped fund amounts or missing service documentation.

Suggested interaction:

- Selecting a service type filters fund totals and outcomes.
- Selecting a site compares service mix to the overall program average.

## Page 4: Outcomes

Purpose: summarize family-level outcomes in a way that supports learning, not punitive ranking.

Visuals:

- Outcome status by site stacked bar chart.
- Outcome status by service type.
- Follow-up completion rate by site.
- Active or unresolved referrals table for case review.

Design note:

Use neutral language such as `No response after outreach` rather than language that blames families. Keep the dashboard focused on program workflow, service connection, and data completeness.

## Page 5: Data Quality

Purpose: make data reliability visible and actionable.

Visuals:

- Missing values by field.
- Duplicate family IDs detected.
- Invalid referral dates removed.
- Flexible fund outliers capped.
- Validation status checklist.

Suggested interaction:

- Site filter allows managers to review local documentation patterns.
- Data quality indicators should be visible before interpreting outcome trends.

## Visual Assets Created

The Python analysis script generates the following chart images:

- `visuals/monthly_referral_volume.png`
- `visuals/engagement_rate_by_site.png`
- `visuals/flexible_funds_by_site.png`
- `visuals/service_type_breakdown.png`
- `visuals/outcome_status_by_site.png`

## Accessibility and Stakeholder Design Notes

- Use plain-language metric labels.
- Include definitions for engagement, outreach completion, follow-up completion, and case review flags.
- Avoid red/green-only status colors.
- Show counts alongside percentages where possible.
- Include a visible synthetic-data/confidentiality note for this work sample version.
