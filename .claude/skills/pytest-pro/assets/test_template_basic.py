"""
Basic test template.
Copy and modify this template for simple unit tests.
"""

import pytest


# Simple test function
def test_example():
    """Test basic functionality."""
    result = 2 + 2
    assert result == 4


# Test with fixture
def test_with_fixture(sample_data):
    """Test using a fixture."""
    assert sample_data["name"] == "Test User"
    assert sample_data["age"] > 0


# Test class grouping related tests
class TestCalculator:
    """Group related tests in a class."""

    def test_addition(self):
        """Test addition operation."""
        assert 1 + 1 == 2

    def test_subtraction(self):
        """Test subtraction operation."""
        assert 5 - 3 == 2

    def test_multiplication(self):
        """Test multiplication operation."""
        assert 3 * 4 == 12

    def test_division(self):
        """Test division operation."""
        assert 10 / 2 == 5


# Test with parametrization
@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (5, 10),
])
def test_double(input_value, expected):
    """Test doubling various inputs."""
    result = input_value * 2
    assert result == expected


# Test exceptions
def test_division_by_zero():
    """Test that division by zero raises exception."""
    with pytest.raises(ZeroDivisionError):
        result = 1 / 0


def test_exception_message():
    """Test exception with specific message."""
    with pytest.raises(ValueError, match="invalid literal"):
        int("not a number")


# Test with markers
@pytest.mark.slow
def test_expensive_operation():
    """Test marked as slow."""
    # Simulate expensive operation
    result = sum(range(1000000))
    assert result > 0


@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    """Test to be implemented."""
    pass


@pytest.mark.skipif(True, reason="Conditionally skipped")
def test_conditional():
    """Test skipped based on condition."""
    pass


# Test with setup and teardown in class
class TestWithSetup:
    """Test class with setup and teardown methods."""

    def setup_method(self):
        """Run before each test method."""
        self.data = [1, 2, 3]

    def teardown_method(self):
        """Run after each test method."""
        self.data = None

    def test_data_exists(self):
        """Test that data was set up."""
        assert self.data == [1, 2, 3]

    def test_data_length(self):
        """Test data length."""
        assert len(self.data) == 3
