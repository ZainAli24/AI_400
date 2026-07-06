import pytest
from fastapi.testclient import TestClient
from refresher import app

client = TestClient(app)

def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == [
    {"id": 1, "description": "Make tea"},
    {"id": 2, "description": "Bring Milk"},
    {"id": 3, "description": "Code"},
]
    


def test_get_task_with_details():
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "description": "Make tea"}

    response = client.get("/tasks/4")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task NOT Found!"}

    response = client.get("/tasks/0")
    assert response.status_code == 401
    assert response.json() == {"detail":"Please enter number that is greater than 0"}

    response = client.get("/tasks/3?include_details=True")
    assert response.status_code == 200
    assert response.json() == {"id": 3,"description": "Code", "details": "This 3 is very important Task!"}