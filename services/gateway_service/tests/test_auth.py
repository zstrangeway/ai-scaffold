"""
Unit tests for auth.py
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.auth import (
    Token, TokenData, AuthUser,
    verify_password, get_password_hash,
    create_access_token, verify_token,
    get_token_from_request, get_current_user_token,
    get_current_user, create_token_response,
    set_auth_cookie, clear_auth_cookie,
    COOKIE_NAME, COOKIE_MAX_AGE
)


class TestPasswordUtilities:
    """Unit tests for password hashing utilities"""

    def test_get_password_hash_returns_string(self):
        """Test that get_password_hash returns a string"""
        password = "test_password"
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password

    def test_get_password_hash_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes"""
        hash1 = get_password_hash("password1")
        hash2 = get_password_hash("password2")
        
        assert hash1 != hash2

    def test_get_password_hash_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Due to salting, same password should produce different hashes
        assert hash1 != hash2

    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password"""
        password = "test_password"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password"""
        password = "test_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_strings(self):
        """Test verify_password with empty strings"""
        # Empty hash strings cause passlib to raise UnknownHashError
        with pytest.raises(Exception):  # passlib.exc.UnknownHashError
            verify_password("", "")
        
        with pytest.raises(Exception):  # passlib.exc.UnknownHashError
            verify_password("password", "")
            
        with pytest.raises(Exception):  # passlib.exc.UnknownHashError
            verify_password("", "invalid_hash_format")


class TestTokenModels:
    """Unit tests for token-related Pydantic models"""

    def test_token_model_creation(self):
        """Test Token model creation"""
        token = Token(
            access_token="test_token",
            token_type="bearer",
            expires_in=1800
        )
        
        assert token.access_token == "test_token"
        assert token.token_type == "bearer"
        assert token.expires_in == 1800

    def test_token_model_default_token_type(self):
        """Test Token model with default token_type"""
        token = Token(access_token="test_token", expires_in=1800)
        
        assert token.token_type == "bearer"

    def test_token_data_model_creation(self):
        """Test TokenData model creation"""
        token_data = TokenData(
            user_id="user123",
            email="test@example.com"
        )
        
        assert token_data.user_id == "user123"
        assert token_data.email == "test@example.com"

    def test_token_data_model_optional_fields(self):
        """Test TokenData model with optional fields"""
        token_data = TokenData()
        
        assert token_data.user_id is None
        assert token_data.email is None

    def test_auth_user_model_creation(self):
        """Test AuthUser model creation"""
        auth_user = AuthUser(
            id="user123",
            email="test@example.com",
            name="Test User"
        )
        
        assert auth_user.id == "user123"
        assert auth_user.email == "test@example.com"
        assert auth_user.name == "Test User"


