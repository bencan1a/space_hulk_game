"""Celery application configuration."""

import logging

from celery import Celery
from celery.signals import task_failure, task_postrun, task_prerun

from .config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "space_hulk_game",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.example_task", "app.tasks.generation_tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=900,  # 15 minutes
    task_soft_time_limit=840,  # 14 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,  # 1 hour
)


@task_prerun.connect
def task_prerun_handler(task_id, task, *_args, **_kwargs):
    """Log when task starts."""
    logger.info(f"Task started: {task.name} [{task_id}]")


@task_postrun.connect
def task_postrun_handler(task_id, task, *_args, **_kwargs):
    """Log when task completes."""
    logger.info(f"Task completed: {task.name} [{task_id}]")


@task_failure.connect
def task_failure_handler(task_id, exception, *_args, **_kwargs):
    """Log when task fails."""
    logger.error(f"Task failed: {task_id} - {exception}")
