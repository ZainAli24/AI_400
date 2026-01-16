import pytest
from fastapi.testclient import TestClient
from main import app, loginResponseData, loginResponseDataReturn


client = TestClient(app)

def test_login_data():
    response = client.get("/login", params={"id": 1, "name": "zain", "email": "ali", "age": 21})
    assert response.status_code == 200
    expected_response = {
        "id": 1,
        "name": "zain",
        "email": "ali",
        "age": 21,
        "is_active": True
    }
    assert response.json() == expected_response



def test_register_data():
    request_data = {
        "id": 2,
        "name": "john",
        "email": "john@example.com",
        "age": 25
    }
    response = client.post("/register", json=request_data)
    assert response.status_code == 200
    expected_response = {
        "id": 2,
        "name": "john",
        "email": "john@example.com",
        "age": 25,
        "is_active": True
    }
    assert response.json() == expected_response


def test_delete_user():
    user_id = 3
    response = client.delete(f"/delete_user/{user_id}")
    assert response.status_code == 200
    expected_response = {"message": f"User with ID {user_id} has been deleted."}
    assert response.json() == expected_response


def test_update_user():
    user_id = 4
    request_data = {
        "id": user_id,
        "name": "alice",
        "email": "alice@example.com",
        "age": 30
    }
    response = client.put(f"/update_user/{user_id}", json=request_data)
    assert response.status_code == 200
    expected_response = {
        "message": f"User with ID {user_id} has been updated.",
        "data": request_data
    }
    assert response.json() == expected_response


def test_update_user_partial_data():
    user_id = 5
    # Simulating partial update by sending only some fields using PATCH
    response = client.patch(
        f"/minor_update_user/{user_id}",
        params={"name": "bob", "email": "bob@example.com"}
    )
    assert response.status_code == 200
    expected_response = {
        "message": f"User with ID {user_id} has been partially updated.",
        "updates": {"name": "bob", "email": "bob@example.com"}
    }
    assert response.json() == expected_response


    