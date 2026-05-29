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

def test_get_items(client):
    response = client.get('/items')
    assert response.status_code == 200

def test_create_item(client):
    response = client.post('/items',
        json={"name": "sneaker", "price": 99})
    assert response.status_code == 201
