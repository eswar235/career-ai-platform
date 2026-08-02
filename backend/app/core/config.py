"""
Configuration management for the FastAPI application
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Career Assistant SaaS API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/career_ai_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 720

    # API Keys
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    LINKEDIN_API_KEY: str = ""
    INDEED_API_KEY: str = ""
    GITHUB_API_KEY: str = ""

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "resumes"

    # Email
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@careeraiplatform.com"
    SENDGRID_FROM_NAME: str = "Career Assistant"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD_SECONDS: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    SENTRY_DSN: str = ""

    # Features
    ENABLE_JOB_ALERTS: bool = True
    ENABLE_RESUME_OPTIMIZATION: bool = True
    ENABLE_COVER_LETTER_GENERATION: bool = True
    ENABLE_SKILL_GAP_ANALYSIS: bool = True

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Database Settings
    SQLALCHEMY_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    class Config:
        """Pydantic configuration"""

        env_file = ".env"
        case_sensitive = True
        extra = "allow"


# Create global settings instance
settings = Settings()

