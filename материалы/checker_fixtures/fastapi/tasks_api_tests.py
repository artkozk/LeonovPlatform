from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_task():
    response = client.post('/tasks', json={'title': 'Buy milk'})
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == 'Buy milk'
    assert data['done'] is False


def test_healthcheck():
    response = client.get('/health')
    assert response.status_code == 200
