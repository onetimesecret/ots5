"""
API Routes

RESTful endpoints for secret management.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from onetimesecret.config import settings
from onetimesecret.core import (
    SecretCreate,
    SecretMetadataResponse,
    SecretResponse,
    SecretRetrieve,
    SecretService,
)
from onetimesecret.core.exceptions import (
    InvalidPassphraseError,
    SecretExpiredError,
    SecretNotFoundError,
    SecretViewLimitError,
)
from onetimesecret.db import get_db

# Create router
router = APIRouter(prefix="/api/v3", tags=["secrets"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/secrets",
    response_model=SecretResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new secret",
    description="Create a new encrypted secret with optional passphrase protection",
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def create_secret(
    request: Request,
    secret_data: SecretCreate,
    db: AsyncSession = Depends(get_db),
) -> SecretResponse:
    """
    Create a new secret.

    - **secret**: The secret content to encrypt (required)
    - **passphrase**: Optional passphrase for additional protection
    - **ttl**: Time to live in seconds (default: 3600, max: 259200)
    - **burn_after_reading**: Delete after first view (default: true)
    - **max_views**: Maximum number of views (default: 1)
    """
    service = SecretService(db)

    try:
        secret, metadata = await service.create_secret(secret_data)

        return SecretResponse(
            secret_id=secret.id,
            secret=None,  # Don't return secret on creation
            metadata_key=metadata.id,
            expires_at=secret.expires_at,
            ttl=secret.ttl,
            burn_after_reading=secret.burn_after_reading,
            created_at=secret.created_at,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create secret: {str(e)}",
        )


@router.post(
    "/secrets/{secret_id}",
    response_model=SecretResponse,
    summary="Retrieve a secret",
    description="Retrieve and decrypt a secret (burns after reading by default)",
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_secret(
    request: Request,
    secret_id: str,
    retrieve_data: Optional[SecretRetrieve] = None,
    db: AsyncSession = Depends(get_db),
) -> SecretResponse:
    """
    Retrieve a secret.

    - **secret_id**: The unique identifier of the secret
    - **passphrase**: Optional passphrase if the secret is protected

    Note: By default, secrets are deleted after retrieval (burn after reading).
    """
    service = SecretService(db)

    try:
        passphrase = retrieve_data.passphrase if retrieve_data else None
        plaintext = await service.get_secret(secret_id, passphrase=passphrase)

        # Note: We can't return the full secret object since it may be deleted
        return SecretResponse(
            secret_id=secret_id,
            secret=plaintext,
            metadata_key=None,
            expires_at=None,  # Already burned
            ttl=0,
            burn_after_reading=True,
            created_at=None,
        )

    except SecretNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found or already burned"
        )
    except SecretExpiredError:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Secret has expired")
    except SecretViewLimitError:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail="Secret view limit reached"
        )
    except InvalidPassphraseError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid passphrase"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve secret: {str(e)}",
        )


@router.get(
    "/secrets/{secret_id}/metadata",
    response_model=SecretMetadataResponse,
    summary="Get secret metadata",
    description="Get secret status without burning it",
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_secret_metadata(
    request: Request, metadata_key: str, db: AsyncSession = Depends(get_db)
) -> SecretMetadataResponse:
    """
    Get secret metadata.

    - **metadata_key**: The metadata key returned when creating the secret

    Returns information about the secret without burning it.
    """
    service = SecretService(db)

    try:
        metadata = await service.get_metadata(metadata_key)

        # Also fetch secret to get current status
        from sqlalchemy import select

        from onetimesecret.db.models import Secret

        result = await db.execute(select(Secret).where(Secret.id == metadata.secret_id))
        secret = result.scalar_one_or_none()

        if not secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found"
            )

        return SecretMetadataResponse(
            secret_id=secret.id,
            created_at=secret.created_at,
            expires_at=secret.expires_at,
            ttl=secret.ttl,
            is_expired=secret.is_expired(),
            view_count=secret.view_count,
            max_views=secret.max_views,
            can_view=secret.can_view(),
            burn_after_reading=secret.burn_after_reading,
            passphrase_required=secret.passphrase_required,
        )

    except SecretNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metadata: {str(e)}",
        )


@router.delete(
    "/secrets/{secret_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a secret",
    description="Manually delete a secret before it expires",
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def delete_secret(
    request: Request, secret_id: str, db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a secret.

    - **secret_id**: The unique identifier of the secret
    """
    service = SecretService(db)

    try:
        deleted = await service.delete_secret(secret_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this secret"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete secret: {str(e)}",
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the service is running",
    tags=["health"],
)
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}
