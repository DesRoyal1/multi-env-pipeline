resource "aws_dynamodb_table" "products" {
  name         = "products-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

output "dynamodb_table" {
  value = aws_dynamodb_table.products.name
}
