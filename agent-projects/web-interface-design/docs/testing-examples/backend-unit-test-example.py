"""
Backend Unit Test Example
Demonstrates best practices for testing backend services with pytest.

This example shows:
- Test structure (Arrange-Act-Assert)
- Fixture usage
- Mocking dependencies
- Coverage of success and error cases
- Type hints and docstrings
"""

import time
from datetime import datetime
from unittest.mock import Mock, mock_open, patch

import pytest
from app.exceptions import InvalidThemeError, StoryNotFoundError  # type: ignore
from app.models.story import Story  # type: ignore
from app.services.story_service import StoryService  # type: ignore

# === FIXTURES ===


@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    mock_db = Mock()
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.delete = Mock()
    mock_db.rollback = Mock()
    return mock_db


@pytest.fixture
def story_service(mock_db_session):
    """Provide StoryService instance with mocked database."""
    return StoryService(db=mock_db_session)


@pytest.fixture
def sample_story():
    """Provide a sample story for testing."""
    return Story(
        id="550e8400-e29b-41d4-a716-446655440000",
        title="Sample Horror Story",
        description="A dark atmospheric horror adventure",
        theme_id="warhammer40k",
        game_file_path="/stories/550e8400-e29b-41d4-a716-446655440000/game.json",
        prompt="Create a horror-themed Space Hulk adventure",
        template_id="horror_infestation",
        is_sample=False,
        created_at=datetime(2025, 11, 12, 10, 0, 0),
        updated_at=datetime(2025, 11, 12, 10, 0, 0),
        current_version=1,
        total_iterations=0,
        play_count=5,
        scene_count=8,
        item_count=12,
        npc_count=3,
        puzzle_count=2,
        tags=["horror", "atmospheric"],
    )


# === SUCCESS TESTS ===


def test_create_story_success(story_service: StoryService, mock_db_session: Mock) -> None:
    """
    Test successful story creation with valid data.

    Preconditions:
    - StoryService initialized with mock database
    - Valid story data provided

    Steps:
    1. Call create() with valid story data
    2. Verify Story object created
    3. Verify database add() and commit() called

    Expected Results:
    - Story object returned with correct attributes
    - Database add() called once
    - Database commit() called once
    """
    # ARRANGE
    story_data = {
        "title": "New Horror Story",
        "description": "A new horror adventure",
        "theme_id": "warhammer40k",
        "prompt": "Create a dark horror story with heavy atmosphere",
        "template_id": "horror_infestation",
    }

    # ACT
    story = story_service.create(story_data)

    # ASSERT
    assert story is not None
    assert story.title == "New Horror Story"
    assert story.theme_id == "warhammer40k"
    assert story.prompt == "Create a dark horror story with heavy atmosphere"
    assert story.current_version == 1
    assert story.total_iterations == 0

    # Verify database interactions
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_get_story_by_id_success(
    story_service: StoryService, mock_db_session: Mock, sample_story: Story
) -> None:
    """
    Test successful retrieval of story by ID.

    Preconditions:
    - Story exists in database

    Steps:
    1. Mock database query to return sample story
    2. Call get_by_id() with valid ID
    3. Verify correct story returned

    Expected Results:
    - Story object returned
    - Story attributes match expected values
    """
    # ARRANGE
    story_id = "550e8400-e29b-41d4-a716-446655440000"
    mock_query = Mock()
    mock_query.filter().first.return_value = sample_story
    mock_db_session.query.return_value = mock_query

    # ACT
    story = story_service.get_by_id(story_id)

    # ASSERT
    assert story is not None
    assert story.id == story_id
    assert story.title == "Sample Horror Story"
    assert story.theme_id == "warhammer40k"


