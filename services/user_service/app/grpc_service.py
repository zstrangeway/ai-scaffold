import grpc
from typing import Optional
from sqlalchemy.orm import Session
import sys
import os

# Add the generated contracts to the path
generated_contracts_path = '/app/generated_contracts/py'
if os.path.exists(generated_contracts_path):
    sys.path.insert(0, generated_contracts_path)

# Import the generated gRPC stubs and messages (from API contracts package)
try:
    from user_service_pb2_grpc import UserServiceServicer
    import user_service_pb2 as pb2
except ImportError:
    # Fallback for development environment
    try:
        sys.path.append('../../packages/api-contracts/generated/py')
        from user_service_pb2_grpc import UserServiceServicer
        import user_service_pb2 as pb2
    except ImportError:
        # Last resort fallback
        sys.path.append('/Users/zacharystrangeway/code/ai-scaffold/packages/api-contracts/generated/py')
        from user_service_pb2_grpc import UserServiceServicer
        import user_service_pb2 as pb2

from .repository import UserRepository
from .database import get_test_db
from .models import User as UserModel


class UserService(UserServiceServicer):
    """gRPC User Service implementation"""

    def __init__(self, db_session_factory=None):
        """Initialize the service with an optional database session factory"""
        self.db_session_factory = db_session_factory or get_test_db

    def _get_db_session(self) -> Session:
        """Get a database session"""
        return self.db_session_factory()

    def _model_to_proto(self, user: UserModel) -> pb2.User:
        """Convert SQLAlchemy model to protobuf User"""
        return pb2.User(
            id=user.id,
            name=user.name,
            email=user.email
        )

    def GetUserById(self, request: pb2.GetUserByIdRequest, context) -> pb2.GetUserByIdResponse:
        """Get user by ID"""
        if not request.id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("User ID is required")
            return pb2.GetUserByIdResponse()

        try:
            db = self._get_db_session()
            repo = UserRepository(db)
            user = repo.get_by_id(request.id)
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return pb2.GetUserByIdResponse()

            return pb2.GetUserByIdResponse(user=self._model_to_proto(user))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return pb2.GetUserByIdResponse()
        finally:
            try:
                db.close()
            except:
                pass  # Ignore cleanup errors

    def GetUserByEmail(self, request: pb2.GetUserByEmailRequest, context) -> pb2.GetUserByEmailResponse:
        """Get user by email"""
        if not request.email:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Email is required")
            return pb2.GetUserByEmailResponse()

        try:
            db = self._get_db_session()
            repo = UserRepository(db)
            user = repo.get_by_email(request.email)
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with email {request.email} not found")
                return pb2.GetUserByEmailResponse()

            return pb2.GetUserByEmailResponse(user=self._model_to_proto(user))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return pb2.GetUserByEmailResponse()
        finally:
            try:
                db.close()
            except:
                pass

    def CreateUser(self, request: pb2.CreateUserRequest, context) -> pb2.CreateUserResponse:
        """Create a new user"""
        if not request.name or not request.email:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Name and email are required")
            return pb2.CreateUserResponse()

        try:
            db = self._get_db_session()
            repo = UserRepository(db)
            user = repo.create(request.name, request.email)
            return pb2.CreateUserResponse(user=self._model_to_proto(user))
        except ValueError as e:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(str(e))
            return pb2.CreateUserResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return pb2.CreateUserResponse()
        finally:
            try:
                db.close()
            except:
                pass

    def UpdateUser(self, request: pb2.UpdateUserRequest, context) -> pb2.UpdateUserResponse:
        """Update an existing user"""
        if not request.id or not request.name or not request.email:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("ID, name and email are required")
            return pb2.UpdateUserResponse()

        try:
            db = self._get_db_session()
            repo = UserRepository(db)
            user = repo.update(request.id, request.name, request.email)
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return pb2.UpdateUserResponse()

            return pb2.UpdateUserResponse(user=self._model_to_proto(user))
        except ValueError as e:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(str(e))
            return pb2.UpdateUserResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return pb2.UpdateUserResponse()
        finally:
            try:
                db.close()
            except:
                pass

    def DeleteUser(self, request: pb2.DeleteUserRequest, context) -> pb2.DeleteUserResponse:
        """Delete a user"""
        if not request.id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("User ID is required")
            return pb2.DeleteUserResponse()

        try:
            db = self._get_db_session()
            repo = UserRepository(db)
            success = repo.delete(request.id)
            
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return pb2.DeleteUserResponse()

            return pb2.DeleteUserResponse(id=request.id)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return pb2.DeleteUserResponse()
        finally:
            try:
                db.close()
            except:
                pass

    def ListUsers(self, request: pb2.ListUsersRequest, context) -> pb2.ListUsersResponse:
        """List users with pagination"""
        page = max(1, request.page) if request.page > 0 else 1
        limit = max(1, min(100, request.limit)) if request.limit > 0 else 10

        try:
            db = self._get_db_session()
            repo = UserRepository(db)
            users, total = repo.list_users(page, limit)
            
            proto_users = [self._model_to_proto(user) for user in users]
            
            return pb2.ListUsersResponse(
                users=proto_users,
                total=total,
                page=page,
                limit=limit
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return pb2.ListUsersResponse()
        finally:
            try:
                db.close()
            except:
                pass 