"""Template management API endpoints."""

import logging
from functools import lru_cache
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ...services.template_service import TemplateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


class TemplateMetadata(BaseModel):
    """Template metadata response model."""

    name: str = Field(..., description="Template identifier")
    title: str = Field(..., description="Human-readable template title")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category")
    variables: list[dict[str, Any]] = Field(
        ..., description="Template variable definitions"
    )


class TemplateDetail(BaseModel):
    """Full template details response model."""

    name: str = Field(..., description="Template identifier")
    title: str = Field(..., description="Human-readable template title")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category")
    variables: list[dict[str, Any]] = Field(
        ..., description="Template variable definitions"
    )
    prompt: str = Field(..., description="Template prompt content")


class TemplateListResponse(BaseModel):
    """Response model for list of templates."""

    templates: list[TemplateMetadata] = Field(..., description="List of templates")
    total: int = Field(..., description="Total number of templates")


@lru_cache
def get_template_service() -> TemplateService:
    """
    Dependency to get template service.

    Returns:
        Cached TemplateService instance (singleton)
    """
    return TemplateService()


@router.get("", response_model=TemplateListResponse)
async def list_templates() -> TemplateListResponse:
    """
    List all available templates.

    Returns:
        List of template metadata

    Raises:
        HTTPException: 500 if templates directory is not found or cannot be read
    """
    try:
        service = get_template_service()
        template_list = service.list_templates()

        # Convert to TemplateMetadata models
        templates = [TemplateMetadata(**t) for t in template_list]

        return TemplateListResponse(templates=templates, total=len(templates))
    except FileNotFoundError as e:
        logger.error(f"Templates directory not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Templates directory not found",
        ) from e
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list templates",
        ) from e


@router.get("/{name}", response_model=TemplateDetail)
async def get_template(name: str) -> TemplateDetail:
    """
    Get a specific template by name.

    Args:
        name: Template name (without .yaml extension)

    Returns:
        Full template details

    Raises:
        HTTPException: 404 if template not found, 500 if template is invalid
    """
    try:
        service = get_template_service()
        template_data = service.get_template(name)

        return TemplateDetail(
            name=name,
            title=template_data.get("title", name),
            description=template_data.get("description", ""),
            category=template_data.get("category", "general"),
            variables=template_data.get("variables", []),
            prompt=template_data.get("prompt", ""),
        )
    except FileNotFoundError:
        logger.warning(f"Template not found: {name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{name}' not found",
        ) from None
    except ValueError as e:
        logger.error(f"Invalid template '{name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid template: {e}",
        ) from e
    except Exception as e:
        logger.error(f"Error getting template '{name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get template",
        ) from e