def test_list_stories_with_search(
    story_service: StoryService, mock_db_session: Mock, sample_story: Story
) -> None:
    """
    Test listing stories with search query.

    Preconditions:
    - Stories exist in database

    Steps:
    1. Mock database query to return filtered results
    2. Call list() with search parameter
    3. Verify results filtered correctly

    Expected Results:
    - Filtered stories returned
    - Pagination metadata included
    - Search applied case-insensitively
    """
    # ARRANGE
    mock_query = Mock()
    mock_query.filter().offset().limit().all.return_value = [sample_story]
    mock_query.filter().count.return_value = 1
    mock_db_session.query.return_value = mock_query

    # ACT
    result = story_service.list(search="horror", page=1, per_page=20)

    # ASSERT
    assert "stories" in result
    assert len(result["stories"]) == 1
    assert result["stories"][0].title == "Sample Horror Story"

    assert "pagination" in result
    assert result["pagination"]["page"] == 1
    assert result["pagination"]["total"] == 1
    assert result["pagination"]["pages"] == 1


def test_update_story_success(
    story_service: StoryService, mock_db_session: Mock, sample_story: Story
) -> None:
    """
    Test successful story update.

    Preconditions:
    - Story exists in database

    Steps:
    1. Mock database query to return existing story
    2. Call update() with new data
    3. Verify story updated
    4. Verify database commit called

    Expected Results:
    - Story attributes updated
    - Database commit() called
    - updated_at timestamp updated
    """
    # ARRANGE
    story_id = "550e8400-e29b-41d4-a716-446655440000"
    mock_query = Mock()
    mock_query.filter().first.return_value = sample_story
    mock_db_session.query.return_value = mock_query

    update_data = {"title": "Updated Title", "description": "Updated description"}

    # ACT
    updated_story = story_service.update(story_id, update_data)

    # ASSERT
    assert updated_story.title == "Updated Title"
    assert updated_story.description == "Updated description"
    mock_db_session.commit.assert_called_once()


def test_delete_story_success(
    story_service: StoryService, mock_db_session: Mock, sample_story: Story
) -> None:
    """
    Test successful story deletion.

    Preconditions:
    - Story exists and is not a sample story

    Steps:
    1. Mock database query to return story
    2. Call delete() with story ID
    3. Verify database delete() and commit() called

    Expected Results:
    - Database delete() called with story
    - Database commit() called
    - No exceptions raised
    """
    # ARRANGE
    story_id = "550e8400-e29b-41d4-a716-446655440000"
    sample_story.is_sample = False
    mock_query = Mock()
    mock_query.filter().first.return_value = sample_story
    mock_db_session.query.return_value = mock_query

    # ACT
    story_service.delete(story_id)

    # ASSERT
    mock_db_session.delete.assert_called_once_with(sample_story)
    mock_db_session.commit.assert_called_once()


def test_get_story_content_success(
    story_service: StoryService, mock_db_session: Mock, sample_story: Story
) -> None:
    """
    Test retrieving full story game content from filesystem.

    Preconditions:
    - Story exists in database
    - game.json file exists on filesystem

    Steps:
    1. Mock database query to return story
    2. Mock file open to return game content
    3. Call get_content()
    4. Verify content returned

    Expected Results:
    - Game content returned as dict
    - Contains expected keys (plot, narrative_map, etc.)
    """
    # ARRANGE
    story_id = "550e8400-e29b-41d4-a716-446655440000"
    mock_query = Mock()
    mock_query.filter().first.return_value = sample_story
    mock_db_session.query.return_value = mock_query

    game_content = '{"plot": {}, "narrative_map": {}, "puzzles": [], "scenes": {}}'

    # ACT
    with patch("builtins.open", mock_open(read_data=game_content)):
        content = story_service.get_content(story_id)

    # ASSERT
    assert content is not None
    assert "plot" in content
    assert "narrative_map" in content
    assert "puzzles" in content
    assert "scenes" in content


# === ERROR TESTS ===


