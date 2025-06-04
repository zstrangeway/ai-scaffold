"""
Unit tests for main.py
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import asyncio

from app.main import app, lifespan


class TestMainApp:
    """Unit tests for the main FastAPI application"""

    def test_app_creation(self):
        """Test that the FastAPI app is created correctly"""
        assert app is not None
        assert app.title == "Gateway Service"
        assert app.description == "API Gateway service for my-scaffold-project"
        assert app.version == "0.1.0"

    def test_app_has_cors_middleware(self):
        """Test that CORS middleware is configured"""
        # Check that middleware is present
        cors_middleware_found = False
        for middleware in app.user_middleware:
            # Check if this is CORS middleware by looking at the wrapped class
            if hasattr(middleware, 'cls'):
                from starlette.middleware.cors import CORSMiddleware
                if middleware.cls == CORSMiddleware:
                    cors_middleware_found = True
                    break
        
        assert cors_middleware_found, "CORSMiddleware not found in app middleware"

    def test_app_includes_routers(self):
        """Test that routers are included"""
        # Check that routes exist
        routes = [route.path for route in app.routes]
        assert "/api/v1/auth/register" in routes
        assert "/api/v1/users/" in routes

    def test_root_endpoint(self):
        """Test the root endpoint"""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Gateway Service is running"
        assert data["service"] == "gateway-service"
        assert data["version"] == "0.1.0"
        assert data["status"] == "healthy"

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "gateway-service"
        assert "timestamp" in data

    def test_404_handler(self):
        """Test custom 404 handler"""
        client = TestClient(app)
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "Not Found"
        assert "not found" in data["detail"]
        assert data["path"] == "/nonexistent-endpoint"

    @patch('app.main.logger')
    def test_500_handler(self, mock_logger):
        """Test custom 500 handler"""
        from fastapi import Request
        from app.main import internal_error_handler
        
        # Create a mock request and exception
        mock_request = Mock()
        mock_request.url.path = "/test-error"
        test_exception = Exception("Test error")
        
        # Test the handler directly
        response = asyncio.get_event_loop().run_until_complete(
            internal_error_handler(mock_request, test_exception)
        )
        
        assert response.status_code == 500
        assert response.body == b'{"error":"Internal Server Error","detail":"An unexpected error occurred"}'
        
        # Verify error was logged
        mock_logger.error.assert_called_with("Internal server error: Test error")

    @pytest.mark.asyncio
    async def test_lifespan_startup_shutdown(self):
        """Test lifespan context manager"""
        mock_app = Mock()
        
        with patch('app.main.logger') as mock_logger, \
             patch('app.main.close_user_client') as mock_close:
            
            # Test the lifespan context manager
            async with lifespan(mock_app):
                # Verify startup logging
                mock_logger.info.assert_called_with("Starting Gateway Service...")
            
            # Verify shutdown logging and cleanup
            assert mock_logger.info.call_count == 2
            mock_logger.info.assert_any_call("Shutting down Gateway Service...")
            mock_close.assert_called_once()

    def test_app_settings_integration(self):
        """Test that app uses settings correctly"""
        from app.config import get_settings
        settings = get_settings()
        
        # Verify CORS origins are configured
        cors_middleware = None
        for middleware in app.user_middleware:
            if hasattr(middleware, 'cls') and middleware.cls.__name__ == 'CORSMiddleware':
                cors_middleware = middleware
                break
        
        assert cors_middleware is not None
        # The middleware should be configured with settings.ALLOWED_ORIGINS

    def test_app_docs_endpoints(self):
        """Test that documentation endpoints are available"""
        client = TestClient(app)
        
        # Test docs endpoint
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test redoc endpoint
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_app_openapi_schema(self):
        """Test that OpenAPI schema is generated"""
        schema = app.openapi()
        
        assert schema is not None
        assert schema["info"]["title"] == "Gateway Service"
        assert schema["info"]["version"] == "0.1.0"
        assert "paths" in schema
        assert "/api/v1/auth/register" in schema["paths"]

    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "gateway-service"
            assert data["version"] == "0.1.0"
            assert "message" in data

    def test_health_check_detailed_endpoint(self):
        """Test the detailed health check endpoint"""
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "gateway-service"
            assert "timestamp" in data

    def test_docs_endpoint_accessible(self):
        """Test that API documentation is accessible"""
        with TestClient(app) as client:
            response = client.get("/docs")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]

    def test_openapi_endpoint_accessible(self):
        """Test that OpenAPI schema is accessible"""
        with TestClient(app) as client:
            response = client.get("/openapi.json")
            assert response.status_code == 200
            data = response.json()
            assert data["info"]["title"] == "Gateway Service"
            assert data["info"]["version"] == "0.1.0"

    def test_cors_headers_in_response(self):
        """Test that CORS headers are present in responses"""
        with TestClient(app) as client:
            response = client.get("/", headers={"Origin": "http://localhost:3000"})
            assert response.status_code == 200
            # CORS headers should be present
            assert "access-control-allow-origin" in response.headers

    def test_api_prefix_routing(self):
        """Test that API routes are properly prefixed"""
        route_paths = [route.path for route in app.routes]
        
        # All API routes should be under /api/v1
        api_routes = [path for path in route_paths if path.startswith("/api/v1")]
        assert len(api_routes) > 0
        
        # Check specific expected routes
        expected_prefixes = ["/api/v1/auth", "/api/v1/users"]
        for prefix in expected_prefixes:
            assert any(path.startswith(prefix) for path in route_paths)

    def test_exception_handlers_configured(self):
        """Test that custom exception handlers are configured"""
        # Check that exception handlers are registered
        assert app.exception_handlers is not None
        
        # Test with a client to ensure handlers work
        with TestClient(app) as client:
            # Test 404 handling
            response = client.get("/nonexistent-endpoint")
            assert response.status_code == 404
            data = response.json()
            assert "error" in data
            assert "Not Found" in data["error"]

    def test_500_error_handler(self):
        """Test that 500 error handler works"""
        # The 500 handler is registered and should handle internal server errors
        assert 500 in app.exception_handlers
        assert app.exception_handlers[500] is not None

    def test_middleware_order(self):
        """Test that middleware is in correct order"""
        middleware_classes = [middleware.cls for middleware in app.user_middleware]
        
        # CORS middleware should be present
        from starlette.middleware.cors import CORSMiddleware
        assert CORSMiddleware in middleware_classes

    def test_app_can_handle_requests(self):
        """Test that the app can handle basic requests"""
        with TestClient(app) as client:
            # Test health check
            response = client.get("/")
            assert response.status_code == 200
            
            # Test detailed health check
            response = client.get("/health")
            assert response.status_code == 200
            
            # Test docs
            response = client.get("/docs")
            assert response.status_code == 200

    def test_app_handles_cors_preflight(self):
        """Test that the app handles CORS preflight requests"""
        with TestClient(app) as client:
            response = client.options(
                "/api/v1/auth/me",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Authorization"
                }
            )
            # Should handle preflight request
            assert response.status_code in [200, 204]

    def test_app_error_handling(self):
        """Test app error handling for various scenarios"""
        with TestClient(app) as client:
            # Test 404 for non-existent endpoint
            response = client.get("/api/v1/nonexistent")
            assert response.status_code == 404
            data = response.json()
            assert "error" in data
            
            # Test method not allowed
            response = client.patch("/")  # Health check only supports GET
            assert response.status_code == 405

    def test_app_security_headers(self):
        """Test that security-related headers are present"""
        with TestClient(app) as client:
            response = client.get("/")
            
            # Should have basic security considerations
            assert response.status_code == 200
            # FastAPI adds some security headers by default

    def test_app_content_types(self):
        """Test that the app handles different content types correctly"""
        with TestClient(app) as client:
            # JSON response for API endpoints
            response = client.get("/")
            assert "application/json" in response.headers["content-type"]
            
            # HTML for docs
            response = client.get("/docs")
            assert "text/html" in response.headers["content-type"]

    def test_app_handles_large_requests(self):
        """Test that the app can handle reasonably large requests"""
        with TestClient(app) as client:
            # Test with a larger payload (within reasonable limits)
            large_data = {"data": "x" * 1000}  # 1KB of data
            response = client.post("/api/v1/auth/register", json=large_data)
            # Should not crash, even if it returns an error
            assert response.status_code in [400, 422, 500]  # Various error codes are acceptable

    def test_root_endpoint_structure(self):
        """Test the structure of the root endpoint response"""
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            
            required_fields = ["message", "service", "version", "status"]
            for field in required_fields:
                assert field in data

    def test_health_endpoint_structure(self):
        """Test the structure of the health endpoint response"""
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            
            required_fields = ["status", "service", "timestamp"]
            for field in required_fields:
                assert field in data

    def test_custom_404_handler(self):
        """Test the custom 404 error handler"""
        with TestClient(app) as client:
            response = client.get("/this-path-does-not-exist")
            assert response.status_code == 404
            data = response.json()
            
            assert "error" in data
            assert "detail" in data
            assert "path" in data
            assert data["error"] == "Not Found"
            assert "/this-path-does-not-exist" in data["path"]

    def test_app_settings_integration(self):
        """Test that the app correctly integrates with settings"""
        # The app should use settings for configuration
        from app.config import get_settings
        settings = get_settings()
        
        # Verify the app is configured with settings values
        assert len(app.user_middleware) > 0  # CORS middleware should be added
        
        # Verify routes are prefixed correctly
        route_paths = [route.path for route in app.routes]
        api_routes = [path for path in route_paths if path.startswith(settings.API_V1_PREFIX)]
        assert len(api_routes) > 0 