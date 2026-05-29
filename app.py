import os
import uuid
import boto3
from flask import Flask, jsonify, request
from boto3.dynamodb.conditions import Key

app = Flask(__name__)

# DynamoDB setup
def get_table():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table_name = os.environ.get('DYNAMODB_TABLE', 'products-dev')
    return dynamodb.Table(table_name)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/products', methods=['GET'])
def get_products():
    table = get_table()
    result = table.scan()
    return jsonify({"products": result['Items']})

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    table = get_table()
    result = table.get_item(Key={'id': product_id})
    if 'Item' not in result:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(result['Item'])

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    table = get_table()
    product = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'price': str(data['price']),
        'stock': str(data.get('stock', 0))
    }
    table.put_item(Item=product)
    return jsonify({"message": "Product created", "product": product}), 201

@app.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    table = get_table()
    table.update_item(
        Key={'id': product_id},
        UpdateExpression='SET stock = :stock',
        ExpressionAttributeValues={':stock': str(data['stock'])}
    )
    return jsonify({"message": "Product updated"})

@app.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    table = get_table()
    table.delete_item(Key={'id': product_id})
    return jsonify({"message": "Product deleted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