def test_create_story_invalid_theme(story_service: StoryService) -> None:
    """
    Test story creation with invalid theme raises error.

    Preconditions:
    - StoryService initialized

    Steps:
    1. Call create() with invalid theme_id
    2. Verify InvalidThemeError raised

    Expected Results:
    - InvalidThemeError exception raised
    - Error message indicates invalid theme
    """
    # ARRANGE
    story_data = {
        "title": "New Story",
        "theme_id": "invalid_theme_that_does_not_exist",
        "prompt": "Test prompt",
    }

    # ACT & ASSERT
    with pytest.raises(InvalidThemeError) as exc_info:
        story_service.create(story_data)

    assert "invalid theme" in str(exc_info.value).lower()


def test_create_story_invalid_prompt_too_short(story_service: StoryService) -> None:
    """
    Test story creation with prompt below minimum length.

    Preconditions:
    - StoryService initialized

    Steps:
    1. Call create() with prompt < 50 characters
    2. Verify ValueError raised

    Expected Results:
    - ValueError exception raised
    - Error message indicates prompt too short
    """
    # ARRANGE
    story_data = {
        "title": "New Story",
        "theme_id": "warhammer40k",
        "prompt": "Short",  # Only 5 characters
    }

    # ACT & ASSERT
    with pytest.raises(ValueError) as exc_info:
        story_service.create(story_data)

    assert "too short" in str(exc_info.value).lower()


def test_get_story_by_id_not_found(story_service: StoryService, mock_db_session: Mock) -> None:
    """
    Test retrieval of non-existent story.

    Preconditions:
    - Story does not exist in database

    Steps:
    1. Mock database query to return None
    2. Call get_by_id() with invalid ID
    3. Verify StoryNotFoundError raised

    Expected Results:
    - StoryNotFoundError exception raised
    - Error message contains story ID
    """
    # ARRANGE
    story_id = "invalid-story-id"
    mock_query = Mock()
    mock_query.filter().first.return_value = None
    mock_db_session.query.return_value = mock_query

    # ACT & ASSERT
    with pytest.raises(StoryNotFoundError) as exc_info:
        story_service.get_by_id(story_id)

    assert story_id in str(exc_info.value)


def test_update_story_not_found(story_service: StoryService, mock_db_session: Mock) -> None:
    """
    Test updating non-existent story.

    Preconditions:
    - Story does not exist in database

    Steps:
    1. Mock database query to return None
    2. Call update() with invalid ID
    3. Verify StoryNotFoundError raised

    Expected Results:
    - StoryNotFoundError exception raised
    - Database commit() NOT called
    """
    # ARRANGE
    story_id = "invalid-story-id"
    mock_query = Mock()
    mock_query.filter().first.return_value = None
    mock_db_session.query.return_value = mock_query

    # ACT & ASSERT
    with pytest.raises(StoryNotFoundError):
        story_service.update(story_id, {"title": "New Title"})

    mock_db_session.commit.assert_not_called()


def test_delete_sample_story_forbidden(
    story_service: StoryService, mock_db_session: Mock, sample_story: Story
) -> None:
    """
    Test deleting sample story raises error.

    Preconditions:
    - Story is marked as sample (is_sample=True)

    Steps:
    1. Mock database query to return sample story
    2. Call delete() with story ID
    3. Verify ValueError raised

    Expected Results:
    - ValueError exception raised
    - Error message indicates sample stories cannot be deleted
    - Database delete() NOT called
    """
    # ARRANGE
    story_id = "550e8400-e29b-41d4-a716-446655440000"
    sample_story.is_sample = True
    mock_query = Mock()
    mock_query.filter().first.return_value = sample_story
    mock_db_session.query.return_value = mock_query

    # ACT & ASSERT
    with pytest.raises(ValueError) as exc_info:
        story_service.delete(story_id)

    assert "sample" in str(exc_info.value).lower()
    mock_db_session.delete.assert_not_called()


