"""
API testing conftest.py template.
Includes fixtures for API clients, authentication, and request mocking.
"""

import pytest
from unittest.mock import Mock

# For FastAPI/Flask testing
# from fastapi.testclient import TestClient
# from myapp.main import app


@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for API testing."""
    return "http://localhost:8000"


@pytest.fixture(scope="module")
def api_client():
    """
    Create an API test client.
    For FastAPI: Use TestClient
    For Flask: Use app.test_client()
    For external APIs: Use requests
    """
    # Example for FastAPI:
    # client = TestClient(app)
    # yield client

    # Example for requests:
    import requests
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture
def auth_token():
    """Provide authentication token for tests."""
    return "test-token-12345"


@pytest.fixture
def auth_headers(auth_token):
    """Provide authentication headers."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def authenticated_client(api_client, auth_headers):
    """API client with authentication headers."""
    api_client.headers.update(auth_headers)
    yield api_client
    # Clear headers after test
    api_client.headers.clear()


# Mock external API responses

@pytest.fixture
def mock_api_response(monkeypatch):
    """Factory for mocking API responses."""

    def _mock_response(status_code=200, json_data=None, text=None):
        mock_resp = Mock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = json_data or {}
        mock_resp.text = text or ""
        mock_resp.ok = 200 <= status_code < 300
        return mock_resp

    return _mock_response


@pytest.fixture
def mock_successful_api_call(monkeypatch, mock_api_response):
    """Mock a successful API call."""
    def _mock_get(*args, **kwargs):
        return mock_api_response(200, {"status": "success"})

    monkeypatch.setattr("requests.get", _mock_get)


# Test user fixtures

@pytest.fixture
def test_user_data():
    """Sample user data for API tests."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }


@pytest.fixture
def admin_user_data():
    """Admin user data for API tests."""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "adminpass123",
        "is_admin": True
    }


# Response validation helpers

@pytest.fixture
def assert_valid_response():
    """Helper for validating API responses."""

    def _assert_valid(response, expected_status=200, expected_keys=None):
        assert response.status_code == expected_status, \
            f"Expected {expected_status}, got {response.status_code}: {response.text}"

        if expected_keys:
            data = response.json()
            for key in expected_keys:
                assert key in data, f"Expected key '{key}' not in response"

        return response.json() if response.ok else None

    return _assert_valid


# API endpoint fixtures

@pytest.fixture
def user_endpoint(api_base_url):
    """User API endpoint URL."""
    return f"{api_base_url}/api/users"


@pytest.fixture
def auth_endpoint(api_base_url):
    """Authentication endpoint URL."""
    return f"{api_base_url}/api/auth"


# Custom markers for API tests

def pytest_configure(config):
    """Register custom markers for API tests."""
    config.addinivalue_line(
        "markers",
        "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers",
        "requires_auth: marks tests that require authentication"
    )
    config.addinivalue_line(
        "markers",
        "requires_network: marks tests that require network access"
    )
    config.addinivalue_line(
        "markers",
        "external_api: marks tests that call external APIs"
    )


# Add command-line option for API URL

def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--api-url",
        action="store",
        default="http://localhost:8000",
        help="API base URL for integration tests"
    )
    parser.addoption(
        "--skip-integration",
        action="store_true",
        help="Skip integration tests"
    )


@pytest.fixture(scope="session")
def api_url(request):
    """Get API URL from command line or use default."""
    return request.config.getoption("--api-url")


# Skip integration tests if flag is set

def pytest_runtest_setup(item):
    """Skip tests based on markers and command-line options."""
    if item.config.getoption("--skip-integration"):
        if "api" in item.keywords or "integration" in item.keywords:
            pytest.skip("Skipping integration tests (--skip-integration)")
