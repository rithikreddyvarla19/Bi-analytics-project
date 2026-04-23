# Cloud Mapping (AWS)

## Local to AWS mapping
- `data/bronze` -> Amazon S3 bronze bucket.
- `data/silver` -> Amazon S3 silver bucket.
- `data/gold` -> Amazon S3 gold bucket.
- `spark_jobs/*.py` -> AWS Glue ETL jobs.
- `scripts/streaming_simulator.py` -> Amazon Kinesis producer (or Kafka producer).
- `data/streaming/processed` -> Kinesis stream consumer output / Glue streaming job sink.
- `data/warehouse/*.csv` -> Amazon Redshift tables.
- `outputs/observability/*` -> CloudWatch metrics + logs.
- quality checks -> CloudWatch + SNS alerts.

## Services represented
- Amazon S3 (data lake zones)
- AWS Glue (batch ETL)
- AWS Lambda (notification hook)
- Amazon Redshift Serverless (serving layer)
- AWS IAM (least privilege roles/policies)
- Amazon EventBridge (scheduling)
- Amazon SNS (alerts)
- Amazon CloudWatch (logs/metrics)
