"""
Authentication routes for the Gateway Service.

Provides endpoints for user registration, login, and profile management.
Supports both HTTP-only cookies (browsers) and JWT tokens (mobile apps).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional

from ..auth import (
    Token, AuthUser, get_current_user, create_token_response,
    get_password_hash, verify_password, set_auth_cookie, clear_auth_cookie,
    authenticate_user
)
from ..user_client import get_user_client, UserServiceClient

router = APIRouter(prefix="/auth", tags=["authentication"])


class UserRegistration(BaseModel):
    """User registration request model"""
    name: str
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }


class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }


class UserProfile(BaseModel):
    """User profile response model"""
    id: str
    name: str
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
                "email": "john@example.com"
            }
        }


class UserProfileUpdate(BaseModel):
    """User profile update request model"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Smith",
                "email": "johnsmith@example.com"
            }
        }


class AuthSuccess(BaseModel):
    """Authentication success response for cookie-based auth"""
    message: str
    user: UserProfile

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Authentication successful",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "John Doe",
                    "email": "john@example.com"
                }
            }
        }


# Token-based authentication (for mobile apps, APIs)

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegistration,
    user_client: UserServiceClient = Depends(get_user_client)
):
    """
    Register a new user (Token-based for mobile apps)
    
    Creates a new user account with password and returns a JWT access token.
    Store this token and send it in the Authorization header for subsequent requests.
    
    Args:
        user_data: User registration information
        user_client: gRPC client for user service
        
    Returns:
        JWT access token for the newly created user
        
    Raises:
        HTTPException: If email is already registered or other validation errors
    """
    try:
        # Check if user already exists
        existing_user = await user_client.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already registered"
            )

        # Create user with password in user service
        created_user = await user_client.create_user_with_password(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password
        )
        
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )

        # Create and return access token
        return create_token_response(created_user.id, created_user.email)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticate user and return access token (Token-based for mobile apps)
    
    Uses OAuth2 password flow for user authentication.
    Store the returned token and send it in the Authorization header.
    
    Args:
        form_data: OAuth2 form with username (email) and password
        
    Returns:
        JWT access token for the authenticated user
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Authenticate user using the user service
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create and return access token
        return create_token_response(user.id, user.email)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )


@router.post("/login/json", response_model=Token)
async def login_json(
    login_data: UserLogin
):
    """
    Authenticate user with JSON payload (Token-based for mobile apps)
    
    Alternative to OAuth2 form data for applications that prefer JSON.
    
    Args:
        login_data: User login credentials
        
    Returns:
        JWT access token for the authenticated user
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Authenticate user using the user service
        user = await authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create and return access token
        return create_token_response(user.id, user.email)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )


# Cookie-based authentication (for browsers)

@router.post("/browser/register", response_model=AuthSuccess, status_code=status.HTTP_201_CREATED)
async def register_browser(
    response: Response,
    user_data: UserRegistration,
    user_client: UserServiceClient = Depends(get_user_client)
):
    """
    Register a new user (Cookie-based for browsers)
    
    Creates a new user account and sets an HTTP-only authentication cookie.
    The browser will automatically send this cookie with subsequent requests.
    
    Args:
        response: FastAPI response object
        user_data: User registration information
        user_client: gRPC client for user service
        
    Returns:
        Authentication success message with user profile
        
    Raises:
        HTTPException: If email is already registered or other validation errors
    """
    try:
        # Check if user already exists
        existing_user = await user_client.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already registered"
            )

        # Create user with password in user service
        created_user = await user_client.create_user_with_password(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password
        )
        
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )

        # Create token and set as HTTP-only cookie
        token_response = create_token_response(created_user.id, created_user.email)
        set_auth_cookie(response, token_response.access_token)

        return AuthSuccess(
            message="Registration successful",
            user=UserProfile(
                id=created_user.id,
                name=created_user.name,
                email=created_user.email
            )
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@router.post("/browser/login", response_model=AuthSuccess)
async def login_browser(
    response: Response,
    login_data: UserLogin
):
    """
    Authenticate user and set authentication cookie (Cookie-based for browsers)
    
    Authenticates the user and sets an HTTP-only cookie for subsequent requests.
    
    Args:
        response: FastAPI response object for setting cookies
        login_data: User login credentials
        
    Returns:
        Success message and user profile information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Authenticate user using the user service
        user = await authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create access token and set cookie
        token_response = create_token_response(user.id, user.email)
        set_auth_cookie(response, token_response.access_token)

        return AuthSuccess(
            message="Authentication successful",
            user=UserProfile(
                id=user.id,
                name=user.name,
                email=user.email
            )
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )


@router.post("/browser/logout")
async def logout_browser(response: Response):
    """
    Logout user (Browser-based)
    
    Clears the HTTP-only authentication cookie.
    
    Args:
        response: FastAPI response object
        
    Returns:
        Success message
    """
    clear_auth_cookie(response)
    return {"message": "Logout successful"}


# Shared endpoints (work with both authentication methods)

@router.get("/me", response_model=UserProfile)
async def get_profile(
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get current user profile
    
    Requires authentication via cookie or Authorization header.
    
    Args:
        current_user: Current authenticated user from dependency
        
    Returns:
        User profile information
    """
    return UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email
    )


@router.put("/me", response_model=UserProfile)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: AuthUser = Depends(get_current_user),
    user_client: UserServiceClient = Depends(get_user_client)
):
    """
    Update current user's profile
    
    Updates the profile information for the currently authenticated user.
    Works with both cookie and token authentication.
    
    Args:
        profile_update: Profile fields to update
        current_user: Currently authenticated user from JWT token/cookie
        user_client: gRPC client for user service
        
    Returns:
        Updated user profile information
        
    Raises:
        HTTPException: If update fails or user is not found
    """
    try:
        # Get current user data
        user = await user_client.get_user_by_id(current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        # Use current values if not provided in update
        updated_name = profile_update.name if profile_update.name is not None else user.name
        updated_email = profile_update.email if profile_update.email is not None else user.email

        # Update user via user service
        updated_user = await user_client.update_user(
            user_id=current_user.id,
            name=updated_name,
            email=updated_email
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )

        return UserProfile(
            id=updated_user.id,
            name=updated_user.name,
            email=updated_user.email
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user profile"
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    current_user: AuthUser = Depends(get_current_user),
    user_client: UserServiceClient = Depends(get_user_client)
):
    """
    Delete current user's account
    
    Permanently deletes the currently authenticated user's account.
    Works with both cookie and token authentication.
    
    Args:
        current_user: Currently authenticated user from JWT token/cookie
        user_client: gRPC client for user service
        
    Raises:
        HTTPException: If deletion fails or user is not found
    """
    try:
        # Delete user via user service
        deleted = await user_client.delete_user(current_user.id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found"
            )

        # Return 204 No Content for successful deletion

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user account"
        ) 