def test_signin_success(client):
    response = client.post("/signin", json={
        "name": "Zain",
        "email": "zain@gmail.com",
        "password": "zain123"
    })
    assert response.status_code == 200
    assert "successfully" in response.json()["message"]


def test_signin_duplicate_email(client, normal_user):
    response = client.post("/signin", json={
        "name": "Another",
        "email": "test@gmail.com",
        "password": "pass123"
    })
    assert response.status_code == 400


def test_login_success(client, normal_user):
    response = client.post("/login", json={
        "email": "test@gmail.com",
        "password": "test123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, normal_user):
    response = client.post("/login", json={
        "email": "test@gmail.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401


def test_login_wrong_email(client):
    response = client.post("/login", json={
        "email": "noone@gmail.com",
        "password": "test123"
    })
    assert response.status_code == 401


def test_get_profile_success(client, user_headers):
    response = client.get("/profile", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "email" in data


def test_get_profile_no_token(client):
    response = client.get("/profile")
    assert response.status_code == 401


def test_get_profile_invalid_token(client):
    headers = {"Authorization": "Bearer fakeinvalidtoken123"}
    response = client.get("/profile", headers=headers)
    assert response.status_code == 401
