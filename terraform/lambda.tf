# Zip the application with dependencies
data "archive_file" "app" {
  type        = "zip"
  source_dir  = "${path.module}/../"
  excludes    = [
    "terraform",
    "venv",
    ".git",
    "tests",
    "__pycache__",
    "*.pyc",
    ".github",
    "lambda/heal.py",
    "lambda/heal.zip",
    "app.zip"
  ]
  output_path = "${path.module}/../app.zip"
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda-api-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Lambda permissions
resource "aws_iam_role_policy" "lambda_permissions" {
  name = "lambda-api-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan"
        ]
        Resource = "arn:aws:dynamodb:us-east-1:416170614208:table/products-*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "logs:GetLogEvents",
          "logs:DescribeLogStreams",
          "logs:DescribeLogGroups",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
          "lambda:GetFunction"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda function
resource "aws_lambda_function" "api" {
  filename         = data.archive_file.app.output_path
  function_name    = "multi-env-api-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_handler.handler"
  runtime          = "python3.12"
  timeout          = 30
  memory_size      = 256
  source_code_hash = data.archive_file.app.output_base64sha256

  environment {
    variables = {
      ENVIRONMENT    = var.environment
      DYNAMODB_TABLE = "products-${var.environment}"
    }
  }
}

# CloudWatch log group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/multi-env-api-${var.environment}"
  retention_in_days = 7
}
