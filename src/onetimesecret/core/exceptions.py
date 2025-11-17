"""Custom exceptions for OneTimeSecret."""


class OTSException(Exception):
    """Base exception for all OneTimeSecret errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SecretNotFoundException(OTSException):
    """Raised when a secret is not found or has already been viewed."""

    def __init__(self, message: str = "Secret not found or already viewed"):
        super().__init__(message, status_code=404)


class SecretExpiredException(OTSException):
    """Raised when a secret has expired."""

    def __init__(self, message: str = "Secret has expired"):
        super().__init__(message, status_code=410)


class InvalidPassphraseException(OTSException):
    """Raised when an invalid passphrase is provided."""

    def __init__(self, message: str = "Invalid passphrase"):
        super().__init__(message, status_code=401)


class SecretTooLargeException(OTSException):
    """Raised when secret content exceeds maximum size."""

    def __init__(self, message: str = "Secret content exceeds maximum size"):
        super().__init__(message, status_code=413)


class InvalidTTLException(OTSException):
    """Raised when TTL value is invalid."""

    def __init__(self, message: str = "Invalid TTL value"):
        super().__init__(message, status_code=400)


class EncryptionException(OTSException):
    """Raised when encryption/decryption fails."""

    def __init__(self, message: str = "Encryption operation failed"):
        super().__init__(message, status_code=500)


class ValidationException(OTSException):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=400)


class StorageException(OTSException):
    """Raised when storage operations fail."""

    def __init__(self, message: str = "Storage operation failed"):
        super().__init__(message, status_code=500)


class AuthenticationException(OTSException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)
