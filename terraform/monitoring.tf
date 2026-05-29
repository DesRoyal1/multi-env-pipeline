# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "multi-env-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          title   = "ECS CPU Utilization"
          region  = "us-east-1"
          period  = 300
          stat    = "Average"
          metrics = [
            ["AWS/ECS", "CPUUtilization",
              "ClusterName", "multi-env-${var.environment}",
              "ServiceName", "multi-env-${var.environment}"
            ]
          ]
        }
      },
      {
        type = "metric"
        properties = {
          title   = "ECS Memory Utilization"
          region  = "us-east-1"
          period  = 300
          stat    = "Average"
          metrics = [
            ["AWS/ECS", "MemoryUtilization",
              "ClusterName", "multi-env-${var.environment}",
              "ServiceName", "multi-env-${var.environment}"
            ]
          ]
        }
      }
    ]
  })
}

# SNS Topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "multi-env-alerts-${var.environment}"
}

# Email subscription
resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "D.royal247@yahoo.com"
}

# High CPU alarm
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "high-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "CPU above 80%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = "multi-env-${var.environment}"
    ServiceName = "multi-env-${var.environment}"
  }
}

# No running tasks alarm
resource "aws_cloudwatch_metric_alarm" "running_tasks" {
  alarm_name          = "no-running-tasks-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "RunningTaskCount"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "No tasks running - app is down"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = "multi-env-${var.environment}"
    ServiceName = "multi-env-${var.environment}"
  }
}
