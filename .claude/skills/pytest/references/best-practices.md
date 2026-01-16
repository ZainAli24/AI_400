# Pytest Best Practices for FastAPI

## Test Organization

### File Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   └── routers/
│       ├── users.py
│       └── items.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_users.py
│   ├── test_items.py
│   └── test_auth.py
├── pytest.ini
└── requirements.txt
```

### Naming Conventions

- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_*`
- Test classes: `Test*`
- Fixtures: descriptive names (e.g., `client`, `test_db`, `auth_token`)

### pytest.ini Configuration

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=app
    --cov-report=term-missing
    --cov-report=html
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## Test Independence and Isolation

### Rule: Tests Must Be Independent

Each test should run successfully in isolation and in any order.

**Bad Example:**

```python
# Test order matters - BAD
def test_create_user():
    global user_id
    response = client.post("/users/", json={"email": "test@example.com"})
    user_id = response.json()["id"]

def test_get_user():
    # Depends on test_create_user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
```

**Good Example:**

```python
# Each test is independent - GOOD
def test_create_user(client):
    response = client.post("/users/", json={"email": "test@example.com"})
    assert response.status_code == 201

def test_get_user(client, test_user):
    response = client.get(f"/users/{test_user.id}")
    assert response.status_code == 200
```

### Use Fresh Data for Each Test

```python
@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)  # Clean slate for next test
```

## Test Coverage

### Aim for Meaningful Coverage

Focus on critical paths rather than arbitrary coverage percentages.

### Use pytest-cov

```bash
pip install pytest-cov
pytest --cov=app --cov-report=html
```

### Coverage Configuration

```ini
[coverage:run]
source = app
omit =
    */tests/*
    */migrations/*
    */__init__.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

### Test What Matters

1. **API endpoints** - All routes and methods
2. **Business logic** - Core functionality
3. **Error handling** - Expected failures
4. **Edge cases** - Boundary conditions
5. **Authentication/Authorization** - Security critical paths

## Parametrization for DRY Tests

### Basic Parametrization

```python
@pytest.mark.parametrize("email,expected_status", [
    ("valid@example.com", 201),
    ("invalid-email", 422),
    ("", 422),
    ("test@", 422),
])
def test_create_user_validation(client, email, expected_status):
    response = client.post("/users/", json={"email": email})
    assert response.status_code == expected_status
```

### Multiple Parameters

```python
@pytest.mark.parametrize("method,endpoint,status", [
    ("GET", "/items", 200),
    ("GET", "/items/1", 200),
    ("POST", "/items", 401),  # No auth
    ("PUT", "/items/1", 401),
    ("DELETE", "/items/1", 401),
])
def test_auth_required(client, method, endpoint, status):
    response = getattr(client, method.lower())(endpoint)
    assert response.status_code == status
```

### With IDs for Readability

```python
@pytest.mark.parametrize("price,valid", [
    (10.0, True),
    (0, False),
    (-5, False),
    (999999, True),
], ids=["normal", "zero", "negative", "large"])
def test_price_validation(price, valid):
    item = {"name": "Test", "price": price}
    result = validate_item(item)
    assert result.is_valid == valid
```

## Error Testing

### Test All Error Conditions

```python
def test_not_found(client):
    response = client.get("/items/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_validation_error(client):
    response = client.post("/items/", json={"invalid": "data"})
    assert response.status_code == 422

def test_unauthorized(client):
    response = client.get("/users/me")
    assert response.status_code == 401

def test_forbidden(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.delete("/admin/users/1", headers=headers)
    assert response.status_code == 403
```

### Exception Testing

```python
def test_raises_exception():
    with pytest.raises(ValueError, match="Invalid input"):
        process_data("invalid")
```

## Markers for Test Organization

### Define Custom Markers

```python
# pytest.ini or conftest.py
pytest.mark.unit = "Unit tests"
pytest.mark.integration = "Integration tests"
pytest.mark.slow = "Slow running tests"
```

### Use Markers

```python
@pytest.mark.unit
def test_pure_function():
    assert add(2, 2) == 4

@pytest.mark.integration
def test_database_query(test_db):
    result = test_db.query(User).all()
    assert isinstance(result, list)

@pytest.mark.slow
def test_large_dataset():
    # Long running test
    pass
```

### Run Specific Markers

```bash
# Run only unit tests
pytest -m unit

# Run everything except slow tests
pytest -m "not slow"

# Run integration or slow tests
pytest -m "integration or slow"
```

## Mocking and Patching

### Mock External Dependencies

```python
from unittest.mock import Mock, patch

@pytest.fixture
def mock_email_service():
    with patch('app.email.send_email') as mock:
        mock.return_value = True
        yield mock

def test_user_registration(client, mock_email_service):
    response = client.post("/register", json={"email": "test@example.com"})
    assert response.status_code == 201
    mock_email_service.assert_called_once()
```

### Mock External APIs

```python
def test_external_api_call(client):
    with patch('app.services.external_api.get') as mock_get:
        mock_get.return_value.json.return_value = {"data": "test"}
        response = client.get("/external-data")
        assert response.status_code == 200
        mock_get.assert_called_once()
```

## Async Testing

### pytest-asyncio

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/async-items")
    assert response.status_code == 200
```

### Async Fixtures

```python
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

## Performance Testing

### Mark Slow Tests

```python
@pytest.mark.slow
def test_heavy_operation():
    # Long running test
    pass
```

### Use Timeouts

```bash
pip install pytest-timeout
```

```python
@pytest.mark.timeout(5)  # Fail if test takes more than 5 seconds
def test_should_be_fast():
    process_data()
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Test Data Management

### Use Factories

```python
class UserFactory:
    @staticmethod
    def create(db, **kwargs):
        defaults = {
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True
        }
        defaults.update(kwargs)
        user = User(**defaults)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

@pytest.fixture
def user_factory(test_db):
    return UserFactory()

def test_with_custom_user(user_factory):
    user = user_factory.create(email="custom@example.com")
    assert user.email == "custom@example.com"
```

### Use Faker for Realistic Data

```bash
pip install faker
```

```python
from faker import Faker

fake = Faker()

def test_with_fake_data(client):
    user_data = {
        "email": fake.email(),
        "name": fake.name(),
        "address": fake.address()
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
```

## Debugging Tests

### Print Debugging

```python
def test_debug(client, capsys):
    response = client.get("/items/1")
    print(response.json())  # Visible with -s flag
    assert response.status_code == 200
```

Run with output:

```bash
pytest -s
```

### Using pdb

```python
def test_with_pdb(client):
    response = client.get("/items/1")
    import pdb; pdb.set_trace()  # Breakpoint
    assert response.status_code == 200
```

### Verbose Output

```bash
pytest -v          # Verbose
pytest -vv         # More verbose
pytest --tb=short  # Short traceback
pytest --tb=long   # Long traceback
```

## Best Practices Checklist

- [ ] Tests are independent and can run in any order
- [ ] Each test has a clear purpose and tests one thing
- [ ] Test names describe what they test
- [ ] Use fixtures for setup and teardown
- [ ] Test both success and failure cases
- [ ] Use parametrization to reduce duplication
- [ ] Mock external dependencies
- [ ] Use appropriate test markers
- [ ] Maintain good test coverage
- [ ] Tests run fast (< 1 second per test ideally)
- [ ] Use conftest.py for shared fixtures
- [ ] Clean up resources after tests
- [ ] Tests are readable and maintainable
- [ ] Integration tests are separated from unit tests
- [ ] CI/CD runs tests on every commit
