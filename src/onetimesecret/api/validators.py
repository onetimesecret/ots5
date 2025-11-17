"""Input validation utilities for API endpoints."""

import re
from typing import Optional

from onetimesecret.core.exceptions import ValidationException


def validate_secret_key(secret_key: str) -> str:
    """
    Validate secret key format.

    Args:
        secret_key: Secret identifier to validate

    Returns:
        Validated secret key

    Raises:
        ValidationException: If secret key format is invalid
    """
    if not secret_key:
        raise ValidationException("Secret key cannot be empty")

    # Secret keys should be URL-safe base64 strings
    if not re.match(r'^[A-Za-z0-9_-]+$', secret_key):
        raise ValidationException("Invalid secret key format")

    if len(secret_key) > 256:
        raise ValidationException("Secret key too long")

    return secret_key


def validate_passphrase(passphrase: Optional[str], required: bool = False) -> Optional[str]:
    """
    Validate passphrase if provided.

    Args:
        passphrase: Passphrase to validate
        required: Whether passphrase is required

    Returns:
        Validated passphrase

    Raises:
        ValidationException: If passphrase is invalid
    """
    if required and not passphrase:
        raise ValidationException("Passphrase is required")

    if passphrase:
        if len(passphrase) < 4:
            raise ValidationException("Passphrase must be at least 4 characters")

        if len(passphrase) > 256:
            raise ValidationException("Passphrase too long (max 256 characters)")

    return passphrase


def sanitize_input(input_str: str, max_length: int = 1048576) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized input

    Raises:
        ValidationException: If input is invalid
    """
    if not isinstance(input_str, str):
        raise ValidationException("Input must be a string")

    if len(input_str) > max_length:
        raise ValidationException(f"Input exceeds maximum length of {max_length}")

    # Remove null bytes which could cause issues
    sanitized = input_str.replace('\0', '')

    return sanitized
