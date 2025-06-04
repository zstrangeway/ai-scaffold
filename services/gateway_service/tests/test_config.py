"""
Unit tests for config.py
"""

import pytest
from unittest.mock import patch, Mock
import os
from app.config import Settings, get_settings


class TestSettings:
    """Unit tests for Settings configuration"""

    def test_settings_has_expected_attributes(self):
        """Test that Settings has all expected attributes"""
        settings = Settings()
        
        # Check all attributes exist
        assert hasattr(settings, 'JWT_SECRET_KEY')
        assert hasattr(settings, 'JWT_ALGORITHM')
        assert hasattr(settings, 'JWT_EXPIRE_MINUTES')
        assert hasattr(settings, 'USER_SERVICE_URL')
        assert hasattr(settings, 'DEBUG')
        assert hasattr(settings, 'LOG_LEVEL')
        assert hasattr(settings, 'ALLOWED_ORIGINS')
        assert hasattr(settings, 'HOST')
        assert hasattr(settings, 'PORT')
        assert hasattr(settings, 'API_V1_PREFIX')

    def test_settings_default_values(self):
        """Test that Settings has expected default values"""
        settings = Settings()
        
        # Test types and reasonable defaults
        assert isinstance(settings.JWT_SECRET_KEY, str)
        assert len(settings.JWT_SECRET_KEY) > 0
        assert settings.JWT_ALGORITHM == "HS256"
        assert isinstance(settings.JWT_EXPIRE_MINUTES, int)
        assert settings.JWT_EXPIRE_MINUTES > 0
        assert isinstance(settings.USER_SERVICE_URL, str)
        assert len(settings.USER_SERVICE_URL) > 0
        assert isinstance(settings.DEBUG, bool)
        assert isinstance(settings.LOG_LEVEL, str)
        assert isinstance(settings.ALLOWED_ORIGINS, list)
        assert len(settings.ALLOWED_ORIGINS) > 0
        assert isinstance(settings.HOST, str)
        assert isinstance(settings.PORT, int)
        assert settings.PORT > 0
        assert settings.API_V1_PREFIX == "/api/v1"

    def test_settings_properties(self):
        """Test Settings properties"""
        settings = Settings()
        
        # Test properties exist and return correct types
        assert isinstance(settings.is_development, bool)
        assert isinstance(settings.is_production, bool)
        
        # Test property relationship
        assert settings.is_development == settings.DEBUG
        assert settings.is_production == (not settings.DEBUG)

    def test_settings_allowed_origins_is_list(self):
        """Test that ALLOWED_ORIGINS is properly formatted as a list"""
        settings = Settings()
        
        assert isinstance(settings.ALLOWED_ORIGINS, list)
        for origin in settings.ALLOWED_ORIGINS:
            assert isinstance(origin, str)

    def test_settings_jwt_expire_minutes_is_integer(self):
        """Test that JWT_EXPIRE_MINUTES is an integer"""
        settings = Settings()
        
        assert isinstance(settings.JWT_EXPIRE_MINUTES, int)
        assert settings.JWT_EXPIRE_MINUTES > 0

    def test_settings_port_is_integer(self):
        """Test that PORT is an integer"""
        settings = Settings()
        
        assert isinstance(settings.PORT, int)
        assert settings.PORT > 0

    def test_settings_instantiation(self):
        """Test that Settings can be instantiated multiple times"""
        settings1 = Settings()
        settings2 = Settings()
        
        # Both should be instances of Settings
        assert isinstance(settings1, Settings)
        assert isinstance(settings2, Settings)
        
        # They should have the same values (class attributes)
        assert settings1.JWT_ALGORITHM == settings2.JWT_ALGORITHM
        assert settings1.API_V1_PREFIX == settings2.API_V1_PREFIX


class TestGetSettings:
    """Unit tests for get_settings function"""

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns a Settings instance"""
        settings = get_settings()
        
        assert isinstance(settings, Settings)

    def test_get_settings_returns_same_instance(self):
        """Test that get_settings returns the same global instance"""
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should return the same instance (global settings object)
        assert settings1 is settings2

    def test_get_settings_consistency(self):
        """Test that get_settings returns consistent values"""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1.JWT_SECRET_KEY == settings2.JWT_SECRET_KEY
        assert settings1.JWT_ALGORITHM == settings2.JWT_ALGORITHM
        assert settings1.DEBUG == settings2.DEBUG
        assert settings1.API_V1_PREFIX == settings2.API_V1_PREFIX

    def test_get_settings_has_all_attributes(self):
        """Test that get_settings result has all expected attributes"""
        settings = get_settings()
        
        # Verify all expected attributes are present
        required_attrs = [
            'JWT_SECRET_KEY', 'JWT_ALGORITHM', 'JWT_EXPIRE_MINUTES',
            'USER_SERVICE_URL', 'DEBUG', 'LOG_LEVEL', 'ALLOWED_ORIGINS',
            'HOST', 'PORT', 'API_V1_PREFIX', 'is_development', 'is_production'
        ]
        
        for attr in required_attrs:
            assert hasattr(settings, attr), f"Missing attribute: {attr}"


class TestSettingsIntegration:
    """Integration tests for Settings with environment variables"""

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_with_no_environment_variables(self):
        """Test Settings behavior with no environment variables set"""
        # This test ensures Settings works even with a clean environment
        settings = Settings()
        
        # Should still have all required attributes with defaults
        assert hasattr(settings, 'JWT_SECRET_KEY')
        assert hasattr(settings, 'JWT_ALGORITHM') 
        assert hasattr(settings, 'API_V1_PREFIX')
        assert settings.API_V1_PREFIX == "/api/v1"

    def test_settings_environment_variable_types(self):
        """Test that environment variables are properly typed"""
        settings = Settings()
        
        # Test that numeric environment variables are properly converted
        assert isinstance(settings.JWT_EXPIRE_MINUTES, int)
        assert isinstance(settings.PORT, int)
        
        # Test that boolean environment variables are properly converted
        assert isinstance(settings.DEBUG, bool)
        
        # Test that string environment variables remain strings
        assert isinstance(settings.JWT_SECRET_KEY, str)
        assert isinstance(settings.USER_SERVICE_URL, str)
        assert isinstance(settings.LOG_LEVEL, str)

    def test_settings_list_parsing(self):
        """Test that ALLOWED_ORIGINS list is properly parsed"""
        settings = Settings()
        
        # Should be a list of strings
        assert isinstance(settings.ALLOWED_ORIGINS, list)
        assert len(settings.ALLOWED_ORIGINS) > 0
        
        for origin in settings.ALLOWED_ORIGINS:
            assert isinstance(origin, str)
            # Basic URL format check
            assert len(origin.strip()) > 0 