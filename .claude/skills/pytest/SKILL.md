---
name: pytest
description: Comprehensive pytest testing framework for FastAPI projects. Use when writing tests, setting up test infrastructure, testing API endpoints, implementing fixtures, database testing, async testing, parametrization, mocking, or implementing testing best practices. Covers TestClient usage, dependency overrides, error testing, coverage, and CI/CD integration.
---

# Pytest for FastAPI Testing

Professional testing framework for FastAPI applications with pytest. This skill provides patterns, best practices, and complete examples for comprehensive API testing.

## Before You Start

### Required Clarifications (Must Ask)
Before writing tests, gather these requirements:

| Question | Options | Impact |
|----------|---------|--------|
| Sync or Async endpoints? | Sync / Async / Both | Determines TestClient vs AsyncClient |
| Database testing needed? | SQLAlchemy / SQLModel / MongoDB / None | Affects fixture setup |
| Authentication testing? | JWT / OAuth2 / Session / None | Auth fixture patterns |
| Existing test setup? | Yes / No | Build on existing or create new |

### Optional Clarifications
| Question | Default |
|----------|---------|
| Coverage threshold? | 80% |
| CI/CD integration? | GitHub Actions |
| Watch mode needed? | No |

### Context Gathering Commands
```bash
# Check existing test structure
ls -la tests/ 2>/dev/null || echo "No tests folder"
cat conftest.py 2>/dev/null || echo "No conftest.py"
cat pytest.ini 2>/dev/null || cat pyproject.toml 2>/dev/null | grep -A 10 "\[tool.pytest"
```

## Quick Start

### Basic Test Structure

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

### Installation

```bash
pip install pytest httpx pytest-cov pytest-asyncio
```

### Run Tests

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=app          # With coverage
pytest -k "test_create"   # Match pattern
```

## Core Concepts

### 1. Test Files and Functions

- Files: `test_*.py` or `*_test.py`
- Functions: `def test_*()`
- Use regular `def` (not `async def`) with TestClient

### 2. Assertions

Use Python's `assert` statement:

```python
assert response.status_code == 200
assert "id" in response.json()
assert response.json()["name"] == "Test"
```

### 3. Fixtures

Reusable setup functions for common test prerequisites:

```python
import pytest

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_db():
    # Setup database
    yield db
    # Teardown
```

### 4. Parametrization

Test multiple inputs with one function:

```python
@pytest.mark.parametrize("email,status", [
    ("valid@example.com", 201),
    ("invalid", 422),
])
def test_validation(email, status):
    response = client.post("/users/", json={"email": email})
    assert response.status_code == status
```

## FastAPI Testing Essentials

### TestClient

```python
from fastapi.testclient import TestClient

client = TestClient(app)

# GET request
response = client.get("/items/1")

# POST with JSON
response = client.post("/items/", json={"name": "Test"})

# With headers
response = client.get("/items/", headers={"Authorization": "Bearer token"})

# With cookies
response = client.get("/dashboard", cookies={"session": "id"})
```

### Dependency Overrides

Mock dependencies for testing:

```python
def override_get_db():
    return test_db

app.dependency_overrides[get_db] = override_get_db

# Test with mock dependency
response = client.get("/items/")

# Cleanup
app.dependency_overrides.clear()
```

### Database Testing Pattern

```python
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    db = SessionLocal()
    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)
```

### Async Testing

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/async-items/")
    assert response.status_code == 200
```

## Testing Checklist

- [ ] Test all HTTP methods (GET, POST, PUT, DELETE)
- [ ] Test success cases (200, 201, 204)
- [ ] Test error cases (404, 422, 401, 403)
- [ ] Test with authentication
- [ ] Test database operations
- [ ] Test validation errors
- [ ] Use fixtures for setup/teardown
- [ ] Keep tests independent
- [ ] Measure coverage
- [ ] Mock external dependencies

## Reference Documentation

For detailed patterns and advanced usage, see:

- **[references/fastapi-testing.md](references/fastapi-testing.md)** - Complete FastAPI testing patterns including TestClient, HTTP methods, dependency overrides, database testing, async testing, error handling, file uploads, and response validation

- **[references/fixtures.md](references/fixtures.md)** - Comprehensive fixture guide covering scopes, parametrization, factory fixtures, async fixtures, conftest.py organization, and common patterns

- **[references/best-practices.md](references/best-practices.md)** - Best practices including test organization, independence, coverage, parametrization, error testing, markers, mocking, performance testing, and CI/CD integration

- **[references/examples.md](references/examples.md)** - Complete working examples of CRUD API testing, database testing with SQLAlchemy, authentication testing, parametrized tests, and async testing

## Key Principles

1. **Test Independence** - Each test runs successfully in isolation
2. **Use Fixtures** - Reduce duplication with reusable setup
3. **Test Errors** - Verify error handling for all failure cases
4. **Dependency Overrides** - Mock databases and external services
5. **Measure Coverage** - Use pytest-cov to track test coverage
6. **Keep Tests Fast** - Use in-memory databases, mock slow operations
7. **Organize Tests** - Mirror app structure in tests directory
8. **Use Markers** - Categorize tests (unit, integration, slow)

