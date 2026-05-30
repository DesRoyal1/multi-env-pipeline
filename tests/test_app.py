import pytest
import json
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_get_products(client):
    mock_table = MagicMock()
    mock_table.scan.return_value = {'Items': []}
    with patch('app.get_table', return_value=mock_table):
        response = client.get('/products')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'products' in data

def test_create_product(client):
    mock_table = MagicMock()
    mock_table.put_item.return_value = {}
    with patch('app.get_table', return_value=mock_table):
        response = client.post('/products',
            json={"name": "Air Force 1", "price": 110, "stock": 50})
        assert response.status_code == 201

def test_get_product_not_found(client):
    mock_table = MagicMock()
    mock_table.get_item.return_value = {}
    with patch('app.get_table', return_value=mock_table):
        response = client.get('/products/fake-id-123')
        assert response.status_code == 404

def test_delete_product(client):
    mock_table = MagicMock()
    mock_table.delete_item.return_value = {}
    with patch('app.get_table', return_value=mock_table):
        response = client.delete('/products/fake-id-123')
        assert response.status_code == 200

def test_get_metrics(client):
    mock_cw = MagicMock()
    mock_cw.get_metric_statistics.return_value = {'Datapoints': []}
    with patch('app.get_cloudwatch', return_value=mock_cw):
        response = client.get('/api/metrics')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'cpu' in data
        assert 'memory' in data

def test_get_tasks(client):
    mock_ecs = MagicMock()
    mock_ecs.list_tasks.return_value = {'taskArns': []}
    with patch('app.get_ecs', return_value=mock_ecs):
        response = client.get('/api/tasks')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'running' in data

def test_get_logs(client):
    mock_logs = MagicMock()
    mock_logs.describe_log_streams.return_value = {'logStreams': []}
    with patch('app.get_logs_client', return_value=mock_logs):
        response = client.get('/api/logs')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'logs' in data

def test_simulate_incident_no_tasks(client):
    mock_ecs = MagicMock()
    mock_ecs.list_tasks.return_value = {'taskArns': []}
    with patch('app.get_ecs', return_value=mock_ecs):
        response = client.post('/api/incident')
        assert response.status_code == 404