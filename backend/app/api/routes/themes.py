"""Theme management API endpoints."""

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from ...services.theme_service import ThemeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/themes", tags=["themes"])


def get_theme_service() -> ThemeService:
    """
    Dependency to get theme service.

    Returns:
        ThemeService instance
    """
    return ThemeService()


@router.get("")
async def list_themes(
    theme_service: ThemeService = Depends(get_theme_service),
) -> dict[str, list[dict[str, Any]]]:
    """
    List all available themes.

    Args:
        theme_service: Theme service dependency

    Returns:
        Dictionary with list of theme metadata

    Example response:
        {
            "data": [
                {
                    "id": "warhammer40k",
                    "name": "Warhammer 40,000",
                    "description": "Grimdark gothic sci-fi horror"
                }
            ]
        }
    """
    themes = theme_service.list_themes()
    return {"data": themes}


@router.get("/{theme_id}")
async def get_theme(
    theme_id: str,
    theme_service: ThemeService = Depends(get_theme_service),
) -> dict[str, dict[str, Any]]:
    """
    Get complete theme configuration.

    Args:
        theme_id: Theme identifier
        theme_service: Theme service dependency

    Returns:
        Dictionary with theme configuration

    Raises:
        HTTPException: 404 if theme not found

    Example response:
        {
            "data": {
                "id": "warhammer40k",
                "name": "Warhammer 40,000",
                "colors": {...},
                "typography": {...},
                ...
            }
        }
    """
    theme = theme_service.load_theme(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theme '{theme_id}' not found",
        )

    return {"data": theme.to_dict()}


@router.get("/{theme_id}/assets/{asset_path:path}")
async def get_theme_asset(
    theme_id: str,
    asset_path: str,
    theme_service: ThemeService = Depends(get_theme_service),
) -> FileResponse:
    """
    Serve theme asset file.

    Args:
        theme_id: Theme identifier
        asset_path: Relative path to asset within theme directory
        theme_service: Theme service dependency

    Returns:
        File response with appropriate Content-Type

    Raises:
        HTTPException: 404 if theme or asset not found
        HTTPException: 400 if asset path is invalid (directory traversal)

    Example:
        GET /api/v1/themes/warhammer40k/assets/logo.png
        GET /api/v1/themes/warhammer40k/assets/background.jpg
    """
    # Validate asset path (prevent directory traversal)
    if ".." in asset_path or asset_path.startswith("/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid asset path",
        )

    # Load theme to verify it exists
    theme = theme_service.load_theme(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theme '{theme_id}' not found",
        )

    # Construct asset path
    asset_file = theme_service.themes_dir / theme_id / asset_path

    # Validate that resolved path is within theme directory (security check)
    theme_dir = theme_service.themes_dir / theme_id
    try:
        asset_file_resolved = asset_file.resolve()
        theme_dir_resolved = theme_dir.resolve()
        if not asset_file_resolved.is_relative_to(theme_dir_resolved):
            logger.warning(
                f"Path traversal attempt blocked: {asset_path} resolves outside theme directory"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid asset path",
            )
    except (ValueError, OSError) as e:
        logger.error(f"Error resolving asset path: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid asset path",
        ) from e

    # Verify asset exists and is a file (not directory)
    if not asset_file.exists() or not asset_file.is_file():
        logger.warning(f"Asset not found: {asset_file}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_path}' not found in theme '{theme_id}'",
        )

    # Serve file with appropriate content type
    return FileResponse(
        path=str(asset_file),
        media_type=_get_media_type(asset_file),
    )


def _get_media_type(file_path: Path) -> str:
    """
    Determine media type from file extension.

    Args:
        file_path: Path to file

    Returns:
        MIME type string
    """
    extension = file_path.suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg",
        ".wav": "audio/wav",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".otf": "font/otf",
        ".json": "application/json",
        ".yaml": "application/x-yaml",
        ".yml": "application/x-yaml",
    }
    return media_types.get(extension, "application/octet-stream")
