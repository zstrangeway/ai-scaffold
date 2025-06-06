"""
gRPC client for communicating with the User Service.

This module provides a client interface to interact with the user service
for user management operations like creation, retrieval, and authentication.
"""

import grpc
import os
from typing import Optional, Tuple
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import generated gRPC stubs from API contracts package
try:
    # Try to import from the API contracts package first
    import user_service_pb2 as user_pb2
    import user_service_pb2_grpc as user_grpc
except ImportError:
    # Fallback import paths for development
    import sys
    
    # Add the generated contracts to the path
    generated_contracts_path = '/app/packages/api-contracts/generated/py'
    if os.path.exists(generated_contracts_path):
        sys.path.insert(0, generated_contracts_path)
    else:
        # Development fallback
        sys.path.append('../../packages/api-contracts/generated/py')
    
    try:
        import user_service_pb2 as user_pb2
        import user_service_pb2_grpc as user_grpc
    except ImportError as e:
        logging.error(f"Failed to import user service protobuf: {e}")
        raise ImportError("Could not import user service protobuf definitions")

logger = logging.getLogger(__name__)

# Thread pool for running synchronous gRPC calls
executor = ThreadPoolExecutor(max_workers=10) # Consider making max_workers configurable

class UserServiceClient:
    """gRPC client for the User Service"""

    def __init__(self, user_service_url: str = None):
        """
        Initialize the User Service client
        
        Args:
            user_service_url: URL for the user service (e.g., 'localhost:50051')
        """
        self.user_service_url = user_service_url or os.getenv(
            "USER_SERVICE_URL", "localhost:50051"
        )
        self.channel = None
        self.stub = None

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def connect(self):
        """Establish connection to the user service"""
        try:
            self.channel = grpc.insecure_channel(self.user_service_url)
            self.stub = user_grpc.UserServiceStub(self.channel)
            logger.info(f"Connected to user service at {self.user_service_url}")
        except Exception as e:
            logger.error(f"Failed to connect to user service: {e}")
            raise

    def close(self):
        """Close the gRPC connection"""
        if self.channel:
            self.channel.close()
            logger.info("Closed user service connection")

    async def get_user_by_id(self, user_id: str) -> Optional[user_pb2.User]:
        """
        Get user by ID
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User object if found, None otherwise
        """
        try:
            if not self.stub:
                self.connect()

            request = user_pb2.GetUserByIdRequest(id=user_id)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(executor, self.stub.GetUserById, request)
            
            if response.user and response.user.id:
                return response.user
            return None
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error getting user by ID {user_id}: {e}")
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[user_pb2.User]:
        """
        Get user by email
        
        Args:
            email: User's email address
            
        Returns:
            User object if found, None otherwise
        """
        try:
            if not self.stub:
                self.connect()

            request = user_pb2.GetUserByEmailRequest(email=email)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(executor, self.stub.GetUserByEmail, request)
            
            if response.user and response.user.id:
                return response.user
            return None
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error getting user by email {email}: {e}")
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise

    async def create_user(self, name: str, email: str) -> Optional[user_pb2.User]:
        """
        Create a new user without password
        
        Args:
            name: User's full name
            email: User's email address
            
        Returns:
            Created user object if successful, None otherwise
        """
        try:
            if not self.stub:
                self.connect()

            request = user_pb2.CreateUserRequest(name=name, email=email)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(executor, self.stub.CreateUser, request)
            
            if response.user and response.user.id:
                return response.user
            return None
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error creating user {email}: {e}")
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise ValueError(f"User with email {email} already exists")
            raise
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            raise

    async def create_user_with_password(self, name: str, email: str, password: str) -> Optional[user_pb2.User]:
        """
        Create a new user with password for authentication
        
        Args:
            name: User's full name
            email: User's email address
            password: User's password
            
        Returns:
            Created user object if successful, None otherwise
        """
        try:
            if not self.stub:
                self.connect()

            request = user_pb2.CreateUserWithPasswordRequest(
                name=name, 
                email=email, 
                password=password
            )
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(executor, self.stub.CreateUserWithPassword, request)
            
            if response.user and response.user.id:
                return response.user
            return None
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error creating user with password {email}: {e}")
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise ValueError(f"User with email {email} already exists")
            raise
        except Exception as e:
            logger.error(f"Error creating user with password {email}: {e}")
            raise

    async def verify_user_password(self, email: str, password: str) -> Tuple[bool, Optional[user_pb2.User]]:
        """
        Verify user credentials for authentication
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (is_valid, user_object_if_valid)
        """
        try:
            if not self.stub:
                self.connect()

            request = user_pb2.VerifyUserPasswordRequest(email=email, password=password)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(executor, self.stub.VerifyUserPassword, request)
            
            if response.valid and response.user:
                return True, response.user
            return False, None
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error verifying password for {email}: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Error verifying password for {email}: {e}")
            return False, None

    async def update_user_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Update user's password
        
        Args:
            user_id: User's unique identifier
            current_password: User's current password
            new_password: User's new password
            
        Returns:
            True if password was updated successfully, False otherwise
        """
        try:
            if not self.stub:
                self.connect()

            request = user_pb2.UpdateUserPasswordRequest(
                id=user_id,
                current_password=current_password,
                new_password=new_password
            )
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(executor, self.stub.UpdateUserPassword, request)
            
            return response.success
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error updating password for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            return False

    async def update_user(
        self, user_id: str, name: str, email: str
    ) -> Optional[user_pb2.User]:
        """
        Update an existing user's basic information
        
        Args:
            user_id: User's unique identifier
            name: User's updated full name
            email: User's updated email address
            
        Returns:
            Updated user object if successful, None if user not found
        """
        try:
            if not self.stub:
                self.connect()

            request = user_pb2.UpdateUserRequest(id=user_id, name=name, email=email)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(executor, self.stub.UpdateUser, request)
            
            if response.user and response.user.id:
                return response.user
            return None
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error updating user {user_id}: {e}")
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise ValueError(f"User with email {email} already exists")
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            True if user was deleted successfully, False if user not found
        """
        try:
            if not self.stub:
                self.connect()

            request = user_pb2.DeleteUserRequest(id=user_id)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(executor, self.stub.DeleteUser, request)
            
            # Check if the response indicates successful deletion
            # The response should have an id field if successful
            return bool(response and hasattr(response, 'id') and response.id)
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error deleting user {user_id}: {e}")
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return False
            raise
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise

    async def list_users(self, page: int = 1, limit: int = 10) -> Tuple[list[user_pb2.User], int]:
        """
        List users with pagination
        
        Args:
            page: Page number (1-based)
            limit: Number of users per page
            
        Returns:
            Tuple of (users_list, total_count)
        """
        try:
            if not self.stub:
                self.connect()

            request = user_pb2.ListUsersRequest(page=page, limit=limit)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(executor, self.stub.ListUsers, request)
            
            return list(response.users), response.total
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error listing users: {e}")
            raise
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise


# Singleton client instance
_user_client = None


def get_user_client() -> UserServiceClient:
    """Get the singleton user service client"""
    global _user_client
    if _user_client is None:
        _user_client = UserServiceClient()
    return _user_client


async def close_user_client():
    """Close the user service client connection"""
    global _user_client
    if _user_client:
        _user_client.close()
        _user_client = None 
    executor.shutdown(wait=True) # Added to gracefully shutdown executor 