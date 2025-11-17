"""Tests for iteration service."""

from unittest.mock import patch

import pytest
from app.models.iteration import Iteration
from app.schemas.story import StoryCreate
from app.services.iteration_service import IterationService
from app.services.story_service import StoryService


@pytest.fixture
def story_with_iterations(db_session, sample_story_data):
    """Create a story with some iterations."""
    # Create the story
    service = StoryService(db_session)
    story_create = StoryCreate(**sample_story_data)
    story = service.create(story_create)

    # Add some iterations
    iterations = []
    for i in range(3):
        iteration = Iteration(
            story_id=story.id,
            iteration_number=i + 1,
            feedback=f"Iteration {i + 1} feedback with enough characters to be valid",
            changes_requested={"tone": "darker"} if i == 0 else None,
            game_file_path=f"data/stories/test_001/iterations/iteration_{i + 1:03d}/game.json",
            status="pending" if i == 2 else "accepted",
        )
        db_session.add(iteration)
        iterations.append(iteration)

    db_session.commit()

    return story, iterations


def test_submit_feedback_creates_iteration(db_session, sample_story_data):
    """Test that submit_feedback creates a new iteration."""
    # Create a story first
    story_service = StoryService(db_session)
    story = story_service.create(StoryCreate(**sample_story_data))

    # Submit feedback
    service = IterationService(db_session)
    feedback = "Please make the story more atmospheric and add more body horror elements"
    changes = {"tone": "darker", "focus": "body horror"}

    iteration = service.submit_feedback(story.id, feedback, changes)

    # Verify iteration was created
    assert iteration.id is not None
    assert iteration.story_id == story.id
    assert iteration.iteration_number == 1
    assert iteration.feedback == feedback
    assert iteration.changes_requested == changes
    assert iteration.status == "pending"
    assert "iteration_001" in iteration.game_file_path


def test_submit_feedback_increments_iteration_number(db_session, story_with_iterations):
    """Test that iteration numbers increment correctly."""
    story, _existing_iterations = story_with_iterations

    service = IterationService(db_session)
    feedback = "New feedback for fourth iteration with more than ten characters"

    iteration = service.submit_feedback(story.id, feedback)

    assert iteration.iteration_number == 4
    assert "iteration_004" in iteration.game_file_path


def test_submit_feedback_validates_story_exists(db_session):
    """Test that submit_feedback validates story existence."""
    service = IterationService(db_session)

    with pytest.raises(ValueError, match="Story with id 999 not found"):
        service.submit_feedback(999, "Some feedback text here")


def test_submit_feedback_enforces_iteration_limit(db_session, sample_story_data):
    """Test that submit_feedback enforces the 5 iteration limit."""
    # Create a story
    story_service = StoryService(db_session)
    story = story_service.create(StoryCreate(**sample_story_data))

    # Create 5 iterations
    for i in range(5):
        iteration = Iteration(
            story_id=story.id,
            iteration_number=i + 1,
            feedback=f"Iteration {i + 1} feedback",
            game_file_path=f"data/stories/test_001/iterations/iteration_{i + 1:03d}/game.json",
            status="accepted",
        )
        db_session.add(iteration)

    db_session.commit()

    # Try to submit 6th iteration
    service = IterationService(db_session)
    with pytest.raises(ValueError, match="Maximum iterations \\(5\\) reached"):
        service.submit_feedback(story.id, "Sixth iteration feedback")


def test_submit_feedback_validates_feedback_length(db_session, sample_story_data):
    """Test that submit_feedback validates feedback length."""
    story_service = StoryService(db_session)
    story = story_service.create(StoryCreate(**sample_story_data))

    service = IterationService(db_session)

    # Test empty feedback
    with pytest.raises(ValueError, match="at least 10 characters"):
        service.submit_feedback(story.id, "")

    # Test too short feedback
    with pytest.raises(ValueError, match="at least 10 characters"):
        service.submit_feedback(story.id, "short")


def test_start_iteration_triggers_generation(db_session, story_with_iterations):
    """Test that start_iteration triggers a generation task."""
    story, iterations = story_with_iterations

    service = IterationService(db_session)

    # Mock the generation service's start_generation method
    with patch.object(service.generation_service, "start_generation") as mock_start_generation:
        mock_start_generation.return_value = "test-session-id-123"

        session_id = service.start_iteration(story.id)

        # Verify generation was triggered
        assert session_id == "test-session-id-123"
        mock_start_generation.assert_called_once()

        # Verify the prompt was enhanced with feedback
        call_args = mock_start_generation.call_args
        enhanced_prompt = call_args[1]["prompt"]
        assert "Story Iteration Request" in enhanced_prompt
        assert story.title in enhanced_prompt
        assert story.prompt in enhanced_prompt
        assert iterations[2].feedback in enhanced_prompt  # Most recent pending
        assert f"Iteration {iterations[2].iteration_number}" in enhanced_prompt


def test_start_iteration_uses_original_template(db_session, sample_story_data):
    """Test that start_iteration uses the original story's template_id."""
    # Create a story with a template
    story_data = sample_story_data.copy()
    story_data["template_id"] = "horror_exploration"
    story_service = StoryService(db_session)
    story = story_service.create(StoryCreate(**story_data))

    # Add a pending iteration
    iteration = Iteration(
        story_id=story.id,
        iteration_number=1,
        feedback="Make it scarier with more atmosphere and tension",
        game_file_path="data/stories/test_001/iterations/iteration_001/game.json",
        status="pending",
    )
    db_session.add(iteration)
    db_session.commit()

    service = IterationService(db_session)

    # Mock the generation service
    with patch.object(service.generation_service, "start_generation") as mock_start_generation:
        mock_start_generation.return_value = "test-session-id"

        service.start_iteration(story.id)

        # Verify template_id was passed
        call_args = mock_start_generation.call_args
        assert call_args[1]["template_id"] == "horror_exploration"


