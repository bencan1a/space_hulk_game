"""Tests for Celery task execution."""

import sys
from pathlib import Path

import pytest
from celery.result import AsyncResult

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.celery_app import celery_app
from app.tasks.example_task import example_failure_task, simple_add


@pytest.fixture
def celery_config():
    """Celery test configuration."""
    return {
        "task_always_eager": True,  # Execute tasks synchronously for testing
        "task_eager_propagates": True,
        "broker_url": "memory://",  # Use in-memory broker for tests
        "result_backend": "cache+memory://",  # Use in-memory backend for tests
    }


@pytest.fixture(autouse=True)
def setup_celery_test_mode(celery_config):
    """Set up Celery in test mode for all tests."""
    celery_app.conf.update(celery_config)
    yield
    # Reset after test
    celery_app.conf.task_always_eager = False


def test_simple_task_execution():
    """Test basic task execution."""
    result = simple_add.apply_async(args=[4, 6])
    assert result.get() == 10


def test_task_failure_handling():
    """Test task failure is handled correctly."""
    with pytest.raises(ValueError):
        result = example_failure_task.apply_async()
        result.get()


def test_task_status_tracking():
    """Test task status can be queried."""
    result = simple_add.apply_async(args=[2, 3])

    assert result.state in ["PENDING", "SUCCESS"]
    assert result.get() == 5
    assert result.state == "SUCCESS"


def test_task_result_storage():
    """Test task results are stored and retrievable."""
    result = simple_add.apply_async(args=[10, 20])

    # In eager mode, result is immediately available
    assert result.get() == 30
    assert result.successful()
