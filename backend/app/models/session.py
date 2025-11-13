"""Session model for tracking active creation sessions."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from .base import Base


class Session(Base):
    """
    Active creation sessions for progress tracking.

    Attributes:
        id: UUID primary key
        story_id: Foreign key to Story (nullable until story created)
        status: creating, iterating, complete, or error
        current_step: Current agent name
        progress_percent: Progress percentage (0-100)
        created_at: Creation timestamp
        completed_at: Completion timestamp
        error_message: Error message if status is error
    """

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)  # UUID
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="SET NULL"), nullable=True)

    status = Column(String(20), nullable=False)  # creating, iterating, complete, error
    current_step = Column(String(50), nullable=True)
    progress_percent = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    error_message = Column(Text, nullable=True)
