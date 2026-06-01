# AWS Deployment

This folder contains deployment scaffolding for ECS Fargate, ECR, ALB, CloudWatch logs, and RDS PostgreSQL.

For production, store secrets in AWS Secrets Manager or SSM Parameter Store and inject them into the task definition.

```bash
cd deploy/aws/terraform
terraform init
terraform plan -var="image_uri=<account>.dkr.ecr.<region>.amazonaws.com/llm-rag-evaluation-platform:latest"
terraform apply
```
