"""Unit tests for cryptographic utilities."""

import pytest

from onetimesecret.utils.crypto import SecretEncryption, generate_secret_key, generate_secret_id
from onetimesecret.core.exceptions import InvalidPassphraseException, EncryptionException


class TestSecretEncryption:
    """Test cases for SecretEncryption class."""

    def test_encrypt_decrypt_without_passphrase(self, encryption: SecretEncryption) -> None:
        """Test basic encryption and decryption without passphrase."""
        plaintext = "This is a secret message"

        # Encrypt
        ciphertext, salt = encryption.encrypt(plaintext)

        # Verify encrypted
        assert ciphertext != plaintext
        assert salt is None  # No passphrase means no salt

        # Decrypt
        decrypted = encryption.decrypt(ciphertext)
        assert decrypted == plaintext

    def test_encrypt_decrypt_with_passphrase(self, encryption: SecretEncryption) -> None:
        """Test encryption and decryption with passphrase."""
        plaintext = "This is a secret message"
        passphrase = "my_secure_passphrase"

        # Encrypt with passphrase
        ciphertext, salt = encryption.encrypt(plaintext, passphrase)

        # Verify encrypted and salt generated
        assert ciphertext != plaintext
        assert salt is not None

        # Decrypt with correct passphrase
        decrypted = encryption.decrypt(ciphertext, passphrase, salt)
        assert decrypted == plaintext

    def test_decrypt_with_wrong_passphrase(self, encryption: SecretEncryption) -> None:
        """Test that decryption fails with wrong passphrase."""
        plaintext = "This is a secret message"
        passphrase = "correct_passphrase"
        wrong_passphrase = "wrong_passphrase"

        # Encrypt with correct passphrase
        ciphertext, salt = encryption.encrypt(plaintext, passphrase)

        # Try to decrypt with wrong passphrase
        with pytest.raises(InvalidPassphraseException):
            encryption.decrypt(ciphertext, wrong_passphrase, salt)

    def test_decrypt_without_passphrase_when_required(
        self, encryption: SecretEncryption
    ) -> None:
        """Test that decryption fails when passphrase is required but not provided."""
        plaintext = "This is a secret message"
        passphrase = "my_passphrase"

        # Encrypt with passphrase
        ciphertext, salt = encryption.encrypt(plaintext, passphrase)

        # Try to decrypt without passphrase
        with pytest.raises((InvalidPassphraseException, EncryptionException)):
            encryption.decrypt(ciphertext)

    def test_decrypt_passphrase_protected_without_salt(
        self, encryption: SecretEncryption
    ) -> None:
        """Test that decryption fails when salt is missing for passphrase-protected secret."""
        plaintext = "This is a secret message"
        passphrase = "my_passphrase"

        # Encrypt with passphrase
        ciphertext, salt = encryption.encrypt(plaintext, passphrase)

        # Try to decrypt with passphrase but without salt
        with pytest.raises(InvalidPassphraseException):
            encryption.decrypt(ciphertext, passphrase, None)

    def test_encrypt_empty_string(self, encryption: SecretEncryption) -> None:
        """Test encryption of empty string."""
        plaintext = ""

        ciphertext, salt = encryption.encrypt(plaintext)
        decrypted = encryption.decrypt(ciphertext)

        assert decrypted == plaintext

    def test_encrypt_unicode(self, encryption: SecretEncryption) -> None:
        """Test encryption of unicode characters."""
        plaintext = "Hello 世界! 🔒🔑"

        ciphertext, salt = encryption.encrypt(plaintext)
        decrypted = encryption.decrypt(ciphertext)

        assert decrypted == plaintext

    def test_encrypt_large_text(self, encryption: SecretEncryption) -> None:
        """Test encryption of large text."""
        plaintext = "A" * 10000  # 10KB of text

        ciphertext, salt = encryption.encrypt(plaintext)
        decrypted = encryption.decrypt(ciphertext)

        assert decrypted == plaintext

    def test_different_passphrases_produce_different_ciphertexts(
        self, encryption: SecretEncryption
    ) -> None:
        """Test that different passphrases produce different ciphertexts."""
        plaintext = "Same message"
        passphrase1 = "passphrase1"
        passphrase2 = "passphrase2"

        ciphertext1, salt1 = encryption.encrypt(plaintext, passphrase1)
        ciphertext2, salt2 = encryption.encrypt(plaintext, passphrase2)

        # Different passphrases should produce different results
        assert ciphertext1 != ciphertext2
        assert salt1 != salt2


class TestCryptoUtilities:
    """Test cases for crypto utility functions."""

    def test_generate_secret_key(self) -> None:
        """Test secret key generation."""
        key1 = generate_secret_key()
        key2 = generate_secret_key()

        # Keys should be different
        assert key1 != key2

        # Keys should have reasonable length
        assert len(key1) > 20
        assert len(key2) > 20

    def test_generate_secret_key_custom_length(self) -> None:
        """Test secret key generation with custom length."""
        length = 64
        key = generate_secret_key(length)

        # Key should exist and be non-empty
        assert key
        assert len(key) > 0

    def test_generate_secret_id(self) -> None:
        """Test secret ID generation."""
        id1 = generate_secret_id()
        id2 = generate_secret_id()

        # IDs should be different
        assert id1 != id2

        # IDs should have reasonable length
        assert len(id1) > 10
        assert len(id2) > 10

    def test_secret_ids_are_url_safe(self) -> None:
        """Test that generated secret IDs are URL-safe."""
        import re

        for _ in range(10):
            secret_id = generate_secret_id()
            # URL-safe base64 uses only alphanumeric, dash, and underscore
            assert re.match(r'^[A-Za-z0-9_-]+$', secret_id)
