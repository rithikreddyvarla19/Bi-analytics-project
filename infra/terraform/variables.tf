variable "project_name" {
  type        = string
  description = "Name prefix for all resources"
  default     = "retail-lakehouse"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "dev"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "bronze_bucket_name" {
  type        = string
  description = "Bronze S3 bucket"
}

variable "silver_bucket_name" {
  type        = string
  description = "Silver S3 bucket"
}

variable "gold_bucket_name" {
  type        = string
  description = "Gold S3 bucket"
}

variable "redshift_namespace" {
  type        = string
  description = "Redshift Serverless namespace"
  default     = "retail-lakehouse-ns"
}

variable "redshift_workgroup" {
  type        = string
  description = "Redshift Serverless workgroup"
  default     = "retail-lakehouse-wg"
}

variable "alert_email" {
  type        = string
  description = "Email for SNS alerts"
}
