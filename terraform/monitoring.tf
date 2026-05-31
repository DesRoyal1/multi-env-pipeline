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

# High error rate alarm
resource "aws_cloudwatch_metric_alarm" "high_errors" {
  alarm_name          = "high-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Lambda error rate is high"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = "multi-env-api-${var.environment}"
  }
}

# High duration alarm
resource "aws_cloudwatch_metric_alarm" "high_duration" {
  alarm_name          = "high-duration-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Average"
  threshold           = 10000
  alarm_description   = "Lambda duration exceeding 10 seconds"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = "multi-env-api-${var.environment}"
  }
}
