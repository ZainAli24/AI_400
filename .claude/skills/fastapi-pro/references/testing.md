# Testing Guide

## Table of Contents
- Test Setup with pytest
- Testing Endpoints
- Testing with Database
- Testing Authentication
- Mocking Dependencies
- Test Coverage

## Test Setup

### Install Testing Dependencies

```bash
pip install pytest pytest-asyncio httpx
```

### Project Structure

```
project/
├── app/
│   ├── api/
│   ├── models/
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_auth.py
│   └── test_database.py
└── pytest.ini
```

### Configuration Files

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

### Test Fixtures

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

## Testing Endpoints

### Basic GET Request

```python
# tests/test_api.py
def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Testing POST Requests

```python
def test_create_item(client):
    response = client.post(
        "/api/v1/items/",
        json={"name": "Test Item", "price": 10.99}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 10.99
    assert "id" in data
```

### Testing PUT/DELETE

```python
def test_update_item(client):
    # First create an item
    create_response = client.post(
        "/api/v1/items/",
        json={"name": "Test", "price": 10.0}
    )
    item_id = create_response.json()["id"]

    # Update it
    response = client.put(
        f"/api/v1/items/{item_id}",
        json={"name": "Updated", "price": 20.0}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"

def test_delete_item(client):
    # Create and then delete
    create_response = client.post(
        "/api/v1/items/",
        json={"name": "Test", "price": 10.0}
    )
    item_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/items/{item_id}")
    assert response.status_code == 204
```

### Testing Error Handling

```python
def test_item_not_found(client):
    response = client.get("/api/v1/items/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_invalid_data(client):
    response = client.post(
        "/api/v1/items/",
        json={"name": "Test"}  # Missing required price field
    )
    assert response.status_code == 422  # Validation error
```

## Testing with Database

### Database Fixtures

```python
@pytest.fixture
def sample_user(db):
    from app.models.user import User
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_get_user(client, sample_user):
    response = client.get(f"/api/v1/users/{sample_user.id}")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

### Testing Database Operations

```python
def test_database_crud(db):
    from app.models.item import Item

    # Create
    item = Item(name="Test", price=10.0)
    db.add(item)
    db.commit()
    db.refresh(item)
    assert item.id is not None

    # Read
    fetched_item = db.query(Item).filter(Item.id == item.id).first()
    assert fetched_item.name == "Test"

    # Update
    fetched_item.price = 20.0
    db.commit()
    assert fetched_item.price == 20.0

    # Delete
    db.delete(fetched_item)
    db.commit()
    assert db.query(Item).filter(Item.id == item.id).first() is None
```

## Testing Authentication

### Auth Fixtures

```python
@pytest.fixture
def auth_headers(client, sample_user):
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": sample_user.username})
    return {"Authorization": f"Bearer {token}"}

def test_protected_endpoint(client, auth_headers):
    response = client.get("/api/v1/protected", headers=auth_headers)
    assert response.status_code == 200

def test_protected_endpoint_no_auth(client):
    response = client.get("/api/v1/protected")
    assert response.status_code == 401
```

### Testing Login

```python
def test_login_success(client, sample_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == 401
```

## Mocking Dependencies

### Mocking External Services

```python
from unittest.mock import Mock, patch

@patch('app.services.email.send_email')
def test_send_email(mock_send_email, client):
    mock_send_email.return_value = True

    response = client.post(
        "/api/v1/send-notification",
        json={"email": "test@example.com", "message": "Hello"}
    )

    assert response.status_code == 200
    mock_send_email.assert_called_once()
```

### Dependency Overrides

```python
def test_with_mock_dependency(client):
    def mock_get_current_user():
        return {"id": 1, "username": "testuser"}

    app.dependency_overrides[get_current_user] = mock_get_current_user

    response = client.get("/api/v1/me")
    assert response.status_code == 200

    app.dependency_overrides.clear()
```

## Async Testing

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
```

## Test Coverage

### Generate Coverage Report

```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = app
omit =
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Use Fixtures**: Reuse setup code with fixtures
3. **Test Edge Cases**: Test error conditions and edge cases
4. **Mock External Services**: Don't call real APIs in tests
5. **Use In-Memory DB**: Use SQLite in-memory for fast tests
6. **Clear Data**: Clean up after each test
7. **Descriptive Names**: Use clear test function names
8. **One Assertion**: Test one thing per test function
9. **Run Tests Often**: Run tests before committing
10. **Aim for Coverage**: Aim for >80% code coverage

## Parametrized Tests

```python
@pytest.mark.parametrize("price,expected", [
    (10.0, 10.0),
    (-5.0, 422),  # Should fail validation
    (0, 0),
])
def test_create_item_with_various_prices(client, price, expected):
    response = client.post(
        "/api/v1/items/",
        json={"name": "Test", "price": price}
    )
    if isinstance(expected, int):
        assert response.status_code == expected
    else:
        assert response.json()["price"] == expected
```
