"""
Unit Tests for Cryptography Module

Tests for encryption, decryption, and token generation.
"""

import pytest

from onetimesecret.crypto import SecretEncryption, TokenGenerator
from onetimesecret.crypto.encryption import DecryptionError, EncryptionError


class TestSecretEncryption:
    """Test SecretEncryption class."""

    @pytest.fixture
    def encryption(self):
        """Create encryption instance with test key."""
        return SecretEncryption("test-master-key-minimum-32-chars-long")

    def test_init_with_short_key(self):
        """Test initialization with short key raises error."""
        with pytest.raises(ValueError, match="at least 32 characters"):
            SecretEncryption("short")

    def test_encrypt_decrypt(self, encryption):
        """Test basic encryption and decryption."""
        plaintext = "Hello, World! This is a secret."

        # Encrypt
        ciphertext, salt = encryption.encrypt(plaintext)

        # Verify outputs are not empty
        assert ciphertext
        assert salt
        assert ciphertext != plaintext

        # Decrypt
        decrypted = encryption.decrypt(ciphertext, salt)
        assert decrypted == plaintext

    def test_encrypt_decrypt_unicode(self, encryption):
        """Test encryption with unicode characters."""
        plaintext = "Hello 世界! 🔒 Secret émojis"

        ciphertext, salt = encryption.encrypt(plaintext)
        decrypted = encryption.decrypt(ciphertext, salt)

        assert decrypted == plaintext

    def test_decrypt_with_wrong_salt(self, encryption):
        """Test decryption with wrong salt fails."""
        plaintext = "Secret message"
        ciphertext, _ = encryption.encrypt(plaintext)

        # Try to decrypt with wrong salt
        wrong_salt = "d3JvbmdzYWx0MTIzNA=="

        with pytest.raises(DecryptionError):
            encryption.decrypt(ciphertext, wrong_salt)

    def test_decrypt_with_tampered_ciphertext(self, encryption):
        """Test decryption with tampered ciphertext fails."""
        plaintext = "Secret message"
        _, salt = encryption.encrypt(plaintext)

        # Tampered ciphertext
        tampered = "dGFtcGVyZWRjaXBoZXJ0ZXh0"

        with pytest.raises(DecryptionError):
            encryption.decrypt(tampered, salt)

    def test_hash_metadata(self):
        """Test metadata hashing."""
        data = "test@example.com"
        hash1 = SecretEncryption.hash_metadata(data)
        hash2 = SecretEncryption.hash_metadata(data)

        # Same input produces same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex chars

        # Different input produces different hash
        hash3 = SecretEncryption.hash_metadata("different@example.com")
        assert hash1 != hash3

    def test_encrypt_with_passphrase(self, encryption):
        """Test encryption with passphrase."""
        plaintext = "Secret with passphrase"
        passphrase = "my-secure-passphrase"

        ciphertext, salt, passphrase_hash = encryption.encrypt_with_passphrase(
            plaintext, passphrase
        )

        assert ciphertext
        assert salt
        assert passphrase_hash
        assert len(passphrase_hash) == 64

    def test_decrypt_with_passphrase(self, encryption):
        """Test decryption with passphrase."""
        plaintext = "Secret with passphrase"
        passphrase = "my-secure-passphrase"

        ciphertext, salt, passphrase_hash = encryption.encrypt_with_passphrase(
            plaintext, passphrase
        )

        # Decrypt with correct passphrase
        decrypted = encryption.decrypt_with_passphrase(
            ciphertext, salt, passphrase, passphrase_hash
        )
        assert decrypted == plaintext

    def test_decrypt_with_wrong_passphrase(self, encryption):
        """Test decryption with wrong passphrase fails."""
        plaintext = "Secret with passphrase"
        passphrase = "correct-passphrase"

        ciphertext, salt, passphrase_hash = encryption.encrypt_with_passphrase(
            plaintext, passphrase
        )

        # Try with wrong passphrase
        with pytest.raises(DecryptionError, match="Incorrect passphrase"):
            encryption.decrypt_with_passphrase(
                ciphertext, salt, "wrong-passphrase", passphrase_hash
            )


class TestTokenGenerator:
    """Test TokenGenerator class."""

    def test_generate_secret_key_default(self):
        """Test default secret key generation."""
        key = TokenGenerator.generate_secret_key()

        assert len(key) == 32
        assert all(c in TokenGenerator.URL_SAFE for c in key)

    def test_generate_secret_key_custom_length(self):
        """Test secret key generation with custom length."""
        key = TokenGenerator.generate_secret_key(64)
        assert len(key) == 64

    def test_generate_secret_key_uniqueness(self):
        """Test that generated keys are unique."""
        keys = [TokenGenerator.generate_secret_key() for _ in range(100)]
        assert len(set(keys)) == 100  # All unique

    def test_generate_hex_key(self):
        """Test hex key generation."""
        key = TokenGenerator.generate_hex_key(16)

        assert len(key) == 32  # 16 bytes = 32 hex chars
        assert all(c in TokenGenerator.HEX for c in key)

    def test_generate_url_safe_token(self):
        """Test URL-safe token generation."""
        token = TokenGenerator.generate_url_safe_token(16)

        assert token
        # URL-safe base64 can include A-Za-z0-9_-
        assert all(c.isalnum() or c in "_-" for c in token)

    def test_generate_metadata_key(self):
        """Test metadata key generation."""
        key = TokenGenerator.generate_metadata_key("secret")

        assert key.startswith("secret_")
        assert len(key.split("_")[1]) == 16

    def test_generate_api_key(self):
        """Test API key generation."""
        key = TokenGenerator.generate_api_key()

        assert len(key) == 48
        assert all(c in TokenGenerator.URL_SAFE for c in key)

    def test_compare_secure_equal(self):
        """Test constant-time comparison with equal strings."""
        assert TokenGenerator.compare_secure("secret", "secret") is True

    def test_compare_secure_not_equal(self):
        """Test constant-time comparison with different strings."""
        assert TokenGenerator.compare_secure("secret", "public") is False

    def test_compare_secure_different_lengths(self):
        """Test constant-time comparison with different length strings."""
        assert TokenGenerator.compare_secure("short", "longer-string") is False
