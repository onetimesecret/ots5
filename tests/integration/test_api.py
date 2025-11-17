"""
Integration Tests for API Endpoints

Tests for the complete API functionality.
"""

import pytest
from httpx import AsyncClient


class TestSecretsAPI:
    """Test secrets API endpoints."""

    @pytest.mark.asyncio
    async def test_create_secret(self, client: AsyncClient, sample_secret: str):
        """Test creating a new secret."""
        response = await client.post(
            "/api/v3/secrets",
            json={
                "secret": sample_secret,
                "ttl": 3600,
                "burn_after_reading": True,
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert "secret_id" in data
        assert "metadata_key" in data
        assert "expires_at" in data
        assert data["ttl"] == 3600
        assert data["burn_after_reading"] is True
        # Secret should not be returned on creation
        assert data["secret"] is None

    @pytest.mark.asyncio
    async def test_create_secret_with_passphrase(
        self, client: AsyncClient, sample_secret: str, sample_passphrase: str
    ):
        """Test creating a secret with passphrase protection."""
        response = await client.post(
            "/api/v3/secrets",
            json={
                "secret": sample_secret,
                "passphrase": sample_passphrase,
                "ttl": 3600,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "secret_id" in data

    @pytest.mark.asyncio
    async def test_create_and_retrieve_secret(
        self, client: AsyncClient, sample_secret: str
    ):
        """Test creating and retrieving a secret."""
        # Create secret
        create_response = await client.post(
            "/api/v3/secrets",
            json={"secret": sample_secret, "ttl": 3600},
        )
        assert create_response.status_code == 201
        secret_id = create_response.json()["secret_id"]

        # Retrieve secret
        retrieve_response = await client.post(f"/api/v3/secrets/{secret_id}")
        assert retrieve_response.status_code == 200

        data = retrieve_response.json()
        assert data["secret"] == sample_secret
        assert data["secret_id"] == secret_id

    @pytest.mark.asyncio
    async def test_retrieve_secret_with_passphrase(
        self, client: AsyncClient, sample_secret: str, sample_passphrase: str
    ):
        """Test retrieving a passphrase-protected secret."""
        # Create secret with passphrase
        create_response = await client.post(
            "/api/v3/secrets",
            json={
                "secret": sample_secret,
                "passphrase": sample_passphrase,
                "ttl": 3600,
            },
        )
        secret_id = create_response.json()["secret_id"]

        # Retrieve with correct passphrase
        retrieve_response = await client.post(
            f"/api/v3/secrets/{secret_id}",
            json={"passphrase": sample_passphrase},
        )
        assert retrieve_response.status_code == 200
        assert retrieve_response.json()["secret"] == sample_secret

    @pytest.mark.asyncio
    async def test_retrieve_secret_wrong_passphrase(
        self, client: AsyncClient, sample_secret: str
    ):
        """Test retrieving with wrong passphrase fails."""
        # Create secret with passphrase
        create_response = await client.post(
            "/api/v3/secrets",
            json={
                "secret": sample_secret,
                "passphrase": "correct-passphrase",
                "ttl": 3600,
            },
        )
        secret_id = create_response.json()["secret_id"]

        # Try to retrieve with wrong passphrase
        retrieve_response = await client.post(
            f"/api/v3/secrets/{secret_id}",
            json={"passphrase": "wrong-passphrase"},
        )
        assert retrieve_response.status_code == 401

    @pytest.mark.asyncio
    async def test_burn_after_reading(self, client: AsyncClient, sample_secret: str):
        """Test that secret is deleted after first read."""
        # Create secret with burn_after_reading=True
        create_response = await client.post(
            "/api/v3/secrets",
            json={
                "secret": sample_secret,
                "ttl": 3600,
                "burn_after_reading": True,
            },
        )
        secret_id = create_response.json()["secret_id"]

        # First retrieval should succeed
        first_response = await client.post(f"/api/v3/secrets/{secret_id}")
        assert first_response.status_code == 200

        # Second retrieval should fail (secret burned)
        second_response = await client.post(f"/api/v3/secrets/{secret_id}")
        assert second_response.status_code == 404

    @pytest.mark.asyncio
    async def test_retrieve_nonexistent_secret(self, client: AsyncClient):
        """Test retrieving a nonexistent secret returns 404."""
        response = await client.post("/api/v3/secrets/nonexistent-id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_secret(self, client: AsyncClient, sample_secret: str):
        """Test manually deleting a secret."""
        # Create secret
        create_response = await client.post(
            "/api/v3/secrets",
            json={"secret": sample_secret, "ttl": 3600},
        )
        secret_id = create_response.json()["secret_id"]

        # Delete secret
        delete_response = await client.delete(f"/api/v3/secrets/{secret_id}")
        assert delete_response.status_code == 204

        # Verify it's deleted
        retrieve_response = await client.post(f"/api/v3/secrets/{secret_id}")
        assert retrieve_response.status_code == 404

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/api/v3/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestValidation:
    """Test input validation."""

    @pytest.mark.asyncio
    async def test_create_secret_empty_content(self, client: AsyncClient):
        """Test creating a secret with empty content fails."""
        response = await client.post(
            "/api/v3/secrets",
            json={"secret": "", "ttl": 3600},
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_secret_invalid_ttl(self, client: AsyncClient):
        """Test creating a secret with invalid TTL fails."""
        response = await client.post(
            "/api/v3/secrets",
            json={"secret": "test", "ttl": 999999999},  # Too large
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_secret_negative_ttl(self, client: AsyncClient):
        """Test creating a secret with negative TTL fails."""
        response = await client.post(
            "/api/v3/secrets",
            json={"secret": "test", "ttl": -100},
        )
        assert response.status_code == 422
