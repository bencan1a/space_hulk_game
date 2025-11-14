"""Service layer for story management."""

import logging
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models.story import Story
from ..schemas.story import StoryCreate, StoryListResponse, StoryResponse, StoryUpdate

logger = logging.getLogger(__name__)


class StoryService:
    """Service for managing game stories."""

    def __init__(self, db: Session):
        """
        Initialize story service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, story_data: StoryCreate) -> Story:
        """
        Create a new story.

        Args:
            story_data: Story creation data

        Returns:
            Created story model

        Raises:
            ValueError: If game file path already exists
        """
        # Check if game file path already exists
        existing = (
            self.db.query(Story).filter(Story.game_file_path == story_data.game_file_path).first()
        )
        if existing:
            raise ValueError(
                f"Story with game_file_path '{story_data.game_file_path}' already exists"
            )

        story = Story(**story_data.model_dump())
        self.db.add(story)
        self.db.commit()
        self.db.refresh(story)

        logger.info("Created story: %s - %s", story.id, story.title)
        return story

    def get(self, story_id: int) -> Story | None:
        """
        Get story by ID.

        Args:
            story_id: Story ID

        Returns:
            Story model or None if not found
        """
        return self.db.query(Story).filter(Story.id == story_id).first()

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        theme_id: str | None = None,
        tags: list[str] | None = None,
    ) -> StoryListResponse:
        """
        List stories with pagination and filters.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page (max 100)
            search: Search query for title/description/tags
            theme_id: Filter by theme
            tags: Filter by tags (OR logic)

        Returns:
            Paginated story list
        """
        # Validate page and page_size
        page = max(page, 1)
        if page_size < 1:
            page_size = 20

        # Build query
        query = self.db.query(Story)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Story.title.ilike(search_term),
                    Story.description.ilike(search_term),
                    Story.tags.op("LIKE")(f'%"{search.lower()}"%'),
                )
            )

        # Apply theme filter
        if theme_id:
            query = query.filter(Story.theme_id == theme_id)

        # Apply tags filter (OR logic - any matching tag)
        if tags:
            normalized_tags = [tag.lower() for tag in tags]
            # Use a different approach for SQLite compatibility
            # Filter stories that have any of the requested tags
            tag_filters = []
            for tag in normalized_tags:
                # This works with both SQLite and PostgreSQL
                tag_filters.append(Story.tags.op("LIKE")(f'%"{tag}"%'))
            query = query.filter(or_(*tag_filters))

        # Get total count
        total = query.count()

        # Apply pagination
        page_size = min(page_size, 100)  # Cap at 100
        offset = (page - 1) * page_size
        items = query.order_by(Story.created_at.desc()).offset(offset).limit(page_size).all()

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size

        return StoryListResponse(
            items=[StoryResponse.model_validate(story) for story in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def update(self, story_id: int, story_data: StoryUpdate) -> Story | None:
        """
        Update story fields.

        Args:
            story_id: Story ID
            story_data: Updated story data

        Returns:
            Updated story or None if not found
        """
        story = self.get(story_id)
        if not story:
            return None

        # Update only provided fields
        update_dict = story_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(story, field, value)

        self.db.commit()
        self.db.refresh(story)

        logger.info("Updated story: %s", story.id)
        return story

    def delete(self, story_id: int) -> bool:
        """
        Delete story by ID.

        Args:
            story_id: Story ID

        Returns:
            True if deleted, False if not found
        """
        story = self.get(story_id)
        if not story:
            return False

        self.db.delete(story)
        self.db.commit()

        logger.info("Deleted story: %s", story_id)
        return True

    def increment_play_count(self, story_id: int) -> Story | None:
        """
        Increment play count and update last_played timestamp.

        Args:
            story_id: Story ID

        Returns:
            Updated story or None if not found
        """
        now = datetime.now(timezone.utc)
        result = (
            self.db.query(Story)
            .filter(Story.id == story_id)
            .update(
                {
                    Story.play_count: Story.play_count + 1,
                    Story.last_played: now,
                },
                synchronize_session="fetch",
            )
        )
        if result == 0:
            return None
        self.db.commit()
        return self.get(story_id)
