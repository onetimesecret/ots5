"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from onetimesecret.api.routes import router
from onetimesecret.core.config import get_settings
from onetimesecret.core.exceptions import OTSException
from onetimesecret.services.redis_client import SecretStorage
from onetimesecret.services.secret_service import SecretService
from onetimesecret.utils.crypto import SecretEncryption


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    print(f"Starting OneTimeSecret API on {settings.host}:{settings.port}")
    print(f"Redis URL: {settings.redis_url}")
    print(f"API Prefix: {settings.api_prefix}")

    # Initialize shared service instances
    storage = SecretStorage(settings.redis_url)
    encryption = SecretEncryption(settings.secret_key)
    secret_service = SecretService(storage, encryption, settings)

    # Store in app state for dependency injection
    app.state.storage = storage
    app.state.encryption = encryption
    app.state.secret_service = secret_service

    yield

    # Shutdown - clean up resources
    print("Shutting down OneTimeSecret API")
    storage.close()


# Create FastAPI application
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance
    """
    settings = get_settings()

    app = FastAPI(
        title="OneTimeSecret",
        description="Secure one-time secret sharing service",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handler for custom exceptions
    @app.exception_handler(OTSException)
    async def ots_exception_handler(request: Request, exc: OTSException) -> JSONResponse:
        """Handle custom OTS exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    # Include API routes
    app.include_router(router)

    # Root endpoint
    @app.get("/")
    async def root() -> dict:
        """Root endpoint with API information."""
        return {
            "service": "OneTimeSecret",
            "version": "1.0.0",
            "api_docs": "/docs",
            "api_prefix": settings.api_prefix
        }

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "onetimesecret.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
