"""Tests for database models."""

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.base import Base
from app.models.iteration import Iteration
from app.models.story import Story


@pytest.fixture
def db_session():
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")

    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_create_story(db_session):
    """Test creating a story."""
    story = Story(
        title="Test Story",
        description="Test description",
        theme_id="warhammer40k",
        game_file_path="/path/to/game.json",
        prompt="Test prompt",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(story)
    db_session.commit()

    assert story.id is not None
    assert story.title == "Test Story"
    assert story.play_count == 0


def test_create_iteration(db_session):
    """Test creating an iteration linked to a story."""
    story = Story(
        title="Test Story",
        game_file_path="/path/to/game.json",
        prompt="Test prompt",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(story)
    db_session.commit()

    iteration = Iteration(
        story_id=story.id,
        iteration_number=1,
        feedback="Make it scarier",
        game_file_path="/path/to/iteration_1.json",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(iteration)
    db_session.commit()

    assert iteration.id is not None
    assert iteration.story_id == story.id
    assert iteration.status == "pending"


def test_cascade_delete(db_session):
    """Test that deleting a story cascades to iterations."""
    story = Story(
        title="Test Story",
        game_file_path="/path/to/game.json",
        prompt="Test prompt",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(story)
    db_session.commit()

    iteration = Iteration(
        story_id=story.id,
        iteration_number=1,
        feedback="Test feedback",
        game_file_path="/path/to/iteration.json",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(iteration)
    db_session.commit()

    # Delete story
    db_session.delete(story)
    db_session.commit()

    # Iteration should be deleted due to CASCADE
    assert db_session.query(Iteration).count() == 0
