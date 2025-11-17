"""
Custom Exceptions

Domain-specific exceptions for secret management.
"""


class SecretError(Exception):
    """Base exception for secret-related errors."""

    pass


class SecretNotFoundError(SecretError):
    """Raised when a secret cannot be found."""

    pass


class SecretExpiredError(SecretError):
    """Raised when a secret has expired."""

    pass


class SecretViewLimitError(SecretError):
    """Raised when a secret's view limit has been reached."""

    pass


class InvalidPassphraseError(SecretError):
    """Raised when an incorrect passphrase is provided."""

    pass


class SecretValidationError(SecretError):
    """Raised when secret validation fails."""

    pass
