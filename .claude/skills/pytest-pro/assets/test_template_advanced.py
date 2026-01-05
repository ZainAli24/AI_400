"""
Advanced test template with fixtures, mocking, and complex scenarios.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


# AAA Pattern (Arrange-Act-Assert)
def test_user_registration():
    """Test following AAA pattern."""
    # Arrange - Set up test data
    username = "testuser"
    email = "test@example.com"
    password = "secure123"

    # Act - Perform the action
    # user = register_user(username, email, password)

    # Assert - Verify the result
    # assert user.username == username
    # assert user.is_active is True
    pass


# Using multiple fixtures
def test_with_multiple_fixtures(db_session, user_factory):
    """Test using multiple fixtures."""
    user = user_factory("alice", "alice@example.com")
    # db_session.add(user)
    # db_session.commit()
    # assert user.id is not None
    pass


# Fixture factory pattern
def test_multiple_users(user_factory):
    """Test creating multiple users with factory."""
    alice = user_factory("alice", "alice@example.com")
    bob = user_factory("bob", "bob@example.com")
    # assert alice.id != bob.id
    pass


# Monkeypatch for mocking
def test_with_monkeypatch(monkeypatch):
    """Test using monkeypatch for mocking."""
    # Mock environment variable
    monkeypatch.setenv("API_KEY", "test-key")

    # Mock function
    def mock_get_user(user_id):
        return {"id": user_id, "name": "Test User"}

    # monkeypatch.setattr("myapp.get_user", mock_get_user)

    # result = get_user(123)
    # assert result["name"] == "Test User"
    pass


# Mock with pytest-mock (mocker fixture)
def test_with_mocker(mocker):
    """Test using mocker fixture for advanced mocking."""
    # Mock function with return value
    # mock_func = mocker.patch("myapp.external_api_call", return_value={"status": "ok"})

    # result = external_api_call()
    # assert result["status"] == "ok"
    # mock_func.assert_called_once()
    pass


# Mock class methods
def test_mock_class_method(mocker):
    """Test mocking class methods."""
    # mock_method = mocker.patch.object(UserService, "get_user")
    # mock_method.return_value = {"id": 1, "name": "Test"}

    # service = UserService()
    # user = service.get_user(1)

    # assert user["name"] == "Test"
    # mock_method.assert_called_once_with(1)
    pass


# Parametrize with marks
@pytest.mark.parametrize("test_input,expected", [
    pytest.param(1, 2, id="simple"),
    pytest.param(5, 10, id="medium"),
    pytest.param(100, 200, marks=pytest.mark.slow, id="large"),
])
def test_parametrize_with_marks(test_input, expected):
    """Test with parametrize and custom IDs."""
    result = test_input * 2
    assert result == expected


# Multiple parametrize decorators
@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [3, 4])
def test_multiple_parametrize(x, y):
    """Test all combinations of parameters."""
    result = x + y
    assert result > 0


# Async test (requires pytest-asyncio)
# @pytest.mark.asyncio
# async def test_async_operation():
#     """Test async function."""
#     result = await async_function()
#     assert result is not None


# Context manager testing
def test_context_manager(tmp_path):
    """Test file operations with context manager."""
    test_file = tmp_path / "test.txt"

    # Test writing
    with open(test_file, "w") as f:
        f.write("test content")

    # Test reading
    with open(test_file, "r") as f:
        content = f.read()

    assert content == "test content"


# Testing with temporary files
def test_temp_file(tmp_path):
    """Test using temporary path fixture."""
    file = tmp_path / "data.json"
    file.write_text('{"key": "value"}')

    content = file.read_text()
    assert "key" in content


# Capturing output
def test_output_capture(capsys):
    """Test capturing stdout/stderr."""
    print("Hello World")
    captured = capsys.readouterr()
    assert captured.out == "Hello World\n"


# Custom assertions with pytest.approx
def test_float_comparison():
    """Test floating point comparison."""
    result = 0.1 + 0.2
    assert result == pytest.approx(0.3, rel=1e-9)


# Testing with warnings
def test_warning():
    """Test that code produces expected warning."""
    with pytest.warns(UserWarning, match="deprecated"):
        # some_deprecated_function()
        import warnings
        warnings.warn("deprecated feature", UserWarning)


# Fixture with request parameter
@pytest.fixture(params=[1, 2, 3])
def number(request):
    """Parametrized fixture."""
    return request.param


def test_with_parametrized_fixture(number):
    """Test runs 3 times with different fixture values."""
    assert number > 0


# Autouse fixture
@pytest.fixture(autouse=True)
def reset_state():
    """Automatically runs before each test in this module."""
    # Setup
    yield
    # Teardown


# Complex test class with fixtures
class TestUserService:
    """Test class demonstrating advanced patterns."""

    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        """Setup that runs before each test in this class."""
        self.db = db_session
        yield
        # Cleanup after each test

    def test_create_user(self, user_factory):
        """Test user creation."""
        user = user_factory("test", "test@example.com")
        # assert user.id is not None

    def test_update_user(self, user_factory):
        """Test user update."""
        user = user_factory("test", "test@example.com")
        # user.name = "Updated"
        # self.db.commit()
        # assert user.name == "Updated"

    @pytest.mark.slow
    def test_complex_query(self, multiple_users):
        """Test complex database query."""
        # results = self.db.query(User).filter(...).all()
        # assert len(results) > 0
        pass
