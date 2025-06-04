"""
Focused unit tests for router functionality with proper mocking
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app


class TestAuthRouterFocused:
    """Focused tests for auth router with proper mocking"""

    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)

    @patch('app.routers.auth.get_user_client')
    @patch('app.routers.auth.get_password_hash')
    def test_register_endpoint_basic_logic(self, mock_hash, mock_get_client, client):
        """Test register endpoint basic logic flow"""
        # Mock dependencies
        mock_client = AsyncMock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        
        mock_client.create_user.return_value = mock_user
        mock_get_client.return_value = mock_client
        mock_hash.return_value = "hashed_password"
        
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify the password was hashed
        mock_hash.assert_called_once_with("password123")

    @patch('app.routers.auth.get_user_client')
    def test_register_handles_user_exists_error(self, mock_get_client, client):
        """Test register handles user already exists error"""
        mock_client = AsyncMock()
        mock_client.create_user.side_effect = ValueError("User already exists")
        mock_get_client.return_value = mock_client
        
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"]

    @patch('app.routers.auth.get_user_client')
    @patch('app.routers.auth.verify_password')
    def test_login_endpoint_success_flow(self, mock_verify, mock_get_client, client):
        """Test login endpoint success flow"""
        # Mock user client
        mock_client = AsyncMock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.password = "hashed_password"
        mock_client.get_user_by_email.return_value = mock_user
        mock_get_client.return_value = mock_client
        
        # Mock password verification
        mock_verify.return_value = True
        
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login/json", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify password was checked
        mock_verify.assert_called_once_with("password123", "hashed_password")

    @patch('app.routers.auth.get_user_client')
    def test_login_user_not_found(self, mock_get_client, client):
        """Test login when user not found"""
        mock_client = AsyncMock()
        mock_client.get_user_by_email.return_value = None
        mock_get_client.return_value = mock_client
        
        login_data = {
            "email": "notfound@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login/json", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid email or password" in data["detail"]

    @patch('app.routers.auth.get_user_client')
    @patch('app.routers.auth.verify_password')
    def test_login_wrong_password(self, mock_verify, mock_get_client, client):
        """Test login with wrong password"""
        mock_client = AsyncMock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.password = "hashed_password"
        mock_client.get_user_by_email.return_value = mock_user
        mock_get_client.return_value = mock_client
        
        # Mock password verification to fail
        mock_verify.return_value = False
        
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login/json", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid email or password" in data["detail"]

    def test_me_endpoint_with_valid_token(self, client):
        """Test /me endpoint with valid token"""
        # Create a valid token using proper mocking
        with patch('app.auth.settings') as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test_secret"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_EXPIRE_MINUTES = 30
            
            from app.auth import create_access_token
            token = create_access_token({"sub": "user123", "email": "test@example.com"})
            
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/v1/auth/me", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "user123"
            assert data["email"] == "test@example.com"
            assert data["name"] == "User"  # Default placeholder

    def test_browser_logout_endpoint(self, client):
        """Test browser logout endpoint"""
        response = client.post("/api/v1/auth/browser/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logout successful"
        
        # Check that set-cookie header is present (clears cookie)
        set_cookie_headers = [h for h in response.headers.get_list('set-cookie') if 'access_token' in h]
        assert len(set_cookie_headers) > 0


class TestUsersRouterFocused:
    """Focused tests for users router with proper mocking"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Create valid auth headers"""
        with patch('app.auth.settings') as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test_secret"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_EXPIRE_MINUTES = 30
            
            from app.auth import create_access_token
            token = create_access_token({"sub": "user123", "email": "test@example.com"})
            
            return {"Authorization": f"Bearer {token}"}

    @patch('app.routers.users.get_user_client')
    def test_list_users_endpoint(self, mock_get_client, client, auth_headers):
        """Test list users endpoint logic"""
        mock_client = AsyncMock()
        mock_users = [
            Mock(id="user1", email="user1@example.com", name="User One"),
            Mock(id="user2", email="user2@example.com", name="User Two")
        ]
        mock_client.list_users.return_value = (mock_users, 2)
        mock_get_client.return_value = mock_client
        
        response = client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["users"]) == 2
        assert data["users"][0]["email"] == "user1@example.com"
        assert data["users"][1]["email"] == "user2@example.com"
        assert data["page"] == 1
        assert data["limit"] == 10

    @patch('app.routers.users.get_user_client')
    def test_get_user_by_id_endpoint(self, mock_get_client, client, auth_headers):
        """Test get user by ID endpoint logic"""
        mock_client = AsyncMock()
        mock_user = Mock(id="user123", email="test@example.com", name="Test User")
        mock_client.get_user_by_id.return_value = mock_user
        mock_get_client.return_value = mock_client
        
        response = client.get("/api/v1/users/user123", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user123"
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    @patch('app.routers.users.get_user_client')
    def test_get_user_not_found(self, mock_get_client, client, auth_headers):
        """Test get user when not found"""
        mock_client = AsyncMock()
        mock_client.get_user_by_id.return_value = None
        mock_get_client.return_value = mock_client
        
        response = client.get("/api/v1/users/nonexistent", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "User with ID nonexistent not found" in data["detail"]

    @patch('app.routers.users.get_user_client')
    def test_get_user_by_email_endpoint(self, mock_get_client, client, auth_headers):
        """Test get user by email endpoint logic"""
        mock_client = AsyncMock()
        mock_user = Mock(id="user123", email="test@example.com", name="Test User")
        mock_client.get_user_by_email.return_value = mock_user
        mock_get_client.return_value = mock_client
        
        response = client.get("/api/v1/users/email/test@example.com", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user123"
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    @patch('app.routers.users.get_user_client')
    def test_delete_user_endpoint(self, mock_get_client, client, auth_headers):
        """Test delete user endpoint logic"""
        mock_client = AsyncMock()
        mock_client.delete_user.return_value = True
        mock_get_client.return_value = mock_client
        
        response = client.delete("/api/v1/users/user456", headers=auth_headers)  # Different ID to avoid self-delete
        
        assert response.status_code == 204
        # 204 No Content should have empty body
        assert response.content == b''

    @patch('app.routers.users.get_user_client')
    def test_delete_user_not_found(self, mock_get_client, client, auth_headers):
        """Test delete user when not found"""
        mock_client = AsyncMock()
        mock_client.delete_user.return_value = False
        mock_get_client.return_value = mock_client
        
        response = client.delete("/api/v1/users/nonexistent", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "User with ID nonexistent not found" in data["detail"]

    @patch('app.routers.users.get_user_client')
    def test_delete_own_account_forbidden(self, mock_get_client, client, auth_headers):
        """Test that users cannot delete their own account via this endpoint"""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Try to delete the same user ID that's in the token (user123)
        response = client.delete("/api/v1/users/user123", headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "Cannot delete your own account" in data["detail"]

    def test_endpoints_require_auth(self, client):
        """Test that endpoints require authentication"""
        # Test various endpoints without auth
        assert client.get("/api/v1/users/").status_code == 401
        assert client.get("/api/v1/users/123").status_code == 401
        assert client.get("/api/v1/users/email/test@example.com").status_code == 401
        assert client.delete("/api/v1/users/123").status_code == 401

    @patch('app.routers.users.get_user_client')
    def test_list_users_with_pagination(self, mock_get_client, client, auth_headers):
        """Test list users with pagination parameters"""
        mock_client = AsyncMock()
        mock_users = [Mock(id="user1", email="user1@example.com", name="User One")]
        mock_client.list_users.return_value = (mock_users, 5)
        mock_get_client.return_value = mock_client
        
        response = client.get("/api/v1/users/?page=2&limit=5", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["limit"] == 5
        assert data["total"] == 5
        
        # Verify the client was called with correct parameters
        mock_client.list_users.assert_called_once_with(page=2, limit=5)

    @patch('app.routers.users.get_user_client')
    def test_users_endpoint_exception_handling(self, mock_get_client, client, auth_headers):
        """Test exception handling in users endpoints"""
        mock_client = AsyncMock()
        mock_client.list_users.side_effect = Exception("Database error")
        mock_get_client.return_value = mock_client
        
        response = client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == 500
        data = response.json()
        assert "Error retrieving users list" in data["detail"]


class TestRouterValidation:
    """Test request validation in routers"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_auth_validation(self, client):
        """Test auth endpoint validation"""
        # Missing fields
        assert client.post("/api/v1/auth/register", json={}).status_code == 422
        assert client.post("/api/v1/auth/login/json", json={}).status_code == 422
        
        # Invalid email
        bad_register = {
            "name": "Test",
            "email": "invalid-email",
            "password": "password"
        }
        assert client.post("/api/v1/auth/register", json=bad_register).status_code == 422

    def test_users_validation_with_auth(self, client):
        """Test users endpoint validation with auth"""
        # Create auth headers
        with patch('app.auth.settings') as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test_secret"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_EXPIRE_MINUTES = 30
            
            from app.auth import create_access_token
            token = create_access_token({"sub": "user123", "email": "test@example.com"})
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test invalid pagination parameters
            assert client.get("/api/v1/users/?page=0", headers=headers).status_code == 422
            assert client.get("/api/v1/users/?limit=0", headers=headers).status_code == 422
            assert client.get("/api/v1/users/?limit=101", headers=headers).status_code == 422 