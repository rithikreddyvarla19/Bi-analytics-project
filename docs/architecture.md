# Architecture

## End-to-end flow
1. Batch sources are synthesized for customers, products, orders, payments, returns, and inventory snapshots.
2. Streaming simulator emits clickstream and inventory-like micro-batch events.
3. Ingestion lands immutable raw inputs into the bronze zone (`data/bronze/domain=.../ingest_date=...`).
4. PySpark transformations standardize data into silver Parquet with typed schemas and deduplication.
5. Gold layer builds conformed dimensions and fact tables for analytics.
6. Warehouse simulation exports gold data to PostgreSQL-compatible tables and CSV snapshots.
7. KPI exports generate BI-ready output datasets under `outputs/kpis`.
8. Dataframe-based quality checks validate key quality rules and write reports.
9. Observability scripts emit step durations, stage row counts, and run metadata.

## Medallion layout
- Bronze: raw immutable landed snapshots.
- Silver: cleaned conformed transactional entities.
- Gold: marts/facts/dimensions and streaming aggregates.

## Orchestration
Airflow DAG `retail_lakehouse_pipeline` chains ingestion, batch transforms, streaming aggregation, quality checks, KPI exports, and success/failure hooks.
