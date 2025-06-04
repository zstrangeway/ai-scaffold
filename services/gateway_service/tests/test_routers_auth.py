"""
Unit tests for auth router endpoints
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app


class TestAuthRouterEndpoints:
    """Unit tests for auth router endpoints"""

    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)

    @patch('app.routers.auth.get_user_client')
    def test_register_success(self, mock_get_user_client, client):
        """Test successful user registration"""
        # Mock user client
        mock_client = AsyncMock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_client.create_user.return_value = mock_user
        mock_get_user_client.return_value = mock_client
        
        # Test data
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
        assert "expires_in" in data

    @patch('app.routers.auth.get_user_client')
    def test_register_user_already_exists(self, mock_get_user_client, client):
        """Test registration when user already exists"""
        # Mock user client to raise ValueError for existing user
        mock_client = AsyncMock()
        mock_client.create_user.side_effect = ValueError("User with email test@example.com already exists")
        mock_get_user_client.return_value = mock_client
        
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
    def test_login_success(self, mock_get_user_client, client):
        """Test successful login"""
        # Mock user client
        mock_client = AsyncMock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.password = "$2b$12$encrypted_password_hash"  # Mock bcrypt hash
        mock_client.get_user_by_email.return_value = mock_user
        mock_get_user_client.return_value = mock_client
        
        # Mock password verification
        with patch('app.routers.auth.verify_password', return_value=True):
            login_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            response = client.post("/api/v1/auth/login/json", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

    @patch('app.routers.auth.get_user_client')
    def test_login_user_not_found(self, mock_get_user_client, client):
        """Test login with non-existent user"""
        mock_client = AsyncMock()
        mock_client.get_user_by_email.return_value = None
        mock_get_user_client.return_value = mock_client
        
        login_data = {
            "email": "notfound@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login/json", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid credentials" in data["detail"]

    @patch('app.routers.auth.get_user_client')
    def test_login_wrong_password(self, mock_get_user_client, client):
        """Test login with wrong password"""
        mock_client = AsyncMock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.password = "$2b$12$encrypted_password_hash"
        mock_client.get_user_by_email.return_value = mock_user
        mock_get_user_client.return_value = mock_client
        
        # Mock password verification to fail
        with patch('app.routers.auth.verify_password', return_value=False):
            login_data = {
                "email": "test@example.com",
                "password": "wrongpassword"
            }
            
            response = client.post("/api/v1/auth/login/json", json=login_data)
            
            assert response.status_code == 401
            data = response.json()
            assert "Invalid credentials" in data["detail"]

    def test_me_endpoint_with_token(self, client):
        """Test /me endpoint with valid token"""
        # Create a valid token
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

    def test_me_endpoint_without_token(self, client):
        """Test /me endpoint without token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]

    @patch('app.routers.auth.get_user_client')
    def test_browser_register_success(self, mock_get_user_client, client):
        """Test successful browser registration with cookie"""
        mock_client = AsyncMock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_client.create_user.return_value = mock_user
        mock_get_user_client.return_value = mock_client
        
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/browser/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Registration successful"
        assert data["user"]["email"] == "test@example.com"
        
        # Check that auth cookie is set
        cookies = response.cookies
        assert "access_token" in cookies

    @patch('app.routers.auth.get_user_client')
    def test_browser_login_success(self, mock_get_user_client, client):
        """Test successful browser login with cookie"""
        mock_client = AsyncMock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.password = "$2b$12$encrypted_password_hash"
        mock_client.get_user_by_email.return_value = mock_user
        mock_get_user_client.return_value = mock_client
        
        with patch('app.routers.auth.verify_password', return_value=True):
            login_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            response = client.post("/api/v1/auth/browser/login", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Login successful"
            assert data["user"]["email"] == "test@example.com"
            
            # Check that auth cookie is set
            cookies = response.cookies
            assert "access_token" in cookies

    def test_browser_logout(self, client):
        """Test browser logout clears cookie"""
        response = client.post("/api/v1/auth/browser/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logout successful"
        
        # Check that auth cookie is cleared
        cookies = response.cookies
        assert "access_token" in cookies
        # The cookie should be set to expire immediately for logout
        assert cookies["access_token"] == ""


class TestAuthRouterValidation:
    """Test input validation for auth endpoints"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        # Missing name
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 422

        # Missing email
        response = client.post("/api/v1/auth/register", json={
            "name": "Test User",
            "password": "password123"
        })
        assert response.status_code == 422

        # Missing password
        response = client.post("/api/v1/auth/register", json={
            "name": "Test User", 
            "email": "test@example.com"
        })
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post("/api/v1/auth/register", json={
            "name": "Test User",
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422

    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        # Missing email
        response = client.post("/api/v1/auth/login/json", json={
            "password": "password123"
        })
        assert response.status_code == 422

        # Missing password
        response = client.post("/api/v1/auth/login/json", json={
            "email": "test@example.com"
        })
        assert response.status_code == 422

    def test_empty_request_body(self, client):
        """Test endpoints with empty request body"""
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422
        
        response = client.post("/api/v1/auth/login/json", json={})
        assert response.status_code == 422 