variable "aws_region" {
  type        = string
  description = "AWS region to deploy resources"
  default     = "us-east-1"
}

variable "ami_id" {
  type        = string
  description = "AMI ID for the EC2 instance. Default is Ubuntu 22.04 LTS in ap-south-1."
  default     = "ami-07b301a23def3266d"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  type        = string
  description = "CIDR block for the public subnet"
  default     = "10.0.1.0/24"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "allowed_cidr" {
  type        = string
  description = "CIDR block allowed to access the exposed ports (SSH, Grafana, Prometheus, App)"
  default     = "0.0.0.0/0"
}

variable "ssh_public_key" {
  type        = string
  description = "The SSH public key text to associate with the EC2 instance"
}

variable "project_name" {
  type        = string
  description = "Name tag prefix for the resources"
  default     = "devops-monitoring"
}
