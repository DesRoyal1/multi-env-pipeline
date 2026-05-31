import os
import uuid
import json
import time
import boto3
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

REGION = 'us-east-1'
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'prod')
LOG_GROUP = f'/aws/lambda/multi-env-api-{ENVIRONMENT}'
FUNCTION_NAME = f'multi-env-api-{ENVIRONMENT}'

def get_table():
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    return dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'products-dev'))

def get_cw():
    return boto3.client('cloudwatch', region_name=REGION)

def get_logs():
    return boto3.client('logs', region_name=REGION)

@app.route('/')
def status_page():
    return render_template('status.html')

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "environment": ENVIRONMENT})

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

@app.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    table = get_table()
    table.delete_item(Key={'id': product_id})
    return jsonify({"message": "Product deleted"})

@app.route('/api/metrics')
def get_metrics():
    try:
        cw = get_cw()
        end = datetime.utcnow()
        start = end - timedelta(minutes=30)

        def get_metric(name, stat='Sum'):
            resp = cw.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName=name,
                Dimensions=[{'Name': 'FunctionName', 'Value': FUNCTION_NAME}],
                StartTime=start,
                EndTime=end,
                Period=300,
                Statistics=[stat]
            )
            points = sorted(resp['Datapoints'], key=lambda x: x['Timestamp'])
            return [{'time': p['Timestamp'].strftime('%H:%M'), 'value': round(p[stat], 2)} for p in points]

        invocations = get_metric('Invocations')
        errors = get_metric('Errors')
        duration = get_metric('Duration', 'Average')

        total_invocations = sum(p['value'] for p in invocations)
        total_errors = sum(p['value'] for p in errors)
        avg_duration = round(sum(p['value'] for p in duration) / len(duration), 1) if duration else 0
        error_rate = round((total_errors / total_invocations * 100), 2) if total_invocations > 0 else 0

        return jsonify({
            'invocations': invocations,
            'errors': errors,
            'duration': duration,
            'totals': {
                'invocations': int(total_invocations),
                'errors': int(total_errors),
                'avg_duration': avg_duration,
                'error_rate': error_rate
            },
            'environment': ENVIRONMENT
        })
    except Exception as e:
        return jsonify({'error': str(e), 'invocations': [], 'errors': [], 'duration': [], 'totals': {'invocations': 0, 'errors': 0, 'avg_duration': 0, 'error_rate': 0}})

@app.route('/api/logs')
def get_log_stream():
    try:
        logs = get_logs()
        streams = logs.describe_log_streams(
            logGroupName=LOG_GROUP,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )['logStreams']

        if not streams:
            return jsonify({'logs': []})

        stream_name = streams[0]['logStreamName']
        events = logs.get_log_events(
            logGroupName=LOG_GROUP,
            logStreamName=stream_name,
            limit=30,
            startFromHead=False
        )['events']

        log_lines = []
        for e in events:
            ts = datetime.utcfromtimestamp(e['timestamp'] / 1000).strftime('%H:%M:%S')
            msg = e['message'].strip()
            if msg and not msg.startswith('START') and not msg.startswith('END') and not msg.startswith('INIT'):
                log_lines.append({'time': ts, 'message': msg[:120]})

        return jsonify({'logs': log_lines[-20:]})
    except Exception as e:
        return jsonify({'logs': [{'time': '00:00:00', 'message': 'Connecting to log stream...'}]})

@app.route('/api/db')
def get_db_stats():
    try:
        table = get_table()
        result = table.scan(Select='COUNT')
        return jsonify({
            'count': result.get('Count', 0),
            'table': os.environ.get('DYNAMODB_TABLE', 'products-dev'),
            'environment': ENVIRONMENT
        })
    except Exception as e:
        return jsonify({'count': 0, 'error': str(e)})

@app.route('/api/test-transaction', methods=['POST'])
def test_transaction():
    try:
        start = time.time()
        table = get_table()
        test_id = str(uuid.uuid4())
        table.put_item(Item={
            'id': test_id,
            'name': f'test-record-{test_id[:8]}',
            'price': '0',
            'stock': '0',
            'test': 'true',
            'created': datetime.utcnow().isoformat()
        })
        duration = round((time.time() - start) * 1000, 1)
        return jsonify({
            'status': 'success',
            'id': test_id,
            'duration_ms': duration,
            'message': f'Written to DynamoDB in {duration}ms'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/loadtest', methods=['POST'])
def run_loadtest():
    try:
        data = request.get_json() or {}
        count = min(int(data.get('requests', 100)), 200)
        results = {'success': 0, 'errors': 0, 'total_ms': 0}

        import urllib.request as urllib_req
        for i in range(count):
            try:
                start = time.time()
                urllib_req.urlopen(
                    f'https://{request.host}/health',
                    timeout=5
                )
                results['success'] += 1
                results['total_ms'] += (time.time() - start) * 1000
            except Exception:
                results['errors'] += 1

        avg_ms = round(results['total_ms'] / results['success'], 1) if results['success'] > 0 else 0
        return jsonify({
            'status': 'complete',
            'requests': count,
            'success': results['success'],
            'errors': results['errors'],
            'success_rate': round(results['success'] / count * 100, 1),
            'avg_ms': avg_ms,
            'cost_usd': round(count * 0.0000002, 8)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
