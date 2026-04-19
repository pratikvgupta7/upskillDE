variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "upskillde"
}

variable "bucket_name" {
  description = "S3 bucket name for data lake — must be globally unique"
  type        = string
  default     = "upskillde-warehouse-pratik"
}