"""
Tests for the create user endpoint in the users router.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import status

from app.main import app
from app.auth import AuthUser


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user"""
    return AuthUser(id="test-user-id", email="admin@test.com", name="Admin User")


@pytest.fixture
def valid_user_data():
    """Valid user creation data"""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com"
    }


class TestCreateUserEndpoint:
    """Test cases for the POST /users/ endpoint"""

    def test_create_user_success(self, client, mock_auth_user, valid_user_data):
        """Test successful user creation"""
        # Mock dependencies
        mock_client = AsyncMock()
        mock_client.get_user_by_email.return_value = None  # User doesn't exist
        
        # Mock created user
        created_user = MagicMock()
        created_user.id = "new-user-id"
        created_user.name = "John Doe"
        created_user.email = "john.doe@example.com"
        mock_client.create_user.return_value = created_user
        
        # Override dependencies
        app.dependency_overrides = {
            app.dependency_overrides.get.__class__: lambda: mock_auth_user
        }
        
        from app.routers.users import get_current_user, get_user_client
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_user_client] = lambda: mock_client
        
        try:
            # Make request
            response = client.post("/api/v1/users/", json=valid_user_data)
            
            # Assertions
            assert response.status_code == 201
            data = response.json()
            assert data["id"] == "new-user-id"
            assert data["name"] == "John Doe"
            assert data["email"] == "john.doe@example.com"
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_create_user_already_exists(self, client, mock_auth_user, valid_user_data):
        """Test user creation when email already exists"""
        # Mock dependencies
        mock_client = AsyncMock()
        
        # Mock existing user
        existing_user = MagicMock()
        existing_user.id = "existing-user-id"
        existing_user.email = "john.doe@example.com"
        mock_client.get_user_by_email.return_value = existing_user
        
        # Override dependencies
        from app.routers.users import get_current_user, get_user_client
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_user_client] = lambda: mock_client
        
        try:
            # Make request
            response = client.post("/api/v1/users/", json=valid_user_data)
            
            # Assertions
            assert response.status_code == 409
            data = response.json()
            assert "already exists" in data["detail"]
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_create_user_invalid_data(self, client, mock_auth_user):
        """Test create user with invalid data"""
        # Mock dependencies
        mock_client = AsyncMock()
        
        # Override dependencies
        from app.routers.users import get_current_user, get_user_client
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_user_client] = lambda: mock_client
        
        try:
            invalid_data = {
                "name": "",  # Empty name
                "email": "invalid-email"  # Invalid email format
            }
            
            response = client.post("/api/v1/users/", json=invalid_data)
            
            # Should fail validation
            assert response.status_code == 422
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_create_user_missing_fields(self, client, mock_auth_user):
        """Test create user with missing required fields"""
        # Mock dependencies
        mock_client = AsyncMock()
        
        # Override dependencies
        from app.routers.users import get_current_user, get_user_client
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_user_client] = lambda: mock_client
        
        try:
            incomplete_data = {
                "name": "John Doe"
                # Missing email field
            }
            
            response = client.post("/api/v1/users/", json=incomplete_data)
            
            # Should fail validation
            assert response.status_code == 422
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_create_user_requires_authentication(self, client, valid_user_data):
        """Test that create user endpoint requires authentication"""
        # Don't override authentication - should fail
        response = client.post("/api/v1/users/", json=valid_user_data)
        
        # Should require authentication
        assert response.status_code == 401 