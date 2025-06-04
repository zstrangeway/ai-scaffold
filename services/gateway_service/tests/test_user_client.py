"""
Unit tests for user_client.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import grpc
from grpc import StatusCode

from app.user_client import UserServiceClient, get_user_client


class TestUserServiceClient:
    """Unit tests for UserServiceClient"""

    @pytest.fixture
    def mock_channel(self):
        """Mock gRPC channel"""
        channel = Mock()
        return channel

    @pytest.fixture
    def mock_stub(self):
        """Mock UserService stub"""
        stub = Mock()
        return stub

    @pytest.fixture
    def client(self, mock_channel, mock_stub):
        """UserServiceClient instance with mocked dependencies"""
        with patch('app.user_client.grpc.insecure_channel', return_value=mock_channel), \
             patch('app.user_client.user_grpc.UserServiceStub', return_value=mock_stub):
            client = UserServiceClient("test:50051")
            client.channel = mock_channel
            client.stub = mock_stub
            return client

    def test_init_creates_client(self):
        """Test that UserServiceClient initializes correctly"""
        client = UserServiceClient("test:50051")
        assert client.user_service_url == "test:50051"
        assert client.channel is None
        assert client.stub is None

    def test_init_with_default_url(self):
        """Test that UserServiceClient uses default URL when none provided"""
        with patch.dict('os.environ', {'USER_SERVICE_URL': 'env:50051'}):
            client = UserServiceClient()
            assert client.user_service_url == "env:50051"

    def test_init_fallback_url(self):
        """Test that UserServiceClient uses fallback URL"""
        with patch.dict('os.environ', {}, clear=True):
            client = UserServiceClient()
            assert client.user_service_url == "localhost:50051"

    def test_connect_creates_channel_and_stub(self, client):
        """Test that connect method creates channel and stub"""
        with patch('app.user_client.grpc.insecure_channel') as mock_channel, \
             patch('app.user_client.user_grpc.UserServiceStub') as mock_stub:
            
            mock_channel_instance = Mock()
            mock_channel.return_value = mock_channel_instance
            mock_stub_instance = Mock()
            mock_stub.return_value = mock_stub_instance
            
            client.connect()
            
            mock_channel.assert_called_once_with("test:50051")
            mock_stub.assert_called_once_with(mock_channel_instance)
            assert client.channel == mock_channel_instance
            assert client.stub == mock_stub_instance

    def test_connect_logs_connection(self):
        """Test that connect logs connection"""
        with patch('app.user_client.grpc.insecure_channel'), \
             patch('app.user_client.user_grpc.UserServiceStub'), \
             patch('app.user_client.logger') as mock_logger:
            
            client = UserServiceClient("test:50051")
            client.connect()
            mock_logger.info.assert_called_once_with("Connected to user service at test:50051")

    def test_connect_handles_exceptions(self):
        """Test that connect handles exceptions properly"""
        with patch('app.user_client.grpc.insecure_channel', side_effect=Exception("Connection failed")), \
             patch('app.user_client.logger') as mock_logger:
            
            client = UserServiceClient("test:50051")
            
            with pytest.raises(Exception):
                client.connect()
            
            mock_logger.error.assert_called_once()
            assert "Failed to connect to user service" in mock_logger.error.call_args[0][0]

    def test_close_channel(self, client):
        """Test that close properly closes the channel"""
        client.close()
        
        client.channel.close.assert_called_once()

    def test_close_with_no_channel(self):
        """Test close when no channel exists"""
        client = UserServiceClient("test:50051")
        client.channel = None
        
        # Should not raise exception
        client.close()

    def test_close_logs(self, client):
        """Test that close logs the action"""
        with patch('app.user_client.logger') as mock_logger:
            client.close()
            mock_logger.info.assert_called_once_with("Closed user service connection")

    def test_context_manager(self):
        """Test that UserServiceClient works as context manager"""
        with patch('app.user_client.grpc.insecure_channel'), \
             patch('app.user_client.user_grpc.UserServiceStub'):
            
            with UserServiceClient("test:50051") as client:
                assert client is not None
                assert hasattr(client, 'channel')
                assert hasattr(client, 'stub')

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, client):
        """Test successful get_user_by_id call"""
        # Mock response
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.name = "John Doe"
        mock_user.email = "john@example.com"
        
        mock_response = Mock()
        mock_response.user = mock_user
        
        client.stub.GetUserById.return_value = mock_response
        
        result = await client.get_user_by_id("user123")
        
        # Verify the call was made correctly
        client.stub.GetUserById.assert_called_once()
        call_args = client.stub.GetUserById.call_args[0][0]
        assert call_args.id == "user123"
        
        # Verify the result
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, client):
        """Test get_user_by_id when user not found"""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=StatusCode.NOT_FOUND)
        mock_error.details = Mock(return_value="User not found")
        client.stub.GetUserById.side_effect = mock_error
        
        with patch('app.user_client.logger') as mock_logger:
            result = await client.get_user_by_id("notfound123")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_grpc_error(self, client):
        """Test get_user_by_id with gRPC error"""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=StatusCode.UNAVAILABLE)
        mock_error.details = Mock(return_value="Service unavailable")
        client.stub.GetUserById.side_effect = mock_error
        
        with patch('app.user_client.logger') as mock_logger:
            with pytest.raises(grpc.RpcError):
                await client.get_user_by_id("user123")

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, client):
        """Test successful get_user_by_email call"""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.name = "John Doe"
        mock_user.email = "john@example.com"
        
        mock_response = Mock()
        mock_response.user = mock_user
        
        client.stub.GetUserByEmail.return_value = mock_response
        
        result = await client.get_user_by_email("john@example.com")
        
        # Verify the call was made correctly
        client.stub.GetUserByEmail.assert_called_once()
        call_args = client.stub.GetUserByEmail.call_args[0][0]
        assert call_args.email == "john@example.com"
        
        # Verify the result
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, client):
        """Test get_user_by_email when user not found"""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=StatusCode.NOT_FOUND)
        mock_error.details = Mock(return_value="User not found")
        client.stub.GetUserByEmail.side_effect = mock_error
        
        result = await client.get_user_by_email("notfound@example.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_user_success(self, client):
        """Test successful create_user call"""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.name = "John Doe"
        mock_user.email = "john@example.com"
        
        mock_response = Mock()
        mock_response.user = mock_user
        
        client.stub.CreateUser.return_value = mock_response
        
        result = await client.create_user("John Doe", "john@example.com")
        
        # Verify the call was made correctly
        client.stub.CreateUser.assert_called_once()
        call_args = client.stub.CreateUser.call_args[0][0]
        assert call_args.name == "John Doe"
        assert call_args.email == "john@example.com"
        
        # Verify the result
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_create_user_already_exists(self, client):
        """Test create_user when user already exists"""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=StatusCode.ALREADY_EXISTS)
        mock_error.details = Mock(return_value="User already exists")
        client.stub.CreateUser.side_effect = mock_error
        
        with pytest.raises(ValueError) as exc_info:
            await client.create_user("John", "john@example.com")
        
        assert "already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_success(self, client):
        """Test successful update_user call"""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.name = "John Updated"
        mock_user.email = "john@example.com"
        
        mock_response = Mock()
        mock_response.user = mock_user
        
        client.stub.UpdateUser.return_value = mock_response
        
        result = await client.update_user("user123", "John Updated", "john@example.com")
        
        # Verify the call was made correctly
        client.stub.UpdateUser.assert_called_once()
        call_args = client.stub.UpdateUser.call_args[0][0]
        assert call_args.id == "user123"
        assert call_args.name == "John Updated"
        assert call_args.email == "john@example.com"
        
        # Verify the result
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client):
        """Test update_user when user not found"""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=StatusCode.NOT_FOUND)
        mock_error.details = Mock(return_value="User not found")
        client.stub.UpdateUser.side_effect = mock_error
        
        result = await client.update_user("notfound123", "Updated", "test@example.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_user_success(self, client):
        """Test successful delete_user call"""
        mock_response = Mock()
        mock_response.success = True
        
        client.stub.DeleteUser.return_value = mock_response
        
        result = await client.delete_user("user123")
        
        # Verify the call was made correctly
        client.stub.DeleteUser.assert_called_once()
        call_args = client.stub.DeleteUser.call_args[0][0]
        assert call_args.id == "user123"
        
        # Verify the result
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, client):
        """Test delete_user when user not found"""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=StatusCode.NOT_FOUND)
        mock_error.details = Mock(return_value="User not found")
        client.stub.DeleteUser.side_effect = mock_error
        
        result = await client.delete_user("notfound123")
        assert result is False

    @pytest.mark.asyncio
    async def test_list_users_success(self, client):
        """Test successful list_users call"""
        # Mock user objects
        mock_user1 = Mock()
        mock_user1.id = "user1"
        mock_user1.name = "User One"
        mock_user1.email = "user1@example.com"
        
        mock_user2 = Mock()
        mock_user2.id = "user2"
        mock_user2.name = "User Two"
        mock_user2.email = "user2@example.com"
        
        mock_response = Mock()
        mock_response.users = [mock_user1, mock_user2]
        mock_response.total = 2
        
        client.stub.ListUsers.return_value = mock_response
        
        users, total = await client.list_users(page=1, limit=10)
        
        # Verify the call was made correctly
        client.stub.ListUsers.assert_called_once()
        call_args = client.stub.ListUsers.call_args[0][0]
        assert call_args.page == 1
        assert call_args.limit == 10
        
        # Verify the result
        assert total == 2
        assert len(users) == 2
        assert users[0] == mock_user1
        assert users[1] == mock_user2

    @pytest.mark.asyncio
    async def test_get_user_by_id_general_exception(self, client):
        """Test get_user_by_id with general exception"""
        client.stub.GetUserById.side_effect = Exception("Database error")
        
        with patch('app.user_client.logger') as mock_logger:
            with pytest.raises(Exception):
                await client.get_user_by_id("user123")
            
            mock_logger.error.assert_called()
            assert "Error getting user by ID" in mock_logger.error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_get_user_by_email_general_exception(self, client):
        """Test get_user_by_email with general exception"""
        client.stub.GetUserByEmail.side_effect = Exception("Database error")
        
        with patch('app.user_client.logger') as mock_logger:
            with pytest.raises(Exception):
                await client.get_user_by_email("test@example.com")
            
            mock_logger.error.assert_called()
            assert "Error getting user by email" in mock_logger.error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_create_user_general_exception(self, client):
        """Test create_user with general exception"""
        client.stub.CreateUser.side_effect = Exception("Database error")
        
        with patch('app.user_client.logger') as mock_logger:
            with pytest.raises(Exception):
                await client.create_user("Test", "test@example.com")
            
            mock_logger.error.assert_called()
            assert "Error creating user" in mock_logger.error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_update_user_general_exception(self, client):
        """Test update_user with general exception"""
        client.stub.UpdateUser.side_effect = Exception("Database error")
        
        with patch('app.user_client.logger') as mock_logger:
            with pytest.raises(Exception):
                await client.update_user("user123", "Updated", "test@example.com")
            
            mock_logger.error.assert_called()
            assert "Error updating user" in mock_logger.error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_update_user_already_exists(self, client):
        """Test update_user when email already exists"""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=StatusCode.ALREADY_EXISTS)
        mock_error.details = Mock(return_value="Email already exists")
        client.stub.UpdateUser.side_effect = mock_error
        
        with pytest.raises(ValueError) as exc_info:
            await client.update_user("user123", "Updated", "existing@example.com")
        
        assert "already in use" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_user_general_exception(self, client):
        """Test delete_user with general exception"""
        client.stub.DeleteUser.side_effect = Exception("Database error")
        
        with patch('app.user_client.logger') as mock_logger:
            with pytest.raises(Exception):
                await client.delete_user("user123")
            
            mock_logger.error.assert_called()
            assert "Error deleting user" in mock_logger.error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_list_users_general_exception(self, client):
        """Test list_users with general exception"""
        client.stub.ListUsers.side_effect = Exception("Database error")
        
        with patch('app.user_client.logger') as mock_logger:
            with pytest.raises(Exception):
                await client.list_users()
            
            mock_logger.error.assert_called()
            assert "Error listing users" in mock_logger.error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_methods_auto_connect_when_no_stub(self):
        """Test that methods auto-connect when stub is None"""
        client = UserServiceClient("test:50051")
        client.stub = None
        
        with patch.object(client, 'connect') as mock_connect:
            mock_connect.side_effect = lambda: setattr(client, 'stub', Mock())
            
            # Test that get_user_by_id auto-connects
            client.stub.GetUserById.return_value = Mock(user=Mock(id="user123"))
            await client.get_user_by_id("user123")
            
            assert mock_connect.called


class TestGetUserClient:
    """Unit tests for get_user_client function"""

    def test_get_user_client_returns_client_instance(self):
        """Test that get_user_client returns UserServiceClient instance"""
        client = get_user_client()
        assert isinstance(client, UserServiceClient)

    def test_get_user_client_returns_same_instance(self):
        """Test that get_user_client returns the same global instance"""
        client1 = get_user_client()
        client2 = get_user_client()
        
        # Should return the same global instance
        assert client1 is client2

    def test_get_user_client_initializes_global_client(self):
        """Test that get_user_client initializes the global client"""
        # Clear the global client first
        import app.user_client
        app.user_client._user_client = None
        
        assert app.user_client._user_client is None
        
        client = get_user_client()
        
        assert app.user_client._user_client is not None
        assert app.user_client._user_client is client

    @pytest.mark.asyncio
    async def test_close_user_client_with_global_client(self):
        """Test close_user_client function with global client"""
        from app.user_client import close_user_client
        import app.user_client
        
        # Set up global client
        mock_client = Mock()
        app.user_client._user_client = mock_client
        
        await close_user_client()
        
        mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_user_client_with_no_global_client(self):
        """Test close_user_client function with no global client"""
        from app.user_client import close_user_client
        import app.user_client
        
        # Clear global client
        app.user_client._user_client = None
        
        # Should not raise exception
        await close_user_client()


class TestUserClientIntegration:
    """Integration tests for user client functionality"""

    def test_client_creation_with_default_settings(self):
        """Test client creation with default settings"""
        client = UserServiceClient()
        assert isinstance(client, UserServiceClient)
        assert client.user_service_url is not None

    @pytest.mark.asyncio
    async def test_client_error_handling_patterns(self):
        """Test common error handling patterns"""
        client = UserServiceClient("test:50051")
        
        # Mock stub for error testing
        mock_stub = Mock()
        client.stub = mock_stub
        
        # Test NOT_FOUND errors are handled gracefully
        not_found_error = grpc.RpcError()
        not_found_error.code = Mock(return_value=StatusCode.NOT_FOUND)
        not_found_error.details = Mock(return_value="User not found")
        
        mock_stub.GetUserByEmail.side_effect = not_found_error
        mock_stub.GetUserById.side_effect = not_found_error
        mock_stub.UpdateUser.side_effect = not_found_error
        mock_stub.DeleteUser.side_effect = not_found_error
        
        with patch('app.user_client.logger'):
            # NOT_FOUND errors should be handled gracefully
            assert await client.get_user_by_email("test@example.com") is None
            assert await client.get_user_by_id("test123") is None
            assert await client.update_user("test123", "Updated", "test@example.com") is None
            assert await client.delete_user("test123") is False
        
        # Test that other gRPC errors are re-raised
        unavailable_error = grpc.RpcError()
        unavailable_error.code = Mock(return_value=StatusCode.UNAVAILABLE)
        unavailable_error.details = Mock(return_value="Service unavailable")
        
        mock_stub.GetUserByEmail.side_effect = unavailable_error
        mock_stub.GetUserById.side_effect = unavailable_error
        mock_stub.CreateUser.side_effect = unavailable_error
        mock_stub.UpdateUser.side_effect = unavailable_error
        mock_stub.DeleteUser.side_effect = unavailable_error
        mock_stub.ListUsers.side_effect = unavailable_error
        
        with patch('app.user_client.logger'):
            # UNAVAILABLE errors should be re-raised
            with pytest.raises(grpc.RpcError):
                await client.get_user_by_email("test@example.com")
            
            with pytest.raises(grpc.RpcError):
                await client.get_user_by_id("test123")
            
            with pytest.raises(grpc.RpcError):
                await client.create_user("Test", "test@example.com")
            
            with pytest.raises(grpc.RpcError):
                await client.update_user("test123", "Updated", "test@example.com")
            
            with pytest.raises(grpc.RpcError):
                await client.delete_user("test123")
            
            with pytest.raises(grpc.RpcError):
                await client.list_users()
        
        # Test ALREADY_EXISTS handling for create_user
        already_exists_error = grpc.RpcError()
        already_exists_error.code = Mock(return_value=StatusCode.ALREADY_EXISTS)
        already_exists_error.details = Mock(return_value="User already exists")
        
        mock_stub.CreateUser.side_effect = already_exists_error
        
        with pytest.raises(ValueError) as exc_info:
            await client.create_user("Test", "test@example.com")
        
        assert "already exists" in str(exc_info.value) 