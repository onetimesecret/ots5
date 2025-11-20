"""API routes for OneTimeSecret."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from onetimesecret.core.exceptions import OTSException
from onetimesecret.models.secret import (
    SecretCreate,
    SecretResponse,
    SecretContent,
    SecretMetadataResponse,
    SecretRetrieve,
)
from onetimesecret.services.secret_service import SecretService
from onetimesecret.api.validators import validate_secret_key


# Dependency for getting the secret service
def get_secret_service(request: Request) -> SecretService:
    """
    Retrieve the SecretService instance from application state.

    Args:
        request: FastAPI request object

    Returns:
        Configured SecretService instance from app state
    """
    return request.app.state.secret_service


# Create API router
router = APIRouter(prefix="/api/v2", tags=["secrets"])


@router.post(
    "/secrets",
    response_model=SecretResponse,
    status_code=201,
    summary="Create a new secret",
    description="Create a new one-time secret that will be automatically destroyed after viewing"
)
async def create_secret(
    secret_data: SecretCreate,
    service: SecretService = Depends(get_secret_service)
) -> SecretResponse:
    """
    Create a new one-time secret.

    Args:
        secret_data: Secret creation request
        service: Secret service instance

    Returns:
        Secret response with key and metadata

    Raises:
        HTTPException: On validation or creation errors
    """
    try:
        return service.create_secret(secret_data)
    except OTSException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/secrets/{secret_key}",
    response_model=SecretContent,
    summary="Retrieve a secret",
    description="Retrieve and automatically destroy a one-time secret"
)
async def retrieve_secret(
    secret_key: str,
    retrieve_data: SecretRetrieve,
    service: SecretService = Depends(get_secret_service)
) -> SecretContent:
    """
    Retrieve and destroy a one-time secret.

    Args:
        secret_key: Unique secret identifier
        retrieve_data: Retrieval request with optional passphrase
        service: Secret service instance

    Returns:
        Decrypted secret content

    Raises:
        HTTPException: If secret not found or passphrase invalid
    """
    try:
        # Validate secret key format
        secret_key = validate_secret_key(secret_key)

        # Retrieve the secret
        return service.retrieve_secret(secret_key, retrieve_data.passphrase)
    except OTSException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/secrets/{secret_key}",
    response_model=SecretContent,
    summary="Retrieve a secret (GET)",
    description="Retrieve and automatically destroy a one-time secret using GET with passphrase in query"
)
async def retrieve_secret_get(
    secret_key: str,
    passphrase: Optional[str] = Query(None, description="Passphrase for protected secrets"),
    service: SecretService = Depends(get_secret_service)
) -> SecretContent:
    """
    Retrieve and destroy a one-time secret using GET method.

    Args:
        secret_key: Unique secret identifier
        passphrase: Optional passphrase for protected secrets
        service: Secret service instance

    Returns:
        Decrypted secret content

    Raises:
        HTTPException: If secret not found or passphrase invalid
    """
    try:
        # Validate secret key format
        secret_key = validate_secret_key(secret_key)

        # Retrieve the secret
        return service.retrieve_secret(secret_key, passphrase)
    except OTSException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/secrets/{secret_key}/metadata",
    response_model=SecretMetadataResponse,
    summary="Get secret metadata",
    description="Retrieve metadata about a secret without destroying it"
)
async def get_secret_metadata(
    secret_key: str,
    service: SecretService = Depends(get_secret_service)
) -> SecretMetadataResponse:
    """
    Get metadata for a secret without destroying it.

    Args:
        secret_key: Unique secret identifier
        service: Secret service instance

    Returns:
        Secret metadata

    Raises:
        HTTPException: If secret not found
    """
    try:
        # Validate secret key format
        secret_key = validate_secret_key(secret_key)

        return service.get_metadata(secret_key)
    except OTSException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete(
    "/secrets/{secret_key}",
    status_code=204,
    summary="Delete a secret",
    description="Manually delete a secret before it's viewed or expires"
)
async def delete_secret(
    secret_key: str,
    service: SecretService = Depends(get_secret_service)
) -> None:
    """
    Manually delete a secret.

    Args:
        secret_key: Unique secret identifier
        service: Secret service instance

    Raises:
        HTTPException: If secret not found
    """
    try:
        # Validate secret key format
        secret_key = validate_secret_key(secret_key)

        deleted = service.delete_secret(secret_key)
        if not deleted:
            raise HTTPException(status_code=404, detail="Secret not found")

    except OTSException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/status",
    summary="Health check",
    description="Check if the API is running"
)
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        Status information
    """
    return {
        "status": "ok",
        "service": "OneTimeSecret",
        "version": "1.0.0"
    }
