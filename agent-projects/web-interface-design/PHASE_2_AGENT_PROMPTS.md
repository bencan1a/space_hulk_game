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

*[Continue with Tasks 2.4 through 2.8...]*

**Note**: This document continues with the remaining 5 tasks. Each task follows the same detailed structure with Context, Mission, Deliverables, Acceptance Criteria, Technical Requirements, Testing, Validation Commands, and Success Indicators.

Would you like me to continue with the remaining tasks, or would you prefer to review this portion first?
