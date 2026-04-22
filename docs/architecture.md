# Project Architecture

## Pipeline Flow

1. **Raw Data Generation** (`scripts/generate_raw_data.py`)
   - Creates synthetic e-commerce source tables in `data/raw/`.
2. **ETL + Dimensional Modeling** (`scripts/etl_pipeline.py`)
   - Cleans raw entities, applies validation rules, and builds star schema tables in `data/processed/`.
3. **KPI + Dashboard Exports** (`scripts/build_kpi_outputs.py`)
   - Produces executive KPI outputs in `outputs/` and dashboard-ready datasets in `dashboard_spec/datasets/`.
4. **SQL Analytics Layer** (`sql/*.sql`)
   - Provides business-question query scripts for PostgreSQL or SQL-compatible BI environments.

## Folder Responsibilities

- `data/raw/`: source-like landing zone
- `data/processed/`: cleaned and modeled analytics tables
- `scripts/`: reusable pipeline modules and orchestration entrypoint
- `sql/`: star schema DDL plus analysis queries
- `outputs/`: KPI tables and analyst-facing export workbook
- `dashboard_spec/`: dashboard definition and datasets for Power BI/Tableau
- `docs/`: stakeholder and technical documentation
