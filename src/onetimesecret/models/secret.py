"""Data models for secrets."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SecretMetadata(BaseModel):
    """Metadata for a secret stored in Redis."""

    secret_key: str = Field(description="Unique identifier for the secret")
    encrypted_content: str = Field(description="Encrypted secret content")
    salt: Optional[str] = Field(default=None, description="Salt for passphrase-based encryption")
    has_passphrase: bool = Field(default=False, description="Whether secret requires passphrase")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    ttl: int = Field(description="Time-to-live in seconds")
    viewed: bool = Field(default=False, description="Whether secret has been viewed")
    metadata_key: Optional[str] = Field(default=None, description="Key for metadata storage")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SecretCreate(BaseModel):
    """Request model for creating a secret."""

    secret: str = Field(description="Secret content to store", min_length=1)
    passphrase: Optional[str] = Field(default=None, description="Optional passphrase for additional security")
    ttl: Optional[int] = Field(default=None, description="Time-to-live in seconds")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "secret": "This is a secret message",
                "passphrase": "mysecretpassword",
                "ttl": 3600
            }
        }


class SecretResponse(BaseModel):
    """Response model for secret creation."""

    secret_key: str = Field(description="Unique key to retrieve the secret")
    metadata_key: str = Field(description="Key to retrieve secret metadata")
    ttl: int = Field(description="Time-to-live in seconds")
    created_at: datetime = Field(description="Creation timestamp")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "secret_key": "abc123def456",
                "metadata_key": "abc123def456_metadata",
                "ttl": 3600,
                "created_at": "2023-01-01T00:00:00"
            }
        }


class SecretRetrieve(BaseModel):
    """Request model for retrieving a secret."""

    passphrase: Optional[str] = Field(default=None, description="Passphrase if secret is protected")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "passphrase": "mysecretpassword"
            }
        }


class SecretContent(BaseModel):
    """Response model for retrieved secret content."""

    secret: str = Field(description="Decrypted secret content")
    created_at: datetime = Field(description="Creation timestamp")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "secret": "This is a secret message",
                "created_at": "2023-01-01T00:00:00"
            }
        }


class SecretMetadataResponse(BaseModel):
    """Response model for secret metadata."""

    secret_key: str = Field(description="Secret identifier")
    created_at: datetime = Field(description="Creation timestamp")
    ttl: int = Field(description="Time-to-live in seconds")
    viewed: bool = Field(description="Whether secret has been viewed")
    has_passphrase: bool = Field(description="Whether secret requires passphrase")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "secret_key": "abc123def456",
                "created_at": "2023-01-01T00:00:00",
                "ttl": 3600,
                "viewed": False,
                "has_passphrase": True
            }
        }
