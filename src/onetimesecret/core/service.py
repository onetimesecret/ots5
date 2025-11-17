"""
Secret Service

Business logic for secret creation, retrieval, and management.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from onetimesecret.config import settings
from onetimesecret.crypto import SecretEncryption, TokenGenerator
from onetimesecret.db.models import Secret, SecretMetadata

from .exceptions import (
    SecretExpiredError,
    SecretNotFoundError,
    SecretViewLimitError,
    InvalidPassphraseError,
)
from .schemas import SecretCreate


class SecretService:
    """
    Service for managing secrets.

    Handles encryption, storage, retrieval, and lifecycle management.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize service with database session.

        Args:
            db: AsyncSession for database operations
        """
        self.db = db
        self.encryption = SecretEncryption(settings.secret_key)
        self.token_gen = TokenGenerator()

    async def create_secret(
        self, secret_data: SecretCreate, owner_id: Optional[str] = None
    ) -> Tuple[Secret, SecretMetadata]:
        """
        Create a new encrypted secret.

        Args:
            secret_data: Secret creation data
            owner_id: Optional user ID who owns the secret

        Returns:
            Tuple of (Secret, SecretMetadata)

        Raises:
            ValueError: If secret data is invalid
        """
        # Validate TTL
        if secret_data.ttl < settings.min_ttl or secret_data.ttl > settings.max_ttl:
            raise ValueError(
                f"TTL must be between {settings.min_ttl} and {settings.max_ttl} seconds"
            )

        # Validate secret size
        if len(secret_data.secret.encode()) > settings.max_secret_size:
            raise ValueError(f"Secret size exceeds maximum of {settings.max_secret_size} bytes")

        # Generate unique ID
        secret_id = self.token_gen.generate_secret_key(32, TokenGenerator.URL_SAFE)

        # Encrypt the secret
        if secret_data.passphrase:
            ciphertext, salt, passphrase_hash = self.encryption.encrypt_with_passphrase(
                secret_data.secret, secret_data.passphrase
            )
        else:
            ciphertext, salt = self.encryption.encrypt(secret_data.secret)
            passphrase_hash = None

        # Calculate expiration
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=secret_data.ttl)

        # Create secret model
        secret = Secret(
            id=secret_id,
            ciphertext=ciphertext,
            salt=salt,
            passphrase_hash=passphrase_hash,
            passphrase_required=secret_data.passphrase is not None,
            burn_after_reading=secret_data.burn_after_reading,
            max_views=secret_data.max_views,
            expires_at=expires_at,
            ttl=secret_data.ttl,
            owner_id=owner_id,
        )

        # Create metadata
        metadata_key = self.token_gen.generate_metadata_key("meta", 32)
        secret.metadata_key = metadata_key

        metadata = SecretMetadata(
            id=metadata_key,
            secret_id=secret_id,
            recipient_hash=(
                self.encryption.hash_metadata(secret_data.recipient)
                if secret_data.recipient
                else None
            ),
            custom_message_hash=(
                self.encryption.hash_metadata(secret_data.custom_message)
                if secret_data.custom_message
                else None
            ),
        )

        # Save to database
        self.db.add(secret)
        self.db.add(metadata)
        await self.db.commit()
        await self.db.refresh(secret)
        await self.db.refresh(metadata)

        return secret, metadata

    async def get_secret(
        self, secret_id: str, passphrase: Optional[str] = None, burn: bool = True
    ) -> str:
        """
        Retrieve and decrypt a secret.

        Args:
            secret_id: Unique secret identifier
            passphrase: Optional passphrase for protected secrets
            burn: Whether to delete/increment view count (default: True)

        Returns:
            Decrypted secret content

        Raises:
            SecretNotFoundError: If secret doesn't exist
            SecretExpiredError: If secret has expired
            SecretViewLimitError: If secret view limit reached
            InvalidPassphraseError: If passphrase is incorrect
        """
        # Fetch secret
        result = await self.db.execute(select(Secret).where(Secret.id == secret_id))
        secret = result.scalar_one_or_none()

        if not secret:
            raise SecretNotFoundError(f"Secret {secret_id} not found")

        # Check expiration
        if secret.is_expired():
            # Delete expired secret
            await self.db.delete(secret)
            await self.db.commit()
            raise SecretExpiredError("Secret has expired")

        # Check view limit
        if not secret.can_view():
            raise SecretViewLimitError("Secret view limit reached")

        # Decrypt secret
        try:
            if secret.passphrase_required:
                if not passphrase:
                    raise InvalidPassphraseError("Passphrase required")
                plaintext = self.encryption.decrypt_with_passphrase(
                    secret.ciphertext, secret.salt, passphrase, secret.passphrase_hash
                )
            else:
                plaintext = self.encryption.decrypt(secret.ciphertext, secret.salt)
        except Exception as e:
            raise InvalidPassphraseError(f"Decryption failed: {str(e)}")

        # Update view count or delete
        if burn:
            secret.increment_view_count()

            if secret.burn_after_reading or secret.view_count >= secret.max_views:
                # Delete the secret after viewing
                await self.db.delete(secret)
            else:
                # Just update view count
                await self.db.commit()

            await self.db.commit()

        return plaintext

    async def get_metadata(self, metadata_key: str) -> SecretMetadata:
        """
        Get secret metadata without burning the secret.

        Args:
            metadata_key: Metadata identifier

        Returns:
            SecretMetadata object

        Raises:
            SecretNotFoundError: If metadata doesn't exist
        """
        result = await self.db.execute(
            select(SecretMetadata).where(SecretMetadata.id == metadata_key)
        )
        metadata = result.scalar_one_or_none()

        if not metadata:
            raise SecretNotFoundError(f"Metadata {metadata_key} not found")

        # Mark as accessed
        metadata.mark_accessed()
        await self.db.commit()
        await self.db.refresh(metadata)

        return metadata

    async def delete_secret(self, secret_id: str, owner_id: Optional[str] = None) -> bool:
        """
        Delete a secret.

        Args:
            secret_id: Secret identifier
            owner_id: Optional owner ID for authorization

        Returns:
            True if deleted, False if not found

        Raises:
            PermissionError: If owner_id doesn't match
        """
        result = await self.db.execute(select(Secret).where(Secret.id == secret_id))
        secret = result.scalar_one_or_none()

        if not secret:
            return False

        # Check ownership if owner_id provided
        if owner_id and secret.owner_id != owner_id:
            raise PermissionError("Not authorized to delete this secret")

        await self.db.delete(secret)
        await self.db.commit()

        return True

    async def cleanup_expired_secrets(self) -> int:
        """
        Clean up expired secrets from the database.

        Returns:
            Number of secrets deleted

        Note:
            This should be run periodically as a background task.
        """
        result = await self.db.execute(
            select(Secret).where(Secret.expires_at <= datetime.now(timezone.utc))
        )
        expired_secrets = result.scalars().all()

        count = len(expired_secrets)
        for secret in expired_secrets:
            await self.db.delete(secret)

        await self.db.commit()
        return count
