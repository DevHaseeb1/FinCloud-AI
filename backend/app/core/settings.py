"""
Application settings and configuration.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application metadata
    app_name: str = "FinCloud-AI Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/fincloud_db"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API configuration
    api_prefix: str = "/api/v1"
    
    # ML Model configuration
    anomaly_contamination: float = 0.05
    forecast_periods: int = 30
    forecast_interval_width: float = 0.95
    
    # File upload configuration
    max_upload_size_mb: int = 100
    allowed_file_extensions: list = ["csv", "xlsx"]
    
    # Optional infrastructure
    redis_url: Optional[str] = None
    celery_broker: Optional[str] = None
    celery_backend: Optional[str] = None

    # Logging configuration
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
