# Zip the healing Lambda
data "archive_file" "heal_lambda" {
  type        = "zip"
  source_file = "${path.module}/../lambda/heal.py"
  output_path = "${path.module}/../lambda/heal.zip"
}

# IAM role for healing Lambda (separate from API Lambda)
resource "aws_iam_role" "heal_role" {
  name = "lambda-heal-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Healing Lambda permissions
resource "aws_iam_role_policy" "heal_policy" {
  name = "lambda-heal-policy-${var.environment}"
  role = aws_iam_role.heal_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "lambda:InvokeFunction",
        "lambda:GetFunction",
        "sns:Publish",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "cloudwatch:GetMetricStatistics"
      ]
      Resource = "*"
    }]
  })
}

# Healing Lambda function
resource "aws_lambda_function" "heal" {
  filename         = data.archive_file.heal_lambda.output_path
  function_name    = "heal-${var.environment}"
  role             = aws_iam_role.heal_role.arn
  handler          = "heal.lambda_handler"
  runtime          = "python3.12"
  source_code_hash = data.archive_file.heal_lambda.output_base64sha256
  timeout          = 60

  environment {
    variables = {
      ENVIRONMENT      = var.environment
      SNS_TOPIC_ARN    = aws_sns_topic.alerts.arn
      API_FUNCTION     = "multi-env-api-${var.environment}"
    }
  }
}

# CloudWatch alarm watches Lambda errors instead of ECS tasks
resource "aws_cloudwatch_metric_alarm" "trigger_heal" {
  alarm_name          = "trigger-heal-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Triggers self-heal when Lambda errors spike"
  alarm_actions       = [aws_lambda_function.heal.arn]

  dimensions = {
    FunctionName = "multi-env-api-${var.environment}"
  }
}

# Allow CloudWatch to invoke healing Lambda
resource "aws_lambda_permission" "cloudwatch" {
  statement_id  = "AllowCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.heal.function_name
  principal     = "lambda.alarms.cloudwatch.amazonaws.com"
  source_arn    = aws_cloudwatch_metric_alarm.trigger_heal.arn
}
