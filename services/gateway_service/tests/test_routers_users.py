"""
Unit tests for users router endpoints
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app


class TestUsersRouterEndpoints:
    """Unit tests for users router endpoints"""

    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        # Create a valid token
        with patch('app.auth.settings') as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test_secret"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_EXPIRE_MINUTES = 30
            
            from app.auth import create_access_token
            token = create_access_token({"sub": "user123", "email": "test@example.com"})
            
            return {"Authorization": f"Bearer {token}"}

    @patch('app.routers.users.get_user_client')
    def test_get_users_success(self, mock_get_user_client, client, auth_headers):
        """Test successful get users"""
        mock_client = AsyncMock()
        mock_users = [
            Mock(id="user1", email="user1@example.com", name="User One"),
            Mock(id="user2", email="user2@example.com", name="User Two")
        ]
        mock_client.list_users.return_value = mock_users
        mock_get_user_client.return_value = mock_client
        
        response = client.get("/api/v1/users", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["email"] == "user1@example.com"
        assert data[1]["email"] == "user2@example.com"

    def test_get_users_no_auth(self, client):
        """Test get users without authentication"""
        response = client.get("/api/v1/users")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]

    @patch('app.routers.users.get_user_client')
    def test_get_user_by_id_success(self, mock_get_user_client, client, auth_headers):
        """Test successful get user by ID"""
        mock_client = AsyncMock()
        mock_user = Mock(id="user123", email="test@example.com", name="Test User")
        mock_client.get_user_by_id.return_value = mock_user
        mock_get_user_client.return_value = mock_client
        
        response = client.get("/api/v1/users/user123", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user123"
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    @patch('app.routers.users.get_user_client')
    def test_get_user_by_id_not_found(self, mock_get_user_client, client, auth_headers):
        """Test get user by ID when user not found"""
        mock_client = AsyncMock()
        mock_client.get_user_by_id.return_value = None
        mock_get_user_client.return_value = mock_client
        
        response = client.get("/api/v1/users/nonexistent", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "User not found" in data["detail"]

    @patch('app.routers.users.get_user_client')
    def test_update_user_success(self, mock_get_user_client, client, auth_headers):
        """Test successful user update"""
        mock_client = AsyncMock()
        mock_user = Mock(id="user123", email="test@example.com", name="Updated User")
        mock_client.update_user.return_value = mock_user
        mock_get_user_client.return_value = mock_client
        
        update_data = {
            "name": "Updated User",
            "email": "test@example.com"
        }
        
        response = client.put("/api/v1/users/user123", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user123"
        assert data["name"] == "Updated User"

    @patch('app.routers.users.get_user_client')
    def test_update_user_not_found(self, mock_get_user_client, client, auth_headers):
        """Test update user when user not found"""
        mock_client = AsyncMock()
        mock_client.update_user.return_value = None
        mock_get_user_client.return_value = mock_client
        
        update_data = {
            "name": "Updated User",
            "email": "test@example.com"
        }
        
        response = client.put("/api/v1/users/nonexistent", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "User not found" in data["detail"]

    @patch('app.routers.users.get_user_client')
    def test_delete_user_success(self, mock_get_user_client, client, auth_headers):
        """Test successful user deletion"""
        mock_client = AsyncMock()
        mock_client.delete_user.return_value = True
        mock_get_user_client.return_value = mock_client
        
        response = client.delete("/api/v1/users/user123", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User deleted successfully"

    @patch('app.routers.users.get_user_client')
    def test_delete_user_not_found(self, mock_get_user_client, client, auth_headers):
        """Test delete user when user not found"""
        mock_client = AsyncMock()
        mock_client.delete_user.return_value = False
        mock_get_user_client.return_value = mock_client
        
        response = client.delete("/api/v1/users/nonexistent", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "User not found" in data["detail"]

    def test_update_user_no_auth(self, client):
        """Test update user without authentication"""
        update_data = {"name": "Updated User"}
        response = client.put("/api/v1/users/user123", json=update_data)
        
        assert response.status_code == 401

    def test_delete_user_no_auth(self, client):
        """Test delete user without authentication"""
        response = client.delete("/api/v1/users/user123")
        
        assert response.status_code == 401


class TestUsersRouterValidation:
    """Test input validation for users endpoints"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        with patch('app.auth.settings') as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test_secret"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_EXPIRE_MINUTES = 30
            
            from app.auth import create_access_token
            token = create_access_token({"sub": "user123", "email": "test@example.com"})
            
            return {"Authorization": f"Bearer {token}"}

    def test_update_user_invalid_email(self, client, auth_headers):
        """Test update user with invalid email format"""
        update_data = {
            "name": "Test User",
            "email": "invalid-email"
        }
        
        response = client.put("/api/v1/users/user123", json=update_data, headers=auth_headers)
        assert response.status_code == 422

    def test_update_user_empty_fields(self, client, auth_headers):
        """Test update user with empty required fields"""
        update_data = {
            "name": "",
            "email": "test@example.com"
        }
        
        response = client.put("/api/v1/users/user123", json=update_data, headers=auth_headers)
        assert response.status_code == 422

    def test_update_user_missing_fields(self, client, auth_headers):
        """Test update user with missing fields"""
        # Both name and email are required for updates
        response = client.put("/api/v1/users/user123", json={}, headers=auth_headers)
        assert response.status_code == 422 