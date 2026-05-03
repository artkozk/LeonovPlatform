from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_task():
    response = client.post('/tasks', json={'title': 'Buy milk'})
    assert response.status_code == 201
    assert response.json()['title'] == 'Buy milk'


def test_empty_title_validation():
    response = client.post('/tasks', json={'title': ''})
    assert response.status_code == 422
