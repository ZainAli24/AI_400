def test_admin_access_success(client, admin_headers):
    response = client.get("/admin/dashboard", headers=admin_headers)
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]


def test_admin_access_forbidden_for_normal_user(client, user_headers):
    response = client.get("/admin/dashboard", headers=user_headers)
    assert response.status_code == 403


def test_admin_access_no_token(client):
    response = client.get("/admin/dashboard")
    assert response.status_code == 401
