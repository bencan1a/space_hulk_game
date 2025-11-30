"""Celery tasks for story generation using CrewAI."""

import json
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# Import the SpaceHulkGame crew
from src.space_hulk_game.crew import SpaceHulkGame

from ..api.websocket import broadcast_progress
from ..celery_app import celery_app
from ..config import settings
from ..database import SessionLocal
from ..integrations.crewai_wrapper import CrewAIWrapper, CrewExecutionError, CrewTimeoutError
from ..schemas.story import StoryCreate
from ..services.generation_service import GenerationService
from ..services.story_service import StoryService

logger = logging.getLogger(__name__)

# Configurable base directory for crew output files
# Defaults to /workspaces/space_hulk_game/game-config for Docker compatibility
GAME_CONFIG_DIR = Path(
    os.environ.get("GAME_CONFIG_DIR", "/workspaces/space_hulk_game/game-config")
)


def _load_crew_output() -> dict[str, Any]:
    """
    Load the crew's output from the playable_game.json file.

    The crew outputs to game-config/playable_game.json. We load this file
    directly and return its contents. The backend will use the crew's format
    as-is, without transformation.

    Returns:
        dict: Dictionary with structure {"game": {...}} where the "game" key
            contains the full game content including title, description,
            starting_scene, scenes, etc.

    Raises:
        CrewExecutionError: If the output file cannot be found or parsed
    """
    game_config_path = GAME_CONFIG_DIR / "playable_game.json"

    if not game_config_path.exists():
        logger.error(f"Crew output file not found at {game_config_path}")
        raise CrewExecutionError(
            "Crew output file not found. "
            "The crew may have failed to generate the game or the output file was not created."
        )

    try:
        with game_config_path.open() as f:
            game_data = json.load(f)
            logger.info(f"Loaded crew output from {game_config_path}")

            # Validate that we have a game structure
            if not isinstance(game_data, dict):
                raise CrewExecutionError(
                    f"Invalid crew output format: expected dict, got {type(game_data).__name__}"
                )

            # The crew outputs {"game": {...}}, return it as-is
            if "game" not in game_data:
                raise CrewExecutionError(
                    "Invalid crew output: missing 'game' key in playable_game.json"
                )

            return game_data

    except json.JSONDecodeError as exc:
        logger.error(f"Failed to parse crew output file {game_config_path}: {exc}")
        raise CrewExecutionError(
            "Failed to parse crew output file. The file may be corrupted or contain invalid JSON."
        ) from exc
    except Exception as exc:
        if isinstance(exc, CrewExecutionError):
            raise
        logger.error(f"Error reading crew output file {game_config_path}: {exc}")
        raise CrewExecutionError(
            "Error reading crew output file. Check logs for details."
        ) from exc


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
        logger.info(f"Starting real CrewAI generation for session {session_id}")

        gen_service.update_session(
            session_id=session_id,
            current_step="Initializing AI crew",
            progress_percent=10,
        )

        # Create crew instance
        try:
            crew_instance = SpaceHulkGame()
            crew = crew_instance.crew()
            logger.info("SpaceHulkGame crew initialized successfully")
        except Exception as exc:
            logger.error(f"Failed to initialize crew: {exc}", exc_info=True)
            raise CrewExecutionError(f"Failed to initialize crew: {exc}") from exc

        gen_service.update_session(
            session_id=session_id,
            current_step="Executing AI generation",
            progress_percent=15,
        )

        # Execute with progress callback using context manager for proper resource cleanup
        logger.info(f"Executing crew with prompt: {prompt[:100]}...")
        with CrewAIWrapper(timeout_seconds=840) as wrapper:
            result = wrapper.execute_generation(
                crew=crew,
                prompt=prompt,
                progress_callback=progress_callback,
            )

        # Check crew execution result
        # The wrapper returns status but the actual game data is written to disk by the crew
        if result.get("status") != "success":
            error_msg = result.get("error", "Unknown error during crew execution")
            logger.error(f"Crew execution failed: {error_msg}")
            raise CrewExecutionError(error_msg)

        logger.info("Crew execution completed successfully")

        # Load crew output from playable_game.json
        # Note: The crew writes output to disk (game-config/playable_game.json),
        # we load from the file rather than the wrapper's result object
        game_data = _load_crew_output()

        logger.info(f"Loaded crew output: {game_data.get('game', {}).get('title', 'Unknown')}")

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
        # The crew outputs {"game": {...}}, so we need to access game_data["game"]
        game_content = game_data.get("game", {})
        if not isinstance(game_content, dict):
            raise CrewExecutionError(
                f"Invalid game structure: expected dict, got {type(game_content).__name__}"
            )

        title = str(game_content.get("title", f"Generated Story {session_id[:8]}"))
        description = str(game_content.get("description", ""))

        # Count statistics from the crew's scene structure
        # The crew outputs scenes as a dict: {"scene_id": {...}, ...}
        scenes_dict = game_content.get("scenes", {})
        if not isinstance(scenes_dict, dict):
            logger.warning(f"Expected scenes to be dict, got {type(scenes_dict).__name__}")
            scenes_dict = {}

        scene_count = len(scenes_dict)

        # Count items and NPCs across all scenes
        item_count = 0
        npc_count = 0
        for scene_data in scenes_dict.values():
            if isinstance(scene_data, dict):
                items = scene_data.get("items", [])
                npcs = scene_data.get("npcs", [])
                if isinstance(items, list):
                    item_count += len(items)
                if isinstance(npcs, list):
                    npc_count += len(npcs)

        # Puzzles might be in events
        puzzle_count = 0
        for scene_data in scenes_dict.values():
            if isinstance(scene_data, dict):
                events = scene_data.get("events", [])
                if isinstance(events, list):
                    puzzle_count += sum(1 for e in events if isinstance(e, dict) and e.get("type") == "puzzle")

        # Create Story record
        story_create = StoryCreate(
            title=title,
            description=description,
            theme_id="warhammer40k",  # Default theme
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
