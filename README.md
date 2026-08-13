# Cloud-Native Retail Lakehouse: Batch + Streaming Data Platform on AWS

Local reference implementation of a retail batch and streaming pipeline. It processes synthetic ecommerce data through bronze, silver, and gold layers and produces warehouse and BI extracts.

## Constraints and trade-offs

- Local runs use generated files and do not establish AWS throughput or delivery guarantees.
- Pandas utilities favor inspectability; Spark jobs are provided for distributed execution.
- Checked-in sample outputs are examples and should be regenerated when pipeline logic changes.

## Business Problem
Retail leadership needs a trusted analytics platform for revenue, customer behavior, returns, and inventory operations across channels and regions. Existing reporting is fragmented and not cloud-native.

## Solution Overview
This project implements a cloud-native-ready pipeline with local execution and clear AWS deployment mapping.

### Architecture Flow
Data Sources (batch files + clickstream/inventory stream)
-> Ingestion
-> Bronze (raw immutable)
-> Silver (cleaned standardized)
-> Gold (facts/dims + aggregates)
-> Warehouse-serving layer (PostgreSQL local / Redshift in AWS)
-> BI-ready KPI extracts
-> Quality + observability + orchestration

## Technology Stack
- Python, SQL, PySpark
- Parquet lakehouse storage
- PostgreSQL warehouse simulation
- dbt project (staging + marts)
- Apache Airflow orchestration DAG
- Pandera-style data quality checks (equivalent DQ framework)
- Docker / docker-compose local stack
- Terraform for AWS infrastructure
- GitHub Actions CI pipeline

## Repository Structure
- `data/raw` source datasets
- `data/bronze` raw landed immutable parquet
- `data/silver` cleansed conformed parquet
- `data/gold` fact/dim and aggregate marts
- `data/warehouse` warehouse-ready table exports
- `scripts` ingestion, warehouse, quality, KPI, orchestration scripts
- `spark_jobs` PySpark transformation jobs
- `sql` warehouse DDL + analytics marts
- `dbt_project` dbt models and tests
- `airflow/dags` orchestration DAG
- `infra/terraform` AWS IaC
- `outputs` KPI, quality, and observability artifacts
- `docs` architecture and operational documentation
- `tests` unit and smoke validations
- `.github/workflows` CI checks

## Pipeline Stages
1. Generate synthetic retail data (`customers`, `products`, `orders`, `payments`, `returns`, `inventory_snapshots`, `clickstream_events`).
2. Ingest to bronze with ingestion metadata and partitioned paths.
3. Simulate streaming micro-batches and aggregate streaming metrics.
4. Transform bronze -> silver with schema standardization and deduplication.
5. Transform silver -> gold conformed facts/dimensions + aggregate marts.
6. Build warehouse tables and optionally load PostgreSQL.
7. Execute dataframe-based quality checks.
8. Export KPI outputs for BI tools.
9. Publish run metadata and telemetry.

## Local Run
### 1) Environment setup
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
# Optional local Airflow extras (Docker-first recommended)
pip install -r requirements-airflow.txt
```

### 2) Run full pipeline
```bash
python scripts/run_pipeline.py
```

### 3) Optional with Makefile
```bash
make setup
make run-pipeline
make test
```

### 4) Optional Docker services
```bash
docker compose up -d postgres
docker compose up airflow
```

## Airflow Orchestration
- DAG: `airflow/dags/retail_lakehouse_dag.py`
- Orchestrates generation, ingestion, streaming, Spark transforms, quality, and KPI export.
- Includes success/failure notification hook placeholders.

## Warehouse & dbt
- Warehouse DDL: `sql/warehouse/01_create_analytics_schema.sql`
- KPI marts in `sql/marts`
- dbt models in `dbt_project/models`
- Compile check:
```bash
cp dbt_project/profiles.yml.example dbt_project/profiles.yml
dbt parse --project-dir dbt_project --profiles-dir dbt_project
```

## Data Quality
Checks include:
- non-null and uniqueness on business keys
- positive revenue/quantity checks
- non-negative inventory checks
- refund-rate threshold
- stage row count outputs

Artifacts:
- `outputs/quality/data_quality_report.csv`
- `outputs/quality/quality_summary.json`

## Observability Outputs
- `outputs/observability/pipeline_step_metrics.csv`
- `outputs/observability/pipeline_run_metadata.json`
- `outputs/observability/stage_row_counts.csv`

## BI-ready Outputs
- `outputs/kpis/daily_sales.csv`
- `outputs/kpis/customer_ltv_proxy.csv`
- `outputs/kpis/repeat_purchase_metrics.csv`
- `outputs/kpis/refund_return_rate.csv`
- `outputs/kpis/conversion_funnel_proxy.csv`
- `outputs/kpis/top_products.csv`
- `outputs/kpis/regional_revenue_performance.csv`

## AWS Deployment Mapping
Terraform scaffolds:
- S3 buckets (bronze/silver/gold)
- IAM roles and policies
- Glue job placeholder
- Lambda notification placeholder
- Redshift Serverless namespace/workgroup
- EventBridge schedule
- SNS topic + subscription
- CloudWatch log group

See:
- `infra/terraform/README.md`
- `docs/cloud_mapping.md`

## Engineering Decisions
- File-based streaming micro-batches for reproducible local simulation while mapping cleanly to Kinesis/Kafka.
- Spark transforms separated by stage for maintainability and reruns.
- Warehouse served as both CSV extracts and optional PostgreSQL loading.
- Observability and quality artifacts persisted as first-class pipeline outputs.

## CI/CD
GitHub Actions workflow runs:
- lint (`ruff`)
- tests (`pytest`)
- pipeline smoke run
- dbt parse validation

## Documentation Index
- `docs/architecture.md`
- `docs/data_dictionary.md`
- `docs/schema_documentation.md`
- `docs/cloud_mapping.md`
- `docs/quality_checks.md`
- `docs/observability.md`
- `docs/business_use_cases.md`
