"""Generation API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas.generation import (
    GenerationRequest,
    GenerationResponse,
    GenerationStatusResponse,
)
from ...services.generation_service import GenerationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/generate", tags=["generation"])


def get_generation_service(db: Session = Depends(get_db)) -> GenerationService:
    """
    Dependency to get generation service.

    Args:
        db: Database session

    Returns:
        GenerationService instance
    """
    return GenerationService(db)


@router.post("", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
async def start_generation(
    request: GenerationRequest,
    service: GenerationService = Depends(get_generation_service),
) -> GenerationResponse:
    """
    Start a new story generation task.

    This endpoint creates a new generation session and enqueues a background task
    to run the CrewAI generation process. The returned session_id can be used to
    poll for progress and status.

    Args:
        request: Generation request with prompt and optional template_id
        service: Generation service dependency

    Returns:
        GenerationResponse with session_id and initial status

    Raises:
        HTTPException: 400 if prompt validation fails
        HTTPException: 500 if session creation fails
    """
    try:
        session_id = service.start_generation(
            prompt=request.prompt,
            template_id=request.template_id,
        )

        logger.info(f"Started generation session: {session_id}")

        return GenerationResponse(
            session_id=session_id,
            status="pending",
            message="Generation task started successfully",
        )

    except ValueError as e:
        logger.warning(f"Invalid generation request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Failed to start generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start generation task",
        ) from e


@router.get("/{session_id}", response_model=GenerationStatusResponse)
async def get_generation_status(
    session_id: str,
    service: GenerationService = Depends(get_generation_service),
) -> GenerationStatusResponse:
    """
    Get the current status and progress of a generation task.

    Args:
        session_id: Session ID from start_generation
        service: Generation service dependency

    Returns:
        GenerationStatusResponse with current status and progress

    Raises:
        HTTPException: 404 if session not found
    """
    session = service.get_session(session_id)

    if not session:
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation session {session_id} not found",
        )

    return GenerationStatusResponse.model_validate(session)
