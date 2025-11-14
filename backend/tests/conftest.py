"""Pytest configuration for backend tests."""

import sys
from pathlib import Path

import pytest
from app.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture
def db_session():
    """Create in-memory test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def sample_story_data():
    """Sample story creation data."""
    return {
        "title": "Test Horror Story",
        "description": "A spooky tale",
        "theme_id": "warhammer40k",
        "prompt": "Create a horror story with body horror and isolation themes",
        "game_file_path": "data/stories/test_001/game.json",
        "tags": ["horror", "atmospheric"],
    }
