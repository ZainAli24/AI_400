"""
Pytest configuration and fixtures for FastAPI testing.

This file contains shared fixtures that can be used across all test files.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="module")
def client():
    """
    Create a FastAPI test client.

    Scope: module - created once per test module, shared across all tests
    This is efficient for read-only API tests.

    Usage:
        def test_endpoint(client):
            response = client.get("/tasks")
            assert response.status_code == 200
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def client_function():
    """
    Create a new FastAPI test client for each test function.

    Scope: function - created fresh for each test
    Use this when tests modify state or need complete isolation.

    Usage:
        def test_endpoint(client_function):
            response = client_function.get("/tasks")
            assert response.status_code == 200
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_task():
    """
    Provide sample task data for testing.

    Usage:
        def test_task_structure(sample_task):
            assert "id" in sample_task
            assert "tasks" in sample_task
    """
    return {"id": 1, "tasks": "Go to the grocery store"}


@pytest.fixture
def sample_tasks_list():
    """
    Provide sample list of tasks for testing.

    Usage:
        def test_tasks_list(sample_tasks_list):
            assert len(sample_tasks_list) == 3
    """
    return [
        {"id": 1, "tasks": "Go to the grocery store"},
        {"id": 2, "tasks": "Walk the dog"},
        {"id": 3, "tasks": "Read a book"},
    ]
