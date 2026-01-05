# Pytest Fixtures

Fixtures provide a reusable way to set up test prerequisites and manage resources.

## Table of Contents

- [Basic Fixtures](#basic-fixtures)
- [Fixture Dependencies](#fixture-dependencies)
- [Fixture Scope](#fixture-scope)
- [Yield Fixtures and Teardown](#yield-fixtures-and-teardown)
- [conftest.py](#conftestpy)
- [Fixture Parameters](#fixture-parameters)
- [Built-in Fixtures](#built-in-fixtures)

## Basic Fixtures

Define fixtures using the `@pytest.fixture` decorator:

```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "John", "age": 30}

def test_sample(sample_data):
    assert sample_data["name"] == "John"
    assert sample_data["age"] == 30
```

## Fixture Dependencies

Fixtures can request other fixtures, enabling modular composition:

```python
import pytest

@pytest.fixture
def first_entry():
    return "a"

@pytest.fixture
def order(first_entry):  # Requests first_entry fixture
    return [first_entry]

def test_string(order):
    order.append("b")
    assert order == ["a", "b"]
```

## Fixture Scope

Control how often fixtures are created with the `scope` parameter:

- `function` (default): Once per test function
- `class`: Once per test class
- `module`: Once per module
- `package`: Once per package
- `session`: Once per test session

```python
import pytest

@pytest.fixture(scope="module")
def database_connection():
    """Created once per test module"""
    conn = create_connection()
    yield conn
    conn.close()

@pytest.fixture(scope="session")
def app_config():
    """Created once for entire test session"""
    return load_config()
```

## Yield Fixtures and Teardown

Use `yield` for setup/teardown patterns:

```python
import pytest
from emaillib import Email, MailAdminClient

@pytest.fixture
def mail_admin():
    return MailAdminClient()

@pytest.fixture
def sending_user(mail_admin):
    user = mail_admin.create_user()  # Setup
    yield user  # Provide to test
    mail_admin.delete_user(user)  # Teardown

@pytest.fixture
def receiving_user(mail_admin):
    user = mail_admin.create_user()
    yield user
    user.clear_mailbox()
    mail_admin.delete_user(user)

def test_email_received(sending_user, receiving_user):
    email = Email(subject="Hey!", body="How's it going?")
    sending_user.send_email(email, receiving_user)
    assert email in receiving_user.inbox
```

**Key points:**
- Code before `yield`: Setup
- Code after `yield`: Teardown (runs in reverse order)
- Teardown runs even if test fails
- Recommended over `addfinalizer`

## conftest.py

Share fixtures across multiple test files by placing them in `conftest.py`:

```python
# content of tests/conftest.py
import pytest

@pytest.fixture
def order():
    return []

@pytest.fixture
def top(order, innermost):
    order.append("top")
```

```python
# content of tests/test_top.py
import pytest

@pytest.fixture
def innermost(order):
    order.append("innermost top")

def test_order(order, top):
    assert order == ["innermost top", "top"]
```

**Fixture discovery:**
- Pytest automatically discovers `conftest.py` files
- Fixtures are available to all tests in that directory and subdirectories
- Subdirectory fixtures can override parent fixtures

**Directory structure:**

```
tests/
├── conftest.py           # Shared fixtures for all tests
├── test_top.py
└── subpackage/
    ├── conftest.py       # Additional fixtures for subpackage
    └── test_sub.py
```

## Fixture Parameters

Create parameterized fixtures to run tests with multiple configurations:

```python
import pytest

@pytest.fixture(params=["smtp.gmail.com", "smtp.outlook.com"])
def smtp_connection(request):
    """Run tests with multiple SMTP servers"""
    server = request.param
    conn = connect_to_smtp(server)
    yield conn
    conn.close()

def test_email_send(smtp_connection):
    # This test runs twice, once for each parameter
    assert smtp_connection.send_email("test@example.com")
```

## Built-in Fixtures

Pytest provides useful built-in fixtures:

### `tmp_path`

Provides a temporary directory unique to each test:

```python
def test_create_file(tmp_path):
    file = tmp_path / "data.txt"
    file.write_text("content")
    assert file.read_text() == "content"
```

### `monkeypatch`

Modify objects, dictionaries, environment variables:

```python
def test_env_var(monkeypatch):
    monkeypatch.setenv("USER", "TestUser")
    assert os.getenv("USER") == "TestUser"
```

### `capsys` / `capfd`

Capture stdout/stderr:

```python
def test_output(capsys):
    print("hello")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"
```

### `request`

Access test context information:

```python
@pytest.fixture
def example(request):
    print(f"Test: {request.node.name}")
    return request.param  # Access parametrize values
```

## Advanced Patterns

### Fixture Factories

Return a factory function for dynamic creation:

```python
import pytest

@pytest.fixture
def make_user():
    users = []

    def _make_user(name, email):
        user = User(name, email)
        users.append(user)
        return user

    yield _make_user

    # Cleanup all created users
    for user in users:
        user.delete()

def test_multiple_users(make_user):
    user1 = make_user("Alice", "alice@example.com")
    user2 = make_user("Bob", "bob@example.com")
    assert user1.name != user2.name
```

### Autouse Fixtures

Automatically run for all tests:

```python
@pytest.fixture(autouse=True)
def reset_database():
    """Automatically reset database before each test"""
    db.reset()
```

### Fixture Naming

Use the `name` parameter to create an alias:

```python
@pytest.fixture(name="db")
def database_connection():
    return connect_to_db()

def test_query(db):  # Use "db" instead of "database_connection"
    assert db.query("SELECT 1")
```
