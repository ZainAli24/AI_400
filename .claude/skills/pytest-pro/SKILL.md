---
name: pytest-pro
description: Comprehensive pytest testing framework skill for Python projects, covering beginner to professional workflows. Use when Claude needs to work with pytest testing for (1) Setting up pytest for a project, (2) Writing unit, integration, or end-to-end tests, (3) Creating test fixtures and conftest.py files, (4) Implementing parametrized tests, (5) Mocking and monkeypatching, (6) Configuring pytest with markers and hooks, (7) Organizing test suites, (8) Debugging test failures, or any Python testing workflow with pytest.
---

# Pytest Professional Testing Skill

Comprehensive guide for Python testing with pytest, from beginner setup to professional patterns.

## Quick Start Workflow

### For New Projects

1. **Install pytest**:
   ```bash
   uv add pytest pytest-cov
   ```

2. **Create test structure**:
   ```
   project/
   ├── src/
   │   └── myapp/
   ├── tests/
   │   ├── conftest.py
   │   └── test_myapp.py
   └── pytest.ini
   ```

3. **Copy configuration**: Use `assets/pytest.ini` as template

4. **Write first test**:
   ```python
   def test_example():
       assert 1 + 1 == 2
   ```

5. **Run tests**: `uv run pytest -v`

### For Existing Projects

1. **Assess current tests**: Run `uv run pytest --collect-only` to see discovered tests
2. **Add configuration**: Copy `assets/pytest.ini` and customize markers
3. **Create conftest.py**: Start with `assets/conftest-basic.py`
4. **Organize tests**: Separate unit/integration/e2e tests
5. **Add markers**: Tag tests (unit, slow, integration, etc.)

## Core Workflows

### Writing Tests

**Simple function test**:
```python
def test_addition():
    result = add(2, 3)
    assert result == 5
```

**Test with fixture**:
```python
@pytest.fixture
def user_data():
    return {"name": "Alice", "age": 30}

def test_user(user_data):
    assert user_data["age"] > 0
```

**See**: `assets/test_template_basic.py` for more examples

### Using Fixtures

Fixtures provide reusable setup/teardown:

```python
@pytest.fixture
def database():
    db = connect_database()
    yield db  # Provide to test
    db.close()  # Cleanup

def test_query(database):
    result = database.query("SELECT 1")
    assert result is not None
```

**Fixture patterns**:
- Basic fixtures: [references/fixtures.md](references/fixtures.md)
- Database fixtures: `assets/conftest-database.py`
- API fixtures: `assets/conftest-api.py`

### Parametrizing Tests

Run same test with different inputs:

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (5, 10),
    (10, 20),
])
def test_double(input, expected):
    assert input * 2 == expected
```

**See**: [references/parametrization.md](references/parametrization.md) for advanced patterns

### Mocking

Replace real implementations with test doubles:

```python
def test_api_call(monkeypatch):
    def mock_get(*args, **kwargs):
        return {"status": "ok"}

    monkeypatch.setattr("requests.get", mock_get)

    result = fetch_data()
    assert result["status"] == "ok"
```

**See**: [references/mocking.md](references/mocking.md) for comprehensive mocking patterns

## Progressive Skill Levels

### Beginner Level

**Goal**: Write and run basic tests

**Topics**:
- Installation and setup
- Test discovery (test_*.py, test_*)
- Basic assertions
- Running tests (pytest, pytest -v)

**Reference**: [references/getting-started.md](references/getting-started.md)

**Template**: `assets/test_template_basic.py`

### Intermediate Level

**Goal**: Use fixtures and organize tests

**Topics**:
- Fixtures and conftest.py
- Fixture scope (function, module, session)
- Setup/teardown with yield
- Test organization and markers
- Parametrization basics

**References**:
- [references/fixtures.md](references/fixtures.md)
- [references/parametrization.md](references/parametrization.md)

**Templates**:
- `assets/conftest-basic.py`
- `assets/conftest-database.py`

### Advanced/Professional Level

**Goal**: Professional test suites with advanced patterns

**Topics**:
- Custom markers and configuration
- Hooks and plugins
- Advanced mocking patterns
- Fixture factories
- Test performance optimization
- Coverage and quality metrics

**References**:
- [references/markers-config.md](references/markers-config.md)
- [references/mocking.md](references/mocking.md)
- [references/best-practices.md](references/best-practices.md)

**Template**: `assets/test_template_advanced.py`

## Common Tasks

### Setting Up Project Testing

1. Copy `assets/pytest.ini` to project root
2. Create `tests/` directory
3. Copy appropriate `conftest-*.py` from assets to `tests/conftest.py`
4. Customize markers in pytest.ini
5. Run `uv run pytest --collect-only` to verify setup

### Creating Test Fixtures

1. Identify reusable setup code
2. Extract to fixture in conftest.py
3. Use appropriate scope (function/module/session)
4. Add yield for teardown if needed
5. Document fixture purpose

**See**: [references/fixtures.md](references/fixtures.md)

### Testing APIs

1. Use `assets/conftest-api.py` as starting point
2. Create fixtures for:
   - Test client
   - Authentication
   - Mock responses
3. Organize by endpoint
4. Use markers (api, integration, requires_network)

### Testing Databases

1. Use `assets/conftest-database.py` as starting point
2. Create session-scoped database engine
3. Use transaction rollback for test isolation
4. Create factory fixtures for test data
5. Use `tmp_path` for SQLite testing

### Organizing Large Test Suites

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── conftest.py          # Unit-specific fixtures
│   ├── test_models.py
│   └── test_utils.py
├── integration/
│   ├── conftest.py          # Integration fixtures
│   ├── test_api.py
│   └── test_database.py
└── e2e/
    └── test_workflows.py
```

