"""
Basic conftest.py template for simple projects.
Place this file in your tests/ directory.
"""

import pytest


# Sample fixture: Provides test data
@pytest.fixture
def sample_data():
    """Provides sample data for tests."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 25
    }


# Sample fixture: Temporary directory setup
@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory with some test files."""
    # Create test files
    (tmp_path / "test.txt").write_text("test content")
    (tmp_path / "data.json").write_text('{"key": "value"}')
    return tmp_path


# Sample fixture with teardown
@pytest.fixture
def resource():
    """Fixture with setup and teardown."""
    # Setup
    print("\nSetting up resource")
    resource_obj = {"status": "initialized"}

    yield resource_obj

    # Teardown
    print("\nCleaning up resource")
    resource_obj["status"] = "cleaned"


# Module-scoped fixture (runs once per test module)
@pytest.fixture(scope="module")
def expensive_resource():
    """Expensive resource created once per module."""
    print("\nCreating expensive resource")
    # Simulate expensive setup
    resource = {"data": "expensive to create"}
    yield resource
    print("\nDestroying expensive resource")


# Session-scoped fixture (runs once per test session)
@pytest.fixture(scope="session")
def app_config():
    """Application configuration for entire test session."""
    return {
        "debug": True,
        "testing": True,
        "database": ":memory:"
    }


# Configure pytest markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
