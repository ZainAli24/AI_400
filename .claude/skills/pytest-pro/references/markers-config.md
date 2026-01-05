# Custom Markers and Configuration

Learn how to customize pytest behavior with markers and configuration files.

## Table of Contents

- [Built-in Markers](#built-in-markers)
- [Custom Markers](#custom-markers)
- [Configuration Files](#configuration-files)
- [Command-line Options](#command-line-options)
- [Hooks and Plugins](#hooks-and-plugins)

## Built-in Markers

Pytest provides several built-in markers:

### `@pytest.mark.skip`

Skip a test unconditionally:

```python
import pytest

@pytest.mark.skip(reason="Not implemented yet")
def test_feature():
    pass
```

### `@pytest.mark.skipif`

Skip based on a condition:

```python
import sys
import pytest

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_new_feature():
    pass

@pytest.mark.skipif(not has_database(), reason="No database available")
def test_database():
    pass
```

### `@pytest.mark.xfail`

Mark test as expected to fail:

```python
@pytest.mark.xfail(reason="Known bug in library")
def test_buggy_feature():
    assert library.buggy_function() == "expected"

@pytest.mark.xfail(sys.platform == "win32", reason="Fails on Windows")
def test_unix_feature():
    pass
```

### `@pytest.mark.parametrize`

See [parametrization.md](parametrization.md) for details.

## Custom Markers

Define and use custom markers to organize and select tests.

### Registering Custom Markers

Register markers in `pytest.ini` or `conftest.py`:

**pytest.ini:**

```ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    smoke: marks tests as smoke tests
    requires_network: marks tests that require network access
```

**conftest.py:**

```python
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_network: marks tests that require network"
    )
```

### Using Custom Markers

```python
import pytest

@pytest.mark.slow
def test_large_computation():
    # Expensive test
    pass

@pytest.mark.integration
def test_api_integration():
    # Integration test
    pass

@pytest.mark.unit
@pytest.mark.smoke
def test_basic_functionality():
    # Quick smoke test
    pass
```

### Running Tests by Marker

```bash
# Run only slow tests
pytest -m slow

# Run all except slow tests
pytest -m "not slow"

# Run integration OR slow tests
pytest -m "integration or slow"

# Run integration AND slow tests
pytest -m "integration and slow"

# Run unit tests but not slow ones
pytest -m "unit and not slow"
```

### Custom Marker with Arguments

```python
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "env(name): mark test to run only on named environment"
    )

def pytest_addoption(parser):
    parser.addoption(
        "-E",
        action="store",
        metavar="NAME",
        help="only run tests matching the environment NAME.",
    )

def pytest_runtest_setup(item):
    envnames = [mark.args[0] for mark in item.iter_markers(name="env")]
    if envnames:
        if item.config.getoption("-E") not in envnames:
            pytest.skip(f"test requires env in {envnames!r}")
```

Usage:

```python
@pytest.mark.env("staging")
def test_staging_feature():
    pass

@pytest.mark.env("production")
def test_production_feature():
    pass
```

Run with: `pytest -E staging`

## Configuration Files

### pytest.ini

Primary configuration file (recommended):

```ini
[pytest]
# Minimum pytest version
minversion = 7.0

# Test discovery patterns
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Command line options always applied
addopts =
    -ra
    --strict-markers
    --strict-config
    --showlocals
    --tb=short

# Test paths
testpaths = tests

# Markers
markers =
    slow: marks tests as slow
    integration: integration tests
    unit: unit tests
    smoke: smoke tests

# Minimum coverage threshold
# (requires pytest-cov)
[coverage:report]
fail_under = 80
```

### pyproject.toml

Alternative configuration using TOML:

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra --strict-markers --strict-config"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

markers = [
    "slow: marks tests as slow",
    "integration: integration tests",
    "unit: unit tests",
]
```

### setup.cfg

Alternative INI-style configuration:

```ini
[tool:pytest]
minversion = 7.0
addopts = -ra --strict-markers
testpaths = tests
```

### tox.ini

If using tox:

```ini
[pytest]
addopts = -v --tb=short
```

## Command-line Options

### Custom Command-line Options

Add custom options in `conftest.py`:

```python
def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to use for tests: chrome, firefox, safari",
    )
    parser.addoption(
        "--slow",
        action="store_true",
        help="Run slow tests",
    )
    parser.addoption(
        "--api-url",
        action="store",
        default="http://localhost:8000",
        help="API URL for integration tests",
    )

@pytest.fixture
def browser(request):
    return request.config.getoption("--browser")

@pytest.fixture
def api_url(request):
    return request.config.getoption("--api-url")

def pytest_collection_modifyitems(config, items):
    if not config.getoption("--slow"):
        skip_slow = pytest.mark.skip(reason="need --slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
```

Usage:

```bash
pytest --browser=firefox
pytest --slow
pytest --api-url=https://staging.example.com
```

## Hooks and Plugins

### Common Hooks

Implement hooks in `conftest.py`:

#### `pytest_configure`

Called after command line options are parsed:

```python
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: slow tests")
    # Set up test environment
```

#### `pytest_collection_modifyitems`

Modify collected test items:

```python
def pytest_collection_modifyitems(config, items):
    # Add marker to all tests in specific directory
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
```

#### `pytest_runtest_setup`

Called before running each test:

```python
def pytest_runtest_setup(item):
    # Skip tests based on custom logic
    if "db" in item.fixturenames:
        if not database_available():
            pytest.skip("Database not available")
```

#### `pytest_sessionstart`

Called before test session starts:

```python
def pytest_sessionstart(session):
    # Set up test database
    setup_test_database()
```

#### `pytest_sessionfinish`

Called after all tests finish:

```python
def pytest_sessionfinish(session, exitstatus):
    # Clean up resources
    cleanup_test_database()
```

### Creating a Simple Plugin

**conftest.py:**

```python
import pytest

class CustomPlugin:
    def pytest_configure(self, config):
        config.addinivalue_line(
            "markers", "custom: custom marker"
        )

    def pytest_collection_modifyitems(self, items):
        for item in items:
            if "custom" in item.keywords:
                print(f"Custom test: {item.name}")

def pytest_configure(config):
    config.pluginmanager.register(CustomPlugin())
```

### Plugin Examples

#### Auto-retry Failed Tests

```python
import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--retries",
        action="store",
        default=0,
        type=int,
        help="Number of times to retry failed tests",
    )

def pytest_runtest_makereport(item, call):
    if call.when == "call":
        if call.excinfo is not None:
            retries = item.config.getoption("--retries")
            if retries > 0:
                item.stash.setdefault("retry_count", 0)
                if item.stash["retry_count"] < retries:
                    item.stash["retry_count"] += 1
                    item.add_marker(pytest.mark.rerun)
```

## Best Practices

1. **Register all markers**: Use `--strict-markers` to catch typos
2. **Document markers**: Add descriptions in pytest.ini
3. **Organize tests**: Use markers to create logical test groups
4. **Custom options**: Add command-line options for flexibility
5. **Use hooks sparingly**: Only when necessary for custom behavior
6. **Keep configuration simple**: Start minimal, add as needed
7. **Version control config**: Commit pytest.ini to repository
8. **Document custom behavior**: Comment hooks and plugins clearly
