"""
User management routes for the Gateway Service.

Provides administrative endpoints for user management operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from ..auth import AuthUser, get_current_user
from ..user_client import get_user_client, UserServiceClient

router = APIRouter(prefix="/users", tags=["user management"])


class UserResponse(BaseModel):
    """User response model"""
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


class UserUpdateRequest(BaseModel):
    """User update request model"""
    name: str
    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com"
            }
        }


class UsersListResponse(BaseModel):
    """Users list response model"""
    users: List[UserResponse]
    total: int
    page: int
    limit: int

    class Config:
        json_schema_extra = {
            "example": {
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "John Doe",
                        "email": "john@example.com"
                    }
                ],
                "total": 1,
                "page": 1,
                "limit": 10
            }
        }


@router.get("/", response_model=UsersListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(10, ge=1, le=100, description="Number of users per page"),
    current_user: AuthUser = Depends(get_current_user),
    user_client: UserServiceClient = Depends(get_user_client)
):
    """
    List all users with pagination
    
    Returns a paginated list of all users in the system.
    Requires authentication.
    
    Args:
        page: Page number (1-based)
        limit: Number of users per page (max 100)
        current_user: Currently authenticated user
        user_client: gRPC client for user service
        
    Returns:
        Paginated list of users with metadata
        
    Raises:
        HTTPException: If there's an error retrieving users
    """
    try:
        users, total = await user_client.list_users(page=page, limit=limit)
        
        user_responses = [
            UserResponse(id=user.id, name=user.name, email=user.email)
            for user in users
        ]
        
        return UsersListResponse(
            users=user_responses,
            total=total,
            page=page,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users list"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: AuthUser = Depends(get_current_user),
    user_client: UserServiceClient = Depends(get_user_client)
):
    """
    Get a specific user by ID
    
    Returns detailed information about a specific user.
    Requires authentication.
    
    Args:
        user_id: Unique identifier of the user to retrieve
        current_user: Currently authenticated user
        user_client: gRPC client for user service
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user is not found or other errors
    """
    try:
        user = await user_client.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: str,
    current_user: AuthUser = Depends(get_current_user),
    user_client: UserServiceClient = Depends(get_user_client)
):
    """
    Get a specific user by email address
    
    Returns detailed information about a user identified by email.
    Requires authentication.
    
    Args:
        email: Email address of the user to retrieve
        current_user: Currently authenticated user
        user_client: gRPC client for user service
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user is not found or other errors
    """
    try:
        user = await user_client.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email} not found"
            )

        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdateRequest,
    current_user: AuthUser = Depends(get_current_user),
    user_client: UserServiceClient = Depends(get_user_client)
):
    """
    Update a specific user's information (Administrative operation)
    
    Updates a user's basic information. This is an administrative operation.
    Users can update their own profile via PUT /auth/me instead.
    
    Args:
        user_id: Unique identifier of the user to update
        user_update: Updated user information
        current_user: Currently authenticated user
        user_client: gRPC client for user service
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user is not found or other validation errors
    """
    try:
        # Update user via user service
        updated_user = await user_client.update_user(
            user_id=user_id,
            name=user_update.name,
            email=user_update.email
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        return UserResponse(
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
            detail="Error updating user information"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: AuthUser = Depends(get_current_user),
    user_client: UserServiceClient = Depends(get_user_client)
):
    """
    Delete a specific user (Administrative operation)
    
    Permanently deletes a user account. This is an administrative operation.
    Users cannot delete their own account through this endpoint (use DELETE /auth/me instead).
    
    Args:
        user_id: Unique identifier of the user to delete
        current_user: Currently authenticated user (must be admin)
        user_client: gRPC client for user service
        
    Raises:
        HTTPException: If user is not found, trying to delete self, or other errors
    """
    try:
        # Prevent users from deleting their own account via this endpoint
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account via this endpoint. Use DELETE /auth/me instead"
            )

        # Delete user via user service
        deleted = await user_client.delete_user(user_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Return 204 No Content for successful deletion

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user account"
        ) 