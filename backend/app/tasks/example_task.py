"""Example Celery task for testing."""

import time
from typing import Any

from celery import Task

from ..celery_app import celery_app


class CallbackTask(Task):
    """Base task with callback support for progress tracking."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute task with progress tracking."""
        return super().__call__(*args, **kwargs)


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="app.tasks.example_task",
    max_retries=3,
    default_retry_delay=60,
)
def example_long_task(self, duration: int = 10) -> dict[str, Any]:
    """
    Example long-running task with progress tracking.

    Args:
        duration: How long the task should run (seconds)

    Returns:
        dict: Task result with status and data

    Raises:
        Exception: If task fails
    """
    try:
        total_steps = 5
        for i in range(total_steps):
            # Update task progress
            progress = int((i + 1) / total_steps * 100)
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": i + 1,
                    "total": total_steps,
                    "progress": progress,
                    "status": f"Processing step {i + 1}/{total_steps}",
                },
            )

            # Simulate work
            time.sleep(duration / total_steps)

        return {
            "status": "complete",
            "result": f"Task completed successfully after {duration} seconds",
            "data": {"steps_completed": total_steps},
        }

    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2**self.request.retries) from exc


@celery_app.task(name="app.tasks.example_failure_task")
def example_failure_task() -> None:
    """Example task that always fails (for testing error handling)."""
    raise ValueError("This task intentionally fails")


@celery_app.task(name="app.tasks.simple_add")
def simple_add(x: int, y: int) -> int:
    """Simple addition task for basic testing."""
    return x + y
