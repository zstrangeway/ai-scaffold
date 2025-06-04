"""
Authentication utilities for the Gateway Service.

Provides JWT token management, password hashing, and authentication dependencies.
Supports both HTTP-only cookies (for browsers) and Authorization headers (for mobile apps).
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import get_settings
from .user_client import get_user_client


# Get settings
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme (optional for mobile apps)
security = HTTPBearer(auto_error=False)

# Cookie settings
COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = settings.JWT_EXPIRE_MINUTES * 60  # Convert to seconds


class Token(BaseModel):
    """JWT Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None
    email: Optional[str] = None


class AuthUser(BaseModel):
    """Authenticated user model"""
    id: str
    email: str
    name: str


async def authenticate_user(email: str, password: str) -> Optional[AuthUser]:
    """
    Authenticate user with email and password using the user service
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        AuthUser if authentication successful, None otherwise
    """
    try:
        user_client = get_user_client()
        is_valid, user = await user_client.verify_user_password(email, password)
        
        if is_valid and user:
            return AuthUser(
                id=user.id,
                email=user.email,
                name=user.name
            )
        return None
        
    except Exception as e:
        # Log error but don't expose details to client
        import logging
        logging.error(f"Authentication error for {email}: {e}")
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash
    
    Note: This is now primarily used for local password verification.
    For user authentication, use authenticate_user() which delegates to the user service.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary of claims to include in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(user_id=user_id, email=email)
        return token_data
        
    except JWTError:
        raise credentials_exception


def get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Extract JWT token from request (either cookie or Authorization header)
    
    Priority order:
    1. Authorization header (for mobile apps, APIs)
    2. HTTP-only cookie (for browsers)
    
    Args:
        request: FastAPI request object
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        JWT token string if found, None otherwise
    """
    # First, try Authorization header (mobile apps, APIs)
    if credentials and credentials.credentials:
        return credentials.credentials
    
    # Second, try HTTP-only cookie (browsers)
    cookie_token = request.cookies.get(COOKIE_NAME)
    if cookie_token:
        return cookie_token
    
    return None


async def get_current_user_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenData:
    """
    Dependency to get current user from JWT token (cookie or header)
    
    Args:
        request: FastAPI request object
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = get_token_from_request(request, credentials)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return verify_token(token)


async def get_current_user(
    token_data: TokenData = Depends(get_current_user_token)
) -> AuthUser:
    """
    Dependency to get current authenticated user with fresh data from user service
    
    Args:
        token_data: Token data from JWT
        
    Returns:
        AuthUser with current user details from user service
        
    Raises:
        HTTPException: If user cannot be found or token is invalid
    """
    if not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    try:
        # Fetch current user details from user service
        user_client = get_user_client()
        user = await user_client.get_user_by_id(token_data.user_id)
        
        if not user:
            # User no longer exists or token is stale
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        return AuthUser(
            id=user.id,
            email=user.email,
            name=user.name
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error but return generic error to client
        import logging
        logging.error(f"Error fetching user {token_data.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


def create_token_response(user_id: str, email: str) -> Token:
    """
    Create a token response for successful authentication
    
    Args:
        user_id: User's unique identifier
        email: User's email address
        
    Returns:
        Token response with access token and metadata
    """
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id, "email": email},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60  # Convert to seconds
    )


def set_auth_cookie(response: Response, access_token: str) -> None:
    """
    Set HTTP-only authentication cookie
    
    Args:
        response: FastAPI response object
        access_token: JWT token to store in cookie
    """
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,  # Prevents JavaScript access (XSS protection)
        secure=settings.is_production,  # HTTPS only in production
        samesite="lax",  # CSRF protection while allowing navigation
        path="/",  # Available for all paths
    )


def clear_auth_cookie(response: Response) -> None:
    """
    Clear authentication cookie (for logout)
    
    Args:
        response: FastAPI response object
    """
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
    ) 