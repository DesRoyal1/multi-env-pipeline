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
        data = json.loads(response.data)
        assert data['product']['name'] == 'Air Force 1'

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
