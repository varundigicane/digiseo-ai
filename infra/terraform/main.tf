# DigiSEO Terraform stub — AWS baseline (Phase 1+)

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "project" {
  type    = string
  default = "digiseo-ai"
}

variable "environment" {
  type    = string
  default = "staging"
}

# Placeholder resources — expand for VPC, RDS Postgres, ElastiCache Redis,
# ECS/Fargate for API+worker, S3 for artifacts, and Qdrant on EC2/EKS.

output "notes" {
  value = "Provision Postgres, Redis, Qdrant, and container services before production cutover."
}
