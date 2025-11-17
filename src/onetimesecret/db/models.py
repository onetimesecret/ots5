"""
Database Models

SQLAlchemy ORM models for secrets, users, and metadata.
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Secret(Base):
    """
    Secret storage model.

    Stores encrypted secrets with metadata and access control.
    """

    __tablename__ = "secrets"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Encrypted data
    ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)

    # Optional passphrase protection
    passphrase_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    passphrase_required: Mapped[bool] = mapped_column(Boolean, default=False)

    # Access control
    burn_after_reading: Mapped[bool] = mapped_column(Boolean, default=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    max_views: Mapped[int] = mapped_column(Integer, default=1)

    # Expiration
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ttl: Mapped[int] = mapped_column(Integer, nullable=False)  # Seconds

    # Owner (optional)
    owner_id: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )

    # Metadata
    metadata_key: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, unique=True)

    # Relationships
    owner: Mapped[Optional["User"]] = relationship("User", back_populates="secrets")
    metadata: Mapped[Optional["SecretMetadata"]] = relationship(
        "SecretMetadata", back_populates="secret", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("ix_secrets_expires_at", "expires_at"),
        Index("ix_secrets_owner_id", "owner_id"),
        Index("ix_secrets_created_at", "created_at"),
    )

    def is_expired(self) -> bool:
        """Check if secret has expired."""
        return datetime.utcnow() >= self.expires_at

    def can_view(self) -> bool:
        """Check if secret can be viewed."""
        if self.is_expired():
            return False
        if self.burn_after_reading and self.view_count >= 1:
            return False
        if self.view_count >= self.max_views:
            return False
        return True

    def increment_view_count(self) -> None:
        """Increment view counter."""
        self.view_count += 1


class SecretMetadata(Base):
    """
    Secret metadata that can be accessed without burning the secret.

    Allows checking secret status without revealing content.
    """

    __tablename__ = "secret_metadata"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Foreign key to secret
    secret_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("secrets.id", ondelete="CASCADE"), unique=True
    )

    # Metadata fields (hashed, not plaintext)
    recipient_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    custom_message_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Status information
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    access_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    secret: Mapped["Secret"] = relationship("Secret", back_populates="metadata")

    def mark_accessed(self) -> None:
        """Mark metadata as accessed."""
        self.accessed_at = datetime.utcnow()
        self.access_count += 1


class User(Base):
    """
    User model for authenticated access.

    Optional feature - secrets can be created anonymously.
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Authentication
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    secrets: Mapped[list["Secret"]] = relationship(
        "Secret", back_populates="owner", cascade="all, delete-orphan"
    )
    api_keys: Mapped[list["APIKey"]] = relationship(
        "APIKey", back_populates="user", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_users_username", "username"),
        Index("ix_users_email", "email"),
    )


class APIKey(Base):
    """
    API key for programmatic access.

    Allows users to create and manage secrets via API.
    """

    __tablename__ = "api_keys"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Key data
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    key_prefix: Mapped[str] = mapped_column(
        String(8), nullable=False
    )  # First 8 chars for identification

    # Owner
    user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Metadata
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")

    # Indexes
    __table_args__ = (
        Index("ix_api_keys_user_id", "user_id"),
        Index("ix_api_keys_key_hash", "key_hash"),
    )

    def is_valid(self) -> bool:
        """Check if API key is valid."""
        if not self.is_active:
            return False
        if self.expires_at and datetime.utcnow() >= self.expires_at:
            return False
        return True

    def update_last_used(self) -> None:
        """Update last used timestamp."""
        self.last_used = datetime.utcnow()
