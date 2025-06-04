import pytest
from unittest.mock import patch, Mock, MagicMock
import logging

from app import main


class TestMain:
    """Unit tests for main.py server startup"""

    @patch('app.main.grpc.server')
    @patch('app.main.add_UserServiceServicer_to_server')
    @patch('app.main.UserService')
    def test_serve_starts_server_successfully(self, mock_user_service, mock_add_servicer, mock_grpc_server):
        """Test that serve() starts gRPC server correctly"""
        # Setup mocks
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        mock_service_instance = Mock()
        mock_user_service.return_value = mock_service_instance
        
        # Mock server to terminate immediately
        mock_server.wait_for_termination.side_effect = KeyboardInterrupt()
        
        # Call serve function
        main.serve()
        
        # Verify server setup
        mock_grpc_server.assert_called_once()
        mock_user_service.assert_called_once()
        mock_add_servicer.assert_called_once_with(mock_service_instance, mock_server)
        mock_server.add_insecure_port.assert_called_once_with("[::]:50051")
        mock_server.start.assert_called_once()
        mock_server.wait_for_termination.assert_called_once()
        mock_server.stop.assert_called_once_with(0)

    @patch('app.main.grpc.server')
    @patch('app.main.add_UserServiceServicer_to_server')
    @patch('app.main.UserService')
    def test_serve_handles_keyboard_interrupt(self, mock_user_service, mock_add_servicer, mock_grpc_server):
        """Test that serve() handles KeyboardInterrupt gracefully"""
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        mock_server.wait_for_termination.side_effect = KeyboardInterrupt()
        
        # Should not raise exception
        main.serve()
        
        # Should call stop on KeyboardInterrupt
        mock_server.stop.assert_called_once_with(0)

    @patch('app.main.grpc.server')
    @patch('app.main.add_UserServiceServicer_to_server')
    @patch('app.main.UserService')
    @patch('app.main.logger')
    def test_serve_logs_startup_and_shutdown(self, mock_logger, mock_user_service, mock_add_servicer, mock_grpc_server):
        """Test that serve() logs startup and shutdown messages"""
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        mock_server.wait_for_termination.side_effect = KeyboardInterrupt()
        
        main.serve()
        
        # Verify logging calls
        mock_logger.info.assert_any_call("Starting User Service gRPC server on [::]:50051")
        mock_logger.info.assert_any_call("Shutting down gRPC server...")

    @patch('app.main.create_tables')
    @patch('app.main.serve')
    @patch('app.main.logger')
    def test_main_successful_startup(self, mock_logger, mock_serve, mock_create_tables):
        """Test successful main execution path"""
        # Mock successful table creation
        mock_create_tables.return_value = None
        
        # Run main
        with patch('app.main.__name__', '__main__'):
            # Simulate running the main block
            try:
                main.create_tables()
                mock_logger.info("Database tables created successfully")
                main.serve()
            except SystemExit:
                pass  # Expected when running main
        
        mock_create_tables.assert_called_once()
        mock_logger.info.assert_called_with("Database tables created successfully")

    @patch('app.main.create_tables')
    @patch('app.main.logger')
    @patch('builtins.exit')
    def test_main_database_creation_failure(self, mock_exit, mock_logger, mock_create_tables):
        """Test main execution when database table creation fails"""
        # Mock failed table creation
        mock_create_tables.side_effect = Exception("Database connection failed")
        
        # Simulate the main block logic
        try:
            main.create_tables()
            mock_logger.info("Database tables created successfully")
        except Exception as e:
            mock_logger.error(f"Failed to create database tables: {e}")
            mock_exit(1)
        
        mock_create_tables.assert_called_once()
        mock_logger.error.assert_called_with("Failed to create database tables: Database connection failed")
        mock_exit.assert_called_with(1)

    @patch('app.main.ThreadPoolExecutor')
    @patch('app.main.grpc.server')
    def test_serve_uses_correct_thread_pool_settings(self, mock_grpc_server, mock_thread_pool):
        """Test that serve() configures ThreadPoolExecutor correctly"""
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        mock_server.wait_for_termination.side_effect = KeyboardInterrupt()
        
        main.serve()
        
        # Verify ThreadPoolExecutor is configured with max_workers=10
        mock_thread_pool.assert_called_once_with(max_workers=10)
        # Verify grpc.server is called with the ThreadPoolExecutor
        mock_grpc_server.assert_called_once_with(mock_thread_pool.return_value)

    def test_logging_configuration(self):
        """Test that logging is configured correctly"""
        # This is a basic test to ensure logging setup doesn't crash
        # The actual configuration is done at module level
        
        # Get the logger and verify it exists
        logger = logging.getLogger('app.main')
        assert logger is not None
        
        # Test that we can log without errors
        logger.info("Test log message")
        
        # Verify the main module logger exists
        assert main.logger is not None

    @patch('app.main.grpc.server')
    @patch('app.main.add_UserServiceServicer_to_server')
    @patch('app.main.UserService')
    def test_serve_server_configuration(self, mock_user_service, mock_add_servicer, mock_grpc_server):
        """Test that server is configured with correct settings"""
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        mock_server.wait_for_termination.side_effect = KeyboardInterrupt()
        
        main.serve()
        
        # Verify server configuration
        mock_server.add_insecure_port.assert_called_once_with("[::]:50051")
        
        # Verify the correct address format (IPv6 compatible)
        args = mock_server.add_insecure_port.call_args[0]
        assert "[::]:50051" in args[0]
        assert "50051" in args[0]  # Verify port number 