"""
Pydantic Schemas

Request/response models for API validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SecretCreate(BaseModel):
    """Schema for creating a new secret."""

    secret: str = Field(..., min_length=1, max_length=1048576, description="Secret content")
    passphrase: Optional[str] = Field(
        None, min_length=1, max_length=256, description="Optional passphrase protection"
    )
    ttl: int = Field(
        default=3600,
        ge=300,
        le=259200,
        description="Time to live in seconds (5min - 3 days)",
    )
    recipient: Optional[str] = Field(
        None, max_length=255, description="Optional recipient identifier"
    )
    custom_message: Optional[str] = Field(
        None, max_length=1000, description="Optional custom message"
    )
    burn_after_reading: bool = Field(
        default=True, description="Delete after first view (default: true)"
    )
    max_views: int = Field(default=1, ge=1, le=100, description="Maximum number of views")

    @field_validator("ttl")
    @classmethod
    def validate_ttl(cls, v: int) -> int:
        """Validate TTL is within allowed range."""
        allowed_ttls = [1800, 3600, 43200, 86400, 259200]  # 30m, 1h, 12h, 24h, 3d
        if v not in allowed_ttls and not (300 <= v <= 259200):
            # Allow custom TTL within range, but prefer standard values
            pass
        return v


class SecretRetrieve(BaseModel):
    """Schema for retrieving a secret."""

    passphrase: Optional[str] = Field(None, description="Passphrase if required")


class SecretResponse(BaseModel):
    """Schema for secret response."""

    secret_id: str = Field(..., description="Unique secret identifier")
    secret: Optional[str] = Field(None, description="Secret content (only on first retrieval)")
    metadata_key: Optional[str] = Field(None, description="Metadata key for status checks")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    ttl: int = Field(..., description="Time to live in seconds")
    burn_after_reading: bool = Field(..., description="Whether secret burns after reading")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class SecretMetadataResponse(BaseModel):
    """Schema for secret metadata response."""

    secret_id: str = Field(..., description="Secret identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    ttl: int = Field(..., description="Time to live in seconds")
    is_expired: bool = Field(..., description="Whether secret has expired")
    view_count: int = Field(..., description="Number of times viewed")
    max_views: int = Field(..., description="Maximum allowed views")
    can_view: bool = Field(..., description="Whether secret can still be viewed")
    burn_after_reading: bool = Field(..., description="Whether secret burns after reading")
    passphrase_required: bool = Field(..., description="Whether passphrase is required")

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(..., min_length=3, max_length=64, pattern="^[a-zA-Z0-9_-]+$")
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    """Schema for user response."""

    id: str
    username: str
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class APIKeyCreate(BaseModel):
    """Schema for creating an API key."""

    name: Optional[str] = Field(None, max_length=255, description="Key name for identification")
    description: Optional[str] = Field(None, max_length=1000, description="Key description")
    expires_in_days: Optional[int] = Field(
        None, ge=1, le=365, description="Expiration in days (optional)"
    )


class APIKeyResponse(BaseModel):
    """Schema for API key response."""

    id: str
    key: Optional[str] = Field(
        None, description="Full key (only returned on creation)"
    )  # Only returned on creation
    key_prefix: str = Field(..., description="First 8 characters for identification")
    name: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[str] = Field(None, description="Additional error details")
