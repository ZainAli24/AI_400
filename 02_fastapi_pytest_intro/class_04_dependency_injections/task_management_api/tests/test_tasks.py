from fastapi.testclient import TestClient


def test_create_task_returns_201(client: TestClient, sample_task_data: dict):
    response = client.post("/api/v1/tasks", json=sample_task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_task_data["title"]
    assert data["description"] == sample_task_data["description"]
    assert data["priority"] == sample_task_data["priority"]
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data


def test_get_all_tasks(client: TestClient, created_task):
    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["title"] == "Existing task"


def test_get_task_by_id(client: TestClient, created_task):
    response = client.get(f"/api/v1/tasks/{created_task.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Existing task"
    assert data["id"] == created_task.id


def test_get_task_not_found_returns_404(client: TestClient):
    response = client.get("/api/v1/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task(client: TestClient, created_task):
    update_data = {"title": "Updated task", "completed": True}
    response = client.patch(f"/api/v1/tasks/{created_task.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated task"
    assert data["completed"] is True
    assert data["description"] == "Already in database"  # unchanged


def test_update_task_not_found(client: TestClient):
    response = client.patch("/api/v1/tasks/999", json={"title": "New title"})
    assert response.status_code == 404


def test_delete_task(client: TestClient, created_task):
    response = client.delete(f"/api/v1/tasks/{created_task.id}")
    assert response.status_code == 204

    # Verify task is deleted
    get_response = client.get(f"/api/v1/tasks/{created_task.id}")
    assert get_response.status_code == 404


def test_delete_task_not_found(client: TestClient):
    response = client.delete("/api/v1/tasks/999")
    assert response.status_code == 404
