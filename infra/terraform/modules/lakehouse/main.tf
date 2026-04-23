locals {
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "bronze" {
  bucket = var.bronze_bucket_name
  tags   = local.tags
}

resource "aws_s3_bucket" "silver" {
  bucket = var.silver_bucket_name
  tags   = local.tags
}

resource "aws_s3_bucket" "gold" {
  bucket = var.gold_bucket_name
  tags   = local.tags
}

resource "aws_s3_bucket_versioning" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "silver" {
  bucket = aws_s3_bucket.silver.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "gold" {
  bucket = aws_s3_bucket.gold.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_iam_role" "glue_job_role" {
  name = "${var.project_name}-${var.environment}-glue-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = { Service = "glue.amazonaws.com" }
    }]
  })
  tags = local.tags
}

resource "aws_iam_policy" "glue_s3_policy" {
  name   = "${var.project_name}-${var.environment}-glue-s3-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
        Resource = [
          aws_s3_bucket.bronze.arn,
          "${aws_s3_bucket.bronze.arn}/*",
          aws_s3_bucket.silver.arn,
          "${aws_s3_bucket.silver.arn}/*",
          aws_s3_bucket.gold.arn,
          "${aws_s3_bucket.gold.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_attach" {
  role       = aws_iam_role.glue_job_role.name
  policy_arn = aws_iam_policy.glue_s3_policy.arn
}

resource "aws_glue_job" "bronze_to_silver" {
  name     = "${var.project_name}-${var.environment}-bronze-to-silver"
  role_arn = aws_iam_role.glue_job_role.arn
  command {
    script_location = "s3://${var.bronze_bucket_name}/glue-scripts/bronze_to_silver.py"
    python_version  = "3"
  }
  max_retries = 1
  timeout     = 30
  glue_version = "4.0"

  default_arguments = {
    "--job-language" = "python"
    "--enable-metrics" = "true"
  }

  tags = local.tags
}

resource "aws_lambda_function" "pipeline_notification" {
  function_name = "${var.project_name}-${var.environment}-pipeline-notification"
  role          = aws_iam_role.glue_job_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  filename      = "${path.module}/lambda_placeholder.zip"

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.pipeline_alerts.arn
    }
  }

  tags = local.tags
}

resource "aws_redshiftserverless_namespace" "analytics" {
  namespace_name      = var.redshift_namespace
  admin_username      = "adminuser"
  admin_user_password = "ChangeMe123!"
  db_name             = "retail_analytics"
  iam_roles           = [aws_iam_role.glue_job_role.arn]
  tags                = local.tags
}

resource "aws_redshiftserverless_workgroup" "analytics" {
  namespace_name = aws_redshiftserverless_namespace.analytics.namespace_name
  workgroup_name = var.redshift_workgroup
  base_capacity  = 32
  publicly_accessible = false
  tags = local.tags
}

resource "aws_sns_topic" "pipeline_alerts" {
  name = "${var.project_name}-${var.environment}-alerts"
  tags = local.tags
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.pipeline_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_event_rule" "pipeline_schedule" {
  name                = "${var.project_name}-${var.environment}-eventbridge-rule"
  schedule_expression = "rate(1 day)"
  description         = "Triggers retail lakehouse orchestration"
  tags                = local.tags
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.pipeline_schedule.name
  target_id = "pipeline-notification"
  arn       = aws_lambda_function.pipeline_notification.arn
}

resource "aws_cloudwatch_log_group" "pipeline_logs" {
  name              = "/aws/retail-lakehouse/${var.environment}"
  retention_in_days = 30
  tags              = local.tags
}
