terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  # Use global STS endpoint to avoid DNS resolution issues
  # with regional endpoints on some Windows/Go configurations
  sts_region = "us-east-1"

  # Skip STS credential validation call during plan
  skip_credentials_validation = true
  skip_requesting_account_id  = true
}
