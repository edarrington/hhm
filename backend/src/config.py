"""HHM Backend Configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API
    api_title: str = "HHM - Happy Household Manager"
    api_version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_log_level: str = "INFO"
    debug: bool = False
    environment: str = "development"  # development, staging, production
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/hhm_dev"
    database_pool_size: int = 20
    database_max_overflow: int = 40
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    
    # Voice Service
    voice_endpoint: str = ""
    voice_api_key: str = ""
    voice_model: str = "gpt-4-realtime"
    
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:3000/auth/callback"
    
    # Todoist
    todoist_api_token: str = ""
    
    # Authentication
    household_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]
    
    # Feature Flags
    enable_voice: bool = True
    enable_memory: bool = True
    enable_calendar: bool = True
    enable_gmail: bool = True
    enable_drive: bool = True
    enable_todoist: bool = True
    enable_conversation_logging: bool = True
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period_seconds: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
