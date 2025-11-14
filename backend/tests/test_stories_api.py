"""Tests for story API endpoints."""

import json
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.schemas.story import StoryCreate
from app.services.story_service import StoryService


@pytest.fixture
def test_game_file(tmp_path):
    """Create a temporary game.json file."""
    game_data = {
        "title": "Test Game",
        "scenes": [],
        "items": [],
    }
    file_path = tmp_path / "game.json"
    with file_path.open("w") as f:
        json.dump(game_data, f)
    return str(file_path)


@pytest.fixture
def invalid_json_file(tmp_path):
    """Create a temporary file with invalid JSON."""
    file_path = tmp_path / "invalid.json"
    with file_path.open("w") as f:
        f.write("{ invalid json content")
    return str(file_path)


@pytest.mark.asyncio
async def test_list_stories_empty(db_session):  # noqa: ARG001 - fixture needed for dependency override
    """Test listing stories when database is empty."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/stories")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total_pages"] == 0


@pytest.mark.asyncio
async def test_list_stories_with_pagination(db_session):
    """Test listing stories with pagination."""
    # Create some test stories
    service = StoryService(db_session)
    for i in range(5):
        story_data = StoryCreate(
            title=f"Story {i}",
            prompt="Test prompt for story creation with enough characters to meet minimum length",
            game_file_path=f"data/stories/test_{i:03d}/game.json",
        )
        service.create(story_data)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/stories?page=1&page_size=3")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert data["total"] == 5
        assert len(data["items"]) == 3
        assert data["page"] == 1
        assert data["page_size"] == 3
        assert data["total_pages"] == 2


@pytest.mark.asyncio
async def test_list_stories_with_search(db_session):
    """Test searching stories."""
    service = StoryService(db_session)
    service.create(
        StoryCreate(
            title="Horror Story",
            prompt="Horror prompt with enough characters to meet the minimum length requirement",
            game_file_path="data/stories/horror/game.json",
        )
    )
    service.create(
        StoryCreate(
            title="Adventure Story",
            prompt="Adventure prompt with enough characters to meet the minimum length",
            game_file_path="data/stories/adventure/game.json",
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/stories?search=horror")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Horror Story"


@pytest.mark.asyncio
async def test_list_stories_with_filters(db_session):
    """Test filtering stories by theme and tags."""
    service = StoryService(db_session)
    service.create(
        StoryCreate(
            title="WH40K Horror",
            theme_id="warhammer40k",
            tags=["horror", "atmospheric"],
            prompt="WH40K horror prompt with enough characters to meet the minimum length requirement",
            game_file_path="data/stories/wh40k/game.json",
        )
    )
    service.create(
        StoryCreate(
            title="Cyberpunk Action",
            theme_id="cyberpunk",
            tags=["action", "combat"],
            prompt="Cyberpunk action prompt with enough characters to meet the minimum length",
            game_file_path="data/stories/cyberpunk/game.json",
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test theme filter
        response = await client.get("/api/v1/stories?theme_id=warhammer40k")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["theme_id"] == "warhammer40k"

        # Test tags filter
        response = await client.get("/api/v1/stories?tags=horror,atmospheric")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "horror" in data["items"][0]["tags"]


@pytest.mark.asyncio
async def test_get_story_success(db_session):
    """Test getting a story by ID successfully."""
    service = StoryService(db_session)
    story = service.create(
        StoryCreate(
            title="Test Story",
            description="A test story",
            prompt="Test prompt with enough characters to meet the minimum length requirement",
            game_file_path="data/stories/test/game.json",
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/stories/{story.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == story.id
        assert data["title"] == "Test Story"
        assert data["description"] == "A test story"


@pytest.mark.asyncio
async def test_get_story_not_found(db_session):  # noqa: ARG001 - fixture needed for dependency override
    """Test getting nonexistent story returns 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/stories/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_story_content_success(db_session, test_game_file):
    """Test getting story content successfully."""
    service = StoryService(db_session)
    story = service.create(
        StoryCreate(
            title="Test Story",
            prompt="Test prompt with enough characters to meet the minimum length requirement",
            game_file_path=test_game_file,
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/stories/{story.id}/content")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Game"
        assert "scenes" in data
        assert "items" in data


@pytest.mark.asyncio
async def test_get_story_content_story_not_found(db_session):  # noqa: ARG001 - fixture needed for dependency override
    """Test getting content for nonexistent story returns 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/stories/999/content")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_story_content_file_not_found(db_session):
    """Test getting content when game file doesn't exist returns 404."""
    service = StoryService(db_session)
    story = service.create(
        StoryCreate(
            title="Test Story",
            prompt="Test prompt with enough characters to meet the minimum length requirement",
            game_file_path="/nonexistent/path/game.json",
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/stories/{story.id}/content")

        assert response.status_code == 404
        assert "game file not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_story_content_invalid_json(db_session, invalid_json_file):
    """Test getting content with invalid JSON returns 500."""
    service = StoryService(db_session)
    story = service.create(
        StoryCreate(
            title="Test Story",
            prompt="Test prompt with enough characters to meet the minimum length requirement",
            game_file_path=invalid_json_file,
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/stories/{story.id}/content")

        assert response.status_code == 500
        assert "invalid json" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_story_success(db_session):
    """Test successful story deletion returns 204."""
    service = StoryService(db_session)
    story = service.create(
        StoryCreate(
            title="Test Story",
            prompt="Test prompt with enough characters to meet the minimum length requirement",
            game_file_path="data/stories/test/game.json",
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/stories/{story.id}")

        assert response.status_code == 204

        # Verify story is deleted
        assert service.get(story.id) is None


@pytest.mark.asyncio
async def test_delete_story_not_found(db_session):  # noqa: ARG001 - fixture needed for dependency override
    """Test deleting nonexistent story returns 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/api/v1/stories/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_stories_pagination_defaults(db_session):
    """Test that pagination uses default values when not specified."""
    service = StoryService(db_session)
    service.create(
        StoryCreate(
            title="Test Story",
            prompt="Test prompt with enough characters to meet the minimum length requirement",
            game_file_path="data/stories/test/game.json",
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/stories")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_list_stories_page_size_limit(db_session):  # noqa: ARG001 - fixture needed for dependency override
    """Test that page_size is limited to maximum of 100."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Try to request more than 100 items
        response = await client.get("/api/v1/stories?page_size=200")

        # FastAPI validation should reject this
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_story_content_path_traversal_blocked(db_session):
    """Test that path traversal attempts are blocked for relative paths."""
    service = StoryService(db_session)
    story = service.create(
        StoryCreate(
            title="Malicious Story",
            prompt="Test prompt with enough characters to meet the minimum length requirement",
            game_file_path="../../../etc/passwd",  # Path traversal attempt
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/stories/{story.id}/content")

        # Should return 403 Forbidden for path traversal attempt
        assert response.status_code == 403
        assert "not allowed" in response.json()["detail"].lower()

