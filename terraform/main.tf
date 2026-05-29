terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "image_url" {
  description = "ECR image URL"
  type        = string
  default     = "416170614208.dkr.ecr.us-east-1.amazonaws.com/multi-env-pipeline:latest"
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "multi-env-${var.environment}"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "main" {
  name              = "/ecs/multi-env-${var.environment}"
  retention_in_days = 7
}
