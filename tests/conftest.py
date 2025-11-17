"""Pytest configuration and fixtures."""

import pytest
from typing import Generator
from unittest.mock import MagicMock

from onetimesecret.core.config import Settings, reset_settings
from onetimesecret.services.redis_client import SecretStorage
from onetimesecret.services.secret_service import SecretService
from onetimesecret.utils.crypto import SecretEncryption


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    reset_settings()
    return Settings(
        redis_url="redis://localhost:6379/15",  # Use test database
        secret_key="test_secret_key_for_testing_only_not_secure",
        ssl_enabled=False,
        auth_required=False,
        passphrase_required=False,
        max_secret_size=1048576,
        default_ttl=3600,
        max_ttl=86400,
        debug=True
    )


@pytest.fixture
def mock_redis() -> MagicMock:
    """Create a mock Redis client."""
    mock = MagicMock()
    mock.ping.return_value = True
    mock.setex.return_value = True
    mock.get.return_value = None
    mock.delete.return_value = 1
    mock.exists.return_value = 0
    mock.ttl.return_value = -1
    mock.pipeline.return_value = mock
    mock.execute.return_value = [1, 1]
    return mock


@pytest.fixture
def encryption(test_settings: Settings) -> SecretEncryption:
    """Create an encryption instance with test settings."""
    return SecretEncryption(test_settings.secret_key)


@pytest.fixture
def mock_storage(mock_redis: MagicMock, monkeypatch: pytest.MonkeyPatch) -> SecretStorage:
    """Create a mock storage instance."""
    storage = MagicMock(spec=SecretStorage)
    storage.client = mock_redis
    return storage


@pytest.fixture
def secret_service(
    mock_storage: SecretStorage,
    encryption: SecretEncryption,
    test_settings: Settings
) -> SecretService:
    """Create a secret service instance with mocked dependencies."""
    return SecretService(mock_storage, encryption, test_settings)


@pytest.fixture(autouse=True)
def reset_config() -> Generator[None, None, None]:
    """Reset configuration after each test."""
    yield
    reset_settings()
