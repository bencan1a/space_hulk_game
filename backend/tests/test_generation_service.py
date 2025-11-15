"""Tests for generation service."""

from unittest.mock import MagicMock, patch

import pytest
from app.models.session import Session as SessionModel
from app.services.generation_service import GenerationService


def test_start_generation_creates_session(db_session):
    """Test that start_generation creates a session record."""
    service = GenerationService(db_session)
    prompt = "Create a horror story with body horror and isolation themes in the grimdark universe"

    # Mock the Celery task to avoid actual task execution
    with patch("app.tasks.generation_tasks.run_generation_crew") as mock_task:
        mock_task.apply_async = MagicMock()

        session_id = service.start_generation(prompt)

        # Verify session was created
        assert session_id is not None
        assert len(session_id) == 36  # UUID format

        # Verify session in database
        session = service.get_session(session_id)
        assert session is not None
        assert session.status == "pending"
        assert session.progress_percent == 0
        assert session.current_step is None

        # Verify task was enqueued
        mock_task.apply_async.assert_called_once()
        call_args = mock_task.apply_async.call_args
        assert call_args[1]["args"][0] == session_id
        assert call_args[1]["args"][1] == prompt
        assert call_args[1]["task_id"] == session_id


def test_start_generation_with_template(db_session):
    """Test start_generation with template_id."""
    service = GenerationService(db_session)
    prompt = "Create a horror story with body horror and isolation themes in the grimdark universe"
    template_id = "horror_exploration"

    with patch("app.tasks.generation_tasks.run_generation_crew") as mock_task:
        mock_task.apply_async = MagicMock()

        session_id = service.start_generation(prompt, template_id)

        assert session_id is not None

        # Verify template_id was passed to task
        call_args = mock_task.apply_async.call_args
        assert call_args[1]["args"][2] == template_id


def test_start_generation_validates_prompt_length(db_session):
    """Test that start_generation validates prompt length."""
    service = GenerationService(db_session)

    # Test empty prompt
    with pytest.raises(ValueError, match="at least 50 characters"):
        service.start_generation("")

    # Test short prompt
    with pytest.raises(ValueError, match="at least 50 characters"):
        service.start_generation("Too short")


def test_get_session(db_session):
    """Test getting session by ID."""
    service = GenerationService(db_session)

    # Create a session directly
    session = SessionModel(
        id="test-session-123",
        status="running",
        progress_percent=50,
        current_step="Processing",
    )
    db_session.add(session)
    db_session.commit()

    # Retrieve it
    retrieved = service.get_session("test-session-123")

    assert retrieved is not None
    assert retrieved.id == "test-session-123"
    assert retrieved.status == "running"
    assert retrieved.progress_percent == 50


def test_get_nonexistent_session(db_session):
    """Test getting nonexistent session returns None."""
    service = GenerationService(db_session)

    result = service.get_session("nonexistent-session")

    assert result is None


def test_update_session_status(db_session):
    """Test updating session status."""
    service = GenerationService(db_session)

    # Create session
    session = SessionModel(
        id="test-session-456",
        status="pending",
        progress_percent=0,
    )
    db_session.add(session)
    db_session.commit()

    # Update status
    updated = service.update_session("test-session-456", status="running")

    assert updated is not None
    assert updated.status == "running"


def test_update_session_progress(db_session):
    """Test updating session progress."""
    service = GenerationService(db_session)

    # Create session
    session = SessionModel(
        id="test-session-789",
        status="running",
        progress_percent=0,
    )
    db_session.add(session)
    db_session.commit()

    # Update progress
    updated = service.update_session(
        "test-session-789",
        current_step="Processing scene creation",
        progress_percent=45,
    )

    assert updated is not None
    assert updated.current_step == "Processing scene creation"
    assert updated.progress_percent == 45


def test_update_session_clamps_progress(db_session):
    """Test that update_session clamps progress to 0-100."""
    service = GenerationService(db_session)

    # Create session
    session = SessionModel(
        id="test-session-clamp",
        status="running",
        progress_percent=50,
    )
    db_session.add(session)
    db_session.commit()

    # Test clamping to 100
    updated = service.update_session("test-session-clamp", progress_percent=150)
    assert updated.progress_percent == 100

    # Test clamping to 0
    updated = service.update_session("test-session-clamp", progress_percent=-10)
    assert updated.progress_percent == 0


def test_update_session_completion(db_session):
    """Test updating session to completed sets timestamp."""
    service = GenerationService(db_session)

    # Create session
    session = SessionModel(
        id="test-session-complete",
        status="running",
        progress_percent=90,
    )
    db_session.add(session)
    db_session.commit()

    assert session.completed_at is None

    # Update to completed
    updated = service.update_session(
        "test-session-complete",
        status="completed",
        progress_percent=100,
        story_id=123,
    )

    assert updated is not None
    assert updated.status == "completed"
    assert updated.progress_percent == 100
    assert updated.story_id == 123
    assert updated.completed_at is not None


def test_update_session_failure(db_session):
    """Test updating session to failed with error message."""
    service = GenerationService(db_session)

    # Create session
    session = SessionModel(
        id="test-session-failed",
        status="running",
        progress_percent=50,
    )
    db_session.add(session)
    db_session.commit()

    # Update to failed
    updated = service.update_session(
        "test-session-failed",
        status="failed",
        error_message="CrewAI execution timed out",
    )

    assert updated is not None
    assert updated.status == "failed"
    assert updated.error_message == "CrewAI execution timed out"
    assert updated.completed_at is not None


def test_update_nonexistent_session(db_session):
    """Test updating nonexistent session returns None."""
    service = GenerationService(db_session)

    result = service.update_session("nonexistent", status="running")

    assert result is None
