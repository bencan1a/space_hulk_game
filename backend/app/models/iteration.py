"""Iteration model for story refinement history."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, Integer, String, Text

from .base import Base


class Iteration(Base):
    """
    Iteration history for story refinement.

    Attributes:
        id: Primary key
        story_id: Foreign key to Story
        iteration_number: Iteration sequence number
        feedback: User feedback text
        changes_requested: Structured feedback data
        game_file_path: Path to iteration game.json
        created_at: Creation timestamp
        status: pending, accepted, or rejected
    """

    __tablename__ = "iterations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(
        Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False
    )

    iteration_number = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=False)
    changes_requested = Column(JSON, nullable=True)

    # Result
    game_file_path = Column(String(500), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Status
    status = Column(String(20), default="pending", nullable=False)

    # Indexes
    __table_args__ = (Index("idx_iterations_story", "story_id", "iteration_number"),)
