"""
Application Configuration
Using Pydantic Settings for environment variable management
"""

from typing import List, Optional
from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "Stumpf.works POS"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: PostgresDsn
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: RedisDsn

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Multi-Tenant
    TENANT_HEADER_NAME: str = "X-Tenant-ID"
    DEFAULT_TENANT_SCHEMA: str = "public"
    ENABLE_SUBDOMAIN_ROUTING: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # SumUp Integration
    SUMUP_API_URL: str = "https://api.sumup.com/v0.1"
    SUMUP_CLIENT_ID: Optional[str] = None
    SUMUP_CLIENT_SECRET: Optional[str] = None
    SUMUP_WEBHOOK_SECRET: Optional[str] = None

    # Cloud-TSE (Fiskaly)
    FISKALY_API_URL: str = "https://kassensichv.io/api/v2"
    FISKALY_API_KEY: Optional[str] = None
    FISKALY_API_SECRET: Optional[str] = None
    TSE_ENABLED: bool = True

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # File Storage
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    EXPORT_DIR: str = "/app/exports"

    # GoBD / DSFinV-K
    GOBD_RETENTION_YEARS: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL (for SQLAlchemy)."""
        return str(self.DATABASE_URL).replace("postgresql://", "postgresql://")

    @property
    def database_url_async(self) -> str:
        """Get asynchronous database URL (for asyncpg)."""
        return str(self.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")


# Global settings instance
settings = Settings()
