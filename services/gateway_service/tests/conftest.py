"""
Shared test configuration and fixtures for Gateway Service tests.
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_user_client():
    """Mock UserServiceClient for testing"""
    mock_client = Mock()
    mock_client.get_user_by_email.return_value = None
    mock_client.get_user_by_id.return_value = None
    mock_client.create_user.return_value = None
    mock_client.update_user.return_value = None
    mock_client.delete_user.return_value = False
    mock_client.list_users.return_value = ([], 0)
    return mock_client


@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "id": "test-user-id-123",
        "name": "John Doe",
        "email": "john@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def valid_jwt_token():
    """Valid JWT token for testing"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQtMTIzIiwiZW1haWwiOiJqb2huQGV4YW1wbGUuY29tIiwiZXhwIjo5OTk5OTk5OTk5fQ.test-signature"


@pytest.fixture
def auth_headers(valid_jwt_token):
    """Authorization headers for testing"""
    return {"Authorization": f"Bearer {valid_jwt_token}"} 