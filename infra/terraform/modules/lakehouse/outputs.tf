output "bronze_bucket" {
  value = aws_s3_bucket.bronze.bucket
}

output "silver_bucket" {
  value = aws_s3_bucket.silver.bucket
}

output "gold_bucket" {
  value = aws_s3_bucket.gold.bucket
}

output "sns_topic_arn" {
  value = aws_sns_topic.pipeline_alerts.arn
}

output "eventbridge_rule_name" {
  value = aws_cloudwatch_event_rule.pipeline_schedule.name
}
