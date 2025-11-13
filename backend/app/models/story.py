"""Story model for game metadata."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Index, Integer, String, Text

from .base import Base


class Story(Base):
    """
    Story metadata and file references.

    Attributes:
        id: Primary key
        title: Story title (max 200 chars)
        description: Story description
        theme_id: Theme identifier (default: warhammer40k)
        game_file_path: Path to game.json file
        created_at: Creation timestamp
        updated_at: Last update timestamp
        play_count: Number of times played
        last_played: Last play timestamp
        prompt: Original user prompt
        template_id: Template identifier if used
        iteration_count: Number of iterations performed
        scene_count: Number of scenes in game
        item_count: Number of items in game
        npc_count: Number of NPCs in game
        puzzle_count: Number of puzzles in game
        tags: List of tags for search/filter
    """

    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    theme_id = Column(String(50), default="warhammer40k", nullable=False)

    # File system reference
    game_file_path = Column(String(500), nullable=False, unique=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    play_count = Column(Integer, default=0, nullable=False)
    last_played = Column(DateTime, nullable=True)

    # Generation info
    prompt = Column(Text, nullable=False)
    template_id = Column(String(50), nullable=True)
    iteration_count = Column(Integer, default=0, nullable=False)

    # Statistics (extracted from game.json)
    scene_count = Column(Integer, nullable=True)
    item_count = Column(Integer, nullable=True)
    npc_count = Column(Integer, nullable=True)
    puzzle_count = Column(Integer, nullable=True)

    # Optional tags for search/filter
    tags = Column(JSON, default=list, nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_stories_created", "created_at"),
        Index("idx_stories_theme", "theme_id"),
    )
