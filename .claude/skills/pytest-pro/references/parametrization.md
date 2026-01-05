# Parametrization in Pytest

Parametrization allows running the same test with different inputs, avoiding code duplication.

## Table of Contents

- [Basic Parametrization](#basic-parametrization)
- [Multiple Parameters](#multiple-parameters)
- [Parametrize with IDs](#parametrize-with-ids)
- [Combining Parametrize Decorators](#combining-parametrize-decorators)
- [Parametrize with Marks](#parametrize-with-marks)
- [Parametrized Fixtures](#parametrized-fixtures)
- [Advanced Patterns](#advanced-patterns)

## Basic Parametrization

Use `@pytest.mark.parametrize` to run a test with multiple inputs:

```python
import pytest

@pytest.mark.parametrize("test_input,expected", [
    ("3+5", 8),
    ("2+4", 6),
    ("6*9", 54),
])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```

This creates 3 separate tests:
- `test_eval[3+5-8]`
- `test_eval[2+4-6]`
- `test_eval[6*9-54]`

## Multiple Parameters

Parametrize with multiple arguments:

```python
@pytest.mark.parametrize("x,y,expected", [
    (1, 2, 3),
    (5, 5, 10),
    (10, -5, 5),
])
def test_add(x, y, expected):
    assert x + y == expected
```

## Parametrize with IDs

Provide custom test IDs for better readability:

```python
@pytest.mark.parametrize("test_input,expected", [
    ("3+5", 8),
    ("2+4", 6),
    ("6*9", 54),
], ids=["addition1", "addition2", "multiplication"])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```

Or use `pytest.param` with `id` parameter:

```python
@pytest.mark.parametrize("test_input,expected", [
    pytest.param("3+5", 8, id="simple_addition"),
    pytest.param("2+4", 6, id="another_addition"),
    pytest.param("6*9", 54, id="multiplication"),
])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```

## Combining Parametrize Decorators

Stack decorators to test all combinations:

```python
@pytest.mark.parametrize("x", [0, 1])
@pytest.mark.parametrize("y", [2, 3])
def test_foo(x, y):
    pass
```

This creates 4 tests with all combinations:
- `test_foo[2-0]` (x=0, y=2)
- `test_foo[2-1]` (x=1, y=2)
- `test_foo[3-0]` (x=0, y=3)
- `test_foo[3-1]` (x=1, y=3)

## Parametrize with Marks

Apply markers to specific test instances:

```python
import pytest

@pytest.mark.parametrize("test_input,expected", [
    ("3+5", 8),
    pytest.param("1+7", 8, marks=pytest.mark.basic),
    pytest.param("2+4", 6, marks=pytest.mark.basic, id="basic_2+4"),
    pytest.param(
        "6*9", 42,
        marks=[pytest.mark.basic, pytest.mark.xfail],
        id="basic_6*9"
    ),
])
def test_eval(test_input, expected):
    """Test how much I know division."""
    assert eval(test_input) == expected
```

Apply markers to individual test instances:

```python
@pytest.mark.foo
@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (1, 2),
        pytest.param(1, 3, marks=pytest.mark.bar),
        (2, 3)
    ]
)
def test_increment(n, expected):
    assert n + 1 == expected
```

Run only marked tests:

```bash
# Run only tests marked with 'basic'
pytest -m basic

# Run only tests marked with 'foo'
pytest -m foo
```

## Parametrized Fixtures

Fixtures can also be parametrized:

```python
import pytest

@pytest.fixture(params=["smtp.gmail.com", "smtp.outlook.com"])
def smtp_connection(request):
    server = request.param
    conn = connect_to_smtp(server)
    yield conn
    conn.close()

def test_send_email(smtp_connection):
    # Runs twice: once for each SMTP server
    assert smtp_connection.send_email("test@example.com")
```

Combine with test parametrization:

```python
@pytest.fixture(params=[1, 2])
def multiplier(request):
    return request.param

@pytest.mark.parametrize("value", [10, 20])
def test_multiply(multiplier, value):
    # Runs 4 times: all combinations of multiplier and value
    result = multiplier * value
    assert result > 0
```

## Advanced Patterns

### Parametrize from External Data

```python
import pytest
import json

def load_test_data():
    with open("test_data.json") as f:
        return json.load(f)

@pytest.mark.parametrize("test_case", load_test_data())
def test_from_file(test_case):
    assert process(test_case["input"]) == test_case["expected"]
```

### Parametrize Classes

Apply parametrization to all methods in a class:

```python
@pytest.mark.parametrize("n", [1, 2, 3])
class TestClass:
    def test_simple(self, n):
        assert n > 0

    def test_complex(self, n):
        assert n * 2 > 0
```

Both methods run 3 times each (6 tests total).

### Conditional Parametrization

Use `pytest_generate_tests` hook for dynamic parametrization:

```python
# conftest.py
def pytest_generate_tests(metafunc):
    if "scenario" in metafunc.fixturenames:
        scenarios = metafunc.config.getoption("--scenarios")
        if scenarios:
            metafunc.parametrize("scenario", scenarios.split(","))
```

### Skip or XFail with Parameters

```python
@pytest.mark.parametrize("value,expected", [
    (1, 2),
    pytest.param(2, 4, marks=pytest.mark.skip(reason="Not ready")),
    pytest.param(3, 6, marks=pytest.mark.xfail(reason="Known bug")),
])
def test_double(value, expected):
    assert value * 2 == expected
```

### Parametrize with Indirect

Use fixtures to transform parameter values:

```python
import pytest

@pytest.fixture
def user(request):
    """Transform user ID to user object"""
    user_id = request.param
    return get_user_by_id(user_id)

@pytest.mark.parametrize("user", [1, 2, 3], indirect=True)
def test_user(user):
    assert user.is_active
```

### Multiple Parametrize Arguments with Indirect

```python
@pytest.fixture
def x(request):
    return request.param * 2

@pytest.fixture
def y(request):
    return request.param * 3

@pytest.mark.parametrize("x,y", [(1, 2), (3, 4)], indirect=True)
def test_something(x, y):
    # x values: 2, 6
    # y values: 6, 12
    assert x > 0 and y > 0
```

## Best Practices

1. **Use descriptive IDs**: Make test output readable
2. **Keep parameter lists short**: If too many, consider fixture parametrization
3. **Group related tests**: Use classes with parametrization
4. **Avoid complex parameter generation**: Keep test data simple and explicit
5. **Use marks effectively**: Tag expected failures, slow tests, etc.
