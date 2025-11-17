"""Configuration management for OneTimeSecret."""

import secrets
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Core settings
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Application secret key for cryptographic operations"
    )

    # Security options
    ssl_enabled: bool = Field(
        default=False,
        description="Enable SSL/TLS enforcement"
    )
    auth_required: bool = Field(
        default=False,
        description="Require authentication for API access"
    )
    passphrase_required: bool = Field(
        default=False,
        description="Require passphrase for all secrets"
    )

    # Application settings
    max_secret_size: int = Field(
        default=1048576,  # 1MB
        description="Maximum size of secret content in bytes"
    )
    default_ttl: int = Field(
        default=604800,  # 7 days
        description="Default time-to-live for secrets in seconds"
    )
    max_ttl: int = Field(
        default=2592000,  # 30 days
        description="Maximum allowed TTL for secrets in seconds"
    )

    # API settings
    api_prefix: str = Field(
        default="/api/v2",
        description="API route prefix"
    )
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )

    # Server settings
    host: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    port: int = Field(
        default=8000,
        description="Server port"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    @validator("max_secret_size")
    def validate_max_secret_size(cls, v: int) -> int:
        """Ensure max_secret_size is positive and reasonable."""
        if v <= 0:
            raise ValueError("max_secret_size must be positive")
        if v > 10485760:  # 10MB
            raise ValueError("max_secret_size cannot exceed 10MB")
        return v

    @validator("default_ttl", "max_ttl")
    def validate_ttl(cls, v: int) -> int:
        """Ensure TTL values are positive."""
        if v <= 0:
            raise ValueError("TTL must be positive")
        return v

    @validator("max_ttl")
    def validate_max_ttl_vs_default(cls, v: int, values: dict) -> int:
        """Ensure max_ttl is greater than or equal to default_ttl."""
        if "default_ttl" in values and v < values["default_ttl"]:
            raise ValueError("max_ttl must be >= default_ttl")
        return v

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_prefix = "OTS_"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (useful for testing)."""
    global _settings
    _settings = None
