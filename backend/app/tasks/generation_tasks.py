"""Celery tasks for story generation using CrewAI."""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from ..api.websocket import broadcast_progress
from ..celery_app import celery_app
from ..config import settings
from ..database import SessionLocal
from ..integrations.crewai_wrapper import CrewExecutionError, CrewTimeoutError
from ..schemas.story import StoryCreate
from ..services.generation_service import GenerationService
from ..services.story_service import StoryService

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.generation_tasks.run_generation_crew",
    max_retries=0,  # Don't retry generation tasks - they're expensive
    task_time_limit=900,  # 15 minutes
    task_soft_time_limit=840,  # 14 minutes
)
def run_generation_crew(
    session_id: str, prompt: str, template_id: str | None = None
) -> dict[str, Any]:
    """
    Run CrewAI generation in the background.

    This task:
    1. Updates the Session model with progress
    2. Executes the CrewAI wrapper
    3. Saves the generated game.json to filesystem
    4. Creates a Story record using StoryService
    5. Updates Session with final status

    Args:
        session_id: Unique session ID
        prompt: User's generation prompt
        template_id: Optional template identifier

    Returns:
        dict: Task result with status and data

    Raises:
        Exception: If generation fails
    """
    logger.info(f"Starting generation task for session: {session_id}")

    # Create database session directly
    db: Session = SessionLocal()  # type: ignore[assignment]
    gen_service: GenerationService | None = None
    story_id: int | None = None

    try:
        gen_service = GenerationService(db)
        story_service = StoryService(db)

        # Update session to running
        gen_service.update_session(
            session_id=session_id,
            status="running",
            current_step="Initializing generation",
            progress_percent=5,
        )

        # Define progress callback
        def progress_callback(status: str, data: dict[str, Any]) -> None:
            """Update session with progress from CrewAI wrapper and broadcast via WebSocket."""
            try:
                if status == "started":
                    gen_service.update_session(
                        session_id=session_id,
                        current_step="Starting AI crew",
                        progress_percent=10,
                    )
                    # Broadcast to WebSocket clients
                    broadcast_progress(
                        session_id,
                        status,
                        {"current_step": "Starting AI crew", "progress_percent": 10},
                    )
                elif status == "task_started":
                    task_name = data.get("task_name", "Processing")
                    task_index = data.get("task_index", 0)
                    total_tasks = data.get("total_tasks", 1)
                    # Calculate progress: 10% start, 90% for tasks
                    progress = 10 + int((task_index / total_tasks) * 80)
                    gen_service.update_session(
                        session_id=session_id,
                        current_step=f"Running: {task_name}",
                        progress_percent=progress,
                    )
                    # Broadcast to WebSocket clients
                    broadcast_progress(
                        session_id,
                        status,
                        {
                            "task_name": task_name,
                            "task_index": task_index,
                            "total_tasks": total_tasks,
                            "current_step": f"Running: {task_name}",
                            "progress_percent": progress,
                        },
                    )
                elif status == "task_completed":
                    task_name = data.get("task_name", "Task")
                    task_index = data.get("task_index", 0)
                    total_tasks = data.get("total_tasks", 1)
                    progress = 10 + int(((task_index + 1) / total_tasks) * 80)
                    gen_service.update_session(
                        session_id=session_id,
                        current_step=f"Completed: {task_name}",
                        progress_percent=progress,
                    )
                    # Broadcast to WebSocket clients
                    broadcast_progress(
                        session_id,
                        status,
                        {
                            "task_name": task_name,
                            "task_index": task_index,
                            "total_tasks": total_tasks,
                            "current_step": f"Completed: {task_name}",
                            "progress_percent": progress,
                        },
                    )
                elif status == "completed":
                    gen_service.update_session(
                        session_id=session_id,
                        current_step="Finalizing generation",
                        progress_percent=95,
                    )
                    # Broadcast to WebSocket clients
                    broadcast_progress(
                        session_id,
                        status,
                        {"current_step": "Finalizing generation", "progress_percent": 95},
                    )
                elif status == "error":
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"CrewAI error for session {session_id}: {error_msg}")
                    # Broadcast error to WebSocket clients
                    broadcast_progress(session_id, status, {"error": error_msg})
                elif status == "timeout":
                    logger.error(f"CrewAI timeout for session {session_id}")
                    # Broadcast timeout to WebSocket clients
                    broadcast_progress(session_id, status, {})

            except Exception as e:
                logger.warning(f"Error in progress callback: {e}")

        # Execute CrewAI generation
        # TODO: Integrate actual CrewAI crew when available in production
        # This would involve:
        #   1. Importing the crew: from src.space_hulk_game.crew import SpaceHulkGame
        #   2. Creating crew instance: crew_instance = SpaceHulkGame().crew()
        #   3. Creating wrapper: wrapper = CrewAIWrapper(timeout_seconds=840)
        #   4. Executing: result = wrapper.execute_generation(crew_instance, prompt, progress_callback)

        gen_service.update_session(
            session_id=session_id,
            current_step="Executing AI generation",
            progress_percent=20,
        )

        # Simulate crew execution for MVP
        logger.info(f"Simulating generation for session {session_id} (TODO: integrate actual crew)")

        # Simulate progress updates
        progress_callback("started", {"prompt": prompt})
        progress_callback(
            "task_started", {"task_index": 0, "task_name": "Story Design", "total_tasks": 3}
        )
        progress_callback(
            "task_completed", {"task_index": 0, "task_name": "Story Design", "total_tasks": 3}
        )
        progress_callback(
            "task_started", {"task_index": 1, "task_name": "Scene Creation", "total_tasks": 3}
        )
        progress_callback(
            "task_completed", {"task_index": 1, "task_name": "Scene Creation", "total_tasks": 3}
        )
        progress_callback(
            "task_started", {"task_index": 2, "task_name": "Game Assembly", "total_tasks": 3}
        )
        progress_callback(
            "task_completed", {"task_index": 2, "task_name": "Game Assembly", "total_tasks": 3}
        )

        # Create simulated game.json output
        game_data = {
            "metadata": {
                "title": f"Generated Story: {prompt[:50]}...",
                "description": f"A story generated from: {prompt}",
                "theme": "warhammer40k",
                "difficulty": "medium",
                "estimated_duration": "30-45 minutes",
            },
            "scenes": [
                {
                    "id": "scene_01",
                    "name": "Starting Area",
                    "description": "The beginning of your journey in the dark corridors.",
                    "exits": {"north": "scene_02"},
                    "items": ["flashlight"],
                }
            ],
            "items": [
                {
                    "id": "flashlight",
                    "name": "Flashlight",
                    "description": "A standard issue flashlight",
                }
            ],
            "npcs": [],
            "puzzles": [],
        }

        progress_callback("completed", {"output": game_data, "status": "success"})

        # Save game.json to filesystem
        gen_service.update_session(
            session_id=session_id,
            current_step="Saving game data",
            progress_percent=90,
        )

        # Use configurable base directory for story files
        base_dir = Path(settings.stories_data_dir).resolve()
        game_dir = base_dir / session_id
        game_dir.mkdir(parents=True, exist_ok=True)
        game_file_path = game_dir / "game.json"

        game_file_path.write_text(json.dumps(game_data, indent=2))

        logger.info(f"Saved game.json to {game_file_path}")

        # Extract metadata from game.json for Story record
        metadata = game_data.get("metadata", {})
        assert isinstance(metadata, dict)  # Ensure type checker knows this is a dict
        title = str(metadata.get("title", f"Generated Story {session_id[:8]}"))
        description = str(metadata.get("description", ""))
        theme_id = str(metadata.get("theme", "warhammer40k"))

        # Count statistics
        scene_count = len(game_data.get("scenes", []))
        item_count = len(game_data.get("items", []))
        npc_count = len(game_data.get("npcs", []))
        puzzle_count = len(game_data.get("puzzles", []))

        # Create Story record
        story_create = StoryCreate(
            title=title,
            description=description,
            theme_id=theme_id,
            prompt=prompt,
            template_id=template_id,
            game_file_path=str(game_file_path),
            tags=[],  # TODO: Extract tags from metadata or generation
        )

        story = story_service.create(story_create)
        story_id = int(story.id)

        # Update story statistics (import here to avoid circular dependency)
        from ..schemas.story import StoryUpdate  # noqa: PLC0415

        try:
            story_service.update(
                story_id,
                StoryUpdate(
                    scene_count=scene_count,
                    item_count=item_count,
                    npc_count=npc_count,
                    puzzle_count=puzzle_count,
                ),
            )
        except Exception as update_exc:
            # If update fails, try to clean up the created story
            logger.error(f"Failed to update story statistics, cleaning up: {update_exc}")
            try:
                story_service.delete(story_id)
            except Exception as delete_exc:
                logger.error(f"Failed to delete story during cleanup: {delete_exc}")
            raise

        logger.info(f"Created story record: {story.id}")

        # Update session with completion
        gen_service.update_session(
            session_id=session_id,
            status="completed",
            current_step="Generation complete",
            progress_percent=100,
            story_id=story_id,
        )

        return {
            "status": "success",
            "session_id": session_id,
            "story_id": story.id,
            "game_file_path": str(game_file_path),
        }

    except (CrewTimeoutError, CrewExecutionError) as exc:
        logger.error(f"CrewAI execution failed for session {session_id}: {exc}")
        if gen_service:
            gen_service.update_session(
                session_id=session_id,
                status="failed",
                error_message=str(exc),
            )
        raise

    except Exception as exc:
        logger.error(f"Generation task failed for session {session_id}: {exc}", exc_info=True)
        if gen_service:
            gen_service.update_session(
                session_id=session_id,
                status="failed",
                error_message=str(exc),
            )
        raise

    finally:
        # Close database session
        db.close()
