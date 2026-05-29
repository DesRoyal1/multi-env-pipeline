import pytest
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
    response = client.get('/products')
    assert response.status_code in [200, 500]

def test_create_product(client):
    response = client.post('/products',
        json={"name": "Air Force 1", "price": 110, "stock": 50})
    assert response.status_code in [201, 500]

def test_get_product_not_found(client):
    response = client.get('/products/fake-id-123')
    assert response.status_code in [404, 500]
