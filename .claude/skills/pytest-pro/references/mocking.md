# Mocking and Monkeypatching in Pytest

Pytest provides the `monkeypatch` fixture for modifying objects, functions, dictionaries, and environment variables during tests.

## Table of Contents

- [Monkeypatch Basics](#monkeypatch-basics)
- [Mocking Functions and Methods](#mocking-functions-and-methods)
- [Environment Variables](#environment-variables)
- [Dictionary Patching](#dictionary-patching)
- [Attribute Patching](#attribute-patching)
- [Module-level Mocking](#module-level-mocking)
- [Fixture-based Mocking Patterns](#fixture-based-mocking-patterns)
- [pytest-mock Plugin](#pytest-mock-plugin)

## Monkeypatch Basics

The `monkeypatch` fixture provides methods to safely modify objects during test execution:

- `setattr(target, name, value)` - Set an attribute
- `delattr(target, name)` - Delete an attribute
- `setitem(dic, name, value)` - Set a dictionary entry
- `delitem(dic, name)` - Delete a dictionary entry
- `setenv(name, value)` - Set an environment variable
- `delenv(name)` - Delete an environment variable
- `syspath_prepend(path)` - Prepend to `sys.path`
- `chdir(path)` - Change current directory

All modifications are automatically undone after the test.

## Mocking Functions and Methods

### Mock External API Calls

```python
import pytest
import requests
import app

class MockResponse:
    @staticmethod
    def json():
        return {"mock_key": "mock_response"}

def test_get_json(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    result = app.get_json("https://fakeurl")
    assert result["mock_key"] == "mock_response"
```

### Mock with Fixture Pattern

Create reusable mocks as fixtures:

```python
import pytest
import requests
import app

class MockResponse:
    @staticmethod
    def json():
        return {"mock_key": "mock_response"}

@pytest.fixture
def mock_response(monkeypatch):
    """Requests.get() mocked to return {'mock_key':'mock_response'}."""

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

def test_get_json(mock_response):
    result = app.get_json("https://fakeurl")
    assert result["mock_key"] == "mock_response"
```

### Mock Method in a Class

```python
class UserService:
    def get_user(self, user_id):
        return database.query(user_id)

def test_user_service(monkeypatch):
    def mock_get_user(self, user_id):
        return {"id": user_id, "name": "Test User"}

    monkeypatch.setattr(UserService, "get_user", mock_get_user)

    service = UserService()
    user = service.get_user(123)
    assert user["name"] == "Test User"
```

## Environment Variables

### Set Environment Variables

```python
import os
import pytest

def get_os_user_lower():
    return os.getenv("USER", "").lower()

def test_upper_to_lower(monkeypatch):
    """Set the USER env var to assert the behavior."""
    monkeypatch.setenv("USER", "TestingUser")
    assert get_os_user_lower() == "testinguser"

def test_raise_exception(monkeypatch):
    """Remove the USER env var and assert OSError is raised."""
    monkeypatch.delenv("USER", raising=False)

    with pytest.raises(OSError):
        _ = get_os_user_lower()
```

### Environment Variable Fixture

```python
@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key-123")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

def test_with_env(mock_env_vars):
    assert os.getenv("API_KEY") == "test-key-123"
```

## Dictionary Patching

### Modify Configuration Dictionaries

```python
import app

def test_connection(monkeypatch):
    monkeypatch.setitem(app.DEFAULT_CONFIG, "user", "test_user")
    monkeypatch.setitem(app.DEFAULT_CONFIG, "database", "test_db")

    expected = "User Id=test_user; Location=test_db;"
    result = app.create_connection_string()
    assert result == expected

def test_missing_user(monkeypatch):
    monkeypatch.delitem(app.DEFAULT_CONFIG, "user", raising=False)

    with pytest.raises(KeyError):
        _ = app.create_connection_string()
```

### Modular Mocking Pattern

Create separate fixtures for each mock configuration:

```python
import pytest
import app

@pytest.fixture
def mock_test_user(monkeypatch):
    """Set the DEFAULT_CONFIG user to test_user."""
    monkeypatch.setitem(app.DEFAULT_CONFIG, "user", "test_user")

@pytest.fixture
def mock_test_database(monkeypatch):
    """Set the DEFAULT_CONFIG database to test_db."""
    monkeypatch.setitem(app.DEFAULT_CONFIG, "database", "test_db")

@pytest.fixture
def mock_missing_default_user(monkeypatch):
    """Remove the user key from DEFAULT_CONFIG"""
    monkeypatch.delitem(app.DEFAULT_CONFIG, "user", raising=False)

# Tests use only needed fixtures
def test_connection(mock_test_user, mock_test_database):
    expected = "User Id=test_user; Location=test_db;"
    result = app.create_connection_string()
    assert result == expected

def test_missing_user(mock_missing_default_user):
    with pytest.raises(KeyError):
        _ = app.create_connection_string()
```

## Attribute Patching

### Patch Object Attributes

```python
class Config:
    DEBUG = False
    MAX_CONNECTIONS = 100

def test_debug_mode(monkeypatch):
    monkeypatch.setattr(Config, "DEBUG", True)
    assert Config.DEBUG is True

def test_max_connections(monkeypatch):
    monkeypatch.setattr(Config, "MAX_CONNECTIONS", 10)
    assert Config.MAX_CONNECTIONS == 10
```

### Patch Built-in Functions

```python
import app

def test_input_mock(monkeypatch):
    # Mock the built-in input() function
    monkeypatch.setattr('builtins.input', lambda _: "mocked input")

    result = app.get_user_input()
    assert result == "mocked input"
```

## Module-level Mocking

### Mock Imported Modules

```python
import pytest

class MockDatabase:
    def query(self, sql):
        return [{"id": 1, "name": "Test"}]

def test_database_query(monkeypatch):
    import myapp
    monkeypatch.setattr(myapp, "database", MockDatabase())

    result = myapp.get_users()
    assert len(result) == 1
```

### Mock with Context Manager

```python
def test_file_operations(monkeypatch, tmp_path):
    # Mock file path
    mock_file = tmp_path / "test.txt"
    mock_file.write_text("test content")

    monkeypatch.setattr("app.get_file_path", lambda: str(mock_file))

    content = app.read_config_file()
    assert content == "test content"
```

## Fixture-based Mocking Patterns

### Factory Pattern for Mocks

```python
@pytest.fixture
def make_mock_user(monkeypatch):
    users = {}

    def _make_user(user_id, name, email):
        users[user_id] = {"id": user_id, "name": name, "email": email}
        monkeypatch.setattr(
            "app.get_user",
            lambda uid: users.get(uid)
        )
        return users[user_id]

    return _make_user

def test_multiple_users(make_mock_user):
    user1 = make_mock_user(1, "Alice", "alice@example.com")
    user2 = make_mock_user(2, "Bob", "bob@example.com")

    from app import get_user
    assert get_user(1)["name"] == "Alice"
```

### Scope-based Mocking

```python
@pytest.fixture(scope="module")
def mock_external_service(monkeypatch):
    """Module-scoped mock - set up once for all tests in module"""
    with monkeypatch.context() as m:
        m.setenv("SERVICE_URL", "http://mock.example.com")
        yield
```

## pytest-mock Plugin

For more advanced mocking, install `pytest-mock`:

```bash
pip install pytest-mock
```

### Using mocker Fixture

```python
def test_with_mocker(mocker):
    # Mock with return value
    mock_func = mocker.patch("app.external_call", return_value=42)

    result = app.external_call()
    assert result == 42
    mock_func.assert_called_once()

def test_mock_method(mocker):
    # Mock class method
    mock_method = mocker.patch.object(UserService, "get_user")
    mock_method.return_value = {"id": 1, "name": "Test"}

    service = UserService()
    user = service.get_user(1)

    assert user["name"] == "Test"
    mock_method.assert_called_once_with(1)
```

### Spy on Functions

```python
def test_spy(mocker):
    # Spy calls the original function and records calls
    spy = mocker.spy(math, "sqrt")

    result = math.sqrt(16)

    assert result == 4.0
    spy.assert_called_once_with(16)
```

### Mock Multiple Calls

```python
def test_side_effect(mocker):
    mock_func = mocker.patch("app.get_data")
    mock_func.side_effect = [1, 2, 3]

    assert app.get_data() == 1
    assert app.get_data() == 2
    assert app.get_data() == 3
```

## Best Practices

1. **Prefer monkeypatch for simple cases**: Built-in, no dependencies
2. **Use pytest-mock for complex scenarios**: Better API for assertions
3. **Create fixture-based mocks**: Reusable and maintainable
4. **Mock at the right level**: Mock where imported, not where defined
5. **Keep mocks simple**: Return minimal data needed for test
6. **Use modular fixtures**: Separate fixtures for different mock configurations
7. **Document mocks**: Explain what's being mocked and why
8. **Clean up automatically**: Leverage pytest's automatic cleanup
