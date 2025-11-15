"""Story management API endpoints."""

import json
import logging
from pathlib import Path
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas.story import StoryListResponse, StoryResponse
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
    search: str | None = Query(default=None, max_length=200, description="Search query"),
    theme_id: str | None = Query(default=None, max_length=50, description="Filter by theme"),
    tags: str | None = Query(default=None, description="Comma-separated tags"),
    is_sample: bool | None = Query(default=None, description="Filter by sample status"),
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
        is_sample: Filter by sample status (true/false)
        service: Story service dependency

    Returns:
        Paginated list of stories
    """
    # Parse tags from comma-separated string, filtering out empty tags
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else None

    return service.list(
        page=page,
        page_size=page_size,
        search=search,
        theme_id=theme_id,
        tags=tags_list,
        is_sample=is_sample,
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
) -> dict[str, Any]:
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

    # Read game.json file with path validation
    game_file = Path(story.game_file_path)

    # Prevent path traversal for relative paths
    if not game_file.is_absolute():
        # For relative paths, try to find the file from current or parent directory
        # This handles both production (run from root) and test contexts (run from backend/)
        resolved_file = None

        for base_dir in [".", ".."]:
            candidate = (Path(base_dir) / story.game_file_path).resolve()

            # Check if file exists and is within allowed directories
            if candidate.exists():
                # Verify the path is within data/stories or data/samples
                try:
                    # Get the resolved base directory
                    base_resolved = Path(base_dir).resolve()

                    # Check against both allowed directories
                    for allowed_subdir in ["data/stories", "data/samples"]:
                        allowed_path = (base_resolved / allowed_subdir).resolve()
                        try:
                            candidate.relative_to(allowed_path)
                            # Path is valid and within allowed directory
                            resolved_file = candidate
                            break
                        except ValueError:
                            # Not within this allowed directory, try next
                            continue

                    if resolved_file:
                        break
                except Exception:
                    continue

        if resolved_file is None:
            logger.error("Invalid game file path attempted: %s", story.game_file_path)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this file path is not allowed",
            )

        game_file = resolved_file

    if not game_file.exists():
        logger.error("Game file not found: %s", story.game_file_path)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game file not found for story {story_id}",
        )

    try:
        with game_file.open(encoding="utf-8") as f:
            content = cast("dict[str, Any]", json.load(f))
        return content
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in game file: %s - %s", story.game_file_path, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Game file contains invalid JSON",
        ) from e
    except HTTPException:
        # Re-raise HTTPException from earlier in the function
        raise
    except OSError as e:
        logger.error("Error reading game file: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read game file",
        ) from e


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
    story_id: int,
    service: StoryService = Depends(get_story_service),
) -> None:
    """
    Delete a story (sample stories cannot be deleted).

    Args:
        story_id: Story ID
        service: Story service dependency

    Raises:
        HTTPException: 404 if story not found
        HTTPException: 403 if trying to delete a sample story
    """
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
