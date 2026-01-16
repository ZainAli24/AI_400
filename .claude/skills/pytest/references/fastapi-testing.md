# FastAPI Testing Patterns

## TestClient Setup

FastAPI uses TestClient from Starlette for testing. TestClient is based on HTTPX and provides a synchronous interface for testing both sync and async endpoints.

### Basic Setup

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

**Important**: Use regular `def` (not `async def`) for test functions with TestClient.

## Testing HTTP Methods

### GET Requests

```python
def test_read_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert "id" in response.json()

def test_with_query_params():
    response = client.get("/items?skip=0&limit=10")
    assert response.status_code == 200
    assert len(response.json()) <= 10
```

### POST Requests

```python
def test_create_item():
    payload = {
        "name": "Test Item",
        "description": "A test item",
        "price": 10.5
    }
    response = client.post("/items/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data
```

### PUT/PATCH Requests

```python
def test_update_item():
    response = client.put(
        "/items/1",
        json={"name": "Updated Item", "price": 20.0}
    )
    assert response.status_code == 200

def test_partial_update():
    response = client.patch(
        "/items/1",
        json={"price": 15.5}
    )
    assert response.status_code == 200
```

### DELETE Requests

```python
def test_delete_item():
    response = client.delete("/items/1")
    assert response.status_code == 204

    # Verify deletion
    response = client.get("/items/1")
    assert response.status_code == 404
```

## Headers, Cookies, and Authentication

### Custom Headers

```python
def test_with_headers():
    headers = {"X-Token": "test-token", "X-Custom": "value"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200

def test_auth_header():
    headers = {"Authorization": "Bearer test-token"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
```

### Cookies

```python
def test_with_cookies():
    cookies = {"session_id": "test-session"}
    response = client.get("/dashboard", cookies=cookies)
    assert response.status_code == 200
```

### Form Data

```python
def test_login_form():
    form_data = {
        "username": "testuser",
        "password": "testpass"
    }
    response = client.post("/login", data=form_data)
    assert response.status_code == 200
```

## Dependency Overrides

Override FastAPI dependencies for testing to mock databases, authentication, etc.

### Basic Override

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def test_with_test_db():
    response = client.get("/items/")
    assert response.status_code == 200
```

### Authentication Override

```python
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Real authentication logic
    pass

def override_get_current_user():
    return {"id": 1, "username": "testuser"}

app.dependency_overrides[get_current_user] = override_get_current_user

def test_protected_endpoint():
    response = client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

### Cleanup Overrides

```python
@pytest.fixture(autouse=True)
def reset_overrides():
    yield
    app.dependency_overrides.clear()
```

## Database Testing

### Test Database Setup

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base

TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
```

### Using Test Database in Tests

```python
def test_create_user(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db

    response = client.post("/users/", json={"email": "test@example.com"})
    assert response.status_code == 201
```

## Async Testing

For endpoints that use async external calls (databases, APIs), use httpx.AsyncClient.

### Installation

```bash
pip install pytest-asyncio httpx
```

### Async Test Example

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/async-items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_async_create():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/async-items/", json={"name": "Test"})
    assert response.status_code == 201
```

### Async Database Fixtures

```python
@pytest.fixture
async def async_db():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = AsyncSession(engine)
    yield async_session

    await async_session.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

## Error Handling Tests

Always test error conditions to ensure proper error responses.

### 404 Not Found

```python
def test_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
```

### 422 Validation Error

```python
def test_invalid_input():
    response = client.post("/items/", json={"invalid": "data"})
    assert response.status_code == 422
    assert "detail" in response.json()
```

### 401 Unauthorized

```python
def test_unauthorized():
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
```

### 403 Forbidden

```python
def test_forbidden():
    headers = {"Authorization": "Bearer user-token"}
    response = client.delete("/admin/users/1", headers=headers)
    assert response.status_code == 403
```

### Custom Error Handling

```python
def test_custom_error():
    response = client.post("/items/", json={"price": -10})
    assert response.status_code == 400
    assert "Price must be positive" in response.json()["detail"]
```

## File Upload Testing

```python
def test_upload_file():
    files = {"file": ("test.txt", b"file content", "text/plain")}
    response = client.post("/upload/", files=files)
    assert response.status_code == 200
    assert response.json()["filename"] == "test.txt"

def test_upload_image():
    with open("test_image.png", "rb") as f:
        files = {"file": ("image.png", f, "image/png")}
        response = client.post("/upload-image/", files=files)
    assert response.status_code == 200
```

## Background Tasks Testing

```python
from unittest.mock import Mock, patch

def test_background_task():
    with patch('app.send_email') as mock_send:
        response = client.post("/users/", json={"email": "test@example.com"})
        assert response.status_code == 201
        mock_send.assert_called_once()
```

## Response Models and Validation

```python
def test_response_model():
    response = client.get("/items/1")
    data = response.json()

    # Verify response structure
    assert "id" in data
    assert "name" in data
    assert "price" in data

    # Verify data types
    assert isinstance(data["id"], int)
    assert isinstance(data["name"], str)
    assert isinstance(data["price"], float)
```

## Testing CORS

```python
def test_cors_headers():
    response = client.options("/items/")
    assert "access-control-allow-origin" in response.headers

def test_cors_preflight():
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
    }
    response = client.options("/items/", headers=headers)
    assert response.status_code == 200
```

## Best Practices Summary

1. **Use TestClient for sync tests** - Simple and efficient for most cases
2. **Use AsyncClient for async operations** - When testing async database calls or external APIs
3. **Override dependencies** - Mock databases, authentication, external services
4. **Test all HTTP methods** - GET, POST, PUT, PATCH, DELETE
5. **Test error conditions** - 404, 422, 401, 403, 400, etc.
6. **Verify response structure** - Check both status codes and response data
7. **Isolate tests** - Each test should be independent
8. **Clean up after tests** - Clear dependency overrides, drop test databases
9. **Test authentication** - Both successful and failed auth scenarios
10. **Test edge cases** - Empty responses, large payloads, special characters
