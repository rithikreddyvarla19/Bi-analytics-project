variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "llm-rag-evaluation-platform"
}

variable "image_uri" {
  type        = string
  description = "Container image URI to deploy."
}

variable "vpc_id" {
  type        = string
  description = "VPC ID for ECS networking."
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnets for ECS tasks."
}

variable "allowed_cidrs" {
  type    = list(string)
  default = ["10.0.0.0/8"]
}

variable "execution_role_arn" {
  type        = string
  description = "ECS task execution role ARN."
}

variable "task_role_arn" {
  type        = string
  description = "Application task role ARN."
}

variable "desired_count" {
  type    = number
  default = 2
}

variable "embedding_provider" {
  type    = string
  default = "openai"
}

variable "llm_provider" {
  type    = string
  default = "openai"
}
