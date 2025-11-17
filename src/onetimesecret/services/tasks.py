"""
Celery Tasks

Background tasks for OneTimeSecret.
"""

from celery import Celery
from celery.schedules import crontab

from onetimesecret.config import settings

# Create Celery instance
celery_app = Celery(
    "onetimesecret",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="cleanup_expired_secrets")
def cleanup_expired_secrets() -> dict:
    """
    Clean up expired secrets from the database.

    This task runs periodically to remove secrets that have expired.
    """
    import asyncio

    from onetimesecret.db import async_session_maker
    from onetimesecret.core.service import SecretService

    async def _cleanup():
        async with async_session_maker() as session:
            service = SecretService(session)
            count = await service.cleanup_expired_secrets()
            return count

    count = asyncio.run(_cleanup())
    return {"deleted_count": count, "status": "success"}


# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-expired-secrets": {
        "task": "cleanup_expired_secrets",
        "schedule": crontab(minute="*/15"),  # Run every 15 minutes
    },
}


if __name__ == "__main__":
    celery_app.start()
