import os
import uuid
import json
import time
import subprocess
import boto3
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

REGION = 'us-east-1'
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'prod')
CLUSTER = f'multi-env-{ENVIRONMENT}'
SERVICE = f'multi-env-{ENVIRONMENT}'
LOG_GROUP = f'/ecs/multi-env-{ENVIRONMENT}'

def get_table():
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table_name = os.environ.get('DYNAMODB_TABLE', 'products-dev')
    return dynamodb.Table(table_name)

def get_cloudwatch():
    return boto3.client('cloudwatch', region_name=REGION)

def get_logs_client():
    return boto3.client('logs', region_name=REGION)

def get_ecs():
    return boto3.client('ecs', region_name=REGION)

# ─────────────────────────────────────────
# EXISTING ENDPOINTS
# ─────────────────────────────────────────

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

# ─────────────────────────────────────────
# GLASS WALL ENDPOINTS
# ─────────────────────────────────────────

@app.route('/api/metrics')
def get_metrics():
    try:
        cw = get_cloudwatch()
        end = datetime.utcnow()
        start = end - timedelta(minutes=10)

        def get_metric(name):
            resp = cw.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName=name,
                Dimensions=[
                    {'Name': 'ClusterName', 'Value': CLUSTER},
                    {'Name': 'ServiceName', 'Value': SERVICE}
                ],
                StartTime=start,
                EndTime=end,
                Period=60,
                Statistics=['Average']
            )
            points = sorted(resp['Datapoints'], key=lambda x: x['Timestamp'])
            return [{'time': p['Timestamp'].strftime('%H:%M'), 'value': round(p['Average'], 1)} for p in points]

        cpu = get_metric('CPUUtilization')
        memory = get_metric('MemoryUtilization')

        return jsonify({
            'cpu': cpu,
            'memory': memory,
            'current_cpu': cpu[-1]['value'] if cpu else 0,
            'current_memory': memory[-1]['value'] if memory else 0,
            'environment': ENVIRONMENT
        })
    except Exception as e:
        return jsonify({'error': str(e), 'cpu': [], 'memory': [], 'current_cpu': 0, 'current_memory': 0})

@app.route('/api/tasks')
def get_tasks():
    try:
        ecs = get_ecs()
        task_arns = ecs.list_tasks(cluster=CLUSTER, serviceName=SERVICE)['taskArns']
        if not task_arns:
            return jsonify({'tasks': [], 'running': 0, 'desired': 1})
        tasks = ecs.describe_tasks(cluster=CLUSTER, tasks=task_arns)['tasks']
        task_list = []
        for t in tasks:
            task_list.append({
                'id': t['taskArn'].split('/')[-1][:8],
                'status': t['lastStatus'],
                'health': t.get('healthStatus', 'UNKNOWN'),
                'started': t.get('startedAt', datetime.utcnow()).strftime('%H:%M:%S') if hasattr(t.get('startedAt', ''), 'strftime') else 'starting',
                'cpu': t.get('cpu', '256'),
                'memory': t.get('memory', '512')
            })
        svc = ecs.describe_services(cluster=CLUSTER, services=[SERVICE])['services'][0]
        return jsonify({
            'tasks': task_list,
            'running': svc['runningCount'],
            'desired': svc['desiredCount'],
            'pending': svc['pendingCount']
        })
    except Exception as e:
        return jsonify({'error': str(e), 'tasks': [], 'running': 0, 'desired': 1})

@app.route('/api/logs')
def get_log_stream():
    try:
        logs = get_logs_client()
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
            limit=25,
            startFromHead=False
        )['events']

        log_lines = []
        for e in events:
            ts = datetime.utcfromtimestamp(e['timestamp'] / 1000).strftime('%H:%M:%S')
            msg = e['message'].strip()
            log_lines.append({'time': ts, 'message': msg})

        return jsonify({'logs': log_lines[-20:]})
    except Exception as e:
        return jsonify({'logs': [{'time': '00:00:00', 'message': f'Log stream initializing... ({str(e)[:50]})'}]})

@app.route('/api/loadtest', methods=['POST'])
def run_loadtest():
    try:
        data = request.get_json() or {}
        requests_count = min(data.get('requests', 500), 1000)
        concurrency = min(data.get('concurrency', 50), 100)
        target = f'http://localhost:5000/health'

        def generate():
            yield json.dumps({'status': 'starting', 'message': f'Firing {requests_count} requests at {concurrency} concurrent...'}) + '\n'
            start = time.time()
            try:
                result = subprocess.run(
                    ['hey', '-n', str(requests_count), '-c', str(concurrency), target],
                    capture_output=True, text=True, timeout=60
                )
                duration = round(time.time() - start, 2)
                output = result.stdout

                rps = 0
                avg = 0
                success = 0
                for line in output.split('\n'):
                    if 'Requests/sec:' in line:
                        try: rps = float(line.split(':')[1].strip())
                        except: pass
                    if 'Average:' in line and 'secs' in line:
                        try: avg = round(float(line.split(':')[1].strip().split(' ')[0]) * 1000, 1)
                        except: pass
                    if '[200]' in line:
                        try: success = int(line.strip().split()[1])
                        except: pass

                yield json.dumps({
                    'status': 'complete',
                    'requests': requests_count,
                    'duration': duration,
                    'rps': round(rps, 1),
                    'avg_ms': avg,
                    'success': success,
                    'success_rate': round((success / requests_count) * 100, 1) if requests_count > 0 else 0
                }) + '\n'
            except subprocess.TimeoutExpired:
                yield json.dumps({'status': 'error', 'message': 'Load test timed out'}) + '\n'
            except FileNotFoundError:
                yield json.dumps({'status': 'error', 'message': 'hey not installed on server'}) + '\n'

        return Response(stream_with_context(generate()), mimetype='application/x-ndjson')
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/incident', methods=['POST'])
def simulate_incident():
    try:
        ecs = get_ecs()
        task_arns = ecs.list_tasks(cluster=CLUSTER, serviceName=SERVICE)['taskArns']
        if not task_arns:
            return jsonify({'status': 'error', 'message': 'No running tasks found'}), 404

        task_to_stop = task_arns[0]
        task_id = task_to_stop.split('/')[-1][:8]

        ecs.stop_task(
            cluster=CLUSTER,
            task=task_to_stop,
            reason='Simulated incident via glass wall demo'
        )

        return jsonify({
            'status': 'incident_triggered',
            'message': f'Container {task_id} stopped. Watch the self-healing system respond.',
            'task_id': task_id,
            'next': 'CloudWatch will detect zero running tasks within 60 seconds and trigger Lambda self-healing'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/pipeline')
def get_pipeline():
    try:
        token = os.environ.get('GITHUB_TOKEN', '')
        if not token:
            return jsonify({'runs': [], 'error': 'No GitHub token configured'})

        import urllib.request
        req = urllib.request.Request(
            'https://api.github.com/repos/DesRoyal1/multi-env-pipeline/actions/runs?per_page=5',
            headers={'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())

        runs = []
        for r in data.get('workflow_runs', [])[:5]:
            runs.append({
                'id': r['id'],
                'name': r['head_commit']['message'][:50] if r.get('head_commit') else 'Unknown',
                'status': r['status'],
                'conclusion': r.get('conclusion', 'in_progress'),
                'created_at': r['created_at'],
                'url': r['html_url']
            })
        return jsonify({'runs': runs})
    except Exception as e:
        return jsonify({'runs': [], 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
