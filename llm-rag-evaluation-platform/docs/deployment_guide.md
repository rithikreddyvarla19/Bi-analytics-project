# Deployment Guide

## Local Docker

```bash
cp .env.example .env
docker compose up --build
```

Services:

- FastAPI: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Knowledge assistant dashboard: http://localhost:8501
- MLflow: http://localhost:5000
- PostgreSQL: localhost:5432

Seed the sample index:

```bash
docker compose run --rm api python scripts/seed_sample_index.py
```

## AWS

The `deploy/aws` folder includes Terraform and ECS task definition templates for an ECS Fargate deployment.

High-level steps:

1. Create an ECR repository and push the image.
2. Provision VPC, ECS, ALB, CloudWatch, and RDS with Terraform.
3. Store secrets in AWS Secrets Manager or SSM Parameter Store.
4. Register the ECS task definition and deploy the service.
5. Configure scheduled evaluation jobs through EventBridge or your orchestration platform.

Required production variables:

- `OPENAI_API_KEY` if using OpenAI.
- `DATABASE_URL`
- `MLFLOW_TRACKING_URI`
- `VECTOR_INDEX_PATH`
- `EMBEDDING_PROVIDER`
- `LLM_PROVIDER`
