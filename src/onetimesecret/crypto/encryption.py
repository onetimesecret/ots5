"""
Secret Encryption Module

Uses Fernet symmetric encryption (AES-128-CBC with HMAC) from the cryptography library.
Fernet is a secure, authenticated encryption scheme that includes:
- AES encryption in CBC mode
- HMAC for authentication
- Automatic IV generation
- Timestamp support
"""

import hashlib
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Tuple

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.hash import argon2


class EncryptionError(Exception):
    """Raised when encryption operations fail."""

    pass


class DecryptionError(Exception):
    """Raised when decryption operations fail."""

    pass


class SecretEncryption:
    """
    Handles encryption and decryption of secrets using Fernet symmetric encryption.

    Features:
    - AES-128-CBC encryption
    - HMAC authentication
    - Automatic IV generation
    - Key derivation from master secret
    """

    def __init__(self, master_key: str):
        """
        Initialize encryption with a master key.

        Args:
            master_key: Master secret key (minimum 32 bytes)

        Raises:
            ValueError: If master key is too short
        """
        if len(master_key) < 32:
            raise ValueError("Master key must be at least 32 characters")
        self._master_key = master_key.encode()

    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive an encryption key from the master key using PBKDF2.

        Args:
            salt: Random salt for key derivation

        Returns:
            32-byte derived key suitable for Fernet
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return urlsafe_b64encode(kdf.derive(self._master_key))

    def encrypt(self, plaintext: str) -> Tuple[str, str]:
        """
        Encrypt plaintext data.

        Args:
            plaintext: Data to encrypt

        Returns:
            Tuple of (ciphertext, salt) both base64-encoded

        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Generate random salt for this secret
            salt = secrets.token_bytes(16)

            # Derive encryption key
            key = self._derive_key(salt)

            # Create Fernet instance and encrypt
            f = Fernet(key)
            ciphertext = f.encrypt(plaintext.encode())

            # Return base64-encoded ciphertext and salt
            return (
                urlsafe_b64encode(ciphertext).decode("utf-8"),
                urlsafe_b64encode(salt).decode("utf-8"),
            )

        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}") from e

    def decrypt(self, ciphertext: str, salt: str) -> str:
        """
        Decrypt ciphertext data.

        Args:
            ciphertext: Base64-encoded encrypted data
            salt: Base64-encoded salt used during encryption

        Returns:
            Decrypted plaintext

        Raises:
            DecryptionError: If decryption fails or data is invalid
        """
        try:
            # Decode inputs
            ciphertext_bytes = urlsafe_b64decode(ciphertext.encode())
            salt_bytes = urlsafe_b64decode(salt.encode())

            # Derive the same encryption key
            key = self._derive_key(salt_bytes)

            # Decrypt
            f = Fernet(key)
            plaintext_bytes = f.decrypt(ciphertext_bytes)

            return plaintext_bytes.decode("utf-8")

        except InvalidToken as e:
            raise DecryptionError("Invalid ciphertext or key") from e
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {str(e)}") from e

    @staticmethod
    def hash_metadata(data: str) -> str:
        """
        Create SHA-256 hash of metadata for secure storage without revealing content.

        Args:
            data: Data to hash

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(data.encode()).hexdigest()

    def encrypt_with_passphrase(
        self, plaintext: str, passphrase: str
    ) -> Tuple[str, str, str]:
        """
        Encrypt data with an additional passphrase layer.

        Args:
            plaintext: Data to encrypt
            passphrase: Additional passphrase for protection

        Returns:
            Tuple of (ciphertext, salt, passphrase_hash)

        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # First encrypt with master key
            ciphertext, salt = self.encrypt(plaintext)

            # Hash the passphrase using Argon2 (secure password hashing)
            passphrase_hash = argon2.hash(passphrase)

            return ciphertext, salt, passphrase_hash

        except Exception as e:
            raise EncryptionError(f"Passphrase encryption failed: {str(e)}") from e

    def decrypt_with_passphrase(
        self, ciphertext: str, salt: str, passphrase: str, stored_hash: str
    ) -> str:
        """
        Decrypt data protected with a passphrase.

        Args:
            ciphertext: Encrypted data
            salt: Encryption salt
            passphrase: User-provided passphrase
            stored_hash: Stored hash of the correct passphrase

        Returns:
            Decrypted plaintext

        Raises:
            DecryptionError: If passphrase is incorrect or decryption fails
        """
        # Verify passphrase using Argon2 (constant-time comparison built-in)
        try:
            argon2.verify(passphrase, stored_hash)
        except Exception:
            raise DecryptionError("Incorrect passphrase")

        # Decrypt data
        return self.decrypt(ciphertext, salt)
