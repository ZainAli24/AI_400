"""
Database testing conftest.py template.
Includes fixtures for database setup, transactions, and test data.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Assuming you have models defined somewhere
# from myapp.models import Base, User


@pytest.fixture(scope="session")
def database_engine():
    """
    Create a test database engine (in-memory SQLite).
    Created once per test session.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    # Base.metadata.create_all(engine)

    yield engine

    # Cleanup
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(database_engine):
    """
    Create a new database session for each test.
    Automatically rolls back after each test.
    """
    connection = database_engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    # Rollback transaction and close
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def db(db_session):
    """Alias for db_session for shorter fixture names."""
    return db_session


# Factory fixtures for creating test data

@pytest.fixture
def user_factory(db_session):
    """Factory for creating test users."""
    created_users = []

    def _create_user(username, email, **kwargs):
        # Example user creation (adjust to your User model)
        user = {
            "id": len(created_users) + 1,
            "username": username,
            "email": email,
            **kwargs
        }
        created_users.append(user)
        # db_session.add(user)
        # db_session.commit()
        return user

    yield _create_user

    # Cleanup is automatic due to transaction rollback


@pytest.fixture
def sample_user(user_factory):
    """Create a single sample user."""
    return user_factory("testuser", "test@example.com")


@pytest.fixture
def multiple_users(user_factory):
    """Create multiple test users."""
    return [
        user_factory("alice", "alice@example.com"),
        user_factory("bob", "bob@example.com"),
        user_factory("charlie", "charlie@example.com"),
    ]


# Database state management

@pytest.fixture(autouse=True)
def reset_database(db_session):
    """Automatically reset database state before each test."""
    # This runs automatically for every test
    yield
    # Cleanup happens here if needed
    db_session.rollback()


# Custom markers for database tests

def pytest_configure(config):
    """Register custom markers for database tests."""
    config.addinivalue_line(
        "markers",
        "database: marks tests that require database access"
    )
    config.addinivalue_line(
        "markers",
        "slow_query: marks tests with slow database queries"
    )


# Skip database tests if database is not available

@pytest.fixture(scope="session")
def database_available():
    """Check if database is available."""
    try:
        # Try to connect to database
        # For SQLite in-memory, always available
        return True
    except Exception:
        return False


def pytest_runtest_setup(item):
    """Skip database tests if database is not available."""
    if "database" in item.keywords:
        # Check if database is available
        # if not database_available:
        #     pytest.skip("Database not available")
        pass
