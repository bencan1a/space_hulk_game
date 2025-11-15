"""Tests for story service."""

import pytest
from app.schemas.story import StoryCreate, StoryUpdate
from app.services.story_service import StoryService


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
            prompt="Test prompt for story creation with enough characters to meet minimum length",
            game_file_path=f"data/stories/test_{i:03d}/game.json",
        )
        service.create(story_data)

    # Test first page (excluding samples)
    result = service.list(page=1, page_size=10, is_sample=False)
    assert result.total == 25
    assert len(result.items) == 10
    assert result.page == 1
    assert result.total_pages == 3

    # Test second page
    result = service.list(page=2, page_size=10, is_sample=False)
    assert len(result.items) == 10
    assert result.page == 2


def test_list_stories_search(db_session):
    """Test listing stories with search filter."""
    service = StoryService(db_session)

    # Create stories with different titles
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

    result = service.list(search="horror")

    assert result.total == 1
    assert result.items[0].title == "Horror Story"


def test_list_stories_theme_filter(db_session):
    """Test filtering stories by theme."""
    service = StoryService(db_session)

    service.create(
        StoryCreate(
            title="WH40K Story",
            theme_id="warhammer40k",
            prompt="WH40K prompt with enough characters to meet the minimum length requirement",
            game_file_path="data/stories/wh40k/game.json",
        )
    )
    service.create(
        StoryCreate(
            title="Cyberpunk Story",
            theme_id="cyberpunk",
            prompt="Cyberpunk prompt with enough characters to meet the minimum length",
            game_file_path="data/stories/cyberpunk/game.json",
        )
    )

    result = service.list(theme_id="cyberpunk", is_sample=False)

    assert result.total == 1
    assert result.items[0].theme_id == "cyberpunk"


def test_list_stories_tags_filter(db_session):
    """Test filtering stories by tags."""
    service = StoryService(db_session)

    service.create(
        StoryCreate(
            title="Horror Story",
            tags=["horror", "atmospheric"],
            prompt="Horror prompt with enough characters to meet the minimum length requirement",
            game_file_path="data/stories/horror/game.json",
        )
    )
    service.create(
        StoryCreate(
            title="Action Story",
            tags=["action", "combat"],
            prompt="Action prompt with enough characters to meet the minimum length requirement",
            game_file_path="data/stories/action/game.json",
        )
    )

    result = service.list(tags=["horror"], is_sample=False)

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
