# Dashboard Specification (Power BI / Tableau)

## 1) Executive Dashboard

**Audience:** VP Sales, Finance Lead, COO  
**Primary Questions:** Are we growing revenue profitably? What is current momentum?

**Data Source**
- `dashboard_spec/datasets/executive_dashboard_dataset.csv`
- `outputs/kpi_summary.csv`

**Core Visuals**
- KPI cards: total revenue, total orders, AOV, repeat purchase rate, refund rate
- Monthly revenue line chart with MoM growth
- Revenue vs profit combo chart
- Regional contribution bar chart

**Filters**
- Date (month/quarter/year)
- Region
- Category

## 2) Customer Insights Dashboard

**Audience:** CRM Manager, Retention Team  
**Primary Questions:** Who are high-value customers and how strong is repeat behavior?

**Data Source**
- `dashboard_spec/datasets/customer_insights_dataset.csv`

**Core Visuals**
- Customer revenue distribution histogram
- Top customers table (revenue, orders, loyalty tier, region)
- Repeat vs one-time customer share donut
- Loyalty tier performance matrix

**Filters**
- Loyalty tier
- Region
- Signup period

## 3) Product Performance Dashboard

**Audience:** Merchandising, Category Managers  
**Primary Questions:** Which products/categories drive revenue and margin?

**Data Source**
- `dashboard_spec/datasets/product_performance_dataset.csv`

**Core Visuals**
- Category revenue ranking bar chart
- Top products table (revenue, units sold, refunded amount)
- Revenue vs refund scatter plot by product
- Category share treemap

**Filters**
- Category
- Product

## 4) Regional Trends Dashboard

**Audience:** Regional Ops, Sales Operations  
**Primary Questions:** Which regions are improving and where do we have risk?

**Data Source**
- `dashboard_spec/datasets/regional_trends_dataset.csv`

**Core Visuals**
- Regional revenue trend lines
- Regional profit heatmap by month
- Regional refund rate bar chart
- Region-level scorecard (revenue, profit, orders, refund rate)

**Filters**
- Region
- Month/Quarter
- Category
