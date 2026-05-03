from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_object():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_create_task():
    response = client.post('/tasks', json={'title': 'Buy milk'})
    assert response.status_code == 201
    assert response.json()['title'] == 'Buy milk'
