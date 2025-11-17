"""Business logic for secret management."""

from datetime import datetime
from typing import Optional

from onetimesecret.core.config import Settings
from onetimesecret.core.exceptions import (
    SecretTooLargeException,
    InvalidTTLException,
    SecretNotFoundException,
    InvalidPassphraseException,
)
from onetimesecret.models.secret import (
    SecretMetadata,
    SecretCreate,
    SecretResponse,
    SecretContent,
    SecretMetadataResponse,
)
from onetimesecret.services.redis_client import SecretStorage
from onetimesecret.utils.crypto import SecretEncryption, generate_secret_id


class SecretService:
    """Service for managing one-time secrets."""

    def __init__(self, storage: SecretStorage, encryption: SecretEncryption, settings: Settings):
        """
        Initialize the secret service.

        Args:
            storage: Redis storage client
            encryption: Encryption handler
            settings: Application settings
        """
        self.storage = storage
        self.encryption = encryption
        self.settings = settings

    def create_secret(self, secret_data: SecretCreate) -> SecretResponse:
        """
        Create a new one-time secret.

        Args:
            secret_data: Secret creation request

        Returns:
            Secret response with key and metadata

        Raises:
            SecretTooLargeException: If secret exceeds maximum size
            InvalidTTLException: If TTL is invalid
        """
        # Validate secret size
        if len(secret_data.secret.encode()) > self.settings.max_secret_size:
            raise SecretTooLargeException(
                f"Secret size exceeds maximum of {self.settings.max_secret_size} bytes"
            )

        # Validate and set TTL
        ttl = secret_data.ttl if secret_data.ttl is not None else self.settings.default_ttl

        if ttl <= 0:
            raise InvalidTTLException("TTL must be positive")

        if ttl > self.settings.max_ttl:
            raise InvalidTTLException(
                f"TTL exceeds maximum of {self.settings.max_ttl} seconds"
            )

        # Check passphrase requirement
        if self.settings.passphrase_required and not secret_data.passphrase:
            raise InvalidPassphraseException("Passphrase is required")

        # Encrypt the secret
        encrypted_content, salt = self.encryption.encrypt(
            secret_data.secret,
            secret_data.passphrase
        )

        # Generate unique secret key
        secret_key = generate_secret_id()

        # Create metadata
        created_at = datetime.utcnow()
        metadata = SecretMetadata(
            secret_key=secret_key,
            encrypted_content=encrypted_content,
            salt=salt,
            has_passphrase=secret_data.passphrase is not None,
            created_at=created_at,
            ttl=ttl,
            viewed=False,
            metadata_key=f"{secret_key}:metadata"
        )

        # Store in Redis
        self.storage.store_secret(metadata)

        # Return response
        return SecretResponse(
            secret_key=secret_key,
            metadata_key=f"{secret_key}:metadata",
            ttl=ttl,
            created_at=created_at
        )

    def retrieve_secret(self, secret_key: str, passphrase: Optional[str] = None) -> SecretContent:
        """
        Retrieve and destroy a one-time secret.

        Args:
            secret_key: Unique secret identifier
            passphrase: Optional passphrase for protected secrets

        Returns:
            Decrypted secret content

        Raises:
            SecretNotFoundException: If secret not found or already viewed
            InvalidPassphraseException: If passphrase is incorrect or missing
        """
        # Get metadata first to check if passphrase is required
        metadata = self.storage.get_metadata(secret_key)

        if not metadata:
            raise SecretNotFoundException()

        # Check if secret has already been viewed
        if metadata.get("viewed", False):
            raise SecretNotFoundException("Secret has already been viewed")

        # Check passphrase requirement
        has_passphrase = metadata.get("has_passphrase", False)

        if has_passphrase and not passphrase:
            raise InvalidPassphraseException("Passphrase required for this secret")

        if self.settings.passphrase_required and not passphrase:
            raise InvalidPassphraseException("Passphrase is required")

        # Retrieve and destroy the secret
        encrypted_content, salt = self.storage.retrieve_secret(secret_key, destroy=True)

        # Decrypt the secret
        plaintext = self.encryption.decrypt(encrypted_content, passphrase, salt)

        return SecretContent(
            secret=plaintext,
            created_at=metadata["created_at"]
        )

    def get_metadata(self, secret_key: str) -> SecretMetadataResponse:
        """
        Get metadata for a secret without retrieving/destroying it.

        Args:
            secret_key: Unique secret identifier

        Returns:
            Secret metadata

        Raises:
            SecretNotFoundException: If secret not found
        """
        metadata = self.storage.get_metadata(secret_key)

        if not metadata:
            raise SecretNotFoundException()

        return SecretMetadataResponse(
            secret_key=metadata["secret_key"],
            created_at=metadata["created_at"],
            ttl=metadata["ttl"],
            viewed=metadata["viewed"],
            has_passphrase=metadata["has_passphrase"]
        )

    def delete_secret(self, secret_key: str) -> bool:
        """
        Manually delete a secret before it's viewed.

        Args:
            secret_key: Unique secret identifier

        Returns:
            True if secret was deleted, False if it didn't exist
        """
        return self.storage.delete_secret(secret_key)

    def secret_exists(self, secret_key: str) -> bool:
        """
        Check if a secret exists.

        Args:
            secret_key: Unique secret identifier

        Returns:
            True if secret exists, False otherwise
        """
        return self.storage.secret_exists(secret_key)
