# Getting Started with Pytest

## Installation

Pytest requires Python 3.8+ or PyPy3.

```bash
pip install -U pytest
pytest --version
```

## Your First Test

Create a file named `test_sample.py`:

```python
# content of test_sample.py
def func(x):
    return x + 1

def test_answer():
    assert func(3) == 4
```

Run your tests:

```bash
pytest
```

## Understanding Test Discovery

Pytest automatically discovers tests by looking for:

- Files matching `test_*.py` or `*_test.py`
- Functions/methods starting with `test_`
- Classes starting with `Test` (without an `__init__` method)

## Basic Assertions

Use plain Python `assert` statements:

```python
def test_ok():
    pass  # Passing test

def test_words_fail():
    fruits1 = ["banana", "apple", "grapes", "melon", "kiwi"]
    fruits2 = ["banana", "apple", "orange", "melon", "kiwi"]
    assert fruits1 == fruits2  # Pytest shows detailed diff on failure

def test_numbers_fail():
    number_to_text1 = {str(x): x for x in range(5)}
    number_to_text2 = {str(x * 10): x * 10 for x in range(5)}
    assert number_to_text1 == number_to_text2

def test_long_text_fail():
    long_text = "Lorem ipsum dolor sit amet " * 10
    assert "hello world" in long_text
```

## Running Tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Run specific file
pytest test_sample.py

# Run specific test
pytest test_sample.py::test_answer

# Run tests matching pattern
pytest -k "answer"

# Stop after first failure
pytest -x

# Show local variables in tracebacks
pytest -l
```

## Understanding Test Output

When a test fails, pytest provides:

- **Location**: File and line number
- **Assertion details**: What was compared
- **Intermediate values**: Results of function calls
- **Diff**: For sequences and dicts

Example output:

```
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-8.x.y, pluggy-1.x.y
rootdir: /home/sweet/project
collected 1 item

test_sample.py F                                                     [100%]

================================= FAILURES =================================
_______________________________ test_answer ________________________________

    def test_answer():
>       assert inc(3) == 5
E       assert 4 == 5
E        +  where 4 = inc(3)

test_sample.py:6: AssertionError
========================= short test summary info ==========================
FAILED test_sample.py::test_answer - assert 4 == 5
============================ 1 failed in 0.12s =============================
```

## Testing Exceptions

```python
import pytest

def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_exception_message():
    with pytest.raises(ValueError, match="invalid literal"):
        int("hello")
```

## Basic Project Structure

```
my_project/
├── src/
│   └── mymodule.py
├── tests/
│   ├── __init__.py
│   ├── test_mymodule.py
│   └── conftest.py
└── pytest.ini
```
