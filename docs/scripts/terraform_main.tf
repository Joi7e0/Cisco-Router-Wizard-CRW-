# Terraform конфігурація для розгортання базової інфраструктури (AWS) для Docker-контейнера
provider "aws" {
  region = "eu-central-1" # Frankfurt
}

# Група безпеки (Security Group)
resource "aws_security_group" "crw_sg" {
  name        = "crw_security_group"
  description = "Allow HTTP inbound traffic to CRW Web Port"

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Передача скрипта ініціалізації при створенні інстансу
resource "aws_instance" "crw_server" {
  ami           = "ami-0abcdef1234567890" # Amazon Linux 2023 (приклад)
  instance_type = "t3.micro"
  vpc_security_group_ids = [aws_security_group.crw_sg.id]

  # Встановлення Docker та запуск контейнеру автоматично при старті ВМ
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install docker -y
              service docker start
              usermod -a -G docker ec2-user
              # docker run -d -p 8000:8000 --name crw_app crw_image:latest
              EOF

  tags = {
    Name        = "CiscoRouterWizard-Prod-Node"
    Environment = "Production"
  }
}

output "instance_public_ip" {
  value = aws_instance.crw_server.public_ip
  description = "Public IP address of the CRW Node"
}
