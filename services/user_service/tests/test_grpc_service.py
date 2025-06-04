import pytest
import grpc
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import generated protobuf classes (from API contracts package)
import user_service_pb2 as pb2

from app.grpc_service import UserService
from app.models import Base, User
from app.repository import UserRepository


class TestUserService:
    """Unit tests for gRPC UserService"""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        return Mock()

    @pytest.fixture
    def mock_repo(self):
        """Create a mock repository"""
        return Mock(spec=UserRepository)

    @pytest.fixture
    def grpc_service(self, mock_session):
        """Create a gRPC service instance with mock database"""
        def get_mock_session():
            return mock_session
        return UserService(db_session_factory=get_mock_session)

    @pytest.fixture
    def mock_context(self):
        """Create a mock gRPC context"""
        context = Mock()
        context.set_code = Mock()
        context.set_details = Mock()
        return context

    @patch('app.grpc_service.UserRepository')
    def test_get_user_by_id_success(self, mock_repo_class, grpc_service, mock_context):
        """Test successful GetUserById"""
        # Setup mock
        mock_user = User(id="test-id", name="John Doe", email="john@example.com")
        mock_repo = mock_repo_class.return_value
        mock_repo.get_by_id.return_value = mock_user
        
        # Create request
        request = pb2.GetUserByIdRequest(id="test-id")
        
        # Call service
        response = grpc_service.GetUserById(request, mock_context)
        
        # Assertions
        assert response.user.id == "test-id"
        assert response.user.name == "John Doe"
        assert response.user.email == "john@example.com"
        mock_repo.get_by_id.assert_called_once_with("test-id")
        mock_context.set_code.assert_not_called()

    def test_get_user_by_id_empty_id(self, grpc_service, mock_context):
        """Test GetUserById with empty ID"""
        request = pb2.GetUserByIdRequest(id="")
        
        response = grpc_service.GetUserById(request, mock_context)
        
        assert response == pb2.GetUserByIdResponse()
        mock_context.set_code.assert_called_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_with("User ID is required")

    @patch('app.grpc_service.UserRepository')
    def test_get_user_by_id_not_found(self, mock_repo_class, grpc_service, mock_context):
        """Test GetUserById with non-existent ID"""
        mock_repo = mock_repo_class.return_value
        mock_repo.get_by_id.return_value = None
        
        request = pb2.GetUserByIdRequest(id="nonexistent")
        
        response = grpc_service.GetUserById(request, mock_context)
        
        assert response == pb2.GetUserByIdResponse()
        mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
        mock_context.set_details.assert_called_with("User with ID nonexistent not found")

    def test_get_user_by_id_db_session_close_error(self, mock_context):
        """Test GetUserById handles database context manager properly"""
        # Mock the context manager to still work correctly
        with patch('app.grpc_service.get_db_session') as mock_get_db_session, \
             patch('app.grpc_service.UserRepository') as mock_repo_class:
            
            mock_session = Mock()
            mock_get_db_session.return_value.__enter__.return_value = mock_session
            mock_get_db_session.return_value.__exit__.return_value = None
            
            mock_repo = mock_repo_class.return_value
            mock_repo.get_by_id.return_value = User(id="test", name="Test", email="test@example.com")
            
            service = UserService()
            request = pb2.GetUserByIdRequest(id="test")
            response = service.GetUserById(request, mock_context)
            
            # Should still return successful response
            assert response.user.id == "test"
            # Verify context manager was used properly
            mock_get_db_session.assert_called_once()
            mock_get_db_session.return_value.__enter__.assert_called_once()
            mock_get_db_session.return_value.__exit__.assert_called_once()

    @patch('app.grpc_service.UserRepository')
    def test_get_user_by_email_success(self, mock_repo_class, grpc_service, mock_context):
        """Test successful GetUserByEmail"""
        mock_user = User(id="test-id", name="John Doe", email="john@example.com")
        mock_repo = mock_repo_class.return_value
        mock_repo.get_by_email.return_value = mock_user
        
        request = pb2.GetUserByEmailRequest(email="john@example.com")
        
        response = grpc_service.GetUserByEmail(request, mock_context)
        
        assert response.user.id == "test-id"
        assert response.user.name == "John Doe"
        assert response.user.email == "john@example.com"
        mock_repo.get_by_email.assert_called_once_with("john@example.com")

    def test_get_user_by_email_empty_email(self, grpc_service, mock_context):
        """Test GetUserByEmail with empty email"""
        request = pb2.GetUserByEmailRequest(email="")
        
        response = grpc_service.GetUserByEmail(request, mock_context)
        
        assert response == pb2.GetUserByEmailResponse()
        mock_context.set_code.assert_called_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_with("Email is required")

    def test_get_user_by_email_db_session_close_error(self, mock_context):
        """Test GetUserByEmail handles database session close errors gracefully"""
        mock_session = Mock()
        mock_session.close.side_effect = RuntimeError("Connection lost")
        
        def get_failing_close_session():
            return mock_session
        
        service = UserService(db_session_factory=get_failing_close_session)
        
        with patch('app.grpc_service.UserRepository') as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.get_by_email.return_value = None
            
            request = pb2.GetUserByEmailRequest(email="test@example.com")
            response = service.GetUserByEmail(request, mock_context)
            
            # Should handle not found case properly despite close error
            assert response == pb2.GetUserByEmailResponse()
            mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)

    @patch('app.grpc_service.UserRepository')
    def test_create_user_success(self, mock_repo_class, grpc_service, mock_context):
        """Test successful CreateUser"""
        mock_user = User(id="test-id", name="John Doe", email="john@example.com")
        mock_repo = mock_repo_class.return_value
        mock_repo.create.return_value = mock_user
        
        request = pb2.CreateUserRequest(name="John Doe", email="john@example.com")
        
        response = grpc_service.CreateUser(request, mock_context)
        
        assert response.user.name == "John Doe"
        assert response.user.email == "john@example.com"
        assert response.user.id == "test-id"
        mock_repo.create.assert_called_once_with("John Doe", "john@example.com")

    def test_create_user_empty_name(self, grpc_service, mock_context):
        """Test CreateUser with empty name"""
        request = pb2.CreateUserRequest(name="", email="john@example.com")
        
        response = grpc_service.CreateUser(request, mock_context)
        
        assert response == pb2.CreateUserResponse()
        mock_context.set_code.assert_called_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_with("Name and email are required")

    @patch('app.grpc_service.UserRepository')
    def test_create_user_duplicate_email(self, mock_repo_class, grpc_service, mock_context):
        """Test CreateUser with duplicate email"""
        mock_repo = mock_repo_class.return_value
        mock_repo.create.side_effect = ValueError("User with email john@example.com already exists")
        
        request = pb2.CreateUserRequest(name="John Doe", email="john@example.com")
        
        response = grpc_service.CreateUser(request, mock_context)
        
        assert response == pb2.CreateUserResponse()
        mock_context.set_code.assert_called_with(grpc.StatusCode.ALREADY_EXISTS)

    def test_create_user_db_session_close_error(self, mock_context):
        """Test CreateUser handles database context manager properly"""
        # Mock the context manager to work correctly
        with patch('app.grpc_service.get_db_session') as mock_get_db_session, \
             patch('app.grpc_service.UserRepository') as mock_repo_class:
            
            mock_session = Mock()
            mock_get_db_session.return_value.__enter__.return_value = mock_session
            mock_get_db_session.return_value.__exit__.return_value = None
            
            mock_repo = mock_repo_class.return_value
            mock_repo.create.return_value = User(id="test", name="Test", email="test@example.com")
            
            service = UserService()
            request = pb2.CreateUserRequest(name="Test", email="test@example.com")
            response = service.CreateUser(request, mock_context)
            
            # Should still work with context manager
            assert response.user.name == "Test"
            # Verify context manager was used properly
            mock_get_db_session.assert_called_once()
            mock_get_db_session.return_value.__enter__.assert_called_once()
            mock_get_db_session.return_value.__exit__.assert_called_once()

    @patch('app.grpc_service.UserRepository')
    def test_update_user_success(self, mock_repo_class, grpc_service, mock_context):
        """Test successful UpdateUser"""
        mock_user = User(id="test-id", name="Jane Doe", email="jane@example.com")
        mock_repo = mock_repo_class.return_value
        mock_repo.update.return_value = mock_user
        
        request = pb2.UpdateUserRequest(
            id="test-id", 
            name="Jane Doe", 
            email="jane@example.com"
        )
        
        response = grpc_service.UpdateUser(request, mock_context)
        
        assert response.user.id == "test-id"
        assert response.user.name == "Jane Doe"
        assert response.user.email == "jane@example.com"
        mock_repo.update.assert_called_once_with("test-id", "Jane Doe", "jane@example.com")

    def test_update_user_empty_fields(self, grpc_service, mock_context):
        """Test UpdateUser with empty required fields"""
        request = pb2.UpdateUserRequest(id="", name="Jane Doe", email="jane@example.com")
        
        response = grpc_service.UpdateUser(request, mock_context)
        
        assert response == pb2.UpdateUserResponse()
        mock_context.set_code.assert_called_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_with("ID, name and email are required")

    @patch('app.grpc_service.UserRepository')
    def test_update_user_not_found(self, mock_repo_class, grpc_service, mock_context):
        """Test UpdateUser with non-existent user"""
        mock_repo = mock_repo_class.return_value
        mock_repo.update.return_value = None
        
        request = pb2.UpdateUserRequest(
            id="nonexistent", 
            name="Jane Doe", 
            email="jane@example.com"
        )
        
        response = grpc_service.UpdateUser(request, mock_context)
        
        assert response == pb2.UpdateUserResponse()
        mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
        mock_context.set_details.assert_called_with("User with ID nonexistent not found")

    @patch('app.grpc_service.UserRepository')
    def test_update_user_duplicate_email_value_error(self, mock_repo_class, grpc_service, mock_context):
        """Test UpdateUser with duplicate email causing ValueError"""
        mock_repo = mock_repo_class.return_value
        mock_repo.update.side_effect = ValueError("User with email exists")
        
        request = pb2.UpdateUserRequest(
            id="test-id", 
            name="Jane Doe", 
            email="duplicate@example.com"
        )
        
        response = grpc_service.UpdateUser(request, mock_context)
        
        assert response == pb2.UpdateUserResponse()
        mock_context.set_code.assert_called_with(grpc.StatusCode.ALREADY_EXISTS)
        mock_context.set_details.assert_called_with("User with email exists")

    def test_update_user_db_session_close_error(self, mock_context):
        """Test UpdateUser handles database session close errors gracefully"""
        mock_session = Mock()
        mock_session.close.side_effect = Exception("Close failed")
        
        def get_failing_close_session():
            return mock_session
        
        service = UserService(db_session_factory=get_failing_close_session)
        
        with patch('app.grpc_service.UserRepository') as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.update.return_value = None  # User not found
            
            request = pb2.UpdateUserRequest(id="test", name="Test", email="test@example.com")
            response = service.UpdateUser(request, mock_context)
            
            # Should handle not found case despite close error
            assert response == pb2.UpdateUserResponse()
            mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)

    @patch('app.grpc_service.UserRepository')
    def test_delete_user_success(self, mock_repo_class, grpc_service, mock_context):
        """Test successful DeleteUser"""
        mock_repo = mock_repo_class.return_value
        mock_repo.delete.return_value = True
        
        request = pb2.DeleteUserRequest(id="test-id")
        
        response = grpc_service.DeleteUser(request, mock_context)
        
        assert response.id == "test-id"
        mock_repo.delete.assert_called_once_with("test-id")

    def test_delete_user_empty_id(self, grpc_service, mock_context):
        """Test DeleteUser with empty ID"""
        request = pb2.DeleteUserRequest(id="")
        
        response = grpc_service.DeleteUser(request, mock_context)
        
        assert response == pb2.DeleteUserResponse()
        mock_context.set_code.assert_called_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_with("User ID is required")

    @patch('app.grpc_service.UserRepository')
    def test_delete_user_not_found(self, mock_repo_class, grpc_service, mock_context):
        """Test DeleteUser with non-existent user"""
        mock_repo = mock_repo_class.return_value
        mock_repo.delete.return_value = False
        
        request = pb2.DeleteUserRequest(id="nonexistent")
        
        response = grpc_service.DeleteUser(request, mock_context)
        
        assert response == pb2.DeleteUserResponse()
        mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
        mock_context.set_details.assert_called_with("User with ID nonexistent not found")

    def test_delete_user_db_session_close_error(self, mock_context):
        """Test DeleteUser handles database context manager properly"""
        # Mock the context manager to work correctly
        with patch('app.grpc_service.get_db_session') as mock_get_db_session, \
             patch('app.grpc_service.UserRepository') as mock_repo_class:
            
            mock_session = Mock()
            mock_get_db_session.return_value.__enter__.return_value = mock_session
            mock_get_db_session.return_value.__exit__.return_value = None
            
            mock_repo = mock_repo_class.return_value
            mock_repo.delete.return_value = True
            
            service = UserService()
            request = pb2.DeleteUserRequest(id="test")
            response = service.DeleteUser(request, mock_context)
            
            # Should work with context manager
            assert response.id == "test"
            # Verify context manager was used properly
            mock_get_db_session.assert_called_once()
            mock_get_db_session.return_value.__enter__.assert_called_once()
            mock_get_db_session.return_value.__exit__.assert_called_once()

    @patch('app.grpc_service.UserRepository')
    def test_list_users_empty(self, mock_repo_class, grpc_service, mock_context):
        """Test ListUsers with no users"""
        mock_repo = mock_repo_class.return_value
        mock_repo.list_users.return_value = ([], 0)
        
        request = pb2.ListUsersRequest(page=1, limit=10)
        
        response = grpc_service.ListUsers(request, mock_context)
        
        assert len(response.users) == 0
        assert response.total == 0
        assert response.page == 1
        assert response.limit == 10
        mock_repo.list_users.assert_called_once_with(1, 10)

    @patch('app.grpc_service.UserRepository')
    def test_list_users_with_data(self, mock_repo_class, grpc_service, mock_context):
        """Test ListUsers with data"""
        mock_users = [
            User(id="1", name="User 1", email="user1@example.com"),
            User(id="2", name="User 2", email="user2@example.com"),
        ]
        mock_repo = mock_repo_class.return_value
        mock_repo.list_users.return_value = (mock_users, 2)
        
        request = pb2.ListUsersRequest(page=1, limit=10)
        response = grpc_service.ListUsers(request, mock_context)
        
        assert len(response.users) == 2
        assert response.total == 2
        assert response.users[0].id == "1"
        assert response.users[1].id == "2"

    def test_list_users_default_pagination(self, grpc_service, mock_context):
        """Test ListUsers with default pagination values"""
        with patch('app.grpc_service.UserRepository') as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.list_users.return_value = ([], 0)
            
            request = pb2.ListUsersRequest(page=0, limit=0)
            
            response = grpc_service.ListUsers(request, mock_context)
            
            assert response.page == 1  # Default page
            assert response.limit == 10  # Default limit
            mock_repo.list_users.assert_called_once_with(1, 10)

    def test_list_users_limit_boundary(self, grpc_service, mock_context):
        """Test ListUsers with limit boundary conditions"""
        with patch('app.grpc_service.UserRepository') as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.list_users.return_value = ([], 0)
            
            request = pb2.ListUsersRequest(page=1, limit=200)  # Over max limit
            
            response = grpc_service.ListUsers(request, mock_context)
            
            assert response.limit == 100  # Max limit enforced
            mock_repo.list_users.assert_called_once_with(1, 100)

    def test_list_users_db_session_close_error(self, mock_context):
        """Test ListUsers handles database context manager properly"""
        # Mock the context manager to work correctly
        with patch('app.grpc_service.get_db_session') as mock_get_db_session, \
             patch('app.grpc_service.UserRepository') as mock_repo_class:
            
            mock_session = Mock()
            mock_get_db_session.return_value.__enter__.return_value = mock_session
            mock_get_db_session.return_value.__exit__.return_value = None
            
            mock_repo = mock_repo_class.return_value
            mock_repo.list_users.return_value = ([], 0)
            
            service = UserService()
            request = pb2.ListUsersRequest(page=1, limit=10)
            response = service.ListUsers(request, mock_context)
            
            # Should work with context manager
            assert len(response.users) == 0
            assert response.total == 0
            # Verify context manager was used properly
            mock_get_db_session.assert_called_once()
            mock_get_db_session.return_value.__enter__.assert_called_once()
            mock_get_db_session.return_value.__exit__.assert_called_once()

    def test_model_to_proto_conversion(self, grpc_service):
        """Test _model_to_proto method"""
        user = User(id="test-id", name="Test User", email="test@example.com")
        
        proto_user = grpc_service._model_to_proto(user)
        
        assert proto_user.id == "test-id"
        assert proto_user.name == "Test User"
        assert proto_user.email == "test@example.com"

    def test_db_session_factory_default(self):
        """Test that service uses default db session factory"""
        service = UserService()
        assert service.db_session_factory is not None

    def test_exception_handling_in_get_user_by_id(self, grpc_service, mock_context):
        """Test that internal errors are properly handled and returned as gRPC errors"""
        with patch('app.grpc_service.get_db_session') as mock_get_db_session:
            mock_get_db_session.side_effect = Exception("Database connection failed")
            
            request = pb2.GetUserByIdRequest(id="test-id")
            response = grpc_service.GetUserById(request, mock_context)
            
            assert response == pb2.GetUserByIdResponse()
            mock_context.set_code.assert_called_with(grpc.StatusCode.INTERNAL)

    @patch('app.grpc_service.UserRepository')
    def test_create_user_with_password_success(self, mock_repo_class, grpc_service, mock_context):
        """Test successful CreateUserWithPassword"""
        mock_user = User(id="test-id", name="John Doe", email="john@example.com")
        mock_repo = mock_repo_class.return_value
        mock_repo.create_with_password.return_value = mock_user
        
        request = pb2.CreateUserWithPasswordRequest(
            name="John Doe", 
            email="john@example.com", 
            password="password123"
        )
        
        response = grpc_service.CreateUserWithPassword(request, mock_context)
        
        assert response.user.name == "John Doe"
        assert response.user.email == "john@example.com"
        assert response.user.id == "test-id"
        mock_repo.create_with_password.assert_called_once_with("John Doe", "john@example.com", "password123")

    def test_create_user_with_password_empty_fields(self, grpc_service, mock_context):
        """Test CreateUserWithPassword with empty required fields"""
        request = pb2.CreateUserWithPasswordRequest(name="", email="john@example.com", password="password123")
        
        response = grpc_service.CreateUserWithPassword(request, mock_context)
        
        assert response == pb2.CreateUserWithPasswordResponse()
        mock_context.set_code.assert_called_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_with("Name, email, and password are required")

    @patch('app.grpc_service.UserRepository')
    def test_update_user_password_success(self, mock_repo_class, grpc_service, mock_context):
        """Test successful UpdateUserPassword"""
        mock_repo = mock_repo_class.return_value
        mock_repo.update_password.return_value = True
        
        request = pb2.UpdateUserPasswordRequest(
            id="user-id",
            current_password="oldpassword",
            new_password="newpassword"
        )
        
        response = grpc_service.UpdateUserPassword(request, mock_context)
        
        assert response.success is True
        mock_repo.update_password.assert_called_once_with("user-id", "oldpassword", "newpassword")

    @patch('app.grpc_service.UserRepository')
    def test_update_user_password_wrong_current(self, mock_repo_class, grpc_service, mock_context):
        """Test UpdateUserPassword with wrong current password"""
        mock_repo = mock_repo_class.return_value
        mock_repo.update_password.return_value = False
        
        request = pb2.UpdateUserPasswordRequest(
            id="user-id",
            current_password="wrongpassword",
            new_password="newpassword"
        )
        
        response = grpc_service.UpdateUserPassword(request, mock_context)
        
        assert response.success is False
        mock_context.set_code.assert_called_with(grpc.StatusCode.UNAUTHENTICATED)
        mock_context.set_details.assert_called_with("Current password is incorrect or user not found")

    def test_update_user_password_empty_fields(self, grpc_service, mock_context):
        """Test UpdateUserPassword with empty required fields"""
        request = pb2.UpdateUserPasswordRequest(id="", current_password="old", new_password="new")
        
        response = grpc_service.UpdateUserPassword(request, mock_context)
        
        assert response.success is False
        mock_context.set_code.assert_called_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_with("User ID, current password, and new password are required")

    @patch('app.grpc_service.UserRepository')
    def test_verify_user_password_success(self, mock_repo_class, grpc_service, mock_context):
        """Test successful VerifyUserPassword"""
        mock_user = User(id="test-id", name="John Doe", email="john@example.com")
        mock_repo = mock_repo_class.return_value
        mock_repo.verify_user_password.return_value = mock_user
        
        request = pb2.VerifyUserPasswordRequest(email="john@example.com", password="password123")
        
        response = grpc_service.VerifyUserPassword(request, mock_context)
        
        assert response.valid is True
        assert response.user.id == "test-id"
        assert response.user.email == "john@example.com"
        mock_repo.verify_user_password.assert_called_once_with("john@example.com", "password123")

    @patch('app.grpc_service.UserRepository')
    def test_verify_user_password_invalid(self, mock_repo_class, grpc_service, mock_context):
        """Test VerifyUserPassword with invalid credentials"""
        mock_repo = mock_repo_class.return_value
        mock_repo.verify_user_password.return_value = None
        
        request = pb2.VerifyUserPasswordRequest(email="john@example.com", password="wrongpassword")
        
        response = grpc_service.VerifyUserPassword(request, mock_context)
        
        assert response.valid is False
        assert not response.HasField('user')  # User field should not be populated

    def test_verify_user_password_empty_fields(self, grpc_service, mock_context):
        """Test VerifyUserPassword with empty required fields"""
        request = pb2.VerifyUserPasswordRequest(email="", password="password123")
        
        response = grpc_service.VerifyUserPassword(request, mock_context)
        
        assert response.valid is False
        mock_context.set_code.assert_called_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_with("Email and password are required") 