"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from onetimesecret.main import create_app
from onetimesecret.core.config import get_settings


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_service():
    """Create a mock secret service."""
    with patch("onetimesecret.api.routes.get_secret_service") as mock:
        service = MagicMock()
        mock.return_value = service
        yield service


class TestHealthEndpoint:
    """Test cases for health check endpoint."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test root endpoint returns service information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "OneTimeSecret"
        assert "version" in data

    def test_health_check(self, client: TestClient) -> None:
        """Test health check endpoint."""
        response = client.get("/api/v2/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestCreateSecret:
    """Test cases for creating secrets."""

    def test_create_secret_basic(self, client: TestClient, mock_service) -> None:
        """Test creating a basic secret."""
        from datetime import datetime
        from onetimesecret.models.secret import SecretResponse

        # Mock service response
        mock_service.create_secret.return_value = SecretResponse(
            secret_key="test_key_123",
            metadata_key="test_key_123:metadata",
            ttl=3600,
            created_at=datetime.utcnow()
        )

        response = client.post(
            "/api/v2/secrets",
            json={"secret": "Test secret", "ttl": 3600}
        )

        assert response.status_code == 201
        data = response.json()
        assert "secret_key" in data
        assert data["ttl"] == 3600

    def test_create_secret_with_passphrase(
        self, client: TestClient, mock_service
    ) -> None:
        """Test creating a secret with passphrase."""
        from datetime import datetime
        from onetimesecret.models.secret import SecretResponse

        mock_service.create_secret.return_value = SecretResponse(
            secret_key="test_key_456",
            metadata_key="test_key_456:metadata",
            ttl=7200,
            created_at=datetime.utcnow()
        )

        response = client.post(
            "/api/v2/secrets",
            json={
                "secret": "Protected secret",
                "passphrase": "my_password",
                "ttl": 7200
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "secret_key" in data

    def test_create_secret_validation_error(
        self, client: TestClient, mock_service
    ) -> None:
        """Test that invalid input returns validation error."""
        response = client.post(
            "/api/v2/secrets",
            json={}  # Missing required 'secret' field
        )

        assert response.status_code == 422  # Validation error

    def test_create_secret_too_large(self, client: TestClient, mock_service) -> None:
        """Test that creating too large secret returns error."""
        from onetimesecret.core.exceptions import SecretTooLargeException

        mock_service.create_secret.side_effect = SecretTooLargeException()

        response = client.post(
            "/api/v2/secrets",
            json={"secret": "A" * 2000000}  # Very large secret
        )

        assert response.status_code == 413


class TestRetrieveSecret:
    """Test cases for retrieving secrets."""

    def test_retrieve_secret_post(self, client: TestClient, mock_service) -> None:
        """Test retrieving a secret using POST method."""
        from datetime import datetime
        from onetimesecret.models.secret import SecretContent

        mock_service.retrieve_secret.return_value = SecretContent(
            secret="Test secret message",
            created_at=datetime.utcnow()
        )

        response = client.post(
            "/api/v2/secrets/test_key_123",
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["secret"] == "Test secret message"

    def test_retrieve_secret_get(self, client: TestClient, mock_service) -> None:
        """Test retrieving a secret using GET method."""
        from datetime import datetime
        from onetimesecret.models.secret import SecretContent

        mock_service.retrieve_secret.return_value = SecretContent(
            secret="Test secret message",
            created_at=datetime.utcnow()
        )

        response = client.get("/api/v2/secrets/test_key_123")

        assert response.status_code == 200
        data = response.json()
        assert data["secret"] == "Test secret message"

    def test_retrieve_secret_with_passphrase(
        self, client: TestClient, mock_service
    ) -> None:
        """Test retrieving a passphrase-protected secret."""
        from datetime import datetime
        from onetimesecret.models.secret import SecretContent

        mock_service.retrieve_secret.return_value = SecretContent(
            secret="Protected message",
            created_at=datetime.utcnow()
        )

        response = client.post(
            "/api/v2/secrets/test_key_456",
            json={"passphrase": "my_password"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["secret"] == "Protected message"

    def test_retrieve_secret_not_found(self, client: TestClient, mock_service) -> None:
        """Test retrieving a non-existent secret."""
        from onetimesecret.core.exceptions import SecretNotFoundException

        mock_service.retrieve_secret.side_effect = SecretNotFoundException()

        response = client.get("/api/v2/secrets/nonexistent")

        assert response.status_code == 404

    def test_retrieve_secret_wrong_passphrase(
        self, client: TestClient, mock_service
    ) -> None:
        """Test retrieving with wrong passphrase."""
        from onetimesecret.core.exceptions import InvalidPassphraseException

        mock_service.retrieve_secret.side_effect = InvalidPassphraseException()

        response = client.post(
            "/api/v2/secrets/test_key",
            json={"passphrase": "wrong_password"}
        )

        assert response.status_code == 401

    def test_retrieve_secret_invalid_key_format(
        self, client: TestClient, mock_service
    ) -> None:
        """Test retrieving with invalid secret key format."""
        from onetimesecret.core.exceptions import ValidationException

        # Use a key with invalid characters
        response = client.get("/api/v2/secrets/invalid@key!")

        # Should get validation error
        assert response.status_code in [400, 422]


class TestSecretMetadata:
    """Test cases for secret metadata endpoint."""

    def test_get_metadata(self, client: TestClient, mock_service) -> None:
        """Test getting secret metadata."""
        from datetime import datetime
        from onetimesecret.models.secret import SecretMetadataResponse

        mock_service.get_metadata.return_value = SecretMetadataResponse(
            secret_key="test_key",
            created_at=datetime.utcnow(),
            ttl=3600,
            viewed=False,
            has_passphrase=True
        )

        response = client.get("/api/v2/secrets/test_key/metadata")

        assert response.status_code == 200
        data = response.json()
        assert data["secret_key"] == "test_key"
        assert data["ttl"] == 3600
        assert data["viewed"] is False
        assert data["has_passphrase"] is True

    def test_get_metadata_not_found(self, client: TestClient, mock_service) -> None:
        """Test getting metadata for non-existent secret."""
        from onetimesecret.core.exceptions import SecretNotFoundException

        mock_service.get_metadata.side_effect = SecretNotFoundException()

        response = client.get("/api/v2/secrets/nonexistent/metadata")

        assert response.status_code == 404


class TestDeleteSecret:
    """Test cases for deleting secrets."""

    def test_delete_secret(self, client: TestClient, mock_service) -> None:
        """Test deleting a secret."""
        mock_service.delete_secret.return_value = True

        response = client.delete("/api/v2/secrets/test_key")

        assert response.status_code == 204

    def test_delete_secret_not_found(self, client: TestClient, mock_service) -> None:
        """Test deleting a non-existent secret."""
        mock_service.delete_secret.return_value = False

        response = client.delete("/api/v2/secrets/nonexistent")

        assert response.status_code == 404
