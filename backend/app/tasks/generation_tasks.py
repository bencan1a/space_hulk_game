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
from ..integrations.crewai_wrapper import CrewAIWrapper, CrewExecutionError, CrewTimeoutError
from ..schemas.story import StoryCreate
from ..services.generation_service import GenerationService
from ..services.story_service import StoryService

# Import the SpaceHulkGame crew
from src.space_hulk_game.crew import SpaceHulkGame

logger = logging.getLogger(__name__)


def _parse_crew_output_to_game_json(crew_output: Any, prompt: str) -> dict[str, Any]:
    """
    Parse CrewAI output into the expected game.json format.
    
    The crew may output in several formats:
    1. A CrewOutput object with .raw, .tasks_output attributes
    2. A dict with the game structure
    3. A string (raw JSON text)
    
    The final crew task (TranslateNarrativeToGameStructure) outputs to
    game-config/playable_game.json with structure:
    {
        "game": {
            "title": str,
            "description": str,
            "starting_scene": str,
            "scenes": { scene_id: {...}, ... }
        }
    }
    
    We need to transform this to:
    {
        "metadata": { title, description, theme, difficulty, estimated_duration },
        "scenes": [ {...}, ... ],
        "items": [ {...}, ... ],
        "npcs": [ {...}, ... ],
        "puzzles": [ {...}, ... ]
    }
    
    Args:
        crew_output: The output from CrewAI execution
        prompt: The original user prompt (for fallback metadata)
        
    Returns:
        dict: Game data in the expected format
    """
    logger.info(f"Parsing crew output. Type: {type(crew_output)}")
    
    # Handle different output formats
    game_structure = None
    
    # Case 1: CrewOutput object (has .raw and .tasks_output attributes)
    if hasattr(crew_output, "raw") or hasattr(crew_output, "tasks_output"):
        logger.info("Crew output is CrewOutput object")
        
        # Try to load from playable_game.json file if it exists
        game_config_path = Path("/workspaces/space_hulk_game/game-config/playable_game.json")
        if game_config_path.exists():
            logger.info(f"Loading game structure from {game_config_path}")
            try:
                with game_config_path.open() as f:
                    file_content = json.load(f)
                    game_structure = file_content.get("game", file_content)
            except Exception as exc:
                logger.warning(f"Failed to load playable_game.json: {exc}")
        
        # Fallback: Try to parse raw output as JSON
        if not game_structure and hasattr(crew_output, "raw"):
            try:
                raw_text = str(crew_output.raw)
                # Try to find JSON in the raw text
                if "{" in raw_text and "}" in raw_text:
                    start = raw_text.find("{")
                    end = raw_text.rfind("}") + 1
                    json_text = raw_text[start:end]
                    parsed = json.loads(json_text)
                    game_structure = parsed.get("game", parsed)
            except Exception as exc:
                logger.warning(f"Failed to parse raw output as JSON: {exc}")
    
    # Case 2: Dict output
    elif isinstance(crew_output, dict):
        logger.info("Crew output is dict")
        game_structure = crew_output.get("game", crew_output)
    
    # Case 3: String output (raw JSON)
    elif isinstance(crew_output, str):
        logger.info("Crew output is string")
        try:
            parsed = json.loads(crew_output)
            game_structure = parsed.get("game", parsed)
        except Exception as exc:
            logger.warning(f"Failed to parse string output as JSON: {exc}")
    
    # If we still don't have game structure, create a minimal fallback
    if not game_structure or not isinstance(game_structure, dict):
        logger.warning("Could not parse crew output, using fallback structure")
        return _create_fallback_game_data(prompt)
    
    # Transform the game structure to expected format
    return _transform_game_structure(game_structure, prompt)