class TestJWTTokenFunctions:
    """Unit tests for JWT token creation and verification"""

    @patch('app.auth.settings')
    def test_create_access_token_default_expiration(self, mock_settings):
        """Test create_access_token with default expiration"""
        mock_settings.JWT_SECRET_KEY = "test_secret"
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_settings.JWT_EXPIRE_MINUTES = 30
        
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify the token
        decoded = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"
        assert "exp" in decoded

    @patch('app.auth.settings')
    def test_create_access_token_custom_expiration(self, mock_settings):
        """Test create_access_token with custom expiration"""
        mock_settings.JWT_SECRET_KEY = "test_secret"
        mock_settings.JWT_ALGORITHM = "HS256"
        
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)
        
        decoded = jwt.decode(token, "test_secret", algorithms=["HS256"])
        
        # Check expiration is approximately 60 minutes from now
        exp_timestamp = decoded["exp"]
        now = datetime.now(timezone.utc)
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        time_diff = exp_datetime - now
        
        # Should be approximately 60 minutes (allow 1 minute tolerance)
        assert 59 <= time_diff.total_seconds() / 60 <= 61

    @patch('app.auth.get_settings')
    def test_verify_token_valid_token(self, mock_get_settings):
        """Test verify_token with valid token"""
        mock_settings = Mock()
        mock_settings.JWT_SECRET_KEY = "test_secret"
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_get_settings.return_value = mock_settings
        
        # Create a valid token
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        
        # Verify the token
        token_data = verify_token(token)
        
        assert isinstance(token_data, TokenData)
        assert token_data.user_id == "user123"
        assert token_data.email == "test@example.com"

    @patch('app.auth.get_settings')
    def test_verify_token_invalid_token(self, mock_get_settings):
        """Test verify_token with invalid token"""
        mock_settings = Mock()
        mock_settings.JWT_SECRET_KEY = "test_secret"
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_get_settings.return_value = mock_settings
        
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)

    @patch('app.auth.get_settings')
    def test_verify_token_expired_token(self, mock_get_settings):
        """Test verify_token with expired token"""
        mock_settings = Mock()
        mock_settings.JWT_SECRET_KEY = "test_secret"
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_get_settings.return_value = mock_settings
        
        # Create an expired token
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        data = {
            "sub": "user123",
            "email": "test@example.com",
            "exp": past_time
        }
        expired_token = jwt.encode(data, "test_secret", algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(expired_token)
        
        assert exc_info.value.status_code == 401

    @patch('app.auth.get_settings')
    def test_verify_token_missing_subject(self, mock_get_settings):
        """Test verify_token with token missing subject"""
        mock_settings = Mock()
        mock_settings.JWT_SECRET_KEY = "test_secret"
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_get_settings.return_value = mock_settings
        
        # Create token without 'sub' field
        data = {"email": "test@example.com"}
        token = jwt.encode(data, "test_secret", algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401


class TestTokenFromRequest:
    """Unit tests for get_token_from_request function"""

    def test_get_token_from_authorization_header(self):
        """Test getting token from Authorization header"""
        mock_request = Mock(spec=Request)
        mock_request.cookies.get.return_value = None
        
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "header_token"
        
        token = get_token_from_request(mock_request, mock_credentials)
        
        assert token == "header_token"

    def test_get_token_from_cookie(self):
        """Test getting token from cookie when no header present"""
        mock_request = Mock(spec=Request)
        mock_request.cookies.get.return_value = "cookie_token"
        
        token = get_token_from_request(mock_request, None)
        
        assert token == "cookie_token"
        mock_request.cookies.get.assert_called_once_with(COOKIE_NAME)

    def test_get_token_header_takes_precedence(self):
        """Test that Authorization header takes precedence over cookie"""
        mock_request = Mock(spec=Request)
        mock_request.cookies.get.return_value = "cookie_token"
        
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "header_token"
        
        token = get_token_from_request(mock_request, mock_credentials)
        
        assert token == "header_token"

    def test_get_token_no_token_present(self):
        """Test when no token is present in header or cookie"""
        mock_request = Mock(spec=Request)
        mock_request.cookies.get.return_value = None
        
        token = get_token_from_request(mock_request, None)
        
        assert token is None

    def test_get_token_empty_credentials(self):
        """Test with empty credentials object"""
        mock_request = Mock(spec=Request)
        mock_request.cookies.get.return_value = "cookie_token"
        
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = ""
        
        token = get_token_from_request(mock_request, mock_credentials)
        
        # Should fall back to cookie when credentials is empty
        assert token == "cookie_token"


class TestCurrentUserDependencies:
    """Unit tests for current user dependency functions"""

    @patch('app.auth.get_token_from_request')
    @patch('app.auth.verify_token')
    async def test_get_current_user_token_success(self, mock_verify_token, mock_get_token):
        """Test get_current_user_token with valid token"""
        mock_request = Mock(spec=Request)
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        
        mock_get_token.return_value = "valid_token"
        mock_token_data = TokenData(user_id="user123", email="test@example.com")
        mock_verify_token.return_value = mock_token_data
        
        result = await get_current_user_token(mock_request, mock_credentials)
        
        assert result == mock_token_data
        mock_get_token.assert_called_once_with(mock_request, mock_credentials)
        mock_verify_token.assert_called_once_with("valid_token")

    @patch('app.auth.get_token_from_request')
    async def test_get_current_user_token_no_token(self, mock_get_token):
        """Test get_current_user_token when no token present"""
        mock_request = Mock(spec=Request)
        mock_credentials = None
        
        mock_get_token.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_token(mock_request, mock_credentials)
        
        assert exc_info.value.status_code == 401
        assert "Not authenticated" in str(exc_info.value.detail)

    @patch('app.auth.get_current_user_token')
    async def test_get_current_user_success(self, mock_get_token):
        """Test get_current_user with valid token data"""
        mock_token_data = TokenData(user_id="user123", email="test@example.com")
        mock_get_token.return_value = mock_token_data
        
        result = await get_current_user(mock_token_data)
        
        assert isinstance(result, AuthUser)
        assert result.id == "user123"
        assert result.email == "test@example.com"
        assert result.name == "User"  # Default placeholder

    @patch('app.auth.get_current_user_token')
    async def test_get_current_user_no_user_id(self, mock_get_token):
        """Test get_current_user when token has no user_id"""
        mock_token_data = TokenData(user_id=None, email="test@example.com")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_token_data)
        
        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in str(exc_info.value.detail)

    @patch('app.auth.get_current_user_token')
    async def test_get_current_user_empty_user_id(self, mock_get_token):
        """Test get_current_user when token has empty user_id"""
        mock_token_data = TokenData(user_id="", email="test@example.com")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_token_data)
        
        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in str(exc_info.value.detail)