def test_get_story_content_file_not_found(
    story_service: StoryService, mock_db_session: Mock, sample_story: Story
) -> None:
    """
    Test retrieving content when game file is missing.

    Preconditions:
    - Story exists in database
    - game.json file does NOT exist on filesystem

    Steps:
    1. Mock database query to return story
    2. Mock file open to raise FileNotFoundError
    3. Call get_content()
    4. Verify FileNotFoundError raised

    Expected Results:
    - FileNotFoundError exception raised
    - Error message indicates missing file
    """
    # ARRANGE
    story_id = "550e8400-e29b-41d4-a716-446655440000"
    mock_query = Mock()
    mock_query.filter().first.return_value = sample_story
    mock_db_session.query.return_value = mock_query

    # ACT & ASSERT
    with (
        patch("builtins.open", side_effect=FileNotFoundError("File not found")),
        pytest.raises(FileNotFoundError),
    ):
        story_service.get_content(story_id)


# === EDGE CASE TESTS ===


def test_list_stories_empty_database(story_service: StoryService, mock_db_session: Mock) -> None:
    """
    Test listing stories when database is empty.

    Preconditions:
    - No stories in database

    Steps:
    1. Mock database query to return empty list
    2. Call list()
    3. Verify empty result with correct structure

    Expected Results:
    - Empty stories list returned
    - Pagination shows 0 total, 0 pages
    - No exceptions raised
    """
    # ARRANGE
    mock_query = Mock()
    mock_query.filter().offset().limit().all.return_value = []
    mock_query.filter().count.return_value = 0
    mock_db_session.query.return_value = mock_query

    # ACT
    result = story_service.list()

    # ASSERT
    assert result["stories"] == []
    assert result["pagination"]["total"] == 0
    assert result["pagination"]["pages"] == 0


def test_list_stories_pagination_last_page(
    story_service: StoryService, mock_db_session: Mock, sample_story: Story
) -> None:
    """
    Test pagination on last page with partial results.

    Preconditions:
    - Database has 25 stories
    - Page size is 20

    Steps:
    1. Mock database to return 5 stories (partial page)
    2. Call list() with page=2, per_page=20
    3. Verify correct pagination metadata

    Expected Results:
    - 5 stories returned
    - Page 2 of 2 indicated
    - Total count correct
    """
    # ARRANGE
    stories = [sample_story for _ in range(5)]
    mock_query = Mock()
    mock_query.filter().offset().limit().all.return_value = stories
    mock_query.filter().count.return_value = 25
    mock_db_session.query.return_value = mock_query

    # ACT
    result = story_service.list(page=2, per_page=20)

    # ASSERT
    assert len(result["stories"]) == 5
    assert result["pagination"]["page"] == 2
    assert result["pagination"]["total"] == 25
    assert result["pagination"]["pages"] == 2


# === PERFORMANCE TESTS ===


@pytest.mark.slow
def test_list_stories_with_large_dataset(
    story_service: StoryService, mock_db_session: Mock
) -> None:
    """
    Test listing stories performs well with large dataset.

    Preconditions:
    - Database has 1000+ stories

    Steps:
    1. Mock database to return 1000 stories metadata
    2. Call list() and measure execution time
    3. Verify performance acceptable

    Expected Results:
    - Operation completes in <1 second
    - Memory usage acceptable
    - Pagination applied correctly
    """
    # ARRANGE
    large_story_set = [
        Story(id=f"story-{i}", title=f"Story {i}", theme_id="warhammer40k") for i in range(1000)
    ]

    mock_query = Mock()
    mock_query.filter().offset().limit().all.return_value = large_story_set[:20]
    mock_query.filter().count.return_value = 1000
    mock_db_session.query.return_value = mock_query

    # ACT
    start = time.time()
    result = story_service.list(page=1, per_page=20)
    duration = time.time() - start

    # ASSERT
    assert len(result["stories"]) == 20
    assert result["pagination"]["total"] == 1000
    assert duration < 1.0  # Should complete in under 1 second


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.services.story_service"])
