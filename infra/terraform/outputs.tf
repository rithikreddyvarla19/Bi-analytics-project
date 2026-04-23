output "bronze_bucket" {
  value = module.lakehouse.bronze_bucket
}

output "silver_bucket" {
  value = module.lakehouse.silver_bucket
}

output "gold_bucket" {
  value = module.lakehouse.gold_bucket
}

output "sns_topic_arn" {
  value = module.lakehouse.sns_topic_arn
}

output "eventbridge_rule_name" {
  value = module.lakehouse.eventbridge_rule_name
}
