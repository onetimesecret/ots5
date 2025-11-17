"""Unit tests for secret service."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest

from onetimesecret.models.secret import SecretCreate, SecretMetadata
from onetimesecret.services.secret_service import SecretService
from onetimesecret.core.exceptions import (
    SecretTooLargeException,
    InvalidTTLException,
    SecretNotFoundException,
    InvalidPassphraseException,
)


class TestSecretService:
    """Test cases for SecretService class."""

    def test_create_secret_basic(self, secret_service: SecretService) -> None:
        """Test creating a basic secret without passphrase."""
        secret_data = SecretCreate(secret="This is a test secret", ttl=3600)

        # Mock storage
        secret_service.storage.store_secret = MagicMock()

        response = secret_service.create_secret(secret_data)

        # Verify response
        assert response.secret_key is not None
        assert response.ttl == 3600
        assert response.created_at is not None
        assert isinstance(response.created_at, datetime)

        # Verify storage was called
        secret_service.storage.store_secret.assert_called_once()

    def test_create_secret_with_passphrase(self, secret_service: SecretService) -> None:
        """Test creating a secret with passphrase protection."""
        secret_data = SecretCreate(
            secret="Protected secret",
            passphrase="my_secure_password",
            ttl=7200
        )

        # Mock storage
        secret_service.storage.store_secret = MagicMock()

        response = secret_service.create_secret(secret_data)

        # Verify response
        assert response.secret_key is not None
        assert response.ttl == 7200

        # Verify storage was called with metadata including passphrase flag
        call_args = secret_service.storage.store_secret.call_args
        metadata = call_args[0][0]
        assert metadata.has_passphrase is True
        assert metadata.salt is not None

    def test_create_secret_default_ttl(
        self, secret_service: SecretService, test_settings
    ) -> None:
        """Test creating a secret with default TTL."""
        secret_data = SecretCreate(secret="Test secret")

        # Mock storage
        secret_service.storage.store_secret = MagicMock()

        response = secret_service.create_secret(secret_data)

        # Should use default TTL from settings
        assert response.ttl == test_settings.default_ttl

    def test_create_secret_too_large(self, secret_service: SecretService) -> None:
        """Test that creating a too-large secret raises exception."""
        # Create secret larger than max size
        large_secret = "A" * (secret_service.settings.max_secret_size + 1)
        secret_data = SecretCreate(secret=large_secret)

        with pytest.raises(SecretTooLargeException):
            secret_service.create_secret(secret_data)

    def test_create_secret_invalid_ttl_negative(self, secret_service: SecretService) -> None:
        """Test that negative TTL raises exception."""
        secret_data = SecretCreate(secret="Test", ttl=-100)

        with pytest.raises(InvalidTTLException):
            secret_service.create_secret(secret_data)

    def test_create_secret_invalid_ttl_zero(self, secret_service: SecretService) -> None:
        """Test that zero TTL raises exception."""
        secret_data = SecretCreate(secret="Test", ttl=0)

        with pytest.raises(InvalidTTLException):
            secret_service.create_secret(secret_data)

    def test_create_secret_ttl_exceeds_max(
        self, secret_service: SecretService, test_settings
    ) -> None:
        """Test that TTL exceeding max raises exception."""
        secret_data = SecretCreate(secret="Test", ttl=test_settings.max_ttl + 1)

        with pytest.raises(InvalidTTLException):
            secret_service.create_secret(secret_data)

    def test_retrieve_secret_success(self, secret_service: SecretService) -> None:
        """Test successful secret retrieval."""
        # Setup
        secret_text = "Secret message"
        secret_key = "test_key_123"

        # Encrypt the secret
        encrypted_content, salt = secret_service.encryption.encrypt(secret_text)

        # Mock storage responses
        secret_service.storage.get_metadata = MagicMock(return_value={
            "secret_key": secret_key,
            "has_passphrase": False,
            "created_at": datetime.now(timezone.utc),
            "ttl": 3600,
            "viewed": False
        })
        secret_service.storage.retrieve_secret = MagicMock(
            return_value=(encrypted_content, None)
        )

        # Retrieve secret
        result = secret_service.retrieve_secret(secret_key)

        # Verify
        assert result.secret == secret_text
        secret_service.storage.retrieve_secret.assert_called_once_with(secret_key, destroy=True)

    def test_retrieve_secret_with_passphrase(self, secret_service: SecretService) -> None:
        """Test retrieving a passphrase-protected secret."""
        # Setup
        secret_text = "Protected message"
        secret_key = "test_key_456"
        passphrase = "my_password"

        # Encrypt with passphrase
        encrypted_content, salt = secret_service.encryption.encrypt(secret_text, passphrase)

        # Mock storage responses
        secret_service.storage.get_metadata = MagicMock(return_value={
            "secret_key": secret_key,
            "has_passphrase": True,
            "created_at": datetime.now(timezone.utc),
            "ttl": 3600,
            "viewed": False
        })
        secret_service.storage.retrieve_secret = MagicMock(
            return_value=(encrypted_content, salt)
        )

        # Retrieve with correct passphrase
        result = secret_service.retrieve_secret(secret_key, passphrase)

        # Verify
        assert result.secret == secret_text

    def test_retrieve_secret_wrong_passphrase(self, secret_service: SecretService) -> None:
        """Test that retrieving with wrong passphrase fails."""
        # Setup
        secret_text = "Protected message"
        secret_key = "test_key_789"
        correct_passphrase = "correct_password"
        wrong_passphrase = "wrong_password"

        # Encrypt with correct passphrase
        encrypted_content, salt = secret_service.encryption.encrypt(
            secret_text, correct_passphrase
        )

        # Mock storage responses
        secret_service.storage.get_metadata = MagicMock(return_value={
            "secret_key": secret_key,
            "has_passphrase": True,
            "created_at": datetime.now(timezone.utc),
            "ttl": 3600,
            "viewed": False
        })
        secret_service.storage.retrieve_secret = MagicMock(
            return_value=(encrypted_content, salt)
        )

        # Try to retrieve with wrong passphrase
        with pytest.raises(InvalidPassphraseException):
            secret_service.retrieve_secret(secret_key, wrong_passphrase)

    def test_retrieve_secret_not_found(self, secret_service: SecretService) -> None:
        """Test retrieving a non-existent secret."""
        secret_service.storage.get_metadata = MagicMock(return_value=None)

        with pytest.raises(SecretNotFoundException):
            secret_service.retrieve_secret("nonexistent_key")

    def test_retrieve_secret_already_viewed(self, secret_service: SecretService) -> None:
        """Test that retrieving an already-viewed secret fails."""
        secret_service.storage.get_metadata = MagicMock(return_value={
            "secret_key": "test_key",
            "has_passphrase": False,
            "created_at": datetime.now(timezone.utc),
            "ttl": 3600,
            "viewed": True  # Already viewed
        })

        with pytest.raises(SecretNotFoundException):
            secret_service.retrieve_secret("test_key")

    def test_retrieve_secret_missing_passphrase(
        self, secret_service: SecretService
    ) -> None:
        """Test that retrieving passphrase-protected secret without passphrase fails."""
        secret_service.storage.get_metadata = MagicMock(return_value={
            "secret_key": "test_key",
            "has_passphrase": True,
            "created_at": datetime.now(timezone.utc),
            "ttl": 3600,
            "viewed": False
        })

        with pytest.raises(InvalidPassphraseException):
            secret_service.retrieve_secret("test_key")

    def test_get_metadata(self, secret_service: SecretService) -> None:
        """Test getting secret metadata."""
        secret_key = "test_key"
        created_at = datetime.now(timezone.utc)

        secret_service.storage.get_metadata = MagicMock(return_value={
            "secret_key": secret_key,
            "has_passphrase": True,
            "created_at": created_at,
            "ttl": 3600,
            "viewed": False
        })

        metadata = secret_service.get_metadata(secret_key)

        assert metadata.secret_key == secret_key
        assert metadata.ttl == 3600
        assert metadata.viewed is False
        assert metadata.has_passphrase is True

    def test_get_metadata_not_found(self, secret_service: SecretService) -> None:
        """Test getting metadata for non-existent secret."""
        secret_service.storage.get_metadata = MagicMock(return_value=None)

        with pytest.raises(SecretNotFoundException):
            secret_service.get_metadata("nonexistent")

    def test_delete_secret(self, secret_service: SecretService) -> None:
        """Test deleting a secret."""
        secret_service.storage.delete_secret = MagicMock(return_value=True)

        result = secret_service.delete_secret("test_key")

        assert result is True
        secret_service.storage.delete_secret.assert_called_once_with("test_key")

    def test_secret_exists(self, secret_service: SecretService) -> None:
        """Test checking if secret exists."""
        secret_service.storage.secret_exists = MagicMock(return_value=True)

        result = secret_service.secret_exists("test_key")

        assert result is True
        secret_service.storage.secret_exists.assert_called_once_with("test_key")
