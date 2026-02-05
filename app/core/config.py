"""
Application configuration using Pydantic Settings.

This module defines all configuration variables loaded from environment variables.
Pydantic Settings provides type validation and IDE autocomplete.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings have defaults for development, but should be overridden
    in production via environment variables or .env file.
    """
    
    # Application Metadata
    app_name: str = "AI Compliance Tool"
    app_version: str = "0.1.0"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@db:5432/ai_compliance"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    
    # CORS (Cross-Origin Resource Sharing)
    # Allow all origins in development, restrict in production
    cors_origins: list[str] = ["http://localhost:8000", "http://localhost:3000"]
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra environment variables
    )


# Create a global settings instance
# This will be imported throughout the application
settings = Settings()