Run different suites:
```bash
uv run pytest tests/unit                    # Unit tests only
uv run pytest -m "not slow"                 # Skip slow tests
uv run pytest -m integration                # Integration tests only
```

### Debugging Test Failures

1. **Verbose output**: `uv run pytest -v`
2. **Show locals**: `uv run pytest -l`
3. **Drop into debugger**: `uv run pytest --pdb`
4. **Stop on first failure**: `uv run pytest -x`
5. **Show print statements**: `uv run pytest -s`
6. **Run specific test**: `uv run pytest path/to/test.py::test_name`

### Adding Coverage

1. Install: `uv add pytest-cov`
2. Run: `uv run pytest --cov=src --cov-report=html`
3. View: Open `htmlcov/index.html`
4. Add to pytest.ini:
   ```ini
   [pytest]
   addopts = --cov=src --cov-report=html --cov-report=term-missing
   ```

## Reference Files

Load these for detailed information on specific topics:

- **[getting-started.md](references/getting-started.md)**: Installation, first tests, basic assertions
- **[fixtures.md](references/fixtures.md)**: Fixture patterns, scope, conftest.py, factories
- **[parametrization.md](references/parametrization.md)**: Parametrize decorator, combining parameters, marks
- **[mocking.md](references/mocking.md)**: Monkeypatch, pytest-mock, environment variables, API mocking
- **[markers-config.md](references/markers-config.md)**: Custom markers, pytest.ini, hooks, plugins
- **[best-practices.md](references/best-practices.md)**: Professional patterns, organization, performance

## Asset Templates

Copy and customize these templates:

- **pytest.ini**: Project configuration with markers and options
- **conftest-basic.py**: Simple project fixtures
- **conftest-database.py**: Database testing fixtures with transactions
- **conftest-api.py**: API testing fixtures with mocking
- **test_template_basic.py**: Basic test examples
- **test_template_advanced.py**: Advanced test patterns

## When to Use Each Reference

- **Just starting**: [getting-started.md](references/getting-started.md)
- **Need reusable setup**: [fixtures.md](references/fixtures.md)
- **Testing multiple inputs**: [parametrization.md](references/parametrization.md)
- **Mocking dependencies**: [mocking.md](references/mocking.md)
- **Custom test organization**: [markers-config.md](references/markers-config.md)
- **Professional test suites**: [best-practices.md](references/best-practices.md)

## Best Practices Summary

1. **Test Independence**: Each test should run independently
2. **AAA Pattern**: Arrange, Act, Assert
3. **Descriptive Names**: `test_user_creation_with_valid_email`
4. **One Assertion**: Test one logical thing per test (when practical)
5. **Use Fixtures**: For setup/teardown and reusable test data
6. **Appropriate Scope**: Use minimal fixture scope needed
7. **Mock External**: Mock only external dependencies
8. **Organize Tests**: Separate unit/integration/e2e
9. **Mark Tests**: Use markers for test categories
10. **Measure Coverage**: But focus on meaningful tests, not just percentage

## Troubleshooting

**Tests not discovered**:
- Check file names match `test_*.py` or `*_test.py`
- Check function names start with `test_`
- Run `uv run pytest --collect-only` to see what's discovered

**Import errors**:
- Install package in development mode: `uv add -e .`
- Check PYTHONPATH includes src directory
- Verify `__init__.py` files exist

**Fixtures not found**:
- Check conftest.py is in test directory
- Verify fixture scope is appropriate
- Check for typos in fixture names

**Slow tests**:
- Use `pytest-xdist` for parallel execution: `uv run pytest -n auto`
- Mark slow tests: `@pytest.mark.slow`
- Use appropriate fixture scope
- Consider mocking instead of real I/O

## Additional Resources

- Pytest documentation: https://docs.pytest.org
- Install pytest-cov for coverage: `uv add pytest-cov`
- Install pytest-xdist for parallel execution: `uv add pytest-xdist`
- Install pytest-mock for advanced mocking: `uv add pytest-mock`
- Install pytest-asyncio for async tests: `uv add pytest-asyncio`
