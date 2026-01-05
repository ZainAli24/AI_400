# Pytest Best Practices

Professional patterns and guidelines for writing effective tests with pytest.

## Table of Contents

- [Test Organization](#test-organization)
- [Test Naming](#test-naming)
- [Test Structure](#test-structure)
- [Fixture Design](#fixture-design)
- [Assertion Patterns](#assertion-patterns)
- [Test Data Management](#test-data-management)
- [Performance](#performance)
- [Common Pitfalls](#common-pitfalls)

## Test Organization

### Directory Structure

```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── models.py
│       ├── services.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── unit/
│   │   ├── conftest.py      # Unit test fixtures
│   │   ├── test_models.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── conftest.py      # Integration test fixtures
│   │   └── test_api.py
│   └── e2e/
│       └── test_workflows.py
├── pytest.ini
└── pyproject.toml
```

### Mirror Source Structure

```
src/myapp/
├── auth/
│   ├── login.py
│   └── permissions.py
└── api/
    ├── users.py
    └── posts.py

tests/
├── unit/
│   ├── auth/
│   │   ├── test_login.py
│   │   └── test_permissions.py
│   └── api/
│       ├── test_users.py
│       └── test_posts.py
```

### Separate Test Types

Use markers to categorize tests:

```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow tests")

# Run different test suites
# pytest -m unit                    # Fast, isolated
# pytest -m integration             # Medium speed, some dependencies
# pytest -m "not slow"              # Skip slow tests
```

## Test Naming

### Descriptive Test Names

```python
# Bad
def test_user():
    pass

def test_login():
    pass

# Good
def test_user_creation_with_valid_email():
    pass

def test_login_fails_with_invalid_password():
    pass

def test_user_cannot_delete_other_users_posts():
    pass
```

### Name Pattern: test_<unit>_<scenario>_<expected>

```python
def test_email_validator_accepts_valid_email():
    assert is_valid_email("user@example.com")

def test_email_validator_rejects_email_without_at():
    assert not is_valid_email("userexample.com")

def test_shopping_cart_calculates_total_with_tax():
    cart = ShoppingCart()
    cart.add_item(Item(price=100))
    assert cart.total_with_tax() == 110
```

## Test Structure

### AAA Pattern (Arrange-Act-Assert)

```python
def test_user_registration():
    # Arrange - Set up test data and preconditions
    username = "testuser"
    email = "test@example.com"
    password = "secure123"

    # Act - Perform the action being tested
    user = register_user(username, email, password)

    # Assert - Verify the expected outcome
    assert user.username == username
    assert user.email == email
    assert user.is_active is True
```

### One Assertion Per Test (When Practical)

```python
# Acceptable - Related assertions testing same behavior
def test_user_registration_creates_active_user():
    user = register_user("test", "test@example.com", "pass123")
    assert user.is_active is True
    assert user.email_verified is False

# Better - Separate concerns
def test_user_registration_creates_active_user():
    user = register_user("test", "test@example.com", "pass123")
    assert user.is_active is True

def test_user_registration_sets_email_unverified():
    user = register_user("test", "test@example.com", "pass123")
    assert user.email_verified is False
```

### Test Independence

```python
# Bad - Tests depend on each other
class TestUserWorkflow:
    user = None

    def test_create_user(self):
        self.user = User.create("test")  # Modifies class state
        assert self.user.id is not None

    def test_update_user(self):
        self.user.update(name="New Name")  # Depends on previous test
        assert self.user.name == "New Name"

# Good - Independent tests
class TestUserWorkflow:
    @pytest.fixture
    def user(self):
        return User.create("test")

    def test_create_user(self, user):
        assert user.id is not None

    def test_update_user(self, user):
        user.update(name="New Name")
        assert user.name == "New Name"
```

## Fixture Design

### Fixture Scope Principles

```python
# Function scope (default) - Fresh data for each test
@pytest.fixture
def user():
    return User.create("test")

# Module scope - Share expensive setup
@pytest.fixture(scope="module")
def database():
    db = Database.connect()
    yield db
    db.close()

# Session scope - One-time setup
@pytest.fixture(scope="session")
def app_config():
    return load_config()
```

### Fixture Composition

```python
# Build complex fixtures from simple ones
@pytest.fixture
def database_url():
    return "postgresql://localhost/testdb"

@pytest.fixture
def database(database_url):
    db = connect(database_url)
    yield db
    db.close()

@pytest.fixture
def user_repository(database):
    return UserRepository(database)

def test_create_user(user_repository):
    user = user_repository.create("test@example.com")
    assert user.id is not None
```

### Fixture Factories

```python
@pytest.fixture
def make_user(database):
    """Factory for creating test users"""
    users = []

    def _make_user(username, email, **kwargs):
        user = User.create(username, email, **kwargs)
        database.add(user)
        users.append(user)
        return user

    yield _make_user

    # Cleanup all created users
    for user in users:
        database.delete(user)

def test_multiple_users(make_user):
    alice = make_user("alice", "alice@example.com")
    bob = make_user("bob", "bob@example.com")
    assert alice.id != bob.id
```

## Assertion Patterns

### Use Specific Assertions

```python
# Bad
assert len(users) > 0

# Good
assert len(users) == 3

# Bad
assert result is not None

# Good
assert isinstance(result, User)
assert result.id == expected_id
```

### Test Exceptions Properly

```python
# Bad
def test_invalid_email():
    try:
        register_user("test", "invalid-email", "pass")
        assert False, "Should have raised"
    except ValueError:
        pass

# Good
def test_invalid_email_raises_value_error():
    with pytest.raises(ValueError, match="Invalid email format"):
        register_user("test", "invalid-email", "pass")
```

### Use pytest Helpers

```python
# Approximate comparisons
assert result == pytest.approx(0.333, rel=1e-3)

# Multiple assertions with detailed output
from pytest import approx
assert {
    "total": result.total,
    "tax": result.tax,
} == {
    "total": approx(110.0),
    "tax": approx(10.0),
}
```

## Test Data Management

### Use Factories Over Fixtures for Complex Data

```python
# Use factory_boy or similar
import factory

class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    is_active = True

def test_user_creation():
    user = UserFactory()
    assert user.username.startswith("user")
```

### Separate Test Data Files

```python
# tests/data/users.json
[
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"}
]

# tests/conftest.py
import json
from pathlib import Path

@pytest.fixture
def test_users():
    data_file = Path(__file__).parent / "data" / "users.json"
    with open(data_file) as f:
        return json.load(f)
```

### Parameterize Test Data

```python
# Good for boundary testing
@pytest.mark.parametrize("age,expected", [
    (0, False),
    (17, False),
    (18, True),
    (65, True),
    (120, True),
])
def test_is_adult(age, expected):
    assert is_adult(age) == expected
```

## Performance

### Use Appropriate Fixture Scope

```python
# Bad - Expensive setup runs for every test
@pytest.fixture
def ml_model():
    return load_large_model()  # Runs 100 times for 100 tests

# Good - Setup runs once
@pytest.fixture(scope="module")
def ml_model():
    return load_large_model()  # Runs once per module
```

### Parallelize Tests

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto          # Auto-detect CPU count
pytest -n 4             # Use 4 processes
```

### Mark Slow Tests

```python
@pytest.mark.slow
def test_large_data_processing():
    # Expensive test
    pass

# Run fast tests only
# pytest -m "not slow"
```

### Use tmp_path for File Operations

```python
def test_file_creation(tmp_path):
    # tmp_path is automatically cleaned up
    file = tmp_path / "test.txt"
    file.write_text("content")
    assert file.read_text() == "content"
```

## Common Pitfalls

### Avoid Test Interdependence

```python
# Bad - Order matters
def test_1_create_user():
    global user
    user = User.create("test")

def test_2_update_user():
    user.update(name="New")  # Fails if test_1 doesn't run

# Good - Independent
@pytest.fixture
def user():
    return User.create("test")

def test_create_user(user):
    assert user.id is not None

def test_update_user(user):
    user.update(name="New")
    assert user.name == "New"
```

### Don't Test Implementation Details

```python
# Bad - Tests internal implementation
def test_user_password_hash():
    user = User(password="secret")
    assert user._password_hash.startswith("$2b$")

# Good - Tests behavior
def test_user_password_verification():
    user = User(password="secret")
    assert user.verify_password("secret") is True
    assert user.verify_password("wrong") is False
```

### Mock Appropriately

```python
# Bad - Over-mocking makes test meaningless
def test_user_service(mocker):
    mocker.patch("app.validate_email", return_value=True)
    mocker.patch("app.hash_password", return_value="hashed")
    mocker.patch("app.save_user", return_value=User())

    result = create_user("test@example.com", "pass")
    assert result is not None  # Test proves nothing

# Good - Mock only external dependencies
def test_user_service(mocker):
    # Mock external email validation service
    mocker.patch("app.external_email_validator", return_value=True)

    # Test actual business logic
    user = create_user("test@example.com", "pass")
    assert user.email == "test@example.com"
    assert verify_password("pass", user.password_hash)
```

### Use Setup/Teardown Properly

```python
# Bad - Teardown not guaranteed
def test_database_operation():
    conn = database.connect()
    # ... test code ...
    conn.close()  # Won't run if test fails

# Good - Guaranteed cleanup
@pytest.fixture
def db_connection():
    conn = database.connect()
    yield conn
    conn.close()  # Always runs

def test_database_operation(db_connection):
    # ... test code ...
```

## Coverage Best Practices

```ini
# pytest.ini
[pytest]
addopts =
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Summary Checklist

- [ ] Tests are independent and can run in any order
- [ ] Test names clearly describe what is being tested
- [ ] One logical assertion per test (when practical)
- [ ] AAA pattern: Arrange, Act, Assert
- [ ] Fixtures are used for setup/teardown
- [ ] Appropriate fixture scope for performance
- [ ] Mocks only external dependencies
- [ ] Test behavior, not implementation
- [ ] Parameterize similar test cases
- [ ] Slow tests are marked and can be skipped
- [ ] Test coverage is meaningful, not just high percentage