class TestTokenResponse:
    """Unit tests for create_token_response function"""

    @patch('app.auth.create_access_token')
    @patch('app.auth.get_settings')
    def test_create_token_response_success(self, mock_get_settings, mock_create_token):
        """Test create_token_response creates proper Token object"""
        mock_settings = Mock()
        mock_settings.JWT_EXPIRE_MINUTES = 30
        mock_get_settings.return_value = mock_settings
        
        mock_create_token.return_value = "generated_token"
        
        result = create_token_response("user123", "test@example.com")
        
        assert isinstance(result, Token)
        assert result.access_token == "generated_token"
        assert result.token_type == "bearer"
        assert result.expires_in == 1800  # 30 minutes * 60 seconds

    @patch('app.auth.settings')
    def test_create_token_response_calls_create_access_token(self, mock_settings):
        """Test that create_token_response calls create_access_token with correct data"""
        mock_settings.JWT_EXPIRE_MINUTES = 30  # Use 30 to match the actual default
        
        with patch('app.auth.create_access_token') as mock_create_token:
            mock_create_token.return_value = "token"
            
            create_token_response("user123", "test@example.com")
            
            # Verify create_access_token was called with correct data
            mock_create_token.assert_called_once()
            call_args = mock_create_token.call_args
            
            # Check the data argument
            data = call_args[1]["data"]
            assert data["sub"] == "user123"
            assert data["email"] == "test@example.com"
            
            # Check the expires_delta argument
            expires_delta = call_args[1]["expires_delta"]
            assert expires_delta == timedelta(minutes=30)


class TestCookieFunctions:
    """Unit tests for cookie-related functions"""

    @patch('app.auth.settings')
    def test_set_auth_cookie_production(self, mock_settings):
        """Test set_auth_cookie in production mode"""
        mock_settings.is_production = True
        
        mock_response = Mock(spec=Response)
        token = "test_token"
        
        set_auth_cookie(mock_response, token)
        
        mock_response.set_cookie.assert_called_once_with(
            key=COOKIE_NAME,
            value="test_token",
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            secure=True,  # Should be True in production
            samesite="lax",
            path="/"
        )

    @patch('app.auth.settings')
    def test_set_auth_cookie_development(self, mock_settings):
        """Test set_auth_cookie in development mode"""
        mock_settings.is_production = False
        
        mock_response = Mock(spec=Response)
        token = "test_token"
        
        set_auth_cookie(mock_response, token)
        
        mock_response.set_cookie.assert_called_once_with(
            key=COOKIE_NAME,
            value="test_token",
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            secure=False,  # Should be False in development
            samesite="lax",
            path="/"
        )

    @patch('app.auth.settings')
    def test_clear_auth_cookie_production(self, mock_settings):
        """Test clear_auth_cookie in production mode"""
        mock_settings.is_production = True
        
        mock_response = Mock(spec=Response)
        
        clear_auth_cookie(mock_response)
        
        mock_response.delete_cookie.assert_called_once_with(
            key=COOKIE_NAME,
            path="/",
            httponly=True,
            secure=True,
            samesite="lax"
        )

    @patch('app.auth.settings')
    def test_clear_auth_cookie_development(self, mock_settings):
        """Test clear_auth_cookie in development mode"""
        mock_settings.is_production = False
        
        mock_response = Mock(spec=Response)
        
        clear_auth_cookie(mock_response)
        
        mock_response.delete_cookie.assert_called_once_with(
            key=COOKIE_NAME,
            path="/",
            httponly=True,
            secure=False,
            samesite="lax"
        ) 