## Common Patterns

### Complete Test Setup (conftest.py)

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from database import Base, get_db
from main import app

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Authentication Testing

```python
@pytest.fixture
def auth_token():
    return create_access_token({"sub": "testuser"})

def test_protected_endpoint(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
```

### Error Testing

```python
def test_not_found(client):
    response = client.get("/items/999")
    assert response.status_code == 404

def test_validation_error(client):
    response = client.post("/items/", json={"invalid": "data"})
    assert response.status_code == 422

def test_unauthorized(client):
    response = client.get("/protected")
    assert response.status_code == 401
```

## Configuration (pytest.ini)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts =
    -v
    --cov=app
    --cov-report=term-missing
    --cov-report=html
markers =
    slow: slow running tests
    integration: integration tests
    unit: unit tests
```

## TDD Workflow: Red-Green-Refactor

TDD ka core principle: **Test First, Code Second**

### The TDD Cycle

```
┌─────────────────────────────────────────────────────────┐
│  1. RED         2. GREEN         3. REFACTOR           │
│  ─────────      ────────         ──────────            │
│  Write test     Write minimum    Improve code          │
│  that FAILS     code to PASS     (tests stay GREEN)    │
│                                                        │
│  ┌───┐          ┌───┐            ┌───┐                 │
│  │ ✗ │ ──────►  │ ✓ │ ────────►  │ ✓ │ ──► Repeat     │
│  └───┘          └───┘            └───┘                 │
└─────────────────────────────────────────────────────────┘
```

### Step 1: RED - Write Failing Test First

```python
# test_users.py - Test likho PEHLE, implementation BAAD mein
def test_create_user_returns_201():
    """User create karne par 201 status milna chahiye"""
    response = client.post("/users/", json={"email": "test@example.com"})
    assert response.status_code == 201  # ❌ FAIL - endpoint exists nahi
    assert response.json()["email"] == "test@example.com"
```

**Run Test (Expected: FAIL)**
```bash
pytest test_users.py -v
# ❌ FAILED - This is EXPECTED!
```

### Step 2: GREEN - Write Minimum Code to Pass

```python
# main.py - Sirf ITNA likho jitna test pass karne ke liye chahiye
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str

@app.post("/users/", status_code=201)
def create_user(user: UserCreate):
    return {"email": user.email}  # Minimum implementation
```

**Run Test (Expected: PASS)**
```bash
pytest test_users.py -v
# ✅ PASSED
```

### Step 3: REFACTOR - Improve While Tests Pass

```python
# Refactor: Add validation, improve structure
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr  # Better validation

class UserResponse(BaseModel):
    email: EmailStr
    id: int

@app.post("/users/", status_code=201, response_model=UserResponse)
def create_user(user: UserCreate):
    # Better implementation with ID
    return {"email": user.email, "id": 1}
```

**Update Test for New Response**
```python
def test_create_user_returns_201():
    response = client.post("/users/", json={"email": "test@example.com"})
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert "id" in response.json()  # New assertion
```

```bash
pytest test_users.py -v
# ✅ PASSED - Refactor successful
```

### TDD Best Practices

| Practice | Description |
|----------|-------------|
| Small Steps | Ek test, ek feature - bade jumps mat lo |
| Fast Tests | Tests < 1 second mein run hone chahiye |
| Independent | Har test independently pass hona chahiye |
| Clear Names | `test_create_user_with_invalid_email_returns_422` |
| One Assert Focus | Primary assertion clear hona chahiye |

### TDD Workflow Commands

```bash
# Watch mode - auto run on file change
pytest --watch  # (requires pytest-watch)
pip install pytest-watch
ptw  # Short command

# Run specific test during development
pytest test_users.py::test_create_user_returns_201 -v

# Run with print output (debugging)
pytest -v -s
```

For complete examples, advanced patterns, and detailed reference material, consult the documentation in the `references/` directory.

- **[references/tdd-workflow.md](references/tdd-workflow.md)** - Complete TDD patterns, error-first testing, incremental development
- **[references/security-testing.md](references/security-testing.md)** - SQL injection, XSS, authentication bypass, OWASP Top 10 testing

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| **Pytest Official** | https://docs.pytest.org/en/stable/ | Fixtures, markers, plugins |
| **FastAPI Testing** | https://fastapi.tiangolo.com/tutorial/testing/ | TestClient, dependency overrides |
| **pytest-asyncio** | https://pytest-asyncio.readthedocs.io/ | Async endpoint testing |
| **pytest-cov** | https://pytest-cov.readthedocs.io/ | Coverage configuration |
| **Hypothesis** | https://hypothesis.readthedocs.io/ | Property-based testing |
| **pytest-watch** | https://github.com/joeyespo/pytest-watch | TDD watch mode |
