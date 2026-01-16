# Pytest Fixtures Guide

## What Are Fixtures?

Fixtures are reusable setup functions that provide data, resources, or test prerequisites. They reduce code duplication and centralize setup logic.

## Basic Fixtures

### Simple Fixture

```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "Test User", "age": 25}

def test_user_name(sample_data):
    assert sample_data["name"] == "Test User"

def test_user_age(sample_data):
    assert sample_data["age"] == 25
```

### Fixture with Setup and Teardown

```python
@pytest.fixture
def database_connection():
    # Setup
    conn = create_connection()
    yield conn
    # Teardown
    conn.close()

def test_query(database_connection):
    result = database_connection.execute("SELECT * FROM users")
    assert result is not None
```

## Fixture Scopes

Control how often fixtures are created and destroyed.

### Function Scope (Default)

Created and destroyed for each test function.

```python
@pytest.fixture(scope="function")
def fresh_data():
    return []
```

### Class Scope

Created once per test class.

```python
@pytest.fixture(scope="class")
def class_data():
    return {"shared": "value"}

class TestSuite:
    def test_one(self, class_data):
        assert "shared" in class_data

    def test_two(self, class_data):
        assert class_data["shared"] == "value"
```

### Module Scope

Created once per test module.

```python
@pytest.fixture(scope="module")
def expensive_resource():
    # Heavy initialization
    resource = load_large_dataset()
    yield resource
    # Cleanup
    resource.cleanup()
```

### Session Scope

Created once per test session (entire test run).

```python
@pytest.fixture(scope="session")
def docker_container():
    container = start_docker_container()
    yield container
    stop_docker_container(container)
```

## FastAPI Testing Fixtures

### TestClient Fixture

```python
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
```

### Database Fixture

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base

@pytest.fixture(scope="function")
def test_db():
    # Create test database
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
```

### Combined Client + Database Fixture

```python
@pytest.fixture
def client_with_db(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_create_user(client_with_db):
    response = client_with_db.post("/users/", json={"email": "test@example.com"})
    assert response.status_code == 201
```

## Authentication Fixtures

### User Fixture

```python
@pytest.fixture
def test_user(test_db):
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user
```

### Token Fixture

```python
@pytest.fixture
def auth_token(test_user):
    from auth import create_access_token
    return create_access_token(data={"sub": test_user.email})
```

### Authenticated Client Fixture

```python
@pytest.fixture
def authenticated_client(client, auth_token):
    client.headers = {"Authorization": f"Bearer {auth_token}"}
    return client

def test_protected_endpoint(authenticated_client):
    response = authenticated_client.get("/users/me")
    assert response.status_code == 200
```

## Fixture Parametrization

Run tests with multiple fixture values.

```python
@pytest.fixture(params=["sqlite", "postgresql", "mysql"])
def db_engine(request):
    if request.param == "sqlite":
        return create_engine("sqlite:///./test.db")
    elif request.param == "postgresql":
        return create_engine("postgresql://localhost/test")
    elif request.param == "mysql":
        return create_engine("mysql://localhost/test")

def test_database_operations(db_engine):
    # This test runs 3 times, once for each database
    assert db_engine is not None
```

## Fixture Dependencies

Fixtures can depend on other fixtures.

```python
@pytest.fixture
def database():
    return setup_database()

@pytest.fixture
def user(database):
    return database.create_user("testuser")

@pytest.fixture
def post(database, user):
    return database.create_post(author=user, title="Test Post")

def test_post(post):
    assert post.title == "Test Post"
    assert post.author.username == "testuser"
```

## Autouse Fixtures

Automatically used by all tests without explicit request.

```python
@pytest.fixture(autouse=True)
def reset_database():
    # Runs before each test
    clear_database()
    yield
    # Runs after each test
    clear_database()

def test_one():
    # Database is automatically cleared before this
    pass

def test_two():
    # Database is automatically cleared before this too
    pass
```

### Reset Dependency Overrides

```python
@pytest.fixture(autouse=True)
def reset_app_state():
    yield
    app.dependency_overrides.clear()
```

## Factory Fixtures

Create fixtures that return factory functions.

```python
@pytest.fixture
def user_factory(test_db):
    def create_user(email, username="testuser"):
        user = User(email=email, username=username)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user
    return create_user

def test_multiple_users(user_factory):
    user1 = user_factory("user1@example.com")
    user2 = user_factory("user2@example.com", "customuser")
    assert user1.email != user2.email
```

## conftest.py

Share fixtures across multiple test files by placing them in conftest.py.

### Project Structure

```
tests/
├── conftest.py          # Shared fixtures
├── test_users.py
├── test_posts.py
└── test_auth.py
```

### conftest.py Example

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine

@pytest.fixture(scope="session")
def test_app():
    return app

@pytest.fixture(scope="function")
def client(test_app):
    return TestClient(test_app)

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
```

All fixtures in conftest.py are automatically available to all test files in the same directory and subdirectories.

## Async Fixtures

For async operations and async database connections.

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///./test.db")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = AsyncSession(engine)
    yield async_session

    await async_session.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_async_operation(async_db):
    result = await async_db.execute(select(User))
    users = result.scalars().all()
    assert isinstance(users, list)
```

## Fixture Best Practices

1. **Use appropriate scopes** - Function for isolation, module/session for expensive resources
2. **Keep fixtures focused** - Each fixture should do one thing
3. **Use conftest.py** - Share common fixtures across test files
4. **Name fixtures clearly** - Use descriptive names (test_db, auth_token, sample_user)
5. **Cleanup resources** - Use yield to ensure teardown happens
6. **Avoid fixture overuse** - Don't create fixtures for simple one-time data
7. **Document complex fixtures** - Add docstrings for non-obvious fixtures
8. **Use factory fixtures** - When you need multiple instances with variations
9. **Leverage autouse sparingly** - Only for truly universal setup/teardown
10. **Chain fixtures logically** - Build complex fixtures from simpler ones

## Common Patterns

### Database Rollback Pattern

```python
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

### Mock External API

```python
from unittest.mock import Mock, patch

@pytest.fixture
def mock_external_api():
    with patch('app.external_api_client') as mock:
        mock.get_data.return_value = {"status": "success"}
        yield mock
```

### Environment Variables

```python
import os

@pytest.fixture
def set_test_env():
    os.environ['ENV'] = 'test'
    os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
    yield
    del os.environ['ENV']
    del os.environ['DATABASE_URL']
```

### Temporary Files

```python
import tempfile
import os

@pytest.fixture
def temp_file():
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.remove(path)
```
