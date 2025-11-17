"""
Configuration Management

Uses pydantic-settings for environment-based configuration with validation.
"""

from typing import List, Optional
from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "OneTimeSecret"
    app_version: str = "3.0.0"
    debug: bool = False
    environment: str = Field(default="production", pattern="^(development|staging|production)$")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False

    # Security
    secret_key: str = Field(
        ...,
        min_length=32,
        description="Cryptographic key for encryption (generate with: openssl rand -hex 32)",
    )
    ssl_enabled: bool = Field(
        default=True, description="SSL/TLS required for production deployments"
    )
    auth_required: bool = Field(default=False, description="Require login for all operations")
    passphrase_required: bool = Field(
        default=False, description="Require passphrase for secret access"
    )

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )
    cors_credentials: bool = True
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers: List[str] = ["*"]

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://ots:ots@localhost:5432/onetimesecret",
        description="PostgreSQL connection URL",
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    # Redis
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    redis_db: int = 0
    redis_max_connections: int = 50

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/2")

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # Secrets Configuration
    default_ttl: int = Field(default=3600, description="Default TTL in seconds (1 hour)")
    max_ttl: int = Field(default=259200, description="Maximum TTL in seconds (3 days)")
    min_ttl: int = Field(default=300, description="Minimum TTL in seconds (5 minutes)")
    max_secret_size: int = Field(
        default=1048576, description="Maximum secret size in bytes (1MB)"
    )
    allowed_ttls: List[int] = Field(
        default=[1800, 43200, 86400, 259200],
        description="Allowed TTL options (30m, 12h, 24h, 3d)",
    )

    # Email (Optional)
    smtp_enabled: bool = False
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None

    # Logging
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    log_format: str = "json"

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is cryptographically secure."""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        return v

    @field_validator("ssl_enabled")
    @classmethod
    def validate_ssl_production(cls, v: bool, info) -> bool:
        """Require SSL in production."""
        if info.data.get("environment") == "production" and not v:
            raise ValueError("SSL must be enabled in production")
        return v


# Global settings instance
settings = Settings()
