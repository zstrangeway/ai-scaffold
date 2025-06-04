"""
Configuration settings for the Gateway Service.

Centralizes all environment-based configuration with sensible defaults.
"""

import os
from typing import List


class Settings:
    """Application settings loaded from environment variables"""
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", 
        "your-secret-key-change-in-production-this-should-be-a-long-random-string"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
    
    # User Service Configuration
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "localhost:50051")
    
    # FastAPI Configuration
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv(
            "ALLOWED_ORIGINS", 
            "http://localhost:3000,http://localhost:3001,http://localhost:3002"
        ).split(",")
    ]
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.DEBUG
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings 