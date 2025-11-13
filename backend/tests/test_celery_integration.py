"""Integration tests for Celery with FastAPI."""

import asyncio
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.celery_app import celery_app
from app.main import app


@pytest.fixture(autouse=True)
def setup_celery_eager_mode():
    """Set up Celery in eager mode for integration tests."""
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    celery_app.conf.broker_url = "memory://"
    celery_app.conf.result_backend = "cache+memory://"
    yield
    celery_app.conf.task_always_eager = False
    celery_app.conf.task_eager_propagates = False


@pytest.mark.asyncio
async def test_trigger_task_via_api():
    """Test triggering Celery task through API endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/tasks/example?duration=1")
        assert response.status_code == 200

        data = response.json()
        assert "task_id" in data
        assert data["status"] == "started"


@pytest.mark.asyncio
async def test_check_task_status_via_api():
    """Test checking task status through API endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Trigger task
        response = await client.post("/api/v1/tasks/example?duration=1")
        task_id = response.json()["task_id"]

        # Wait a bit for eager mode to complete
        await asyncio.sleep(0.1)

        # Check status
        status_response = await client.get(f"/api/v1/tasks/{task_id}/status")
        assert status_response.status_code == 200

        status_data = status_response.json()
        assert "state" in status_data
        # In eager mode, task completes immediately
        assert status_data["state"] in ["PENDING", "PROGRESS", "SUCCESS"]
