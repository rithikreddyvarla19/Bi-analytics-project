# Terraform Deployment

## Steps
1. Copy `terraform.tfvars.example` to `terraform.tfvars` and update values.
2. Run `terraform init`.
3. Run `terraform plan`.
4. Run `terraform apply`.

## Resources Provisioned
- S3 buckets: bronze, silver, gold
- IAM role and policy for Glue + Lambda
- Glue job placeholder
- Lambda notification placeholder
- Redshift Serverless namespace + workgroup
- CloudWatch Log Group
- EventBridge schedule rule and target
- SNS topic + email subscription