def _transform_game_structure(game_structure: dict[str, Any], prompt: str) -> dict[str, Any]:
    """
    Transform the crew's game structure to the expected format.
    
    Args:
        game_structure: The game structure from crew output
        prompt: Original user prompt (for fallback metadata)
        
    Returns:
        dict: Transformed game data
    """
    # Extract metadata
    title = game_structure.get("title", f"Generated Story: {prompt[:50]}")
    description = game_structure.get("description", f"A story generated from: {prompt}")
    
    # Build scenes array from scenes dict
    scenes_dict = game_structure.get("scenes", {})
    scenes = []
    items = []
    npcs = []
    puzzles = []
    
    for scene_id, scene_data in scenes_dict.items():
        if not isinstance(scene_data, dict):
            continue
            
        # Transform scene
        scene = {
            "id": scene_data.get("id", scene_id),
            "name": scene_data.get("name", "Unknown Area"),
            "description": scene_data.get("description", ""),
            "exits": scene_data.get("exits", {}),
            "items": scene_data.get("items", []),
        }
        scenes.append(scene)
        
        # Collect items from scene
        scene_items = scene_data.get("items", [])
        if isinstance(scene_items, list):
            for item in scene_items:
                if isinstance(item, dict) and item.get("id"):
                    # Item is a full object
                    items.append(item)
                elif isinstance(item, str):
                    # Item is just an ID reference - skip for now
                    pass
        
        # Collect NPCs from scene
        scene_npcs = scene_data.get("npcs", [])
        if isinstance(scene_npcs, list):
            for npc in scene_npcs:
                if isinstance(npc, dict) and npc.get("id"):
                    npcs.append(npc)
        
        # Collect puzzles from scene events
        scene_events = scene_data.get("events", [])
        if isinstance(scene_events, list):
            for event in scene_events:
                if isinstance(event, dict) and event.get("type") == "puzzle":
                    puzzles.append(event)
    
    # Return transformed structure
    return {
        "metadata": {
            "title": title,
            "description": description,
            "theme": "warhammer40k",
            "difficulty": "medium",
            "estimated_duration": "30-45 minutes",
        },
        "scenes": scenes,
        "items": items,
        "npcs": npcs,
        "puzzles": puzzles,
    }


def _create_fallback_game_data(prompt: str) -> dict[str, Any]:
    """
    Create fallback game data when crew output cannot be parsed.
    
    Args:
        prompt: Original user prompt
        
    Returns:
        dict: Minimal valid game data
    """
    logger.warning("Creating fallback game data")
    return {
        "metadata": {
            "title": f"Generated Story: {prompt[:50]}",
            "description": f"A story generated from: {prompt}",
            "theme": "warhammer40k",
            "difficulty": "medium",
            "estimated_duration": "30-45 minutes",
        },
        "scenes": [
            {
                "id": "scene_start",
                "name": "Starting Area",
                "description": "The beginning of your journey in the dark corridors of a Space Hulk.",
                "exits": {},
                "items": [],
            }
        ],
        "items": [],
        "npcs": [],
        "puzzles": [],
    }


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

        # Create wrapper with timeout (14 minutes)
        wrapper = CrewAIWrapper(timeout_seconds=840)

        gen_service.update_session(
            session_id=session_id,
            current_step="Executing AI generation",
            progress_percent=15,
        )

        # Execute with progress callback
        logger.info(f"Executing crew with prompt: {prompt[:100]}...")
        result = wrapper.execute_generation(
            crew=crew,
            prompt=prompt,
            progress_callback=progress_callback,
        )

        # Extract output from crew result
        # The result is a dict with 'status', 'output', and 'metadata'
        if result.get("status") != "success":
            error_msg = result.get("error", "Unknown error during crew execution")
            logger.error(f"Crew execution failed: {error_msg}")
            raise CrewExecutionError(error_msg)

        crew_output = result.get("output", {})
        logger.info(f"Crew execution completed. Output type: {type(crew_output)}")

        # Parse crew output to game.json format
        # The crew outputs to game-config/playable_game.json with structure:
        # { "game": { "title", "description", "starting_scene", "scenes": {...} } }
        game_data = _parse_crew_output_to_game_json(crew_output, prompt)
        
        logger.info(f"Parsed game data with {len(game_data.get('scenes', []))} scenes")

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
