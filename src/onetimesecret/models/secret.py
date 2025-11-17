"""Data models for secrets."""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class SecretMetadata(BaseModel):
    """Metadata for a secret stored in Redis."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "secret_key": "abc123",
                "created_at": "2023-01-01T00:00:00+00:00",
                "ttl": 3600
            }
        }
    )

    secret_key: str = Field(description="Unique identifier for the secret")
    encrypted_content: str = Field(description="Encrypted secret content")
    salt: Optional[str] = Field(default=None, description="Salt for passphrase-based encryption")
    has_passphrase: bool = Field(default=False, description="Whether secret requires passphrase")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    ttl: int = Field(description="Time-to-live in seconds")
    viewed: bool = Field(default=False, description="Whether secret has been viewed")
    metadata_key: Optional[str] = Field(default=None, description="Key for metadata storage")

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime) -> str:
        """Serialize datetime to ISO format."""
        return dt.isoformat()


class SecretCreate(BaseModel):
    """Request model for creating a secret."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "secret": "This is a secret message",
                "passphrase": "mysecretpassword",
                "ttl": 3600
            }
        }
    )

    secret: str = Field(description="Secret content to store", min_length=1)
    passphrase: Optional[str] = Field(default=None, description="Optional passphrase for additional security")
    ttl: Optional[int] = Field(default=None, description="Time-to-live in seconds")


class SecretResponse(BaseModel):
    """Response model for secret creation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "secret_key": "abc123def456",
                "metadata_key": "abc123def456_metadata",
                "ttl": 3600,
                "created_at": "2023-01-01T00:00:00+00:00"
            }
        }
    )

    secret_key: str = Field(description="Unique key to retrieve the secret")
    metadata_key: str = Field(description="Key to retrieve secret metadata")
    ttl: int = Field(description="Time-to-live in seconds")
    created_at: datetime = Field(description="Creation timestamp")

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime) -> str:
        """Serialize datetime to ISO format."""
        return dt.isoformat()


class SecretRetrieve(BaseModel):
    """Request model for retrieving a secret."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "passphrase": "mysecretpassword"
            }
        }
    )

    passphrase: Optional[str] = Field(default=None, description="Passphrase if secret is protected")


class SecretContent(BaseModel):
    """Response model for retrieved secret content."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "secret": "This is a secret message",
                "created_at": "2023-01-01T00:00:00+00:00"
            }
        }
    )

    secret: str = Field(description="Decrypted secret content")
    created_at: datetime = Field(description="Creation timestamp")

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime) -> str:
        """Serialize datetime to ISO format."""
        return dt.isoformat()


class SecretMetadataResponse(BaseModel):
    """Response model for secret metadata."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "secret_key": "abc123def456",
                "created_at": "2023-01-01T00:00:00+00:00",
                "ttl": 3600,
                "viewed": False,
                "has_passphrase": True
            }
        }
    )

    secret_key: str = Field(description="Secret identifier")
    created_at: datetime = Field(description="Creation timestamp")
    ttl: int = Field(description="Time-to-live in seconds")
    viewed: bool = Field(description="Whether secret has been viewed")
    has_passphrase: bool = Field(description="Whether secret requires passphrase")

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime) -> str:
        """Serialize datetime to ISO format."""
        return dt.isoformat()
