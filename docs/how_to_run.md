# How to Run

## 1) Environment Setup

```powershell
python -m pip install -r requirements.txt
```

## 2) Run End-to-End Pipeline

```powershell
python scripts/run_pipeline.py
```

This command executes:
- raw data generation
- ETL and star schema build
- KPI output generation
- dashboard dataset exports

## 3) Key Outputs

- Processed tables: `data/processed/*.csv`
- KPI outputs: `outputs/kpi_summary.csv`, `outputs/monthly_kpi_trend.csv`, `outputs/regional_performance.csv`, `outputs/product_category_performance.csv`, `outputs/customer_ltv_proxy.csv`
- Excel pack: `outputs/bi_dashboard_pack.xlsx`
- Dashboard data extracts: `dashboard_spec/datasets/*.csv`

## 4) (Optional) Load into PostgreSQL

1. Run `sql/01_create_star_schema.sql`
2. Use `COPY` commands from the CSVs in `data/processed/` into matching tables
3. Execute analysis scripts `sql/02_*.sql` through `sql/07_*.sql`