def test_start_iteration_validates_story_exists(db_session):
    """Test that start_iteration validates story existence."""
    service = IterationService(db_session)

    with pytest.raises(ValueError, match="Story with id 999 not found"):
        service.start_iteration(999)


def test_start_iteration_requires_pending_iteration(db_session, sample_story_data):
    """Test that start_iteration requires a pending iteration."""
    # Create a story with no iterations
    story_service = StoryService(db_session)
    story = story_service.create(StoryCreate(**sample_story_data))

    service = IterationService(db_session)

    with pytest.raises(ValueError, match="No pending iteration found"):
        service.start_iteration(story.id)


def test_start_iteration_uses_most_recent_pending(db_session, story_with_iterations):
    """Test that start_iteration uses the most recent pending iteration."""
    story, _iterations = story_with_iterations

    # Add another pending iteration
    new_iteration = Iteration(
        story_id=story.id,
        iteration_number=4,
        feedback="This is the newest feedback that should be used",
        game_file_path="data/stories/test_001/iterations/iteration_004/game.json",
        status="pending",
    )
    db_session.add(new_iteration)
    db_session.commit()

    service = IterationService(db_session)

    with patch.object(service.generation_service, "start_generation") as mock_start_generation:
        mock_start_generation.return_value = "test-session-id"

        service.start_iteration(story.id)

        # Verify it used the newest pending iteration (iteration 4)
        call_args = mock_start_generation.call_args
        enhanced_prompt = call_args[1]["prompt"]
        assert "This is the newest feedback that should be used" in enhanced_prompt
        assert "Iteration 4" in enhanced_prompt


def test_list_iterations_returns_all_iterations(db_session, story_with_iterations):
    """Test that list_iterations returns all iterations for a story."""
    story, _existing_iterations = story_with_iterations

    service = IterationService(db_session)
    iterations = service.list_iterations(story.id)

    assert len(iterations) == 3
    # Verify they're in descending order
    assert iterations[0].iteration_number == 3
    assert iterations[1].iteration_number == 2
    assert iterations[2].iteration_number == 1


def test_list_iterations_validates_story_exists(db_session):
    """Test that list_iterations validates story existence."""
    service = IterationService(db_session)

    with pytest.raises(ValueError, match="Story with id 999 not found"):
        service.list_iterations(999)


def test_list_iterations_returns_empty_for_no_iterations(db_session, sample_story_data):
    """Test that list_iterations returns empty list for story with no iterations."""
    story_service = StoryService(db_session)
    story = story_service.create(StoryCreate(**sample_story_data))

    service = IterationService(db_session)
    iterations = service.list_iterations(story.id)

    assert iterations == []


def test_build_iteration_prompt_includes_all_context(db_session, story_with_iterations):
    """Test that the iteration prompt includes all necessary context."""
    story, iterations = story_with_iterations

    service = IterationService(db_session)
    prompt = service._build_iteration_prompt(story, iterations[0])

    # Verify all key components are present
    assert "Story Iteration Request" in prompt
    assert f"Title: {story.title}" in prompt
    assert f"Theme: {story.theme_id}" in prompt
    assert story.prompt in prompt
    assert iterations[0].feedback in prompt
    assert f"Iteration {iterations[0].iteration_number}" in prompt
    assert "Instructions" in prompt

    # Verify structured changes if present
    if iterations[0].changes_requested:
        assert str(iterations[0].changes_requested) in prompt


def test_generate_iteration_path_creates_correct_path(db_session, sample_story_data):
    """Test that iteration paths are generated correctly."""
    story_service = StoryService(db_session)
    story = story_service.create(StoryCreate(**sample_story_data))

    service = IterationService(db_session)

    # Test path generation for different iteration numbers
    path1 = service._generate_iteration_path(story, 1)
    assert str(path1) == "data/stories/test_001/iterations/iteration_001/game.json"

    path2 = service._generate_iteration_path(story, 10)
    assert str(path2) == "data/stories/test_001/iterations/iteration_010/game.json"

    path3 = service._generate_iteration_path(story, 100)
    assert str(path3) == "data/stories/test_001/iterations/iteration_100/game.json"


def test_submit_feedback_without_changes_requested(db_session, sample_story_data):
    """Test that submit_feedback works without changes_requested."""
    story_service = StoryService(db_session)
    story = story_service.create(StoryCreate(**sample_story_data))

    service = IterationService(db_session)
    feedback = "Just some general feedback without structured changes"

    iteration = service.submit_feedback(story.id, feedback)

    assert iteration.feedback == feedback
    assert iteration.changes_requested is None


def test_submit_feedback_strips_whitespace(db_session, sample_story_data):
    """Test that submit_feedback strips leading/trailing whitespace."""
    story_service = StoryService(db_session)
    story = story_service.create(StoryCreate(**sample_story_data))

    service = IterationService(db_session)
    feedback = "  Feedback with extra whitespace  "

    iteration = service.submit_feedback(story.id, feedback)

    assert iteration.feedback == feedback.strip()
