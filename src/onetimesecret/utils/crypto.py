"""Cryptographic utilities for OneTimeSecret."""

import base64
import secrets
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

from onetimesecret.core.exceptions import EncryptionException, InvalidPassphraseException


class SecretEncryption:
    """Handles encryption and decryption of secrets with optional passphrase protection."""

    def __init__(self, app_secret_key: str):
        """
        Initialize the encryption handler.

        Args:
            app_secret_key: Application-wide secret key for base encryption
        """
        self.app_secret_key = app_secret_key.encode() if isinstance(app_secret_key, str) else app_secret_key

    def _derive_key(self, passphrase: str, salt: bytes) -> bytes:
        """
        Derive an encryption key from a passphrase using PBKDF2.

        Args:
            passphrase: User-provided passphrase
            salt: Cryptographic salt

        Returns:
            Derived encryption key
        """
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

    def _create_base_key(self) -> bytes:
        """
        Create a base encryption key from the app secret key.

        Returns:
            Base encryption key for Fernet
        """
        # Use first 32 bytes of app secret key, padded if necessary
        key_material = self.app_secret_key[:32].ljust(32, b'\0')
        return base64.urlsafe_b64encode(key_material)

    def encrypt(self, plaintext: str, passphrase: Optional[str] = None) -> tuple[str, Optional[str]]:
        """
        Encrypt secret content with optional passphrase protection.

        Args:
            plaintext: Secret content to encrypt
            passphrase: Optional user passphrase for additional encryption

        Returns:
            Tuple of (encrypted_content, salt_if_passphrase_used)

        Raises:
            EncryptionException: If encryption fails
        """
        try:
            if passphrase:
                # Generate random salt for passphrase-based encryption
                salt = secrets.token_bytes(16)
                key = self._derive_key(passphrase, salt)

                # First encrypt with passphrase-derived key
                fernet = Fernet(key)
                encrypted = fernet.encrypt(plaintext.encode())

                # Then encrypt again with app secret key for defense in depth
                app_fernet = Fernet(self._create_base_key())
                double_encrypted = app_fernet.encrypt(encrypted)

                # Return base64-encoded result and salt
                return (
                    base64.urlsafe_b64encode(double_encrypted).decode(),
                    base64.urlsafe_b64encode(salt).decode()
                )
            else:
                # Single encryption with app secret key only
                fernet = Fernet(self._create_base_key())
                encrypted = fernet.encrypt(plaintext.encode())
                return base64.urlsafe_b64encode(encrypted).decode(), None

        except Exception as e:
            raise EncryptionException(f"Failed to encrypt secret: {str(e)}")

    def decrypt(self, ciphertext: str, passphrase: Optional[str] = None, salt: Optional[str] = None) -> str:
        """
        Decrypt secret content with optional passphrase.

        Args:
            ciphertext: Encrypted secret content
            passphrase: User passphrase if secret is passphrase-protected
            salt: Salt used for passphrase-based encryption

        Returns:
            Decrypted secret content

        Raises:
            InvalidPassphraseException: If passphrase is incorrect
            EncryptionException: If decryption fails for other reasons
        """
        try:
            ciphertext_bytes = base64.urlsafe_b64decode(ciphertext.encode())

            if passphrase:
                if not salt:
                    raise InvalidPassphraseException("Salt required for passphrase-protected secrets")

                # Decode salt
                salt_bytes = base64.urlsafe_b64decode(salt.encode())

                # First decrypt with app secret key
                app_fernet = Fernet(self._create_base_key())
                once_decrypted = app_fernet.decrypt(ciphertext_bytes)

                # Then decrypt with passphrase-derived key
                key = self._derive_key(passphrase, salt_bytes)
                fernet = Fernet(key)
                plaintext = fernet.decrypt(once_decrypted)

                return plaintext.decode()
            else:
                # Single decryption with app secret key
                fernet = Fernet(self._create_base_key())
                plaintext = fernet.decrypt(ciphertext_bytes)
                return plaintext.decode()

        except InvalidToken:
            raise InvalidPassphraseException("Invalid passphrase or corrupted secret")
        except Exception as e:
            if isinstance(e, (InvalidPassphraseException, EncryptionException)):
                raise
            raise EncryptionException(f"Failed to decrypt secret: {str(e)}")


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure random key.

    Args:
        length: Length of the key in bytes

    Returns:
        URL-safe base64-encoded random key
    """
    return secrets.token_urlsafe(length)


def generate_secret_id() -> str:
    """
    Generate a unique identifier for a secret.

    Returns:
        URL-safe random identifier
    """
    return secrets.token_urlsafe(16)
