"""Service layer for managing story iterations and feedback."""

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from ..models.iteration import Iteration
from ..models.story import Story
from .generation_service import GenerationService
from .story_service import StoryService

logger = logging.getLogger(__name__)


class IterationService:
    """Service for managing story iterations with user feedback."""

    MAX_ITERATIONS = 5

    def __init__(self, db: Session):
        """
        Initialize iteration service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.story_service = StoryService(db)
        self.generation_service = GenerationService(db)

    def submit_feedback(
        self, story_id: int, feedback: str, changes_requested: dict[str, str] | None = None
    ) -> Iteration:
        """
        Submit feedback for a story iteration.

        Creates a new Iteration record with pending status. Does not trigger
        generation - use start_iteration() for that.

        Args:
            story_id: ID of the story to iterate on
            feedback: User feedback text
            changes_requested: Optional structured feedback data (JSON)

        Returns:
            Created Iteration model

        Raises:
            ValueError: If story not found, iteration limit reached, or feedback invalid
        """
        # Validate story exists
        story = self.story_service.get(story_id)
        if not story:
            raise ValueError(f"Story with id {story_id} not found")

        # Check iteration limit
        current_iteration_count = (
            self.db.query(Iteration).filter(Iteration.story_id == story_id).count()
        )

        if current_iteration_count >= self.MAX_ITERATIONS:
            raise ValueError(
                f"Maximum iterations ({self.MAX_ITERATIONS}) reached for story {story_id}"
            )

        # Validate feedback
        if not feedback or len(feedback.strip()) < 10:
            raise ValueError("Feedback must be at least 10 characters")

        try:
            # Calculate next iteration number
            iteration_number = current_iteration_count + 1

            # Create placeholder game file path (will be set when iteration completes)
            game_file_path = self._generate_iteration_path(story, iteration_number)

            # Create iteration record
            iteration = Iteration(
                story_id=story_id,
                iteration_number=iteration_number,
                feedback=feedback.strip(),
                changes_requested=changes_requested,
                game_file_path=str(game_file_path),
                status="pending",
            )

            self.db.add(iteration)
            self.db.commit()
            self.db.refresh(iteration)

            logger.info(
                f"Created iteration {iteration_number} for story {story_id} (ID: {iteration.id})"
            )
            return iteration

        except Exception:
            self.db.rollback()
            raise

    def start_iteration(self, story_id: int) -> str:
        """
        Start a new iteration by triggering generation with feedback context.

        Takes the most recent pending iteration and triggers a new generation
        task with the original prompt + feedback as context.

        Args:
            story_id: ID of the story to iterate on

        Returns:
            str: Session ID for tracking generation progress

        Raises:
            ValueError: If story not found or no pending iteration exists
        """
        # Validate story exists
        story = self.story_service.get(story_id)
        if not story:
            raise ValueError(f"Story with id {story_id} not found")

        # Get the most recent pending iteration
        iteration = (
            self.db.query(Iteration)
            .filter(Iteration.story_id == story_id, Iteration.status == "pending")
            .order_by(Iteration.iteration_number.desc())
            .first()
        )

        if not iteration:
            raise ValueError(f"No pending iteration found for story {story_id}")

        try:
            # Build context-aware prompt
            enhanced_prompt = self._build_iteration_prompt(story, iteration)

            # Trigger generation using the generation service
            # Use the same template_id as the original story if available
            template_id: str | None = story.template_id  # type: ignore[assignment]
            session_id = self.generation_service.start_generation(
                prompt=enhanced_prompt, template_id=template_id
            )

            logger.info(
                f"Started iteration {iteration.iteration_number} for story {story_id}, "
                f"session: {session_id}"
            )

            return session_id

        except Exception:
            logger.exception(
                f"Failed to start iteration {iteration.iteration_number} for story {story_id}"
            )
            raise

    def list_iterations(self, story_id: int) -> list[Iteration]:
        """
        List all iterations for a story.

        Args:
            story_id: ID of the story

        Returns:
            List of Iteration models, ordered by iteration_number descending

        Raises:
            ValueError: If story not found
        """
        # Validate story exists
        story = self.story_service.get(story_id)
        if not story:
            raise ValueError(f"Story with id {story_id} not found")

        iterations: list[Iteration] = (
            self.db.query(Iteration)
            .filter(Iteration.story_id == story_id)
            .order_by(Iteration.iteration_number.desc())
            .all()
        )

        return iterations

    def _generate_iteration_path(self, story: Story, iteration_number: int) -> Path:
        """
        Generate file path for iteration game.json.

        Args:
            story: Story model
            iteration_number: Iteration number

        Returns:
            Path: Generated file path
        """
        # Extract base path from story's game_file_path
        # e.g., "data/stories/story_001/game.json" -> "data/stories/story_001"
        story_path = Path(story.game_file_path).parent

        # Create iteration subdirectory path
        # e.g., "data/stories/story_001/iterations/iteration_001/game.json"
        iteration_path = (
            story_path / "iterations" / f"iteration_{iteration_number:03d}" / "game.json"
        )

        return iteration_path

    def _build_iteration_prompt(self, story: Story, iteration: Iteration) -> str:
        """
        Build an enhanced prompt for iteration generation.

        Combines the original prompt with user feedback to provide context
        for the AI generation crew.

        Args:
            story: Original story
            iteration: Iteration with user feedback

        Returns:
            str: Enhanced prompt with feedback context
        """
        # Build context-aware prompt
        prompt_parts: list[str] = [
            "# Story Iteration Request",
            "",
            "## Original Story",
            f"Title: {story.title}",
            f"Theme: {story.theme_id!s}",
            "",
            "## Original Prompt",
            f"{story.prompt!s}",
            "",
            f"## Iteration {iteration.iteration_number} - User Feedback",
            f"{iteration.feedback!s}",
        ]

        # Add structured feedback if available
        if iteration.changes_requested:
            prompt_parts.extend(
                [
                    "",
                    "## Specific Changes Requested",
                    str(iteration.changes_requested),
                ]
            )

        prompt_parts.extend(
            [
                "",
                "## Instructions",
                "Generate an improved version of the story that addresses the user's feedback "
                "while maintaining the core theme and narrative structure. Preserve what worked "
                "well in the original and improve the areas identified in the feedback.",
            ]
        )

        return "\n".join(prompt_parts)
