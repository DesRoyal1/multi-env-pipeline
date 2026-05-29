# Application Load Balancer
resource "aws_lb" "main" {
  name               = "multi-env-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_sg.id]
  subnets            = var.subnet_ids
}

# Target Group
resource "aws_lb_target_group" "app" {
  name        = "multi-env-${var.environment}"
  port        = 5000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }
}

# Listener
resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Output the URL
output "app_url" {
  value = "http://${aws_lb.main.dns_name}"
}
