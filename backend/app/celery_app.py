"""Celery application for async task processing."""

import logging

from celery import Celery

from .config import settings

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "space_hulk_game",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)


@celery_app.task(name="app.celery_app.test_task")
def test_task() -> str:
    """
    Test task for verifying Celery is working.

    Returns:
        str: Success message
    """
    logger.info("Test task executed successfully")
    return "Test task completed"
