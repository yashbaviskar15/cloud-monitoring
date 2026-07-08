output "public_ip" {
  description = "The Elastic IP address associated with the EC2 instance"
  value       = aws_eip.monitoring_eip.public_ip
}

output "ssh_command" {
  description = "Convenient command to SSH into the monitoring server"
  value       = "ssh -i <path_to_private_key> ubuntu@${aws_eip.monitoring_eip.public_ip}"
}
