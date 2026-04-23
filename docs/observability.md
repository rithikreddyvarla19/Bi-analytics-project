# Observability

## Pipeline telemetry
- Step execution durations from pipeline orchestration.
- Stage-level file counts across raw/bronze/silver/gold/warehouse.
- Warehouse row counts per table.
- Data quality pass/fail summaries.

## Artifacts
- `outputs/observability/pipeline_step_metrics.csv`
- `outputs/observability/pipeline_run_metadata.json`
- `outputs/observability/stage_row_counts.csv`

## Cloud extension
In AWS, these metrics map to CloudWatch logs and custom metrics. Airflow/Glue/Lambda failures can trigger SNS notifications and EventBridge retry policies.
