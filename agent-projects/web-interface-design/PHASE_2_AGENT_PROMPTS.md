# Phase 2 Agent Prompts: Story Library Tasks

## Browser-Based Game Interface Implementation

**Phase**: 2 - Story Library (Weeks 5-6)
**Objective**: Story CRUD, library UI, theme system, sample data
**Deliverables**: Story API, library page, search/filter, theme loader, sample stories

---

## Table of Contents

1. [Task 2.1: Story Service & Repository](#task-21-story-service--repository)
2. [Task 2.2: Story API Endpoints](#task-22-story-api-endpoints)
3. [Task 2.3: Theme System - Backend](#task-23-theme-system---backend)
4. [Task 2.4: Theme API Endpoints](#task-24-theme-api-endpoints)
5. [Task 2.5: Story Library UI - Components](#task-25-story-library-ui---components)
6. [Task 2.6: Story Library UI - Integration](#task-26-story-library-ui---integration)
7. [Task 2.7: Theme Selector UI](#task-27-theme-selector-ui)
8. [Task 2.8: Sample Story Data & Database Seeding](#task-28-sample-story-data--database-seeding)

---

## Task 2.1: Story Service & Repository

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 1.2 (Database Setup)

### Context

You are implementing the service layer for story management in the browser-based game interface. This service provides CRUD operations, search, filtering, and pagination for game stories. The service follows the repository pattern and acts as an abstraction layer between the API routes and the database.

**Project Documentation**:

- Architecture: [ARCHITECTURAL_DESIGN.md](./ARCHITECTURAL_DESIGN.md) Section 3.2
- Implementation Plan: [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) Task 2.1
- Database Models: `backend/app/models/story.py` (already implemented)

### Your Mission

Create a service layer class `StoryService` with full CRUD operations, search, filtering, and pagination. Use Pydantic schemas for request/response validation.

### Deliverables

```
backend/
├── app/
│   ├── services/
│   │   ├── __init__.py
│   │   └── story_service.py    # Main service class
│   └── schemas/
│       ├── __init__.py
│       └── story.py             # Pydantic request/response schemas
└── tests/
    ├── test_story_service.py    # Service tests
    └── conftest.py              # Test fixtures (update)
```

### Acceptance Criteria

- [ ] StoryService class with methods: `create()`, `get()`, `list()`, `update()`, `delete()`
- [ ] Search functionality (case-insensitive, searches title/description/tags)
- [ ] Filtering by theme_id, tags
- [ ] Pagination with page/page_size parameters
- [ ] Pydantic schemas for StoryCreate, StoryUpdate, StoryResponse, StoryListResponse
- [ ] Type hints on all methods
- [ ] Comprehensive docstrings (Google style)
- [ ] Unit tests with 90%+ coverage
- [ ] Tests use in-memory SQLite database
- [ ] Code passes ruff and mypy

### Technical Requirements

**Pydantic Schemas (`schemas/story.py`)**:

```python
"""Pydantic schemas for story API."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class StoryBase(BaseModel):
    """Base story schema with common fields."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    theme_id: str = Field(default="warhammer40k", max_length=50)
    tags: list[str] = Field(default_factory=list)


class StoryCreate(StoryBase):
    """Schema for creating a new story."""

    prompt: str = Field(..., min_length=50, max_length=5000)
    template_id: Optional[str] = Field(None, max_length=50)
    game_file_path: str = Field(..., min_length=1, max_length=500)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate tags are lowercase and unique."""
        return list(set(tag.lower().strip() for tag in v if tag.strip()))


class StoryUpdate(BaseModel):
    """Schema for updating a story."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    tags: Optional[list[str]] = None


class StoryResponse(StoryBase):
    """Schema for story response."""

    id: int
    game_file_path: str
    created_at: datetime
    updated_at: datetime
    play_count: int
    last_played: Optional[datetime]
    prompt: str
    template_id: Optional[str]
    iteration_count: int
    scene_count: Optional[int]
    item_count: Optional[int]
    npc_count: Optional[int]
    puzzle_count: Optional[int]

    model_config = {"from_attributes": True}


class StoryListResponse(BaseModel):
    """Paginated list of stories."""

    items: list[StoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
```

**Story Service (`services/story_service.py`)**:

```python
"""Service layer for story management."""
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from ..models.story import Story
from ..schemas.story import StoryCreate, StoryUpdate, StoryResponse, StoryListResponse

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
        existing = self.db.query(Story).filter(
            Story.game_file_path == story_data.game_file_path
        ).first()
        if existing:
            raise ValueError(f"Story with game_file_path '{story_data.game_file_path}' already exists")

        story = Story(**story_data.model_dump())
        self.db.add(story)
        self.db.commit()
        self.db.refresh(story)

        logger.info(f"Created story: {story.id} - {story.title}")
        return story

    def get(self, story_id: int) -> Optional[Story]:
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
        search: Optional[str] = None,
        theme_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> StoryListResponse:
        """
        List stories with pagination and filters.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page (max 100)
            search: Search query for title/description
            theme_id: Filter by theme
            tags: Filter by tags (OR logic)

        Returns:
            Paginated story list
        """
        # Build query
        query = self.db.query(Story)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Story.title.ilike(search_term),
                    Story.description.ilike(search_term),
                    Story.tags.contains([search.lower()])
                )
            )

        # Apply theme filter
        if theme_id:
            query = query.filter(Story.theme_id == theme_id)

        # Apply tags filter (OR logic - any matching tag)
        if tags:
            normalized_tags = [tag.lower() for tag in tags]
            query = query.filter(
                or_(*[Story.tags.contains([tag]) for tag in normalized_tags])
            )

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

    def update(self, story_id: int, story_data: StoryUpdate) -> Optional[Story]:
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

        logger.info(f"Updated story: {story.id}")
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

        logger.info(f"Deleted story: {story_id}")
        return True

    def increment_play_count(self, story_id: int) -> Optional[Story]:
        """
        Increment play count and update last_played timestamp.

        Args:
            story_id: Story ID

        Returns:
            Updated story or None if not found
        """
        story = self.get(story_id)
        if not story:
            return None

        story.play_count += 1
        from datetime import datetime, timezone
        story.last_played = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(story)

        return story
```

### Testing Requirements

**Test Fixtures (`tests/conftest.py` - add to existing)**:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models.base import Base
from backend.app.models.story import Story


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
```

**Service Tests (`tests/test_story_service.py`)**:

```python
"""Tests for story service."""
import pytest
from backend.app.services.story_service import StoryService
from backend.app.schemas.story import StoryCreate, StoryUpdate


def test_create_story(db_session, sample_story_data):
    """Test creating a new story."""
    service = StoryService(db_session)
    story_create = StoryCreate(**sample_story_data)

    story = service.create(story_create)

    assert story.id is not None
    assert story.title == sample_story_data["title"]
    assert story.theme_id == "warhammer40k"
    assert story.play_count == 0


def test_create_duplicate_path_raises_error(db_session, sample_story_data):
    """Test creating story with duplicate game_file_path raises error."""
    service = StoryService(db_session)
    story_create = StoryCreate(**sample_story_data)

    # Create first story
    service.create(story_create)

    # Attempt to create duplicate
    with pytest.raises(ValueError, match="already exists"):
        service.create(story_create)


def test_get_story(db_session, sample_story_data):
    """Test getting story by ID."""
    service = StoryService(db_session)
    story_create = StoryCreate(**sample_story_data)
    created = service.create(story_create)

    retrieved = service.get(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.title == created.title


def test_get_nonexistent_story(db_session):
    """Test getting nonexistent story returns None."""
    service = StoryService(db_session)

    story = service.get(999)

    assert story is None


def test_list_stories_pagination(db_session):
    """Test listing stories with pagination."""
    service = StoryService(db_session)

    # Create 25 stories
    for i in range(25):
        story_data = StoryCreate(
            title=f"Story {i}",
            prompt="Test prompt for story creation",
            game_file_path=f"data/stories/test_{i:03d}/game.json",
        )
        service.create(story_data)

    # Test first page
    result = service.list(page=1, page_size=10)
    assert result.total == 25
    assert len(result.items) == 10
    assert result.page == 1
    assert result.total_pages == 3

    # Test second page
    result = service.list(page=2, page_size=10)
    assert len(result.items) == 10
    assert result.page == 2


def test_list_stories_search(db_session):
    """Test listing stories with search filter."""
    service = StoryService(db_session)

    # Create stories with different titles
    service.create(StoryCreate(
        title="Horror Story",
        prompt="Horror prompt",
        game_file_path="data/stories/horror/game.json"
    ))
    service.create(StoryCreate(
        title="Adventure Story",
        prompt="Adventure prompt",
        game_file_path="data/stories/adventure/game.json"
    ))

    result = service.list(search="horror")

    assert result.total == 1
    assert result.items[0].title == "Horror Story"


def test_list_stories_theme_filter(db_session):
    """Test filtering stories by theme."""
    service = StoryService(db_session)

    service.create(StoryCreate(
        title="WH40K Story",
        theme_id="warhammer40k",
        prompt="WH40K prompt",
        game_file_path="data/stories/wh40k/game.json"
    ))
    service.create(StoryCreate(
        title="Cyberpunk Story",
        theme_id="cyberpunk",
        prompt="Cyberpunk prompt",
        game_file_path="data/stories/cyberpunk/game.json"
    ))

    result = service.list(theme_id="cyberpunk")

    assert result.total == 1
    assert result.items[0].theme_id == "cyberpunk"


def test_list_stories_tags_filter(db_session):
    """Test filtering stories by tags."""
    service = StoryService(db_session)

    service.create(StoryCreate(
        title="Horror Story",
        tags=["horror", "atmospheric"],
        prompt="Horror prompt",
        game_file_path="data/stories/horror/game.json"
    ))
    service.create(StoryCreate(
        title="Action Story",
        tags=["action", "combat"],
        prompt="Action prompt",
        game_file_path="data/stories/action/game.json"
    ))

    result = service.list(tags=["horror"])

    assert result.total == 1
    assert "horror" in result.items[0].tags


def test_update_story(db_session, sample_story_data):
    """Test updating story fields."""
    service = StoryService(db_session)
    story_create = StoryCreate(**sample_story_data)
    created = service.create(story_create)

    update_data = StoryUpdate(title="Updated Title", tags=["new-tag"])
    updated = service.update(created.id, update_data)

    assert updated is not None
    assert updated.title == "Updated Title"
    assert "new-tag" in updated.tags


def test_update_nonexistent_story(db_session):
    """Test updating nonexistent story returns None."""
    service = StoryService(db_session)

    update_data = StoryUpdate(title="New Title")
    result = service.update(999, update_data)

    assert result is None


def test_delete_story(db_session, sample_story_data):
    """Test deleting a story."""
    service = StoryService(db_session)
    story_create = StoryCreate(**sample_story_data)
    created = service.create(story_create)

    deleted = service.delete(created.id)

    assert deleted is True
    assert service.get(created.id) is None


def test_delete_nonexistent_story(db_session):
    """Test deleting nonexistent story returns False."""
    service = StoryService(db_session)

    deleted = service.delete(999)

    assert deleted is False


def test_increment_play_count(db_session, sample_story_data):
    """Test incrementing play count."""
    service = StoryService(db_session)
    story_create = StoryCreate(**sample_story_data)
    created = service.create(story_create)

    assert created.play_count == 0
    assert created.last_played is None

    updated = service.increment_play_count(created.id)

    assert updated is not None
    assert updated.play_count == 1
    assert updated.last_played is not None
```

### Validation Commands

```bash
# Install dependencies
cd backend
pip install -r requirements.txt -r requirements-dev.txt

# Run type checking
mypy app/services/story_service.py app/schemas/story.py

# Run linting
ruff check app/services/ app/schemas/

# Run tests with coverage
pytest tests/test_story_service.py -v --cov=app.services.story_service --cov-report=term

# Should show 90%+ coverage
```

### Success Indicators

✅ All CRUD operations work correctly
✅ Search returns relevant results (case-insensitive)
✅ Pagination calculates total_pages correctly
✅ Filters work independently and combined
✅ All tests pass with 90%+ coverage
✅ No type errors from mypy
✅ No linting errors from ruff

---

## Task 2.2: Story API Endpoints

**Priority**: P0
**Effort**: 1 day
**Dependencies**: Task 2.1 (Story Service)

### Context

Create REST API endpoints for story management using the StoryService. These endpoints will be consumed by the frontend library UI. Follow RESTful conventions and provide proper error handling.

**Project Documentation**:

- API Specification: [API_SPECIFICATION.md](./API_SPECIFICATION.md)
- Architecture: [ARCHITECTURAL_DESIGN.md](./ARCHITECTURAL_DESIGN.md) Section 5

### Your Mission

Implement FastAPI routes for story CRUD operations with proper validation, error handling, and status codes.

### Deliverables

```
backend/
├── app/
│   └── api/
│       └── routes/
│           └── stories.py          # Story endpoints
└── tests/
    └── test_stories_api.py          # API route tests
```

### Acceptance Criteria

- [ ] GET /api/v1/stories - List stories with query params (page, page_size, search, theme_id, tags)
- [ ] GET /api/v1/stories/{id} - Get story details
- [ ] GET /api/v1/stories/{id}/content - Get game.json file content
- [ ] DELETE /api/v1/stories/{id} - Delete story
- [ ] All endpoints use proper HTTP status codes (200, 404, 400, 500)
- [ ] Request validation with Pydantic
- [ ] Error responses follow standard format
- [ ] Routes registered in main.py
- [ ] API tests for all endpoints
- [ ] Tests cover success and error cases

### Technical Requirements

**API Routes (`api/routes/stories.py`)**:

```python
"""Story management API endpoints."""
import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas.story import StoryResponse, StoryListResponse
from ...services.story_service import StoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/stories", tags=["stories"])


def get_story_service(db: Session = Depends(get_db)) -> StoryService:
    """
    Dependency to get story service.

    Args:
        db: Database session

    Returns:
        StoryService instance
    """
    return StoryService(db)


@router.get("", response_model=StoryListResponse)
async def list_stories(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, max_length=200, description="Search query"),
    theme_id: Optional[str] = Query(default=None, max_length=50, description="Filter by theme"),
    tags: Optional[str] = Query(default=None, description="Comma-separated tags"),
    service: StoryService = Depends(get_story_service),
) -> StoryListResponse:
    """
    List stories with pagination and filters.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        search: Search query for title/description
        theme_id: Filter by theme ID
        tags: Comma-separated list of tags
        service: Story service dependency

    Returns:
        Paginated list of stories
    """
    # Parse tags from comma-separated string
    tags_list = [tag.strip() for tag in tags.split(",")] if tags else None

    return service.list(
        page=page,
        page_size=page_size,
        search=search,
        theme_id=theme_id,
        tags=tags_list,
    )


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: int,
    service: StoryService = Depends(get_story_service),
) -> StoryResponse:
    """
    Get story details by ID.

    Args:
        story_id: Story ID
        service: Story service dependency

    Returns:
        Story details

    Raises:
        HTTPException: 404 if story not found
    """
    story = service.get(story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )

    return StoryResponse.model_validate(story)


@router.get("/{story_id}/content")
async def get_story_content(
    story_id: int,
    service: StoryService = Depends(get_story_service),
) -> dict:
    """
    Get story game.json content.

    Args:
        story_id: Story ID
        service: Story service dependency

    Returns:
        Game JSON content

    Raises:
        HTTPException: 404 if story or file not found
    """
    story = service.get(story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )

    # Read game.json file
    game_file = Path(story.game_file_path)
    if not game_file.exists():
        logger.error(f"Game file not found: {story.game_file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game file not found for story {story_id}",
        )

    try:
        with open(game_file, "r", encoding="utf-8") as f:
            content = json.load(f)
        return content
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in game file: {story.game_file_path} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Game file contains invalid JSON",
        )
    except Exception as e:
        logger.error(f"Error reading game file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read game file",
        )


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
    story_id: int,
    service: StoryService = Depends(get_story_service),
) -> None:
    """
    Delete a story.

    Args:
        story_id: Story ID
        service: Story service dependency

    Raises:
        HTTPException: 404 if story not found
    """
    deleted = service.delete(story_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
```

**Register Routes (`app/main.py` - add to existing)**:

```python
from .api.routes import stories

# Add after middleware setup
app.include_router(stories.router)
```

### Testing Requirements

**API Tests (`tests/test_stories_api.py`)**:

```python
"""Tests for story API endpoints."""
import json
import pytest
from pathlib import Path
from httpx import AsyncClient

from backend.app.main import app
from backend.app.models.story import Story


@pytest.fixture
def test_game_file(tmp_path):
    """Create a temporary game.json file."""
    game_data = {
        "title": "Test Game",
        "scenes": [],
        "items": [],
    }
    file_path = tmp_path / "game.json"
    with open(file_path, "w") as f:
        json.dump(game_data, f)
    return str(file_path)


@pytest.mark.asyncio
async def test_list_stories_empty():
    """Test listing stories when database is empty."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/stories")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


@pytest.mark.asyncio
async def test_list_stories_with_pagination():
    """Test listing stories with pagination."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/stories?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data


@pytest.mark.asyncio
async def test_list_stories_with_search():
    """Test searching stories."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/stories?search=horror")

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_stories_with_filters():
    """Test filtering stories by theme and tags."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/stories?theme_id=warhammer40k&tags=horror,atmospheric"
        )

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_story_not_found():
    """Test getting nonexistent story returns 404."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/stories/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_story_content_not_found():
    """Test getting content for nonexistent story returns 404."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/stories/999/content")

        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_story_not_found():
    """Test deleting nonexistent story returns 404."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/api/v1/stories/999")

        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_story_success():
    """Test successful story deletion returns 204."""
    # This test would require database setup with actual story
    # For now, just test the endpoint exists
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/api/v1/stories/1")

        assert response.status_code in [204, 404]  # 204 if exists, 404 if not
```

### Validation Commands

```bash
# Start the server
cd backend
uvicorn app.main:app --reload

# Test endpoints manually
curl http://localhost:8000/api/v1/stories
curl http://localhost:8000/api/v1/stories?page=1&page_size=10
curl http://localhost:8000/api/v1/stories?search=horror
curl http://localhost:8000/api/v1/stories/1
curl http://localhost:8000/api/v1/stories/1/content
curl -X DELETE http://localhost:8000/api/v1/stories/1

# Run API tests
pytest tests/test_stories_api.py -v

# Check API docs
# Visit: http://localhost:8000/docs
```

### Success Indicators

✅ All endpoints return correct status codes
✅ List endpoint supports pagination and filters
✅ 404 errors for nonexistent stories
✅ game.json content is returned as JSON
✅ DELETE returns 204 on success
✅ All tests pass
✅ API docs show all endpoints

---

## Task 2.3: Theme System - Backend

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 1.1 (Backend Setup)

### Context

Implement the multi-theme system backend that allows the interface to support multiple game genres (Warhammer 40K, Cyberpunk, Fantasy, etc.). Each theme defines colors, fonts, icons, and terminology.

**Project Documentation**:

- Theming System: [THEMING_SYSTEM.md](./THEMING_SYSTEM.md)
- Architecture: [ARCHITECTURAL_DESIGN.md](./ARCHITECTURAL_DESIGN.md) Section 4.2

### Your Mission

Create theme loading service with validation and caching, plus create initial theme configurations for Warhammer 40K and Cyberpunk.

### Deliverables

```
data/
└── themes/
    ├── warhammer40k/
    │   ├── theme.yaml
    │   └── assets/
    │       ├── logo.png
    │       └── background.jpg
    └── cyberpunk/
        ├── theme.yaml
        └── assets/
            ├── logo.png
            └── background.jpg

backend/
├── app/
│   └── services/
│       └── theme_service.py
└── tests/
    └── test_theme_service.py
```

### Acceptance Criteria

- [ ] ThemeService class with methods: `load_theme()`, `list_themes()`, `validate_theme()`
- [ ] In-memory theme caching
- [ ] Default theme fallback (warhammer40k)
- [ ] Theme YAML validation
- [ ] Asset path resolution
- [ ] Two complete theme configurations (warhammer40k, cyberpunk)
- [ ] Unit tests with valid/invalid themes
- [ ] Type hints and docstrings

### Technical Requirements

**Theme YAML Structure (`data/themes/warhammer40k/theme.yaml`)**:

```yaml
# Warhammer 40K Theme Configuration
id: warhammer40k
name: "Warhammer 40,000"
description: "Grimdark gothic sci-fi horror"

# Visual Design
colors:
  primary: "#8B0000"        # Dark red
  secondary: "#C0C0C0"      # Silver
  background: "#1A1A1A"     # Near black
  surface: "#2D2D2D"        # Dark gray
  text: "#E0E0E0"           # Light gray
  textSecondary: "#A0A0A0"  # Medium gray
  accent: "#FFD700"         # Gold
  error: "#FF4444"
  success: "#44FF44"
  warning: "#FFAA00"

typography:
  fontFamily: "'Cinzel', 'Georgia', serif"
  fontFamilyMono: "'Courier New', monospace"
  fontSize:
    xs: "0.75rem"
    sm: "0.875rem"
    base: "1rem"
    lg: "1.125rem"
    xl: "1.25rem"
    xxl: "1.5rem"

# Terminology
terminology:
  story: "Mission"
  stories: "Missions"
  character: "Space Marine"
  characters: "Space Marines"
  enemy: "Xenos"
  enemies: "Xenos"
  item: "Artifact"
  items: "Artifacts"
  location: "Sector"
  locations: "Sectors"

# UI Text
ui:
  welcome: "Enter the grim darkness of the far future"
  createStory: "Deploy New Mission"
  libraryTitle: "Mission Archive"
  playButton: "Deploy"

# Assets (relative to theme directory)
assets:
  logo: "assets/logo.png"
  background: "assets/background.jpg"
  icon: "assets/icon.svg"
```

**Cyberpunk Theme (`data/themes/cyberpunk/theme.yaml`)**:

```yaml
# Cyberpunk Theme Configuration
id: cyberpunk
name: "Cyberpunk"
description: "High-tech dystopian future"

colors:
  primary: "#FF00FF"        # Neon magenta
  secondary: "#00FFFF"      # Neon cyan
  background: "#0A0A0A"     # Very dark
  surface: "#1A1A2E"        # Dark blue
  text: "#00FF00"           # Neon green
  textSecondary: "#00AA00"  # Dimmer green
  accent: "#FFFF00"         # Neon yellow
  error: "#FF0000"
  success: "#00FF00"
  warning: "#FFAA00"

typography:
  fontFamily: "'Orbitron', 'Arial', sans-serif"
  fontFamilyMono: "'Share Tech Mono', monospace"
  fontSize:
    xs: "0.75rem"
    sm: "0.875rem"
    base: "1rem"
    lg: "1.125rem"
    xl: "1.25rem"
    xxl: "1.5rem"

terminology:
  story: "Run"
  stories: "Runs"
  character: "Runner"
  characters: "Runners"
  enemy: "Corp"
  enemies: "Corps"
  item: "Cyberware"
  items: "Cyberware"
  location: "Zone"
  locations: "Zones"

ui:
  welcome: "Jack in to the grid"
  createStory: "Start New Run"
  libraryTitle: "Run Archive"
  playButton: "Jack In"

assets:
  logo: "assets/logo.png"
  background: "assets/background.jpg"
  icon: "assets/icon.svg"
```

**Theme Service (`services/theme_service.py`)**:

```python
"""Service for managing themes."""
import logging
from pathlib import Path
from typing import Optional
import yaml

logger = logging.getLogger(__name__)


class ThemeConfig:
    """Theme configuration data."""

    def __init__(self, data: dict):
        """
        Initialize theme config.

        Args:
            data: Theme configuration dictionary
        """
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.colors: dict = data["colors"]
        self.typography: dict = data["typography"]
        self.terminology: dict = data["terminology"]
        self.ui: dict = data["ui"]
        self.assets: dict = data["assets"]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "colors": self.colors,
            "typography": self.typography,
            "terminology": self.terminology,
            "ui": self.ui,
            "assets": self.assets,
        }


class ThemeService:
    """Service for loading and managing themes."""

    def __init__(self, themes_dir: str = "data/themes"):
        """
        Initialize theme service.

        Args:
            themes_dir: Path to themes directory
        """
        self.themes_dir = Path(themes_dir)
        self._cache: dict[str, ThemeConfig] = {}
        self.default_theme_id = "warhammer40k"

    def load_theme(self, theme_id: str) -> Optional[ThemeConfig]:
        """
        Load theme configuration.

        Args:
            theme_id: Theme identifier

        Returns:
            Theme configuration or None if not found
        """
        # Check cache first
        if theme_id in self._cache:
            logger.debug(f"Theme '{theme_id}' loaded from cache")
            return self._cache[theme_id]

        # Load from file
        theme_file = self.themes_dir / theme_id / "theme.yaml"
        if not theme_file.exists():
            logger.warning(f"Theme file not found: {theme_file}")
            return None

        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Validate theme
            if not self.validate_theme(data):
                logger.error(f"Invalid theme configuration: {theme_id}")
                return None

            # Create config and cache
            config = ThemeConfig(data)
            self._cache[theme_id] = config

            logger.info(f"Loaded theme: {theme_id}")
            return config

        except Exception as e:
            logger.error(f"Failed to load theme '{theme_id}': {e}")
            return None

    def list_themes(self) -> list[dict]:
        """
        List all available themes.

        Returns:
            List of theme metadata (id, name, description)
        """
        themes = []

        if not self.themes_dir.exists():
            logger.warning(f"Themes directory not found: {self.themes_dir}")
            return themes

        for theme_dir in self.themes_dir.iterdir():
            if not theme_dir.is_dir():
                continue

            theme_file = theme_dir / "theme.yaml"
            if not theme_file.exists():
                continue

            try:
                with open(theme_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                themes.append({
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "description": data.get("description"),
                })
            except Exception as e:
                logger.error(f"Failed to read theme metadata from {theme_file}: {e}")

        return sorted(themes, key=lambda x: x["name"])

    def validate_theme(self, data: dict) -> bool:
        """
        Validate theme configuration structure.

        Args:
            data: Theme configuration dictionary

        Returns:
            True if valid, False otherwise
        """
        required_keys = ["id", "name", "description", "colors", "typography", "terminology", "ui", "assets"]

        for key in required_keys:
            if key not in data:
                logger.error(f"Missing required key in theme: {key}")
                return False

        # Validate colors
        required_colors = ["primary", "secondary", "background", "surface", "text"]
        for color in required_colors:
            if color not in data["colors"]:
                logger.error(f"Missing required color: {color}")
                return False

        return True

    def get_default_theme(self) -> ThemeConfig:
        """
        Get default theme (fallback).

        Returns:
            Default theme configuration
        """
        theme = self.load_theme(self.default_theme_id)
        if not theme:
            raise RuntimeError(f"Default theme '{self.default_theme_id}' not found")
        return theme

    def get_asset_path(self, theme_id: str, asset_key: str) -> Optional[Path]:
        """
        Get absolute path to theme asset.

        Args:
            theme_id: Theme identifier
            asset_key: Asset key (e.g., 'logo', 'background')

        Returns:
            Absolute path to asset or None if not found
        """
        theme = self.load_theme(theme_id)
        if not theme or asset_key not in theme.assets:
            return None

        asset_path = self.themes_dir / theme_id / theme.assets[asset_key]
        return asset_path if asset_path.exists() else None
```

### Testing Requirements

```python
"""Tests for theme service."""
import pytest
from pathlib import Path
import yaml

from backend.app.services.theme_service import ThemeService, ThemeConfig


@pytest.fixture
def theme_service(tmp_path):
    """Create theme service with temporary directory."""
    return ThemeService(themes_dir=str(tmp_path))


@pytest.fixture
def valid_theme_data():
    """Valid theme configuration data."""
    return {
        "id": "test-theme",
        "name": "Test Theme",
        "description": "Test theme description",
        "colors": {
            "primary": "#FF0000",
            "secondary": "#00FF00",
            "background": "#000000",
            "surface": "#111111",
            "text": "#FFFFFF",
        },
        "typography": {
            "fontFamily": "Arial",
            "fontSize": {"base": "1rem"},
        },
        "terminology": {
            "story": "Story",
        },
        "ui": {
            "welcome": "Welcome",
        },
        "assets": {
            "logo": "assets/logo.png",
        },
    }


def test_validate_theme_valid(theme_service, valid_theme_data):
    """Test validating valid theme returns True."""
    assert theme_service.validate_theme(valid_theme_data) is True


def test_validate_theme_missing_key(theme_service, valid_theme_data):
    """Test validating theme with missing key returns False."""
    del valid_theme_data["colors"]
    assert theme_service.validate_theme(valid_theme_data) is False


def test_validate_theme_missing_color(theme_service, valid_theme_data):
    """Test validating theme with missing required color returns False."""
    del valid_theme_data["colors"]["primary"]
    assert theme_service.validate_theme(valid_theme_data) is False


def test_load_theme_not_found(theme_service):
    """Test loading nonexistent theme returns None."""
    theme = theme_service.load_theme("nonexistent")
    assert theme is None


def test_list_themes_empty(theme_service):
    """Test listing themes when directory is empty."""
    themes = theme_service.list_themes()
    assert themes == []


def test_theme_config_to_dict(valid_theme_data):
    """Test ThemeConfig to_dict method."""
    config = ThemeConfig(valid_theme_data)
    result = config.to_dict()

    assert result["id"] == "test-theme"
    assert result["name"] == "Test Theme"
    assert "colors" in result
```

### Validation Commands

```bash
# Create themes directory structure
mkdir -p data/themes/warhammer40k/assets
mkdir -p data/themes/cyberpunk/assets

# Create theme YAML files (copy from examples above)

# Run tests
pytest tests/test_theme_service.py -v

# Test theme loading in Python
python -c "
from backend.app.services.theme_service import ThemeService
service = ThemeService()
theme = service.load_theme('warhammer40k')
print(f'Loaded: {theme.name}')
print(f'Colors: {theme.colors}')
"
```

### Success Indicators

✅ Both theme YAML files are valid
✅ Theme service loads and caches themes
✅ Validation rejects invalid themes
✅ Default theme fallback works
✅ list_themes() returns all themes
✅ Asset paths resolve correctly
✅ All tests pass

---

## Task 2.4: Theme API Endpoints

**Priority**: P0
**Effort**: 0.5 days
**Dependencies**: Task 2.3 (Theme System - Backend)

### Context

You are implementing REST API endpoints to expose the theme system to the frontend. These endpoints allow the browser interface to list available themes, load theme configurations, and serve theme assets. The API follows RESTful conventions and leverages the ThemeService implemented in Task 2.3.

**Project Documentation**:

- API Specification: [API_SPECIFICATION.md](./API_SPECIFICATION.md) Section "Themes"
- Architecture: [ARCHITECTURAL_DESIGN.md](./ARCHITECTURAL_DESIGN.md) Section 5
- Theme System: [THEMING_SYSTEM.md](./THEMING_SYSTEM.md)

### Your Mission

Create FastAPI routes for theme management with proper validation, error handling, and asset serving. Ensure themes can be discovered and loaded dynamically by the frontend.

### Deliverables

```
backend/
├── app/
│   └── api/
│       └── routes/
│           └── themes.py           # Theme API endpoints
└── tests/
    └── test_themes_api.py          # API route tests
```

### Acceptance Criteria

- [ ] GET /api/v1/themes - List all available themes with metadata
- [ ] GET /api/v1/themes/{theme_id} - Get complete theme configuration
- [ ] GET /api/v1/themes/{theme_id}/assets/{asset_path} - Serve theme assets (images, fonts, etc.)
- [ ] All endpoints use proper HTTP status codes (200, 404, 500)
- [ ] Theme not found returns 404 with descriptive error
- [ ] Asset serving includes proper Content-Type headers
- [ ] Routes registered in main.py
- [ ] API tests for all endpoints
- [ ] Tests cover success and error cases

### Technical Requirements

**API Routes (`api/routes/themes.py`)**:

```python
"""Theme management API endpoints."""
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from ...services.theme_service import ThemeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/themes", tags=["themes"])

# Initialize theme service (shared instance)
theme_service = ThemeService()


@router.get("")
async def list_themes() -> dict[str, list[dict[str, Any]]]:
    """
    List all available themes.

    Returns:
        Dictionary with list of theme metadata

    Example response:
        {
            "data": [
                {
                    "id": "warhammer40k",
                    "name": "Warhammer 40,000",
                    "description": "Grimdark gothic sci-fi horror"
                }
            ]
        }
    """
    themes = theme_service.list_themes()
    return {"data": themes}


@router.get("/{theme_id}")
async def get_theme(theme_id: str) -> dict[str, dict[str, Any]]:
    """
    Get complete theme configuration.

    Args:
        theme_id: Theme identifier

    Returns:
        Dictionary with theme configuration

    Raises:
        HTTPException: 404 if theme not found

    Example response:
        {
            "data": {
                "id": "warhammer40k",
                "name": "Warhammer 40,000",
                "colors": {...},
                "typography": {...},
                ...
            }
        }
    """
    theme = theme_service.load_theme(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theme '{theme_id}' not found",
        )

    return {"data": theme.to_dict()}


@router.get("/{theme_id}/assets/{asset_path:path}")
async def get_theme_asset(theme_id: str, asset_path: str) -> FileResponse:
    """
    Serve theme asset file.

    Args:
        theme_id: Theme identifier
        asset_path: Relative path to asset within theme directory

    Returns:
        File response with appropriate Content-Type

    Raises:
        HTTPException: 404 if theme or asset not found
        HTTPException: 400 if asset path is invalid (directory traversal)

    Example:
        GET /api/v1/themes/warhammer40k/assets/logo.png
        GET /api/v1/themes/warhammer40k/assets/background.jpg
    """
    # Validate asset path (prevent directory traversal)
    if ".." in asset_path or asset_path.startswith("/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid asset path",
        )

    # Load theme to verify it exists
    theme = theme_service.load_theme(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theme '{theme_id}' not found",
        )

    # Construct asset path
    asset_file = theme_service.themes_dir / theme_id / asset_path

    # Verify asset exists and is a file (not directory)
    if not asset_file.exists() or not asset_file.is_file():
        logger.warning(f"Asset not found: {asset_file}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_path}' not found in theme '{theme_id}'",
        )

    # Serve file with appropriate content type
    return FileResponse(
        path=str(asset_file),
        media_type=_get_media_type(asset_file),
    )


def _get_media_type(file_path: Path) -> str:
    """
    Determine media type from file extension.

    Args:
        file_path: Path to file

    Returns:
        MIME type string
    """
    extension = file_path.suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg",
        ".wav": "audio/wav",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".otf": "font/otf",
        ".json": "application/json",
        ".yaml": "application/x-yaml",
        ".yml": "application/x-yaml",
    }
    return media_types.get(extension, "application/octet-stream")
```

**Register Routes (`app/main.py` - add to existing)**:

```python
from .api.routes import themes

# Add after stories router
app.include_router(themes.router)
```

### Testing Requirements

**API Tests (`tests/test_themes_api.py`)**:

```python
"""Tests for theme API endpoints."""
import json
import pytest
from pathlib import Path
from httpx import AsyncClient

from backend.app.main import app


@pytest.fixture
def test_theme_dir(tmp_path):
    """Create test theme directory structure."""
    theme_dir = tmp_path / "themes" / "test-theme"
    theme_dir.mkdir(parents=True)

    # Create theme.yaml
    theme_config = {
        "id": "test-theme",
        "name": "Test Theme",
        "description": "Test theme description",
        "colors": {
            "primary": "#FF0000",
            "secondary": "#00FF00",
            "background": "#000000",
            "surface": "#111111",
            "text": "#FFFFFF",
        },
        "typography": {
            "fontFamily": "Arial",
            "fontSize": {"base": "1rem"},
        },
        "terminology": {
            "story": "Story",
        },
        "ui": {
            "welcome": "Welcome",
        },
        "assets": {
            "logo": "assets/logo.png",
        },
    }

    import yaml
    with open(theme_dir / "theme.yaml", "w") as f:
        yaml.dump(theme_config, f)

    # Create asset file
    assets_dir = theme_dir / "assets"
    assets_dir.mkdir()
    logo_file = assets_dir / "logo.png"
    logo_file.write_bytes(b"\x89PNG\r\n\x1a\n")  # PNG header

    return tmp_path


@pytest.mark.asyncio
async def test_list_themes_empty():
    """Test listing themes when no themes available."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/themes")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_list_themes_with_themes(test_theme_dir):
    """Test listing themes returns theme metadata."""
    # This test would need to configure theme_service with test_theme_dir
    # For simplicity, we're just testing the endpoint structure
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/themes")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data


@pytest.mark.asyncio
async def test_get_theme_not_found():
    """Test getting nonexistent theme returns 404."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/themes/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_theme_success():
    """Test getting theme returns complete configuration."""
    # This test assumes warhammer40k theme exists
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/themes/warhammer40k")

        # May return 200 or 404 depending on whether theme exists
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            theme = data["data"]
            assert "id" in theme
            assert "name" in theme
            assert "colors" in theme


@pytest.mark.asyncio
async def test_get_theme_asset_not_found():
    """Test getting asset from nonexistent theme returns 404."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/themes/nonexistent/assets/logo.png")

        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_theme_asset_invalid_path():
    """Test getting asset with invalid path returns 400."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test directory traversal
        response = await client.get("/api/v1/themes/warhammer40k/assets/../../../etc/passwd")

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_theme_asset_nonexistent_file():
    """Test getting nonexistent asset returns 404."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/themes/warhammer40k/assets/nonexistent.png")

        # May return 404 (asset not found) or 404 (theme not found)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_theme_asset_content_type():
    """Test asset serving includes correct Content-Type."""
    # This test would require actual theme setup
    # Testing the _get_media_type function instead
    from backend.app.api.routes.themes import _get_media_type

    assert _get_media_type(Path("logo.png")) == "image/png"
    assert _get_media_type(Path("background.jpg")) == "image/jpeg"
    assert _get_media_type(Path("icon.svg")) == "image/svg+xml"
    assert _get_media_type(Path("font.woff2")) == "font/woff2"
    assert _get_media_type(Path("unknown.xyz")) == "application/octet-stream"
```

### Validation Commands

```bash
# Start the server
cd backend
uvicorn app.main:app --reload

# Test endpoints manually
curl http://localhost:8000/api/v1/themes
curl http://localhost:8000/api/v1/themes/warhammer40k
curl http://localhost:8000/api/v1/themes/warhammer40k/assets/logo.png

# Test error cases
curl http://localhost:8000/api/v1/themes/nonexistent
curl http://localhost:8000/api/v1/themes/warhammer40k/assets/../../../etc/passwd

# Run API tests
pytest tests/test_themes_api.py -v

# Check type hints
mypy app/api/routes/themes.py

# Run linting
ruff check app/api/routes/

# Check API docs
# Visit: http://localhost:8000/docs
```

### Success Indicators

✅ List endpoint returns all available themes
✅ Get endpoint returns complete theme configuration
✅ Asset endpoint serves files with correct Content-Type
✅ 404 errors for nonexistent themes/assets
✅ 400 error for invalid asset paths (directory traversal)
✅ All tests pass
✅ No type errors from mypy
✅ API docs show all endpoints with examples

---

## Task 2.5: Story Library UI - Components

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 2.2 (Story API), Task 1.7 (Frontend Setup)

### Context

You are building the React/TypeScript UI components for the story library page. This is the main interface where users browse, search, and filter existing game stories before playing them. The components must be responsive, accessible, and handle various states (loading, empty, error).

**Project Documentation**:

- UI Design: [USER_JOURNEYS_DIAGRAMS.md](./USER_JOURNEYS_DIAGRAMS.md) Section "Story Library"
- Architecture: [ARCHITECTURAL_DESIGN.md](./ARCHITECTURAL_DESIGN.md) Section 6.2
- Component Patterns: Frontend best practices for React with TypeScript

### Your Mission

Create reusable, accessible React components for the story library with proper TypeScript types, loading states, and responsive design. Follow modern React patterns (functional components, hooks).

### Deliverables

```
frontend/
├── src/
│   ├── components/
│   │   └── library/
│   │       ├── StoryCard.tsx           # Individual story card
│   │       ├── StoryCard.module.css    # Card styles
│   │       ├── StoryGrid.tsx           # Grid layout
│   │       ├── StoryGrid.module.css    # Grid styles
│   │       ├── SearchBar.tsx           # Search input
│   │       ├── SearchBar.module.css    # Search styles
│   │       ├── FilterPanel.tsx         # Filter controls
│   │       ├── FilterPanel.module.css  # Filter styles
│   │       └── index.ts                # Barrel export
│   ├── pages/
│   │   ├── LibraryPage.tsx             # Main library page
│   │   └── LibraryPage.module.css      # Page styles
│   └── types/
│       └── story.ts                    # Story TypeScript interfaces
└── tests/
    └── components/
        └── library/
            ├── StoryCard.test.tsx
            ├── StoryGrid.test.tsx
            ├── SearchBar.test.tsx
            └── FilterPanel.test.tsx
```

### Acceptance Criteria

- [ ] StoryCard displays story metadata (title, description, theme, tags, play count)
- [ ] StoryCard has hover effects and click handler
- [ ] StoryGrid uses responsive CSS Grid (1-4 columns based on viewport)
- [ ] StoryGrid handles loading state (skeleton cards)
- [ ] StoryGrid handles empty state ("No stories found")
- [ ] StoryGrid handles error state
- [ ] SearchBar with debounced input (300ms delay)
- [ ] SearchBar has clear button when text entered
- [ ] FilterPanel with theme dropdown and tag checkboxes
- [ ] FilterPanel has "Clear Filters" button
- [ ] All components use CSS Modules for scoped styling
- [ ] All components are accessible (ARIA labels, keyboard navigation)
- [ ] Component tests with React Testing Library
- [ ] Tests cover rendering, interactions, and states

### Technical Requirements

**TypeScript Types (`types/story.ts`)**:

```typescript
/**
 * Story-related TypeScript interfaces.
 */

export interface Story {
  id: number;
  title: string;
  description: string | null;
  theme_id: string;
  tags: string[];
  game_file_path: string;
  created_at: string;
  updated_at: string;
  play_count: number;
  last_played: string | null;
  prompt: string;
  template_id: string | null;
  iteration_count: number;
  scene_count: number | null;
  item_count: number | null;
  npc_count: number | null;
  puzzle_count: number | null;
}

export interface StoryListResponse {
  items: Story[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface StoryFilters {
  search?: string;
  theme_id?: string;
  tags?: string[];
}
```

**StoryCard Component (`components/library/StoryCard.tsx`)**:

```typescript
import React from 'react';
import styles from './StoryCard.module.css';
import type { Story } from '../../types/story';

interface StoryCardProps {
  story: Story;
  onClick?: (story: Story) => void;
}

export const StoryCard: React.FC<StoryCardProps> = ({ story, onClick }) => {
  const handleClick = () => {
    if (onClick) {
      onClick(story);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  return (
    <div
      className={styles.card}
      onClick={handleClick}
      onKeyPress={handleKeyPress}
      role="button"
      tabIndex={0}
      aria-label={`Story: ${story.title}`}
    >
      <div className={styles.header}>
        <h3 className={styles.title}>{story.title}</h3>
        <span className={styles.theme} aria-label={`Theme: ${story.theme_id}`}>
          {story.theme_id}
        </span>
      </div>

      {story.description && (
        <p className={styles.description}>{story.description}</p>
      )}

      <div className={styles.tags} aria-label="Tags">
        {story.tags.map((tag) => (
          <span key={tag} className={styles.tag}>
            {tag}
          </span>
        ))}
      </div>

      <div className={styles.footer}>
        <div className={styles.stats}>
          <span className={styles.stat} aria-label={`Played ${story.play_count} times`}>
            ▶ {story.play_count}
          </span>
          {story.scene_count && (
            <span className={styles.stat} aria-label={`${story.scene_count} scenes`}>
              📍 {story.scene_count}
            </span>
          )}
        </div>
        <time className={styles.date} dateTime={story.created_at}>
          {new Date(story.created_at).toLocaleDateString()}
        </time>
      </div>
    </div>
  );
};
```

**StoryCard Styles (`components/library/StoryCard.module.css`)**:

```css
.card {
  background: var(--color-surface, #2d2d2d);
  border: 1px solid var(--color-border, #444);
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card:hover {
  border-color: var(--color-primary, #8B0000);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transform: translateY(-2px);
}

.card:focus {
  outline: 2px solid var(--color-primary, #8B0000);
  outline-offset: 2px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.title {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-text, #e0e0e0);
  flex: 1;
}

.theme {
  background: var(--color-primary, #8B0000);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  text-transform: uppercase;
  white-space: nowrap;
}

.description {
  margin: 0;
  color: var(--color-text-secondary, #a0a0a0);
  font-size: 0.875rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  background: var(--color-surface-light, #3d3d3d);
  color: var(--color-text-secondary, #a0a0a0);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border, #444);
}

.stats {
  display: flex;
  gap: 1rem;
}

.stat {
  color: var(--color-text-secondary, #a0a0a0);
  font-size: 0.875rem;
}

.date {
  color: var(--color-text-secondary, #a0a0a0);
  font-size: 0.75rem;
}
```

**StoryGrid Component (`components/library/StoryGrid.tsx`)**:

```typescript
import React from 'react';
import { StoryCard } from './StoryCard';
import styles from './StoryGrid.module.css';
import type { Story } from '../../types/story';

interface StoryGridProps {
  stories: Story[];
  loading?: boolean;
  error?: string | null;
  onStoryClick?: (story: Story) => void;
}

export const StoryGrid: React.FC<StoryGridProps> = ({
  stories,
  loading = false,
  error = null,
  onStoryClick,
}) => {
  // Loading state
  if (loading) {
    return (
      <div className={styles.grid} aria-busy="true" aria-label="Loading stories">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className={styles.skeleton} aria-hidden="true">
            <div className={styles.skeletonHeader} />
            <div className={styles.skeletonText} />
            <div className={styles.skeletonText} />
            <div className={styles.skeletonFooter} />
          </div>
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={styles.error} role="alert">
        <p className={styles.errorIcon}>⚠️</p>
        <p className={styles.errorMessage}>{error}</p>
        <button
          className={styles.retryButton}
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      </div>
    );
  }

  // Empty state
  if (stories.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyIcon}>📚</p>
        <p className={styles.emptyMessage}>No stories found</p>
        <p className={styles.emptyHint}>Try adjusting your filters or create a new story</p>
      </div>
    );
  }

  // Success state
  return (
    <div className={styles.grid} role="list" aria-label="Story library">
      {stories.map((story) => (
        <StoryCard
          key={story.id}
          story={story}
          onClick={onStoryClick}
        />
      ))}
    </div>
  );
};
```

**StoryGrid Styles (`components/library/StoryGrid.module.css`)**:

```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 1rem 0;
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

/* Skeleton Loading */
.skeleton {
  background: var(--color-surface, #2d2d2d);
  border: 1px solid var(--color-border, #444);
  border-radius: 8px;
  padding: 1.5rem;
  animation: pulse 1.5s ease-in-out infinite;
}

.skeletonHeader {
  height: 1.5rem;
  background: var(--color-surface-light, #3d3d3d);
  border-radius: 4px;
  margin-bottom: 1rem;
}

.skeletonText {
  height: 0.875rem;
  background: var(--color-surface-light, #3d3d3d);
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.skeletonFooter {
  height: 1rem;
  background: var(--color-surface-light, #3d3d3d);
  border-radius: 4px;
  margin-top: 1rem;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Error State */
.error {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--color-text, #e0e0e0);
}

.errorIcon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.errorMessage {
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
  color: var(--color-error, #dc143c);
}

.retryButton {
  background: var(--color-primary, #8B0000);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.retryButton:hover {
  background: var(--color-primary-dark, #6B0000);
}

/* Empty State */
.empty {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--color-text, #e0e0e0);
}

.emptyIcon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.emptyMessage {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.emptyHint {
  color: var(--color-text-secondary, #a0a0a0);
  font-size: 1rem;
}
```

**SearchBar Component (`components/library/SearchBar.tsx`)**:

```typescript
import React, { useState, useEffect, useCallback } from 'react';
import styles from './SearchBar.module.css';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  debounceMs?: number;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = 'Search stories...',
  debounceMs = 300,
}) => {
  const [value, setValue] = useState('');

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(value);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [value, debounceMs, onSearch]);

  const handleClear = useCallback(() => {
    setValue('');
    onSearch('');
  }, [onSearch]);

  return (
    <div className={styles.container}>
      <div className={styles.inputWrapper}>
        <span className={styles.icon} aria-hidden="true">
          🔍
        </span>
        <input
          type="text"
          className={styles.input}
          placeholder={placeholder}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          aria-label="Search stories"
        />
        {value && (
          <button
            className={styles.clearButton}
            onClick={handleClear}
            aria-label="Clear search"
            type="button"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
};
```

**SearchBar Styles (`components/library/SearchBar.module.css`)**:

```css
.container {
  margin-bottom: 1.5rem;
}

.inputWrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.icon {
  position: absolute;
  left: 1rem;
  font-size: 1.25rem;
  pointer-events: none;
}

.input {
  width: 100%;
  padding: 0.75rem 3rem 0.75rem 3rem;
  background: var(--color-surface, #2d2d2d);
  border: 1px solid var(--color-border, #444);
  border-radius: 8px;
  color: var(--color-text, #e0e0e0);
  font-size: 1rem;
  transition: border-color 0.2s;
}

.input:focus {
  outline: none;
  border-color: var(--color-primary, #8B0000);
}

.input::placeholder {
  color: var(--color-text-secondary, #a0a0a0);
}

.clearButton {
  position: absolute;
  right: 1rem;
  background: transparent;
  border: none;
  color: var(--color-text-secondary, #a0a0a0);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.clearButton:hover {
  color: var(--color-text, #e0e0e0);
}

.clearButton:focus {
  outline: 2px solid var(--color-primary, #8B0000);
  outline-offset: 2px;
  border-radius: 2px;
}
```

**FilterPanel Component (`components/library/FilterPanel.tsx`)**:

```typescript
import React from 'react';
import styles from './FilterPanel.module.css';
import type { StoryFilters } from '../../types/story';

interface FilterPanelProps {
  filters: StoryFilters;
  onFilterChange: (filters: StoryFilters) => void;
  availableThemes?: string[];
  availableTags?: string[];
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onFilterChange,
  availableThemes = ['warhammer40k', 'cyberpunk'],
  availableTags = ['horror', 'action', 'exploration', 'mystery'],
}) => {
  const handleThemeChange = (themeId: string) => {
    onFilterChange({
      ...filters,
      theme_id: themeId === '' ? undefined : themeId,
    });
  };

  const handleTagToggle = (tag: string) => {
    const currentTags = filters.tags || [];
    const newTags = currentTags.includes(tag)
      ? currentTags.filter((t) => t !== tag)
      : [...currentTags, tag];

    onFilterChange({
      ...filters,
      tags: newTags.length > 0 ? newTags : undefined,
    });
  };

  const handleClearFilters = () => {
    onFilterChange({});
  };

  const hasActiveFilters = filters.theme_id || (filters.tags && filters.tags.length > 0);

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h3 className={styles.title}>Filters</h3>
        {hasActiveFilters && (
          <button
            className={styles.clearButton}
            onClick={handleClearFilters}
            aria-label="Clear all filters"
          >
            Clear All
          </button>
        )}
      </div>

      <div className={styles.section}>
        <label htmlFor="theme-select" className={styles.label}>
          Theme
        </label>
        <select
          id="theme-select"
          className={styles.select}
          value={filters.theme_id || ''}
          onChange={(e) => handleThemeChange(e.target.value)}
        >
          <option value="">All Themes</option>
          {availableThemes.map((theme) => (
            <option key={theme} value={theme}>
              {theme}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.section}>
        <span className={styles.label}>Tags</span>
        <div className={styles.tagGrid} role="group" aria-label="Filter by tags">
          {availableTags.map((tag) => (
            <label key={tag} className={styles.tagLabel}>
              <input
                type="checkbox"
                className={styles.checkbox}
                checked={filters.tags?.includes(tag) || false}
                onChange={() => handleTagToggle(tag)}
                aria-label={`Filter by ${tag}`}
              />
              <span className={styles.tagText}>{tag}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};
```

**FilterPanel Styles (`components/library/FilterPanel.module.css`)**:

```css
.panel {
  background: var(--color-surface, #2d2d2d);
  border: 1px solid var(--color-border, #444);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.title {
  margin: 0;
  font-size: 1.125rem;
  color: var(--color-text, #e0e0e0);
}

.clearButton {
  background: transparent;
  border: 1px solid var(--color-border, #444);
  color: var(--color-text-secondary, #a0a0a0);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.clearButton:hover {
  border-color: var(--color-primary, #8B0000);
  color: var(--color-text, #e0e0e0);
}

.section {
  margin-bottom: 1.5rem;
}

.section:last-child {
  margin-bottom: 0;
}

.label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--color-text, #e0e0e0);
  font-size: 0.875rem;
  font-weight: 500;
}

.select {
  width: 100%;
  padding: 0.75rem;
  background: var(--color-background, #1a1a1a);
  border: 1px solid var(--color-border, #444);
  border-radius: 4px;
  color: var(--color-text, #e0e0e0);
  font-size: 1rem;
  cursor: pointer;
}

.select:focus {
  outline: none;
  border-color: var(--color-primary, #8B0000);
}

.tagGrid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
}

.tagLabel {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.tagLabel:hover {
  background: var(--color-surface-light, #3d3d3d);
}

.checkbox {
  cursor: pointer;
  width: 1rem;
  height: 1rem;
  accent-color: var(--color-primary, #8B0000);
}

.tagText {
  color: var(--color-text-secondary, #a0a0a0);
  font-size: 0.875rem;
}

.tagLabel:has(.checkbox:checked) .tagText {
  color: var(--color-text, #e0e0e0);
  font-weight: 500;
}
```

**Barrel Export (`components/library/index.ts`)**:

```typescript
export { StoryCard } from './StoryCard';
export { StoryGrid } from './StoryGrid';
export { SearchBar } from './SearchBar';
export { FilterPanel } from './FilterPanel';
```

**Library Page (`pages/LibraryPage.tsx`)**:

```typescript
import React, { useState } from 'react';
import { SearchBar, FilterPanel, StoryGrid } from '../components/library';
import type { Story, StoryFilters } from '../types/story';
import styles from './LibraryPage.module.css';

export const LibraryPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<StoryFilters>({});

  // TODO: Connect to real data in Task 2.6
  const stories: Story[] = [];
  const loading = false;
  const error = null;

  const handleStoryClick = (story: Story) => {
    console.log('Story clicked:', story.id);
    // TODO: Navigate to play page
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Story Library</h1>
        <button className={styles.createButton}>
          + Create New Story
        </button>
      </header>

      <div className={styles.content}>
        <aside className={styles.sidebar}>
          <FilterPanel filters={filters} onFilterChange={setFilters} />
        </aside>

        <main className={styles.main}>
          <SearchBar onSearch={setSearch} />
          <StoryGrid
            stories={stories}
            loading={loading}
            error={error}
            onStoryClick={handleStoryClick}
          />
        </main>
      </div>
    </div>
  );
};
```

**Library Page Styles (`pages/LibraryPage.module.css`)**:

```css
.page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.title {
  margin: 0;
  font-size: 2rem;
  color: var(--color-text, #e0e0e0);
}

.createButton {
  background: var(--color-primary, #8B0000);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.createButton:hover {
  background: var(--color-primary-dark, #6B0000);
}

.content {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
}

@media (max-width: 1024px) {
  .content {
    grid-template-columns: 1fr;
  }

  .sidebar {
    order: 2;
  }

  .main {
    order: 1;
  }
}

.sidebar {
  position: sticky;
  top: 2rem;
  height: fit-content;
}

.main {
  min-width: 0;
}
```

### Testing Requirements

**Component Tests (`tests/components/library/StoryCard.test.tsx`)**:

```typescript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { StoryCard } from '../../../src/components/library/StoryCard';
import type { Story } from '../../../src/types/story';

const mockStory: Story = {
  id: 1,
  title: 'Test Horror Story',
  description: 'A spooky test story',
  theme_id: 'warhammer40k',
  tags: ['horror', 'atmospheric'],
  game_file_path: 'data/test/game.json',
  created_at: '2024-01-15T10:00:00Z',
  updated_at: '2024-01-15T10:00:00Z',
  play_count: 5,
  last_played: null,
  prompt: 'Test prompt',
  template_id: null,
  iteration_count: 1,
  scene_count: 10,
  item_count: 5,
  npc_count: 3,
  puzzle_count: 2,
};

describe('StoryCard', () => {
  it('renders story information correctly', () => {
    render(<StoryCard story={mockStory} />);

    expect(screen.getByText('Test Horror Story')).toBeInTheDocument();
    expect(screen.getByText('A spooky test story')).toBeInTheDocument();
    expect(screen.getByText('warhammer40k')).toBeInTheDocument();
    expect(screen.getByText('horror')).toBeInTheDocument();
    expect(screen.getByText('atmospheric')).toBeInTheDocument();
  });

  it('calls onClick when card is clicked', () => {
    const handleClick = vi.fn();
    render(<StoryCard story={mockStory} onClick={handleClick} />);

    fireEvent.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledWith(mockStory);
  });

  it('calls onClick when Enter key is pressed', () => {
    const handleClick = vi.fn();
    render(<StoryCard story={mockStory} onClick={handleClick} />);

    fireEvent.keyPress(screen.getByRole('button'), { key: 'Enter' });

    expect(handleClick).toHaveBeenCalledWith(mockStory);
  });

  it('displays play count', () => {
    render(<StoryCard story={mockStory} />);

    expect(screen.getByLabelText(/played 5 times/i)).toBeInTheDocument();
  });

  it('displays scene count when available', () => {
    render(<StoryCard story={mockStory} />);

    expect(screen.getByLabelText(/10 scenes/i)).toBeInTheDocument();
  });

  it('handles missing description gracefully', () => {
    const storyWithoutDescription = { ...mockStory, description: null };
    render(<StoryCard story={storyWithoutDescription} />);

    expect(screen.queryByText('A spooky test story')).not.toBeInTheDocument();
  });
});
```

**More Tests (`tests/components/library/SearchBar.test.tsx`)**:

```typescript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SearchBar } from '../../../src/components/library/SearchBar';

describe('SearchBar', () => {
  it('renders with placeholder text', () => {
    render(<SearchBar onSearch={vi.fn()} />);

    expect(screen.getByPlaceholderText('Search stories...')).toBeInTheDocument();
  });

  it('debounces search input', async () => {
    const handleSearch = vi.fn();
    render(<SearchBar onSearch={handleSearch} debounceMs={100} />);

    const input = screen.getByRole('textbox');

    fireEvent.change(input, { target: { value: 'test' } });

    // Should not call immediately
    expect(handleSearch).not.toHaveBeenCalled();

    // Should call after debounce delay
    await waitFor(() => {
      expect(handleSearch).toHaveBeenCalledWith('test');
    }, { timeout: 200 });
  });

  it('shows clear button when text is entered', () => {
    render(<SearchBar onSearch={vi.fn()} />);

    const input = screen.getByRole('textbox');

    expect(screen.queryByLabelText('Clear search')).not.toBeInTheDocument();

    fireEvent.change(input, { target: { value: 'test' } });

    expect(screen.getByLabelText('Clear search')).toBeInTheDocument();
  });

  it('clears search when clear button is clicked', () => {
    const handleSearch = vi.fn();
    render(<SearchBar onSearch={handleSearch} />);

    const input = screen.getByRole('textbox') as HTMLInputElement;

    fireEvent.change(input, { target: { value: 'test' } });

    const clearButton = screen.getByLabelText('Clear search');
    fireEvent.click(clearButton);

    expect(input.value).toBe('');
    expect(handleSearch).toHaveBeenCalledWith('');
  });
});
```

### Validation Commands

```bash
# Install dependencies
cd frontend
npm install

# Run type checking
npm run type-check

# Run linting
npm run lint

# Run component tests
npm test -- components/library

# Run tests with coverage
npm test -- components/library --coverage

# Start development server
npm run dev

# Build for production
npm run build
```

### Success Indicators

✅ All components render without errors
✅ StoryCard displays all story information
✅ StoryGrid handles loading/empty/error states
✅ SearchBar debounces input correctly (300ms)
✅ FilterPanel updates filters on interaction
✅ Responsive design works on mobile/tablet/desktop
✅ All components are keyboard accessible
✅ ARIA labels present for screen readers
✅ All component tests pass
✅ No TypeScript errors
✅ No linting errors

---

## Task 2.6: Story Library UI - Integration

**Priority**: P0
**Effort**: 1 day
**Dependencies**: Task 2.5 (Story Library UI - Components)

### Context

You are integrating the story library UI components with the backend API. This involves creating React Context for state management, custom hooks for API calls, and connecting the library page to real data. The integration should handle loading states, errors, pagination, and real-time filtering.

**Project Documentation**:

- API Specification: [API_SPECIFICATION.md](./API_SPECIFICATION.md) Section "Stories"
- Architecture: [ARCHITECTURAL_DESIGN.md](./ARCHITECTURAL_DESIGN.md) Section 6.3
- Frontend Structure: React Context + Hooks pattern

### Your Mission

Create a robust data layer that fetches stories from the API, manages application state, and provides a clean interface for components to consume story data with proper error handling and caching.

### Deliverables

```
frontend/
├── src/
│   ├── contexts/
│   │   ├── StoryContext.tsx        # Story state management
│   │   └── index.ts                # Context barrel export
│   ├── hooks/
│   │   ├── useStories.ts           # Story fetching hook
│   │   ├── useStory.ts             # Single story hook
│   │   └── index.ts                # Hooks barrel export
│   ├── services/
│   │   ├── api.ts                  # Base API client
│   │   ├── storyApi.ts             # Story API methods
│   │   └── index.ts                # Services barrel export
│   └── pages/
│       └── LibraryPage.tsx         # Updated with context integration
└── tests/
    ├── contexts/
    │   └── StoryContext.test.tsx
    └── hooks/
        ├── useStories.test.ts
        └── useStory.test.ts
```

### Acceptance Criteria

- [ ] StoryContext provides stories, loading, error, filters state
- [ ] StoryContext provides methods: fetchStories, setFilters, setSearch
- [ ] useStories hook with automatic fetching and pagination
- [ ] useStory hook for fetching single story by ID
- [ ] API client with base URL configuration and error handling
- [ ] StoryAPI service methods: getStories, getStory, deleteStory
- [ ] LibraryPage integrated with StoryContext
- [ ] Auto-fetch stories on component mount
- [ ] Debounced search triggers API call
- [ ] Filter changes trigger API call
- [ ] Pagination support (load more)
- [ ] Context tests with mock API
- [ ] Hook tests with React Testing Library
- [ ] E2E test for library page flow

### Technical Requirements

**API Client (`services/api.ts`)**:

```typescript
/**
 * Base API client for making HTTP requests.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export interface APIResponse<T> {
  data: T;
}

export class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          response.status,
          response.statusText,
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }

      // Network error or other fetch error
      throw new Error(
        error instanceof Error ? error.message : 'Network request failed'
      );
    }
  }

  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const queryString = params
      ? '?' + new URLSearchParams(params).toString()
      : '';

    return this.request<T>(`${endpoint}${queryString}`, {
      method: 'GET',
    });
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }
}

export const apiClient = new APIClient();
```

**Story API Service (`services/storyApi.ts`)**:

```typescript
/**
 * Story API service methods.
 */
import { apiClient } from './api';
import type { Story, StoryListResponse, StoryFilters } from '../types/story';

export const storyApi = {
  /**
   * Get paginated list of stories with optional filters.
   */
  async getStories(
    page: number = 1,
    pageSize: number = 20,
    filters?: StoryFilters
  ): Promise<StoryListResponse> {
    const params: Record<string, any> = {
      page,
      page_size: pageSize,
    };

    if (filters?.search) {
      params.search = filters.search;
    }

    if (filters?.theme_id) {
      params.theme_id = filters.theme_id;
    }

    if (filters?.tags && filters.tags.length > 0) {
      params.tags = filters.tags.join(',');
    }

    return apiClient.get<StoryListResponse>('/api/v1/stories', params);
  },

  /**
   * Get single story by ID.
   */
  async getStory(storyId: number): Promise<Story> {
    return apiClient.get<Story>(`/api/v1/stories/${storyId}`);
  },

  /**
   * Get story game content (game.json).
   */
  async getStoryContent(storyId: number): Promise<any> {
    return apiClient.get<any>(`/api/v1/stories/${storyId}/content`);
  },

  /**
   * Delete story by ID.
   */
  async deleteStory(storyId: number): Promise<void> {
    return apiClient.delete<void>(`/api/v1/stories/${storyId}`);
  },
};
```

**Story Context (`contexts/StoryContext.tsx`)**:

```typescript
/**
 * Story context for managing story state across the application.
 */
import React, { createContext, useContext, useState, useCallback } from 'react';
import { storyApi } from '../services/storyApi';
import type { Story, StoryListResponse, StoryFilters } from '../types/story';

interface StoryContextState {
  // State
  stories: Story[];
  loading: boolean;
  error: string | null;
  filters: StoryFilters;
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };

  // Actions
  fetchStories: () => Promise<void>;
  setFilters: (filters: StoryFilters) => void;
  setPage: (page: number) => void;
  refreshStories: () => Promise<void>;
}

const StoryContext = createContext<StoryContextState | undefined>(undefined);

interface StoryProviderProps {
  children: React.ReactNode;
}

export const StoryProvider: React.FC<StoryProviderProps> = ({ children }) => {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFiltersState] = useState<StoryFilters>({});
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0,
  });

  const fetchStories = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response: StoryListResponse = await storyApi.getStories(
        pagination.page,
        pagination.pageSize,
        filters
      );

      setStories(response.items);
      setPagination({
        page: response.page,
        pageSize: response.page_size,
        total: response.total,
        totalPages: response.total_pages,
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to fetch stories';
      setError(errorMessage);
      console.error('Error fetching stories:', err);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.pageSize, filters]);

  const setFilters = useCallback((newFilters: StoryFilters) => {
    setFiltersState(newFilters);
    setPagination((prev) => ({ ...prev, page: 1 })); // Reset to page 1 on filter change
  }, []);

  const setPage = useCallback((page: number) => {
    setPagination((prev) => ({ ...prev, page }));
  }, []);

  const refreshStories = useCallback(async () => {
    await fetchStories();
  }, [fetchStories]);

  const value: StoryContextState = {
    stories,
    loading,
    error,
    filters,
    pagination,
    fetchStories,
    setFilters,
    setPage,
    refreshStories,
  };

  return (
    <StoryContext.Provider value={value}>{children}</StoryContext.Provider>
  );
};

export const useStoryContext = (): StoryContextState => {
  const context = useContext(StoryContext);
  if (!context) {
    throw new Error('useStoryContext must be used within StoryProvider');
  }
  return context;
};
```

**useStories Hook (`hooks/useStories.ts`)**:

```typescript
/**
 * Hook for fetching and managing stories list.
 */
import { useEffect } from 'react';
import { useStoryContext } from '../contexts/StoryContext';

export const useStories = () => {
  const context = useStoryContext();

  // Auto-fetch on mount and when filters/page change
  useEffect(() => {
    context.fetchStories();
  }, [context.filters, context.pagination.page]);

  return context;
};
```

**useStory Hook (`hooks/useStory.ts`)**:

```typescript
/**
 * Hook for fetching a single story by ID.
 */
import { useState, useEffect } from 'react';
import { storyApi } from '../services/storyApi';
import type { Story } from '../types/story';

interface UseStoryResult {
  story: Story | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useStory = (storyId: number | null): UseStoryResult => {
  const [story, setStory] = useState<Story | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStory = async () => {
    if (!storyId) {
      setStory(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await storyApi.getStory(storyId);
      setStory(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to fetch story';
      setError(errorMessage);
      console.error('Error fetching story:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStory();
  }, [storyId]);

  return {
    story,
    loading,
    error,
    refetch: fetchStory,
  };
};
```

**Updated Library Page (`pages/LibraryPage.tsx`)**:

```typescript
import React, { useState, useCallback } from 'react';
import { SearchBar, FilterPanel, StoryGrid } from '../components/library';
import { useStories } from '../hooks';
import type { Story, StoryFilters } from '../types/story';
import styles from './LibraryPage.module.css';

export const LibraryPage: React.FC = () => {
  const { stories, loading, error, filters, setFilters } = useStories();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = useCallback(
    (query: string) => {
      setSearchQuery(query);
      setFilters({ ...filters, search: query || undefined });
    },
    [filters, setFilters]
  );

  const handleFilterChange = useCallback(
    (newFilters: StoryFilters) => {
      setFilters({ ...newFilters, search: searchQuery || undefined });
    },
    [searchQuery, setFilters]
  );

  const handleStoryClick = (story: Story) => {
    console.log('Story clicked:', story.id);
    // TODO: Navigate to play page
    // navigate(`/play/${story.id}`);
  };

  const handleCreateStory = () => {
    console.log('Create new story');
    // TODO: Navigate to create page
    // navigate('/create');
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Story Library</h1>
        <button className={styles.createButton} onClick={handleCreateStory}>
          + Create New Story
        </button>
      </header>

      <div className={styles.content}>
        <aside className={styles.sidebar}>
          <FilterPanel filters={filters} onFilterChange={handleFilterChange} />
        </aside>

        <main className={styles.main}>
          <SearchBar onSearch={handleSearch} />
          <StoryGrid
            stories={stories}
            loading={loading}
            error={error}
            onStoryClick={handleStoryClick}
          />
        </main>
      </div>
    </div>
  );
};
```

**App Integration (`App.tsx` - add provider)**:

```typescript
import { StoryProvider } from './contexts/StoryContext';

function App() {
  return (
    <StoryProvider>
      {/* Rest of app */}
    </StoryProvider>
  );
}
```

### Testing Requirements

**Context Tests (`tests/contexts/StoryContext.test.tsx`)**:

```typescript
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { StoryProvider, useStoryContext } from '../../src/contexts/StoryContext';
import { storyApi } from '../../src/services/storyApi';
import { vi } from 'vitest';

vi.mock('../../src/services/storyApi');

const TestComponent = () => {
  const { stories, loading, error, fetchStories } = useStoryContext();

  return (
    <div>
      <div data-testid="loading">{loading ? 'Loading' : 'Not Loading'}</div>
      <div data-testid="error">{error || 'No Error'}</div>
      <div data-testid="count">{stories.length}</div>
      <button onClick={fetchStories}>Fetch</button>
    </div>
  );
};

describe('StoryContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('provides initial state', () => {
    render(
      <StoryProvider>
        <TestComponent />
      </StoryProvider>
    );

    expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading');
    expect(screen.getByTestId('error')).toHaveTextContent('No Error');
    expect(screen.getByTestId('count')).toHaveTextContent('0');
  });

  it('fetches stories successfully', async () => {
    const mockStories = {
      items: [
        { id: 1, title: 'Story 1' },
        { id: 2, title: 'Story 2' },
      ],
      total: 2,
      page: 1,
      page_size: 20,
      total_pages: 1,
    };

    vi.mocked(storyApi.getStories).mockResolvedValue(mockStories);

    render(
      <StoryProvider>
        <TestComponent />
      </StoryProvider>
    );

    fireEvent.click(screen.getByText('Fetch'));

    // Should show loading
    expect(screen.getByTestId('loading')).toHaveTextContent('Loading');

    // Wait for fetch to complete
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading');
    });

    expect(screen.getByTestId('count')).toHaveTextContent('2');
    expect(screen.getByTestId('error')).toHaveTextContent('No Error');
  });

  it('handles fetch errors', async () => {
    vi.mocked(storyApi.getStories).mockRejectedValue(
      new Error('API Error')
    );

    render(
      <StoryProvider>
        <TestComponent />
      </StoryProvider>
    );

    fireEvent.click(screen.getByText('Fetch'));

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('API Error');
    });

    expect(screen.getByTestId('count')).toHaveTextContent('0');
  });
});
```

**Hook Tests (`tests/hooks/useStory.test.ts`)**:

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useStory } from '../../src/hooks/useStory';
import { storyApi } from '../../src/services/storyApi';
import { vi } from 'vitest';

vi.mock('../../src/services/storyApi');

describe('useStory', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches story on mount', async () => {
    const mockStory = {
      id: 1,
      title: 'Test Story',
      description: 'Test description',
    };

    vi.mocked(storyApi.getStory).mockResolvedValue(mockStory as any);

    const { result } = renderHook(() => useStory(1));

    expect(result.current.loading).toBe(true);
    expect(result.current.story).toBe(null);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.story).toEqual(mockStory);
    expect(result.current.error).toBe(null);
  });

  it('handles null storyId', () => {
    const { result } = renderHook(() => useStory(null));

    expect(result.current.story).toBe(null);
    expect(result.current.loading).toBe(false);
    expect(storyApi.getStory).not.toHaveBeenCalled();
  });

  it('handles fetch errors', async () => {
    vi.mocked(storyApi.getStory).mockRejectedValue(
      new Error('Story not found')
    );

    const { result } = renderHook(() => useStory(1));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.story).toBe(null);
    expect(result.current.error).toBe('Story not found');
  });
});
```

### Validation Commands

```bash
# Install dependencies
cd frontend
npm install

# Run type checking
npm run type-check

# Run tests
npm test

# Run integration tests
npm test -- LibraryPage

# Start dev server with backend
# Terminal 1: Start backend
cd ../backend && uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend && npm run dev

# Test the integration
# 1. Open http://localhost:5173/library
# 2. Verify stories load from API
# 3. Test search functionality
# 4. Test filter functionality
# 5. Verify loading states
# 6. Test error handling (stop backend)
```

### Success Indicators

✅ StoryContext provides stories from API
✅ Stories auto-fetch on page mount
✅ Search input triggers debounced API call
✅ Filter changes trigger API call with correct params
✅ Loading state shows skeleton cards
✅ Error state shows error message
✅ Empty state shows "No stories" message
✅ Pagination state updates correctly
✅ All context tests pass
✅ All hook tests pass
✅ Integration with LibraryPage works end-to-end
✅ No TypeScript errors
✅ No console errors in browser

---

## Task 2.7: Theme Selector UI

**Priority**: P1
**Effort**: 1 day
**Dependencies**: Task 2.4 (Theme API), Task 1.3 (Frontend Setup)

### Context

You are implementing the theme selector UI that allows users to dynamically switch between visual themes (Warhammer 40K, Cyberpunk, etc.) at runtime. The theme system uses CSS custom properties (variables) that are updated when the user selects a different theme. Theme preference is persisted to localStorage.

**Project Documentation**:

- Theming System: [THEMING_SYSTEM.md](./THEMING_SYSTEM.md)
- Architecture: [ARCHITECTURAL_DESIGN.md](./ARCHITECTURAL_DESIGN.md) Section 4.2
- Implementation: CSS Variables + React Context

### Your Mission

Create a ThemeContext for managing theme state and a ThemeSelector component for switching themes. Implement CSS variable injection to dynamically update the interface appearance without page reload.

### Deliverables

```
frontend/
├── src/
│   ├── contexts/
│   │   └── ThemeContext.tsx        # Theme state management
│   ├── components/
│   │   └── theme/
│   │       ├── ThemeSelector.tsx   # Theme dropdown component
│   │       ├── ThemeSelector.module.css
│   │       └── index.ts
│   ├── services/
│   │   └── themeApi.ts             # Theme API methods
│   ├── types/
│   │   └── theme.ts                # Theme TypeScript interfaces
│   └── styles/
│       └── themes.css              # Base CSS variable definitions
└── tests/
    ├── contexts/
    │   └── ThemeContext.test.tsx
    └── components/
        └── theme/
            └── ThemeSelector.test.tsx
```

### Acceptance Criteria

- [ ] ThemeContext provides current theme, available themes, and setTheme method
- [ ] ThemeContext loads theme list from API on mount
- [ ] ThemeContext applies CSS variables when theme changes
- [ ] Theme preference persisted to localStorage
- [ ] Default theme (warhammer40k) used on first visit
- [ ] ThemeSelector dropdown component shows all available themes
- [ ] ThemeSelector displays current theme with checkmark
- [ ] CSS variables update instantly on theme change
- [ ] Theme changes affect all themed components
- [ ] Context tests with mock API
- [ ] Component tests with theme changes
- [ ] No flash of unstyled content (FOUC)

### Technical Requirements

**Theme Types (`types/theme.ts`)**:

```typescript
/**
 * Theme-related TypeScript interfaces.
 */

export interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  accent: string;
  error: string;
  success: string;
  warning: string;
  [key: string]: string;
}

export interface ThemeTypography {
  fontFamily: string;
  fontFamilyMono: string;
  fontSize: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    xxl: string;
  };
}

export interface ThemeTerminology {
  story: string;
  stories: string;
  character: string;
  characters: string;
  enemy: string;
  enemies: string;
  item: string;
  items: string;
  location: string;
  locations: string;
  [key: string]: string;
}

export interface ThemeUI {
  welcome: string;
  createStory: string;
  libraryTitle: string;
  playButton: string;
  [key: string]: string;
}

export interface ThemeAssets {
  logo: string;
  background: string;
  icon: string;
  [key: string]: string;
}

export interface Theme {
  id: string;
  name: string;
  description: string;
  colors: ThemeColors;
  typography: ThemeTypography;
  terminology: ThemeTerminology;
  ui: ThemeUI;
  assets: ThemeAssets;
}

export interface ThemeMetadata {
  id: string;
  name: string;
  description: string;
}
```

**Theme API Service (`services/themeApi.ts`)**:

```typescript
/**
 * Theme API service methods.
 */
import { apiClient } from './api';
import type { Theme, ThemeMetadata } from '../types/theme';

export const themeApi = {
  /**
   * Get list of available themes.
   */
  async getThemes(): Promise<ThemeMetadata[]> {
    const response = await apiClient.get<{ data: ThemeMetadata[] }>(
      '/api/v1/themes'
    );
    return response.data;
  },

  /**
   * Get complete theme configuration.
   */
  async getTheme(themeId: string): Promise<Theme> {
    const response = await apiClient.get<{ data: Theme }>(
      `/api/v1/themes/${themeId}`
    );
    return response.data;
  },

  /**
   * Get theme asset URL.
   */
  getAssetUrl(themeId: string, assetPath: string): string {
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    return `${baseURL}/api/v1/themes/${themeId}/assets/${assetPath}`;
  },
};
```

**Theme Context (`contexts/ThemeContext.tsx`)**:

```typescript
/**
 * Theme context for managing visual theme across the application.
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { themeApi } from '../services/themeApi';
import type { Theme, ThemeMetadata } from '../types/theme';

const THEME_STORAGE_KEY = 'selectedThemeId';
const DEFAULT_THEME_ID = 'warhammer40k';

interface ThemeContextState {
  currentTheme: Theme | null;
  availableThemes: ThemeMetadata[];
  loading: boolean;
  error: string | null;
  setTheme: (themeId: string) => Promise<void>;
}

const ThemeContext = createContext<ThemeContextState | undefined>(undefined);

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState<Theme | null>(null);
  const [availableThemes, setAvailableThemes] = useState<ThemeMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Apply theme CSS variables to document root.
   */
  const applyCSSVariables = useCallback((theme: Theme) => {
    const root = document.documentElement;

    // Apply color variables
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });

    // Apply typography variables
    root.style.setProperty('--font-family', theme.typography.fontFamily);
    root.style.setProperty('--font-family-mono', theme.typography.fontFamilyMono);

    Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
      root.style.setProperty(`--font-size-${key}`, value);
    });

    // Update document title terminology
    document.title = `Space Hulk Game - ${theme.name}`;
  }, []);

  /**
   * Load and apply a theme.
   */
  const loadTheme = useCallback(
    async (themeId: string) => {
      try {
        const theme = await themeApi.getTheme(themeId);
        setCurrentTheme(theme);
        applyCSSVariables(theme);
        localStorage.setItem(THEME_STORAGE_KEY, themeId);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to load theme';
        setError(errorMessage);
        console.error('Error loading theme:', err);
      }
    },
    [applyCSSVariables]
  );

  /**
   * Change the current theme.
   */
  const setTheme = useCallback(
    async (themeId: string) => {
      setLoading(true);
      setError(null);
      await loadTheme(themeId);
      setLoading(false);
    },
    [loadTheme]
  );

  /**
   * Initialize theme system on mount.
   */
  useEffect(() => {
    const initializeThemes = async () => {
      setLoading(true);
      setError(null);

      try {
        // Load available themes list
        const themes = await themeApi.getThemes();
        setAvailableThemes(themes);

        // Determine which theme to load
        const savedThemeId = localStorage.getItem(THEME_STORAGE_KEY);
        const themeToLoad = savedThemeId || DEFAULT_THEME_ID;

        // Verify theme exists
        const themeExists = themes.some((t) => t.id === themeToLoad);
        const finalThemeId = themeExists ? themeToLoad : DEFAULT_THEME_ID;

        // Load the theme
        await loadTheme(finalThemeId);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to initialize themes';
        setError(errorMessage);
        console.error('Error initializing themes:', err);
      } finally {
        setLoading(false);
      }
    };

    initializeThemes();
  }, [loadTheme]);

  const value: ThemeContextState = {
    currentTheme,
    availableThemes,
    loading,
    error,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextState => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
```

**ThemeSelector Component (`components/theme/ThemeSelector.tsx`)**:

```typescript
import React, { useState, useRef, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import styles from './ThemeSelector.module.css';

export const ThemeSelector: React.FC = () => {
  const { currentTheme, availableThemes, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleThemeSelect = async (themeId: string) => {
    await setTheme(themeId);
    setIsOpen(false);
  };

  const handleKeyDown = (event: React.KeyboardEvent, themeId: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleThemeSelect(themeId);
    }
  };

  if (!currentTheme) {
    return null;
  }

  return (
    <div className={styles.container} ref={dropdownRef}>
      <button
        className={styles.trigger}
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label="Select theme"
      >
        <span className={styles.triggerIcon}>🎨</span>
        <span className={styles.triggerText}>{currentTheme.name}</span>
        <span className={styles.triggerArrow}>{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className={styles.dropdown} role="listbox">
          {availableThemes.map((theme) => (
            <div
              key={theme.id}
              className={`${styles.option} ${
                theme.id === currentTheme.id ? styles.optionSelected : ''
              }`}
              role="option"
              aria-selected={theme.id === currentTheme.id}
              onClick={() => handleThemeSelect(theme.id)}
              onKeyDown={(e) => handleKeyDown(e, theme.id)}
              tabIndex={0}
            >
              <div className={styles.optionContent}>
                <span className={styles.optionName}>{theme.name}</span>
                <span className={styles.optionDescription}>
                  {theme.description}
                </span>
              </div>
              {theme.id === currentTheme.id && (
                <span className={styles.optionCheck} aria-hidden="true">
                  ✓
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

**ThemeSelector Styles (`components/theme/ThemeSelector.module.css`)**:

```css
.container {
  position: relative;
  display: inline-block;
}

.trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-surface, #2d2d2d);
  border: 1px solid var(--color-border, #444);
  border-radius: 4px;
  color: var(--color-text, #e0e0e0);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.trigger:hover {
  border-color: var(--color-primary, #8B0000);
}

.trigger:focus {
  outline: 2px solid var(--color-primary, #8B0000);
  outline-offset: 2px;
}

.triggerIcon {
  font-size: 1.125rem;
}

.triggerText {
  font-weight: 500;
}

.triggerArrow {
  font-size: 0.75rem;
  margin-left: 0.25rem;
}

.dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 250px;
  background: var(--color-surface, #2d2d2d);
  border: 1px solid var(--color-border, #444);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  overflow: hidden;
}

.option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.option:hover,
.option:focus {
  background: var(--color-surface-light, #3d3d3d);
  outline: none;
}

.optionSelected {
  background: var(--color-surface-light, #3d3d3d);
}

.optionContent {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.optionName {
  color: var(--color-text, #e0e0e0);
  font-weight: 500;
  font-size: 0.875rem;
}

.optionDescription {
  color: var(--color-text-secondary, #a0a0a0);
  font-size: 0.75rem;
}

.optionCheck {
  color: var(--color-primary, #8B0000);
  font-size: 1.125rem;
  font-weight: bold;
}
```

**Base CSS Variables (`styles/themes.css`)**:

```css
/**
 * Base CSS custom properties (variables) for theming.
 * These are overridden at runtime by ThemeContext.
 */

:root {
  /* Colors - Default (Warhammer 40K) */
  --color-primary: #8B0000;
  --color-secondary: #C0C0C0;
  --color-background: #1A1A1A;
  --color-surface: #2D2D2D;
  --color-surface-light: #3D3D3D;
  --color-text: #E0E0E0;
  --color-text-secondary: #A0A0A0;
  --color-accent: #FFD700;
  --color-error: #FF4444;
  --color-success: #44FF44;
  --color-warning: #FFAA00;
  --color-border: #444444;

  /* Typography */
  --font-family: 'Cinzel', 'Georgia', serif;
  --font-family-mono: 'Courier New', monospace;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-xxl: 1.5rem;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Border radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-base: 0.2s ease;
  --transition-slow: 0.3s ease;
}
```

### Testing Requirements

**Context Tests (`tests/contexts/ThemeContext.test.tsx`)**:

```typescript
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../../src/contexts/ThemeContext';
import { themeApi } from '../../src/services/themeApi';
import { vi } from 'vitest';

vi.mock('../../src/services/themeApi');

const TestComponent = () => {
  const { currentTheme, availableThemes, setTheme, loading } = useTheme();

  return (
    <div>
      <div data-testid="loading">{loading ? 'Loading' : 'Loaded'}</div>
      <div data-testid="current-theme">{currentTheme?.name || 'None'}</div>
      <div data-testid="theme-count">{availableThemes.length}</div>
      <button onClick={() => setTheme('cyberpunk')}>Change Theme</button>
    </div>
  );
};

describe('ThemeContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('loads default theme on mount', async () => {
    const mockThemes = [
      { id: 'warhammer40k', name: 'Warhammer 40K', description: 'Grimdark' },
      { id: 'cyberpunk', name: 'Cyberpunk', description: 'High-tech' },
    ];

    const mockTheme = {
      id: 'warhammer40k',
      name: 'Warhammer 40,000',
      description: 'Grimdark',
      colors: { primary: '#8B0000' },
      typography: { fontFamily: 'Cinzel', fontSize: {} },
      terminology: {},
      ui: {},
      assets: {},
    };

    vi.mocked(themeApi.getThemes).mockResolvedValue(mockThemes);
    vi.mocked(themeApi.getTheme).mockResolvedValue(mockTheme as any);

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Loaded');
    });

    expect(screen.getByTestId('current-theme')).toHaveTextContent('Warhammer 40,000');
    expect(screen.getByTestId('theme-count')).toHaveTextContent('2');
  });

  it('persists theme selection to localStorage', async () => {
    const mockTheme = {
      id: 'cyberpunk',
      name: 'Cyberpunk',
      colors: {},
      typography: { fontFamily: 'Orbitron', fontSize: {} },
    };

    vi.mocked(themeApi.getTheme).mockResolvedValue(mockTheme as any);

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Loaded');
    });

    fireEvent.click(screen.getByText('Change Theme'));

    await waitFor(() => {
      expect(localStorage.getItem('selectedThemeId')).toBe('cyberpunk');
    });
  });

  it('applies CSS variables when theme changes', async () => {
    const mockTheme = {
      id: 'cyberpunk',
      name: 'Cyberpunk',
      colors: { primary: '#FF00FF', background: '#0A0A0A' },
      typography: { fontFamily: 'Orbitron', fontFamilyMono: 'Mono', fontSize: { base: '1rem' } },
    };

    vi.mocked(themeApi.getTheme).mockResolvedValue(mockTheme as any);

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Loaded');
    });

    fireEvent.click(screen.getByText('Change Theme'));

    await waitFor(() => {
      const root = document.documentElement;
      expect(root.style.getPropertyValue('--color-primary')).toBe('#FF00FF');
      expect(root.style.getPropertyValue('--font-family')).toBe('Orbitron');
    });
  });
});
```

**Component Tests (`tests/components/theme/ThemeSelector.test.tsx`)**:

```typescript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeSelector } from '../../../src/components/theme/ThemeSelector';
import { ThemeProvider } from '../../../src/contexts/ThemeContext';
import { themeApi } from '../../../src/services/themeApi';
import { vi } from 'vitest';

vi.mock('../../../src/services/themeApi');

describe('ThemeSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    const mockThemes = [
      { id: 'warhammer40k', name: 'Warhammer 40K', description: 'Grimdark' },
      { id: 'cyberpunk', name: 'Cyberpunk', description: 'High-tech' },
    ];

    const mockTheme = {
      id: 'warhammer40k',
      name: 'Warhammer 40,000',
      description: 'Grimdark',
      colors: {},
      typography: { fontSize: {} },
    };

    vi.mocked(themeApi.getThemes).mockResolvedValue(mockThemes);
    vi.mocked(themeApi.getTheme).mockResolvedValue(mockTheme as any);
  });

  it('displays current theme name', async () => {
    render(
      <ThemeProvider>
        <ThemeSelector />
      </ThemeProvider>
    );

    await screen.findByText('Warhammer 40,000');

    expect(screen.getByText('Warhammer 40,000')).toBeInTheDocument();
  });

  it('opens dropdown when clicked', async () => {
    render(
      <ThemeProvider>
        <ThemeSelector />
      </ThemeProvider>
    );

    const trigger = await screen.findByLabelText('Select theme');

    fireEvent.click(trigger);

    expect(screen.getByText('Grimdark')).toBeInTheDocument();
    expect(screen.getByText('High-tech')).toBeInTheDocument();
  });

  it('shows checkmark on current theme', async () => {
    render(
      <ThemeProvider>
        <ThemeSelector />
      </ThemeProvider>
    );

    const trigger = await screen.findByLabelText('Select theme');
    fireEvent.click(trigger);

    const selected = screen.getByRole('option', { selected: true });

    expect(selected).toHaveTextContent('✓');
  });
});
```

### Validation Commands

```bash
# Install dependencies
cd frontend
npm install

# Run type checking
npm run type-check

# Run tests
npm test -- theme

# Start dev server
npm run dev

# Test theme switching
# 1. Open http://localhost:5173
# 2. Click theme selector
# 3. Select different theme
# 4. Verify CSS variables update
# 5. Verify theme persists on reload
# 6. Check localStorage in DevTools
```

### Success Indicators

✅ ThemeSelector component renders correctly
✅ Available themes load from API
✅ Current theme displays in selector
✅ Dropdown shows all available themes
✅ Theme selection updates CSS variables immediately
✅ No visual flash when changing themes
✅ Theme preference persists to localStorage
✅ Page reload uses saved theme
✅ All themed components update colors
✅ All tests pass
✅ No TypeScript errors
✅ Theme works across all pages

---

## Task 2.8: Sample Story Data & Database Seeding

**Priority**: P1
**Effort**: 1 day
**Dependencies**: Task 2.1 (Story Service), Task 2.2 (Story API)

### Context

You are creating sample story data to populate the database for development and testing. These sample stories provide realistic data for testing the library UI, demonstrating different themes and gameplay styles, and allowing immediate hands-on exploration of the interface without requiring story generation.

**Project Documentation**:

- Game Design: Game configuration YAML structure from existing examples
- Database: Alembic migrations for data seeding
- Sample Requirements: Diverse scenarios covering various themes and mechanics

### Your Mission

Create 3-5 complete sample story game.json files covering different themes, difficulties, and story types. Implement an Alembic migration to seed the database with sample story metadata and protect these samples from deletion.

### Deliverables

```
data/
└── samples/
    ├── sample-001-derelict-station/
    │   └── game.json
    ├── sample-002-hive-assault/
    │   └── game.json
    ├── sample-003-cyberpunk-heist/
    │   └── game.json
    ├── sample-004-mystery-cult/
    │   └── game.json
    └── sample-005-rescue-mission/
        └── game.json

backend/
├── app/
│   └── alembic/
│       └── versions/
│           └── 002_seed_sample_stories.py   # Migration
└── tests/
    └── test_sample_stories.py               # Sample story tests
```

### Acceptance Criteria

- [ ] 5 complete sample stories with full game.json structure
- [ ] Stories cover different themes: Warhammer 40K (3), Cyberpunk (1), Generic Horror (1)
- [ ] Stories demonstrate different mechanics: exploration, combat, puzzle, dialogue
- [ ] Each story has 3-10 scenes
- [ ] Each story includes items, NPCs, puzzles
- [ ] Sample stories marked with `is_sample=True` flag in database
- [ ] Alembic migration creates sample story records
- [ ] Sample stories cannot be deleted via API (protected)
- [ ] API endpoint filters: `GET /api/v1/stories?is_sample=true`
- [ ] Migration tests verify seeding works
- [ ] Sample data validation tests

### Technical Requirements

**Sample Story 1: Derelict Station (`sample-001-derelict-station/game.json`)**:

```json
{
  "title": "Derelict Station Omega-7",
  "description": "Explore an abandoned space station in the Ghoul Stars sector. Uncover what happened to the crew while battling corrupted servitors and avoiding environmental hazards.",
  "theme": "warhammer40k",
  "metadata": {
    "difficulty": "medium",
    "estimated_duration": "45-60 minutes",
    "themes": ["exploration", "horror", "mystery"],
    "tags": ["horror", "atmospheric", "combat", "exploration"]
  },
  "player": {
    "name": "Brother Cassius",
    "class": "Space Marine Tactical",
    "inventory": ["bolt_pistol", "combat_knife", "auspex"],
    "stats": {
      "health": 100,
      "strength": 80,
      "perception": 60
    }
  },
  "scenes": [
    {
      "id": "entrance",
      "name": "Station Entrance",
      "description": "You board the derelict station through a shattered airlock. Emergency lighting flickers, casting eerie shadows down the corridor. The air is stale and cold.",
      "connections": ["main_corridor"],
      "items": ["medkit_basic"],
      "npcs": [],
      "events": [
        {
          "id": "first_contact",
          "type": "narrative",
          "trigger": "on_enter",
          "text": "As you step inside, a corrupted vox-system crackles to life: 'Warning... contamination... breach detected...'"
        }
      ]
    },
    {
      "id": "main_corridor",
      "name": "Main Corridor",
      "description": "A long corridor littered with debris and spent shell casings. Claw marks score the walls. Blood stains the floor—some human, some... other.",
      "connections": ["entrance", "crew_quarters", "engineering"],
      "items": ["ammo_bolt"],
      "npcs": ["corrupted_servitor"],
      "events": []
    },
    {
      "id": "crew_quarters",
      "name": "Crew Quarters",
      "description": "Personal quarters in disarray. Belongings scattered, beds overturned. A dataslate flickers on a desk.",
      "connections": ["main_corridor"],
      "items": ["dataslate_log_1"],
      "npcs": [],
      "puzzles": ["decrypt_log"],
      "events": [
        {
          "id": "log_found",
          "type": "discovery",
          "trigger": "examine_dataslate",
          "text": "The log reveals the crew's final days: 'Day 47: The voices from the lower decks grow louder. We've sealed engineering. God-Emperor protect us.'"
        }
      ]
    },
    {
      "id": "engineering",
      "name": "Engineering Bay",
      "description": "The station's heart. Machinery hums with unholy energy. Shadows move in the darkness beyond the plasma conduits.",
      "connections": ["main_corridor"],
      "items": ["power_cell"],
      "npcs": ["possessed_tech_priest"],
      "puzzles": ["restore_power"],
      "events": [
        {
          "id": "boss_encounter",
          "type": "combat",
          "trigger": "on_enter",
          "text": "A figure emerges from the shadows—a tech-priest, but twisted and corrupted. Binary cant becomes a scream as it charges!"
        }
      ]
    }
  ],
  "items": [
    {
      "id": "bolt_pistol",
      "name": "Bolt Pistol",
      "description": "Standard issue Astartes sidearm. Fires explosive bolts.",
      "type": "weapon",
      "properties": {
        "damage": 30,
        "ammo": 12
      }
    },
    {
      "id": "medkit_basic",
      "name": "Basic Medkit",
      "description": "Emergency medical supplies.",
      "type": "consumable",
      "properties": {
        "healing": 25
      }
    },
    {
      "id": "dataslate_log_1",
      "name": "Crew Dataslate",
      "description": "Personal log of Station Commander Varak.",
      "type": "key_item",
      "properties": {
        "readable": true
      }
    },
    {
      "id": "power_cell",
      "name": "Emergency Power Cell",
      "description": "Portable power source for critical systems.",
      "type": "key_item",
      "properties": {
        "quest_item": true
      }
    }
  ],
  "npcs": [
    {
      "id": "corrupted_servitor",
      "name": "Corrupted Servitor",
      "description": "A once-loyal machine servant, now twisted by Chaos.",
      "type": "enemy",
      "stats": {
        "health": 40,
        "damage": 15
      },
      "dialogue": [],
      "hostile": true
    },
    {
      "id": "possessed_tech_priest",
      "name": "Possessed Tech-Priest Krell",
      "description": "The station's chief engineer, now a vessel for something malevolent.",
      "type": "boss",
      "stats": {
        "health": 120,
        "damage": 35
      },
      "dialogue": [
        "The Omnissiah... has shown me... the TRUTH!",
        "Join us... in blessed corruption..."
      ],
      "hostile": true
    }
  ],
  "puzzles": [
    {
      "id": "decrypt_log",
      "name": "Decrypt Corrupted Log",
      "description": "The dataslate is damaged. Restore power to read the full log.",
      "type": "key_item_puzzle",
      "solution": {
        "requires": ["power_cell"],
        "success_text": "The log reveals the station's dark secret..."
      }
    },
    {
      "id": "restore_power",
      "name": "Restore Main Power",
      "description": "Realign the plasma conduits to restore power.",
      "type": "sequence_puzzle",
      "solution": {
        "sequence": ["conduit_a", "conduit_b", "conduit_c"],
        "success_text": "Power surges through the station. Lights blaze to life."
      }
    }
  ]
}
```

**Sample Story 2: Hive Assault (`sample-002-hive-assault/game.json`)**:

```json
{
  "title": "Hive Assault: Purge of Sector 7-G",
  "description": "Lead a squad through a hive city's underbelly to eliminate a genestealer cult. Fast-paced combat and tactical decisions.",
  "theme": "warhammer40k",
  "metadata": {
    "difficulty": "hard",
    "estimated_duration": "30-45 minutes",
    "themes": ["combat", "action", "tactical"],
    "tags": ["action", "combat", "squad-based"]
  },
  "player": {
    "name": "Sergeant Voss",
    "class": "Space Marine Sergeant",
    "inventory": ["bolter", "frag_grenades", "chainsword"],
    "stats": {
      "health": 120,
      "strength": 90,
      "leadership": 75
    }
  },
  "scenes": [
    {
      "id": "drop_zone",
      "name": "Drop Zone",
      "description": "Your drop pod crashes into the hive's upper levels. Smoke and debris fill the air. Enemy contacts detected.",
      "connections": ["hab_district"],
      "items": ["ammo_bolter"],
      "npcs": ["battle_brother_1", "battle_brother_2"],
      "events": [
        {
          "id": "squad_assembles",
          "type": "narrative",
          "trigger": "on_enter",
          "text": "'Brethren, form up! For the Emperor and Ultramar!'"
        }
      ]
    },
    {
      "id": "hab_district",
      "name": "Hab District",
      "description": "Cramped living quarters. Civilians flee in terror. Cult ambush imminent.",
      "connections": ["drop_zone", "cult_hideout"],
      "items": [],
      "npcs": ["cultist_squad_alpha"],
      "events": [
        {
          "id": "ambush",
          "type": "combat",
          "trigger": "on_enter",
          "text": "Cultists pour from the shadows! Contact front!"
        }
      ]
    },
    {
      "id": "cult_hideout",
      "name": "Cult Hideout",
      "description": "A defiled shrine to the Four-Armed Emperor. Alien ichor stains the walls.",
      "connections": ["hab_district"],
      "items": ["sacred_icon"],
      "npcs": ["genestealer_patriarch"],
      "events": [
        {
          "id": "final_battle",
          "type": "boss_combat",
          "trigger": "on_enter",
          "text": "The Patriarch emerges—massive, alien, utterly abominable. This ends here!"
        }
      ]
    }
  ],
  "items": [
    {
      "id": "bolter",
      "name": "Godwyn Pattern Bolter",
      "description": "Standard Astartes bolter. Emperor's Wrath incarnate.",
      "type": "weapon",
      "properties": {
        "damage": 40,
        "ammo": 30,
        "fire_mode": "auto"
      }
    },
    {
      "id": "frag_grenades",
      "name": "Frag Grenades",
      "description": "High-explosive anti-personnel grenades.",
      "type": "weapon",
      "properties": {
        "damage": 50,
        "area_effect": true,
        "quantity": 3
      }
    }
  ],
  "npcs": [
    {
      "id": "battle_brother_1",
      "name": "Brother Marcus",
      "description": "Your tactical support. Reliable and steadfast.",
      "type": "ally",
      "stats": {
        "health": 100,
        "damage": 30
      },
      "hostile": false
    },
    {
      "id": "cultist_squad_alpha",
      "name": "Cult Ambush Squad",
      "description": "Fanatical cultists armed with autoguns and improvised weapons.",
      "type": "enemy_group",
      "stats": {
        "health": 60,
        "damage": 20,
        "count": 5
      },
      "hostile": true
    },
    {
      "id": "genestealer_patriarch",
      "name": "Genestealer Patriarch",
      "description": "Ancient, cunning, and deadly. Leader of the cult.",
      "type": "boss",
      "stats": {
        "health": 200,
        "damage": 50,
        "speed": "fast"
      },
      "hostile": true
    }
  ],
  "puzzles": []
}
```

**Sample Story 3: Cyberpunk Heist (`sample-003-cyberpunk-heist/game.json`)**:

```json
{
  "title": "Neon Heist: The Arasaka Job",
  "description": "Infiltrate a megacorp tower to steal valuable data. Stealth, hacking, and quick thinking required.",
  "theme": "cyberpunk",
  "metadata": {
    "difficulty": "medium",
    "estimated_duration": "40-55 minutes",
    "themes": ["stealth", "hacking", "tech"],
    "tags": ["cyberpunk", "stealth", "hacking"]
  },
  "player": {
    "name": "Ghost",
    "class": "Netrunner",
    "inventory": ["cyberdeck", "silenced_pistol", "smoke_grenades"],
    "stats": {
      "health": 80,
      "hacking": 95,
      "stealth": 85
    }
  },
  "scenes": [
    {
      "id": "lobby",
      "name": "Corporate Lobby",
      "description": "Gleaming chrome and neon. Corporate drones shuffle past security checkpoints.",
      "connections": ["elevator_bay"],
      "items": ["keycard_level_1"],
      "npcs": ["security_guard"],
      "events": []
    },
    {
      "id": "elevator_bay",
      "name": "Elevator Bay",
      "description": "Multiple elevators lead to different tower levels. Security cameras sweep the area.",
      "connections": ["lobby", "server_room"],
      "items": [],
      "npcs": [],
      "puzzles": ["bypass_elevator_security"],
      "events": []
    },
    {
      "id": "server_room",
      "name": "Data Center",
      "description": "Rows of servers humming with data. This is the prize.",
      "connections": ["elevator_bay"],
      "items": ["corporate_data_chip"],
      "npcs": ["ice_ai"],
      "puzzles": ["hack_mainframe"],
      "events": [
        {
          "id": "ice_encounter",
          "type": "hacking_combat",
          "trigger": "hack_attempt",
          "text": "ICE detected! Defensive programs activating!"
        }
      ]
    }
  ],
  "items": [
    {
      "id": "cyberdeck",
      "name": "Military-Grade Cyberdeck",
      "description": "Top-tier hacking hardware. State of the art.",
      "type": "tool",
      "properties": {
        "hacking_bonus": 30
      }
    },
    {
      "id": "corporate_data_chip",
      "name": "Encrypted Data Chip",
      "description": "The payload. Billions in corporate secrets.",
      "type": "quest_item",
      "properties": {
        "quest_item": true
      }
    }
  ],
  "npcs": [
    {
      "id": "security_guard",
      "name": "Corp Security",
      "description": "Standard rent-a-cop. Armed but not alert.",
      "type": "enemy",
      "stats": {
        "health": 50,
        "damage": 15
      },
      "hostile": true
    },
    {
      "id": "ice_ai",
      "name": "Black ICE Defense System",
      "description": "Deadly AI defense program. Will fry your brain if you're not careful.",
      "type": "digital_enemy",
      "stats": {
        "health": 100,
        "damage": 40
      },
      "hostile": true
    }
  ],
  "puzzles": [
    {
      "id": "bypass_elevator_security",
      "name": "Bypass Elevator Lock",
      "description": "Hack the elevator control system.",
      "type": "hacking_puzzle",
      "solution": {
        "requires": ["cyberdeck"],
        "difficulty": "medium",
        "success_text": "Elevator unlocked. Access granted to level 47."
      }
    },
    {
      "id": "hack_mainframe",
      "name": "Hack Corporate Mainframe",
      "description": "Extract the data while avoiding ICE.",
      "type": "hacking_puzzle",
      "solution": {
        "requires": ["cyberdeck"],
        "difficulty": "hard",
        "success_text": "Data extracted. Time to jack out before security arrives."
      }
    }
  ]
}
```

**Alembic Migration (`app/alembic/versions/002_seed_sample_stories.py`)**:

```python
"""Seed sample stories.

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add sample stories to database."""
    # Sample story metadata
    samples = [
        {
            "title": "Derelict Station Omega-7",
            "description": "Explore an abandoned space station in the Ghoul Stars sector. Uncover what happened to the crew while battling corrupted servitors and avoiding environmental hazards.",
            "theme_id": "warhammer40k",
            "tags": ["horror", "atmospheric", "combat", "exploration"],
            "game_file_path": "data/samples/sample-001-derelict-station/game.json",
            "prompt": "Create a horror-themed Space Hulk mission exploring a derelict station with corrupted servitors and environmental hazards.",
            "template_id": "exploration_horror",
            "is_sample": True,
            "scene_count": 4,
            "item_count": 4,
            "npc_count": 2,
            "puzzle_count": 2,
        },
        {
            "title": "Hive Assault: Purge of Sector 7-G",
            "description": "Lead a squad through a hive city's underbelly to eliminate a genestealer cult. Fast-paced combat and tactical decisions.",
            "theme_id": "warhammer40k",
            "tags": ["action", "combat", "squad-based"],
            "game_file_path": "data/samples/sample-002-hive-assault/game.json",
            "prompt": "Create an action-packed combat mission in a hive city with a genestealer cult as the enemy.",
            "template_id": "combat_tactical",
            "is_sample": True,
            "scene_count": 3,
            "item_count": 2,
            "npc_count": 4,
            "puzzle_count": 0,
        },
        {
            "title": "Neon Heist: The Arasaka Job",
            "description": "Infiltrate a megacorp tower to steal valuable data. Stealth, hacking, and quick thinking required.",
            "theme_id": "cyberpunk",
            "tags": ["cyberpunk", "stealth", "hacking"],
            "game_file_path": "data/samples/sample-003-cyberpunk-heist/game.json",
            "prompt": "Create a cyberpunk stealth mission involving infiltration and hacking of a corporate tower.",
            "template_id": "stealth_heist",
            "is_sample": True,
            "scene_count": 3,
            "item_count": 2,
            "npc_count": 2,
            "puzzle_count": 2,
        },
        {
            "title": "The Ritual of Crimson Stars",
            "description": "Investigate a mysterious cult in the underhive. Uncover ancient secrets and prevent a dark ritual.",
            "theme_id": "warhammer40k",
            "tags": ["mystery", "investigation", "horror"],
            "game_file_path": "data/samples/sample-004-mystery-cult/game.json",
            "prompt": "Create a mystery investigation mission involving a dark cult and ancient secrets.",
            "template_id": "mystery_investigation",
            "is_sample": True,
            "scene_count": 5,
            "item_count": 6,
            "npc_count": 3,
            "puzzle_count": 3,
        },
        {
            "title": "Rescue at Firebase Zeta",
            "description": "Extract Imperial Guard survivors from an overrun firebase. Time is running out.",
            "theme_id": "warhammer40k",
            "tags": ["rescue", "action", "time-pressure"],
            "game_file_path": "data/samples/sample-005-rescue-mission/game.json",
            "prompt": "Create a time-sensitive rescue mission to extract survivors from an overrun military base.",
            "template_id": "rescue_operation",
            "is_sample": True,
            "scene_count": 4,
            "item_count": 3,
            "npc_count": 5,
            "puzzle_count": 1,
        },
    ]

    # Insert sample stories
    conn = op.get_bind()
    now = datetime.now(timezone.utc)

    for sample in samples:
        conn.execute(
            sa.text("""
                INSERT INTO stories (
                    title, description, theme_id, tags, game_file_path,
                    prompt, template_id, is_sample, scene_count, item_count,
                    npc_count, puzzle_count, created_at, updated_at,
                    play_count, iteration_count
                )
                VALUES (
                    :title, :description, :theme_id, :tags::jsonb, :game_file_path,
                    :prompt, :template_id, :is_sample, :scene_count, :item_count,
                    :npc_count, :puzzle_count, :created_at, :updated_at,
                    0, 1
                )
            """),
            {
                **sample,
                "tags": sa.JSON(sample["tags"]),
                "created_at": now,
                "updated_at": now,
            }
        )


def downgrade() -> None:
    """Remove sample stories."""
    conn = op.get_bind()
    conn.execute(
        sa.text("DELETE FROM stories WHERE is_sample = true")
    )
```

**Updated Story Model (add is_sample field) (`app/models/story.py`)**:

```python
# Add to Story model
is_sample = Column(Boolean, default=False, nullable=False, index=True)
```

**Updated Delete Endpoint (protect samples) (`app/api/routes/stories.py`)**:

```python
@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
    story_id: int,
    service: StoryService = Depends(get_story_service),
) -> None:
    """Delete a story (sample stories cannot be deleted)."""
    story = service.get(story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )

    # Protect sample stories from deletion
    if story.is_sample:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sample stories cannot be deleted",
        )

    deleted = service.delete(story_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
```

### Testing Requirements

**Migration Tests (`tests/test_sample_stories.py`)**:

```python
"""Tests for sample story seeding."""
import pytest
from pathlib import Path
import json

from backend.app.models.story import Story
from backend.app.database import SessionLocal


def test_sample_stories_exist():
    """Test that sample stories are seeded in database."""
    db = SessionLocal()
    try:
        samples = db.query(Story).filter(Story.is_sample == True).all()

        assert len(samples) >= 3
        assert all(s.is_sample for s in samples)
    finally:
        db.close()


def test_sample_game_files_exist():
    """Test that sample game.json files exist."""
    samples_dir = Path("data/samples")

    required_samples = [
        "sample-001-derelict-station",
        "sample-002-hive-assault",
        "sample-003-cyberpunk-heist",
    ]

    for sample in required_samples:
        game_file = samples_dir / sample / "game.json"
        assert game_file.exists(), f"Missing game file: {game_file}"

        # Validate JSON structure
        with open(game_file) as f:
            data = json.load(f)

        assert "title" in data
        assert "scenes" in data
        assert "items" in data
        assert "npcs" in data


def test_sample_stories_cannot_be_deleted():
    """Test that sample stories are protected from deletion."""
    from httpx import AsyncClient
    from backend.app.main import app

    db = SessionLocal()
    try:
        # Get a sample story
        sample = db.query(Story).filter(Story.is_sample == True).first()

        if sample:
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.delete(f"/api/v1/stories/{sample.id}")

                assert response.status_code == 403
                assert "cannot be deleted" in response.json()["detail"].lower()
    finally:
        db.close()
```

### Validation Commands

```bash
# Create sample directories
mkdir -p data/samples/sample-001-derelict-station
mkdir -p data/samples/sample-002-hive-assault
mkdir -p data/samples/sample-003-cyberpunk-heist
mkdir -p data/samples/sample-004-mystery-cult
mkdir -p data/samples/sample-005-rescue-mission

# Create game.json files (copy from examples above)

# Run migration
cd backend
alembic upgrade head

# Verify samples in database
python -c "
from app.database import SessionLocal
from app.models.story import Story

db = SessionLocal()
samples = db.query(Story).filter(Story.is_sample == True).all()
print(f'Sample stories: {len(samples)}')
for s in samples:
    print(f'  - {s.title}')
"

# Test sample protection
curl -X DELETE http://localhost:8000/api/v1/stories/1
# Should return 403 if story 1 is a sample

# Run tests
pytest tests/test_sample_stories.py -v
```

### Success Indicators

✅ 5 complete sample story game.json files created
✅ Sample stories cover different themes and mechanics
✅ Each story has complete structure (scenes, items, NPCs, puzzles)
✅ Alembic migration successfully seeds database
✅ Sample stories visible in library UI
✅ Sample stories cannot be deleted via API (403 error)
✅ Sample stories can be filtered: `?is_sample=true`
✅ All migration tests pass
✅ Game.json files are valid JSON
✅ Sample data enhances development/testing experience

---
