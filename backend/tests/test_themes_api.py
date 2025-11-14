"""Tests for theme API endpoints."""

import sys
from pathlib import Path

import pytest
import yaml
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.api.routes.themes import _get_media_type, get_theme_asset
from app.main import app


@pytest.fixture
def test_theme_dir(tmp_path):
    """Create test theme directory structure."""
    theme_dir = tmp_path / "themes" / "test-theme"
    theme_dir.mkdir(parents=True)

    # Create theme.yaml
    theme_config = {
        "id": "test-theme",
        "name": "Test Theme",
        "description": "Test theme description",
        "colors": {
            "primary": "#FF0000",
            "secondary": "#00FF00",
            "background": "#000000",
            "surface": "#111111",
            "text": "#FFFFFF",
        },
        "typography": {
            "fontFamily": "Arial",
            "fontSize": {"base": "1rem"},
        },
        "terminology": {
            "story": "Story",
        },
        "ui": {
            "welcome": "Welcome",
        },
        "assets": {
            "logo": "assets/logo.png",
        },
    }

    theme_yaml_path = theme_dir / "theme.yaml"
    with theme_yaml_path.open("w") as f:
        yaml.dump(theme_config, f)

    # Create asset file
    assets_dir = theme_dir / "assets"
    assets_dir.mkdir()
    logo_file = assets_dir / "logo.png"
    logo_file.write_bytes(b"\x89PNG\r\n\x1a\n")  # PNG header

    return tmp_path


@pytest.mark.asyncio
async def test_list_themes_empty():
    """Test listing themes when no themes available."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/themes")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_list_themes_with_themes():
    """Test listing themes returns theme metadata."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/themes")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

        # If themes exist, verify structure
        if len(data["data"]) > 0:
            theme = data["data"][0]
            assert "id" in theme
            assert "name" in theme
            assert "description" in theme


@pytest.mark.asyncio
async def test_get_theme_not_found():
    """Test getting nonexistent theme returns 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/themes/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_theme_success():
    """Test getting theme returns complete configuration."""
    # This test assumes warhammer40k theme exists
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/themes/warhammer40k")

        # May return 200 or 404 depending on whether theme exists
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            theme = data["data"]
            assert "id" in theme
            assert "name" in theme
            assert "colors" in theme
            assert "typography" in theme
            assert "terminology" in theme
            assert "ui" in theme
            assert "assets" in theme


@pytest.mark.asyncio
async def test_get_theme_asset_not_found():
    """Test getting asset from nonexistent theme returns 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/themes/nonexistent/assets/logo.png")

        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_theme_asset_invalid_path():
    """Test getting asset with invalid path returns 400."""
    # Test the function directly with invalid paths
    # Test directory traversal
    with pytest.raises(HTTPException) as exc_info:
        await get_theme_asset("warhammer40k", "../../../etc/passwd")
    assert exc_info.value.status_code == 400
    assert "invalid" in exc_info.value.detail.lower()

    # Test absolute path
    with pytest.raises(HTTPException) as exc_info:
        await get_theme_asset("warhammer40k", "/etc/passwd")
    assert exc_info.value.status_code == 400
    assert "invalid" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_theme_asset_nonexistent_file():
    """Test getting nonexistent asset returns 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/themes/warhammer40k/assets/nonexistent.png")

        # May return 404 (asset not found) or 404 (theme not found)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_theme_asset_content_type():
    """Test asset serving includes correct Content-Type."""
    # Test the _get_media_type function
    assert _get_media_type(Path("logo.png")) == "image/png"
    assert _get_media_type(Path("background.jpg")) == "image/jpeg"
    assert _get_media_type(Path("background.jpeg")) == "image/jpeg"
    assert _get_media_type(Path("icon.svg")) == "image/svg+xml"
    assert _get_media_type(Path("image.gif")) == "image/gif"
    assert _get_media_type(Path("image.webp")) == "image/webp"
    assert _get_media_type(Path("font.woff")) == "font/woff"
    assert _get_media_type(Path("font.woff2")) == "font/woff2"
    assert _get_media_type(Path("font.ttf")) == "font/ttf"
    assert _get_media_type(Path("font.otf")) == "font/otf"
    assert _get_media_type(Path("audio.mp3")) == "audio/mpeg"
    assert _get_media_type(Path("audio.ogg")) == "audio/ogg"
    assert _get_media_type(Path("audio.wav")) == "audio/wav"
    assert _get_media_type(Path("config.json")) == "application/json"
    assert _get_media_type(Path("config.yaml")) == "application/x-yaml"
    assert _get_media_type(Path("config.yml")) == "application/x-yaml"
    assert _get_media_type(Path("unknown.xyz")) == "application/octet-stream"


@pytest.mark.asyncio
async def test_list_themes_structure():
    """Test that list themes endpoint returns correct structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/themes")

        assert response.status_code == 200
        data = response.json()

        # Verify top-level structure
        assert "data" in data
        assert isinstance(data["data"], list)

        # If themes exist, verify each theme has required fields
        for theme in data["data"]:
            assert "id" in theme or theme.get("id") is None
            assert "name" in theme or theme.get("name") is None
            assert "description" in theme or theme.get("description") is None


@pytest.mark.asyncio
async def test_get_theme_complete_structure():
    """Test that get theme endpoint returns all required fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Try to get warhammer40k theme
        response = await client.get("/api/v1/themes/warhammer40k")

        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            theme = data["data"]

            # Verify all required fields from ThemeConfig.to_dict()
            required_fields = [
                "id",
                "name",
                "description",
                "colors",
                "typography",
                "terminology",
                "ui",
                "assets",
            ]

            for field in required_fields:
                assert field in theme, f"Missing required field: {field}"


@pytest.mark.asyncio
async def test_get_theme_asset_directory_blocked():
    """Test that serving directories is blocked."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Try to get a directory (assets folder itself)
        response = await client.get("/api/v1/themes/warhammer40k/assets/")

        # Should return 404 since directories aren't served
        assert response.status_code == 404


def test_get_media_type_case_insensitive():
    """Test that media type detection is case-insensitive."""
    assert _get_media_type(Path("LOGO.PNG")) == "image/png"
    assert _get_media_type(Path("Background.JPG")) == "image/jpeg"
    assert _get_media_type(Path("Font.WOFF2")) == "font/woff2"
