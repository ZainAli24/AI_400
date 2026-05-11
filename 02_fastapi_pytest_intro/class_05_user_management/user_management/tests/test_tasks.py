def test_create_task_success(client, user_headers):
    response = client.post("/tasks", json={
        "title": "Buy milk",
        "description": "From the store",
        "status": "pending"
    }, headers=user_headers)
    assert response.status_code == 200
    assert "successfully" in response.json()["message"]


def test_create_task_no_auth(client):
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 401


def test_get_tasks_success(client, user_headers):
    client.post("/tasks", json={"title": "Buy milk"}, headers=user_headers)
    response = client.get("/tasks", headers=user_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_tasks_empty(client, user_headers):
    response = client.get("/tasks", headers=user_headers)
    assert response.status_code == 404


def test_filter_tasks_pending(client, user_headers):
    client.post("/tasks", json={"title": "Pending Task", "status": "pending"}, headers=user_headers)
    response = client.get("/tasks/filter?task_status=pending", headers=user_headers)
    assert response.status_code == 200
    for task in response.json():
        assert task["status"] == "pending"


def test_filter_tasks_not_found(client, user_headers):
    response = client.get("/tasks/filter?task_status=completed", headers=user_headers)
    assert response.status_code == 404


def test_update_task_success(client, user_headers):
    client.post("/tasks", json={"title": "Old Title"}, headers=user_headers)
    task_id = client.get("/tasks", headers=user_headers).json()[0]["id"]

    response = client.put(f"/tasks/update/{task_id}", json={"title": "New Title"}, headers=user_headers)
    assert response.status_code == 200
    assert "updated" in response.json()["message"]


def test_update_task_not_found(client, user_headers):
    response = client.put("/tasks/update/9999", json={"title": "New"}, headers=user_headers)
    assert response.status_code == 404


def test_delete_task_success(client, user_headers):
    client.post("/tasks", json={"title": "Delete me"}, headers=user_headers)
    task_id = client.get("/tasks", headers=user_headers).json()[0]["id"]

    response = client.delete(f"/tasks/delete/{task_id}", headers=user_headers)
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]


def test_delete_task_not_found(client, user_headers):
    response = client.delete("/tasks/delete/9999", headers=user_headers)
    assert response.status_code == 404


def test_data_isolation_between_users(client, user_headers, admin_headers):
    client.post("/tasks", json={"title": "User task"}, headers=user_headers)
    response = client.get("/tasks", headers=admin_headers)
    assert response.status_code == 404
