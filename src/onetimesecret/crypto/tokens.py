"""
Secure Token Generation

Provides cryptographically secure random token generation for secret IDs and keys.
"""

import secrets
import string
from typing import Optional


class TokenGenerator:
    """
    Generate cryptographically secure random tokens.

    Uses the secrets module which is designed for cryptographic operations.
    """

    # Character sets for different token types
    ALPHANUMERIC = string.ascii_letters + string.digits
    ALPHANUMERIC_LOWER = string.ascii_lowercase + string.digits
    URL_SAFE = string.ascii_letters + string.digits + "-_"
    HEX = string.hexdigits.lower()

    @staticmethod
    def generate_secret_key(length: int = 32, charset: Optional[str] = None) -> str:
        """
        Generate a cryptographically secure random secret key.

        Args:
            length: Length of the generated key (default: 32)
            charset: Character set to use (default: URL_SAFE)

        Returns:
            Random string of specified length

        Examples:
            >>> key = TokenGenerator.generate_secret_key()
            >>> len(key)
            32
        """
        if charset is None:
            charset = TokenGenerator.URL_SAFE

        return "".join(secrets.choice(charset) for _ in range(length))

    @staticmethod
    def generate_hex_key(byte_length: int = 16) -> str:
        """
        Generate a hexadecimal token.

        Args:
            byte_length: Number of random bytes (default: 16)

        Returns:
            Hexadecimal string (2x byte_length characters)

        Examples:
            >>> key = TokenGenerator.generate_hex_key(16)
            >>> len(key)
            32
        """
        return secrets.token_hex(byte_length)

    @staticmethod
    def generate_url_safe_token(byte_length: int = 16) -> str:
        """
        Generate a URL-safe token.

        Args:
            byte_length: Number of random bytes (default: 16)

        Returns:
            URL-safe base64-encoded string

        Examples:
            >>> token = TokenGenerator.generate_url_safe_token()
            >>> all(c in TokenGenerator.URL_SAFE for c in token)
            True
        """
        return secrets.token_urlsafe(byte_length)

    @staticmethod
    def generate_metadata_key(prefix: str = "meta", length: int = 16) -> str:
        """
        Generate a metadata key with prefix.

        Args:
            prefix: Prefix for the key (default: "meta")
            length: Length of random portion (default: 16)

        Returns:
            Prefixed key string

        Examples:
            >>> key = TokenGenerator.generate_metadata_key("secret")
            >>> key.startswith("secret_")
            True
        """
        random_part = TokenGenerator.generate_secret_key(length, TokenGenerator.ALPHANUMERIC_LOWER)
        return f"{prefix}_{random_part}"

    @staticmethod
    def generate_api_key() -> str:
        """
        Generate an API key for authentication.

        Returns:
            48-character URL-safe API key

        Examples:
            >>> key = TokenGenerator.generate_api_key()
            >>> len(key)
            48
        """
        return TokenGenerator.generate_secret_key(48, TokenGenerator.URL_SAFE)

    @staticmethod
    def compare_secure(a: str, b: str) -> bool:
        """
        Constant-time string comparison to prevent timing attacks.

        Args:
            a: First string
            b: Second string

        Returns:
            True if strings match, False otherwise

        Examples:
            >>> TokenGenerator.compare_secure("secret", "secret")
            True
            >>> TokenGenerator.compare_secure("secret", "public")
            False
        """
        return secrets.compare_digest(a, b)
