import logging
from concurrent.futures import ThreadPoolExecutor
import grpc

# Import the generated gRPC stubs
try:
    # Try to import from the local path dependency first
    from user_service_pb2_grpc import add_UserServiceServicer_to_server
except ImportError:
    # Fallback import paths for development
    import sys
    import os
    
    # Add the generated contracts to the path
    generated_contracts_path = '/app/generated_contracts/py'
    if os.path.exists(generated_contracts_path):
        sys.path.insert(0, generated_contracts_path)
    else:
        # Development fallback
        sys.path.append('../../packages/api-contracts/generated/py')
    
    try:
        from user_service_pb2_grpc import add_UserServiceServicer_to_server
    except ImportError as e:
        raise ImportError(f"Failed to import gRPC contracts: {e}")

from .grpc_service import UserService
from .database import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def serve():
    """Start the gRPC server"""
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    user_service = UserService()
    add_UserServiceServicer_to_server(user_service, server)
    
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting User Service gRPC server on {listen_addr}")
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
        server.stop(0)


if __name__ == "__main__":
    # Initialize database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        exit(1)
    
    # Start gRPC server
    serve() 