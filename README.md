# E-commerce Revenue & Customer Intelligence Platform

End-to-end Business Intelligence Analyst portfolio project that demonstrates realistic BI workflow execution:

- synthetic e-commerce source data generation
- Python + Pandas ETL and data quality handling
- dimensional modeling into a star schema
- SQL analytics for business questions
- KPI layer and dashboard-ready data exports
- stakeholder-facing insights and documentation

## Tech Stack

- Python
- Pandas / NumPy
- SQL (PostgreSQL-compatible scripts)
- CSV + Excel outputs
- Git / GitHub workflow

## Repository Structure

```text
data/
  raw/                 # Generated source-style data
  processed/           # Cleaned and modeled star schema tables
sql/                   # DDL + BI analysis SQL queries
scripts/               # Data generation, ETL, KPI export pipeline
docs/                  # Technical and stakeholder documentation
outputs/               # KPI summaries and Excel reporting pack
dashboard_spec/        # Dashboard design and ready-to-load datasets
```

## Architecture

1. Generate raw entities (`customers`, `products`, `orders`, `order_items`, `returns`, `regions`)
2. Clean and validate raw data
3. Build star schema tables:
   - `fact_sales`
   - `dim_customers`
   - `dim_products`
   - `dim_date`
   - `dim_region`
4. Produce KPI outputs and dashboard extracts
5. Analyze with SQL scripts that answer business questions

See:
- `docs/architecture.md`
- `docs/schema_documentation.md`

## How to Run

```powershell
python -m pip install -r requirements.txt
python scripts/run_pipeline.py
```

## Key Outputs

### Processed Model Tables

- `data/processed/fact_sales.csv`
- `data/processed/dim_customers.csv`
- `data/processed/dim_products.csv`
- `data/processed/dim_date.csv`
- `data/processed/dim_region.csv`

### KPI Outputs

- `outputs/kpi_summary.csv`
- `outputs/monthly_kpi_trend.csv`
- `outputs/product_category_performance.csv`
- `outputs/regional_performance.csv`
- `outputs/customer_ltv_proxy.csv`
- `outputs/bi_dashboard_pack.xlsx`

### Dashboard-Ready Datasets

- `dashboard_spec/datasets/executive_dashboard_dataset.csv`
- `dashboard_spec/datasets/customer_insights_dataset.csv`
- `dashboard_spec/datasets/product_performance_dataset.csv`
- `dashboard_spec/datasets/regional_trends_dataset.csv`

## SQL Analytics Pack

- `sql/01_create_star_schema.sql`
- `sql/02_revenue_trends.sql`
- `sql/03_top_customers_products.sql`
- `sql/04_repeat_customer_rate.sql`
- `sql/05_regional_performance.sql`
- `sql/06_category_growth.sql`
- `sql/07_cohort_retention.sql`

These scripts include joins, aggregations, CTEs, ranking, and window functions for common BI analysis workflows.

## KPI Coverage

- Total revenue
- Average order value
- Monthly growth
- Repeat purchase rate
- Refund rate
- Product / category performance
- Regional performance
- Customer LTV proxy

## Documentation Index

- `docs/how_to_run.md`
- `docs/data_dictionary.md`
- `docs/schema_documentation.md`
- `docs/assumptions_limitations.md`
- `docs/insights.md`
- `dashboard_spec/dashboard_spec.md`
