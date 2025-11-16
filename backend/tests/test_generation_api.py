"""Tests for generation API endpoints."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.models.session import Session as SessionModel


@pytest.mark.asyncio
async def test_start_generation_success(db_session):  # noqa: ARG001 - fixture needed for dependency override
    """Test starting a generation task with valid prompt."""
    transport = ASGITransport(app=app)

    # Mock the Celery task to avoid actual task execution
    with patch("app.tasks.generation_tasks.run_generation_crew") as mock_task:
        mock_task.apply_async = MagicMock()

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/generate",
                json={
                    "prompt": "Create a horror story with body horror and isolation themes in the grimdark universe",
                },
            )

            assert response.status_code == 201
            data = response.json()
            assert "session_id" in data
            assert data["status"] == "pending"
            assert data["message"] == "Generation task started successfully"
            assert len(data["session_id"]) == 36  # UUID format


@pytest.mark.asyncio
async def test_start_generation_with_template(db_session):  # noqa: ARG001
    """Test starting a generation task with template_id."""
    transport = ASGITransport(app=app)

    with patch("app.tasks.generation_tasks.run_generation_crew") as mock_task:
        mock_task.apply_async = MagicMock()

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/generate",
                json={
                    "prompt": "Create a horror story with body horror and isolation themes in the grimdark universe",
                    "template_id": "horror_exploration",
                },
            )

            assert response.status_code == 201
            data = response.json()
            assert "session_id" in data
            assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_start_generation_invalid_prompt_too_short(db_session):  # noqa: ARG001
    """Test that prompts shorter than 50 characters are rejected."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test with prompt shorter than 50 characters
        response = await client.post(
            "/api/v1/generate",
            json={
                "prompt": "Too short",
            },
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_start_generation_invalid_prompt_empty(db_session):  # noqa: ARG001
    """Test that empty prompts are rejected."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/generate",
            json={
                "prompt": "",
            },
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_start_generation_invalid_prompt_too_long(db_session):  # noqa: ARG001
    """Test that prompts longer than 5000 characters are rejected."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a prompt longer than 5000 characters
        long_prompt = "A" * 5001

        response = await client.post(
            "/api/v1/generate",
            json={
                "prompt": long_prompt,
            },
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_start_generation_missing_prompt(db_session):  # noqa: ARG001
    """Test that missing prompt field is rejected."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/generate",
            json={},
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_get_generation_status_success(db_session):
    """Test getting status of an existing generation session."""
    # Create a session directly
    session = SessionModel(
        id="test-session-123",
        status="running",
        progress_percent=50,
        current_step="Generating story content",
    )
    db_session.add(session)
    db_session.commit()

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/generate/test-session-123")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"
        assert data["status"] == "running"
        assert data["progress_percent"] == 50
        assert data["current_step"] == "Generating story content"
        assert data["error_message"] is None
        assert data["story_id"] is None


@pytest.mark.asyncio
async def test_get_generation_status_completed(db_session):
    """Test getting status of a completed generation session."""
    # Create a completed session
    session = SessionModel(
        id="completed-session",
        status="completed",
        progress_percent=100,
        current_step="Finished",
        story_id=42,
    )
    db_session.add(session)
    db_session.commit()

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/generate/completed-session")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "completed-session"
        assert data["status"] == "completed"
        assert data["progress_percent"] == 100
        assert data["story_id"] == 42


@pytest.mark.asyncio
async def test_get_generation_status_failed(db_session):
    """Test getting status of a failed generation session."""
    # Create a failed session
    session = SessionModel(
        id="failed-session",
        status="failed",
        progress_percent=25,
        current_step="Story generation",
        error_message="Failed to generate content",
    )
    db_session.add(session)
    db_session.commit()

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/generate/failed-session")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "failed-session"
        assert data["status"] == "failed"
        assert data["progress_percent"] == 25
        assert data["error_message"] == "Failed to generate content"


@pytest.mark.asyncio
async def test_get_generation_status_not_found(db_session):  # noqa: ARG001
    """Test getting status of a non-existent session."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/generate/nonexistent-session-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_start_and_poll_generation(db_session):  # noqa: ARG001
    """Integration test: Start a generation and poll for status."""
    transport = ASGITransport(app=app)

    with patch("app.tasks.generation_tasks.run_generation_crew") as mock_task:
        mock_task.apply_async = MagicMock()

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Step 1: Start generation
            start_response = await client.post(
                "/api/v1/generate",
                json={
                    "prompt": "Create a horror story with body horror and isolation themes in the grimdark universe",
                    "template_id": "horror_exploration",
                },
            )

            assert start_response.status_code == 201
            start_data = start_response.json()
            session_id = start_data["session_id"]

            # Step 2: Poll for status
            status_response = await client.get(f"/api/v1/generate/{session_id}")

            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["session_id"] == session_id
            assert status_data["status"] == "pending"
            assert status_data["progress_percent"] == 0
            assert status_data["current_step"] is None
