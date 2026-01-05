"""
Comprehensive tests for FastAPI endpoints in main.py

Following the AAA pattern: Arrange, Act, Assert
"""

import pytest
from fastapi.testclient import TestClient


# ============================================================================
# Tests for GET /tasks - Get all tasks
# ============================================================================

@pytest.mark.api
@pytest.mark.unit
def test_get_all_tasks(client):
    """Test GET /tasks returns list of all tasks."""
    # Act
    response = client.get("/tasks")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 3


@pytest.mark.api
def test_get_all_tasks_structure(client, sample_tasks_list):
    """Test GET /tasks returns tasks with correct structure."""
    # Act
    response = client.get("/tasks")
    tasks = response.json()

    # Assert
    assert tasks == sample_tasks_list
    for task in tasks:
        assert "id" in task
        assert "tasks" in task
        assert isinstance(task["id"], int)
        assert isinstance(task["tasks"], str)


@pytest.mark.api
def test_get_all_tasks_content(client):
    """Test GET /tasks returns expected task content."""
    # Act
    response = client.get("/tasks")
    tasks = response.json()

    # Assert
    assert tasks[0] == {"id": 1, "tasks": "Go to the grocery store"}
    assert tasks[1] == {"id": 2, "tasks": "Walk the dog"}
    assert tasks[2] == {"id": 3, "tasks": "Read a book"}


# ============================================================================
# Tests for GET /tasks/1 and /tasks/2 - Static task endpoints
# ============================================================================

@pytest.mark.api
@pytest.mark.unit
def test_get_task_1(client):
    """Test GET /tasks/1 returns first task."""
    # Act
    response = client.get("/tasks/1")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"id": 1, "tasks": "Go to the grocery store"}


@pytest.mark.api
@pytest.mark.unit
def test_get_task_2(client):
    """Test GET /tasks/2 returns second task."""
    # Act
    response = client.get("/tasks/2")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"id": 2, "tasks": "Walk the dog"}


# ============================================================================
# Tests for GET /tasks/{task_id} - Dynamic task endpoint with query params
# ============================================================================

@pytest.mark.api
@pytest.mark.unit
def test_get_task_dynamic(client):
    """Test GET /tasks/{task_id} with valid task ID."""
    # Act
    response = client.get("/tasks/5")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 5
    assert data["tasks"] == "Task number 5"


@pytest.mark.api
@pytest.mark.parametrize("task_id,expected_task", [
    # Note: IDs 1 and 2 have static endpoints that override the dynamic one
    (3, "Task number 3"),
    (5, "Task number 5"),
    (10, "Task number 10"),
    (100, "Task number 100"),
])
def test_get_task_dynamic_multiple_ids(client, task_id, expected_task):
    """Test GET /tasks/{task_id} with multiple valid task IDs."""
    # Act
    response = client.get(f"/tasks/{task_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["tasks"] == expected_task


@pytest.mark.api
def test_get_task_ignores_unknown_query_params(client):
    """Test GET /tasks/{task_id} ignores unknown query parameters.

    Note: main.py has two definitions of /tasks/{task_id} (lines 29 & 39).
    FastAPI uses the FIRST definition (line 29) which doesn't support included_details.
    The second definition with included_details parameter is not used.
    """
    # Act - Query parameter is ignored by the first route definition
    response = client.get("/tasks/5?included_details=True")

    # Assert
    assert response.status_code == 200
    data = response.json()
    # The query parameter is ignored, so no details field
    assert "details" not in data
    assert data["id"] == 5
    assert data["tasks"] == "Task number 5"


@pytest.mark.api
def test_get_task_basic_structure(client):
    """Test GET /tasks/{task_id} returns basic task structure."""
    # Act
    response = client.get("/tasks/5")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "tasks" in data
    assert data["id"] == 5
    assert data["tasks"] == "Task number 5"


@pytest.mark.api
def test_get_task_invalid_id_less_than_one(client):
    """Test GET /tasks/{task_id} with task_id < 1 returns error."""
    # Act
    response = client.get("/tasks/0")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"] == "Task ID must be greater than 0"


@pytest.mark.api
@pytest.mark.parametrize("invalid_id", [-1, -10, -100, 0])
def test_get_task_multiple_invalid_ids(client, invalid_id):
    """Test GET /tasks/{task_id} with multiple invalid IDs."""
    # Act
    response = client.get(f"/tasks/{invalid_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"] == "Task ID must be greater than 0"


# ============================================================================
# Tests for GET /users/{user_id}/tasks/{task_id} - Async endpoint
# ============================================================================

@pytest.mark.api
def test_get_user_task_without_details(client):
    """Test GET /users/{user_id}/tasks/{task_id} without include_details.

    Note: The endpoint is async but TestClient handles it automatically.
    """
    # Act
    response = client.get("/users/1/tasks/5")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["task_id"] == 5
    assert "details" not in data


@pytest.mark.api
def test_get_user_task_with_details_true(client):
    """Test GET /users/{user_id}/tasks/{task_id} with include_details=True.

    Note: The endpoint is async but TestClient handles it automatically.
    """
    # Act
    response = client.get("/users/1/tasks/5?include_details=True")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["task_id"] == 5
    assert "details" in data
    assert data["details"] == "Details included: True"


@pytest.mark.api
def test_get_user_task_with_details_false(client):
    """Test GET /users/{user_id}/tasks/{task_id} with include_details=False.

    Note: The endpoint is async but TestClient handles it automatically.
    """
    # Act
    response = client.get("/users/1/tasks/5?include_details=False")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["task_id"] == 5
    assert "details" not in data


@pytest.mark.api
@pytest.mark.parametrize("user_id,task_id", [
    (1, 1),
    (1, 5),
    (10, 20),
    (100, 200),
])
def test_get_user_task_multiple_ids(client, user_id, task_id):
    """Test GET /users/{user_id}/tasks/{task_id} with multiple ID combinations.

    Note: The endpoint is async but TestClient handles it automatically.
    """
    # Act
    response = client.get(f"/users/{user_id}/tasks/{task_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["task_id"] == task_id


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================

@pytest.mark.api
def test_invalid_endpoint_returns_404(client):
    """Test requesting non-existent endpoint returns 404."""
    # Act
    response = client.get("/nonexistent")

    # Assert
    assert response.status_code == 404


@pytest.mark.api
def test_tasks_endpoint_returns_json(client):
    """Test /tasks endpoint returns JSON content type."""
    # Act
    response = client.get("/tasks")

    # Assert
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
def test_all_task_endpoints_return_consistent_data(client):
    """Integration test: Verify all task endpoints return consistent data structure."""
    # Act
    all_tasks = client.get("/tasks").json()
    task_1 = client.get("/tasks/1").json()
    task_2 = client.get("/tasks/2").json()

    # Assert - Check that individual tasks match the list
    assert all_tasks[0] == task_1
    assert all_tasks[1] == task_2


@pytest.mark.integration
def test_user_task_and_task_endpoints_work_together(client):
    """Integration test: Verify user-task and task endpoints can work together."""
    # Arrange
    task_id = 5

    # Act
    task_response = client.get(f"/tasks/{task_id}")
    user_task_response = client.get(f"/users/1/tasks/{task_id}")

    # Assert
    assert task_response.status_code == 200
    assert user_task_response.status_code == 200
    assert task_response.json()["id"] == user_task_response.json()["task_id"]
