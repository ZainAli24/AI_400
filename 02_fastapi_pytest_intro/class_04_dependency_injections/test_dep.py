from fastapi.testclient import TestClient
from dep import app, connect_database


def fake_db():
    return {"db": "sqlite:///test.db", "connected": True}


def test_connect_db():
    app.dependency_overrides[connect_database] = fake_db

    client = TestClient(app)
    response = client.get("/db")
    assert response.json() == {"status": {"db": "sqlite:///test.db", "connected": True}}

    app.dependency_overrides.clear()
