terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "lakehouse" {
  source = "./modules/lakehouse"

  project_name          = var.project_name
  environment           = var.environment
  aws_region            = var.aws_region
  bronze_bucket_name    = var.bronze_bucket_name
  silver_bucket_name    = var.silver_bucket_name
  gold_bucket_name      = var.gold_bucket_name
  redshift_namespace    = var.redshift_namespace
  redshift_workgroup    = var.redshift_workgroup
  alert_email           = var.alert_email
}
