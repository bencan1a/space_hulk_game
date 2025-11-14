"""Tests for theme service."""

from pathlib import Path

import pytest
import yaml
from app.services.theme_service import ThemeConfig, ThemeService


@pytest.fixture
def theme_service(tmp_path):
    """Create theme service with temporary directory."""
    return ThemeService(themes_dir=str(tmp_path))


@pytest.fixture
def valid_theme_data():
    """Valid theme configuration data."""
    return {
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


@pytest.fixture
def theme_with_files(tmp_path, valid_theme_data):
    """Create a theme with files on disk."""
    theme_dir = tmp_path / "test-theme"
    theme_dir.mkdir()

    # Create theme.yaml
    theme_file = theme_dir / "theme.yaml"
    with theme_file.open("w", encoding="utf-8") as f:
        yaml.dump(valid_theme_data, f)

    # Create assets directory
    assets_dir = theme_dir / "assets"
    assets_dir.mkdir()

    # Create placeholder logo
    logo_file = assets_dir / "logo.png"
    logo_file.write_bytes(b"PNG_DATA")

    return tmp_path


def test_validate_theme_valid(theme_service, valid_theme_data):
    """Test validating valid theme returns True."""
    assert theme_service.validate_theme(valid_theme_data) is True


def test_validate_theme_missing_key(theme_service, valid_theme_data):
    """Test validating theme with missing key returns False."""
    del valid_theme_data["colors"]
    assert theme_service.validate_theme(valid_theme_data) is False


def test_validate_theme_missing_color(theme_service, valid_theme_data):
    """Test validating theme with missing required color returns False."""
    del valid_theme_data["colors"]["primary"]
    assert theme_service.validate_theme(valid_theme_data) is False


def test_load_theme_not_found(theme_service):
    """Test loading nonexistent theme returns None."""
    theme = theme_service.load_theme("nonexistent")
    assert theme is None


def test_load_theme_success(theme_with_files):
    """Test loading valid theme from disk."""
    service = ThemeService(themes_dir=str(theme_with_files))
    theme = service.load_theme("test-theme")

    assert theme is not None
    assert theme.id == "test-theme"
    assert theme.name == "Test Theme"
    assert theme.description == "Test theme description"
    assert "primary" in theme.colors
    assert "typography" in theme.to_dict()


def test_load_theme_caching(theme_with_files):
    """Test that themes are cached after first load."""
    service = ThemeService(themes_dir=str(theme_with_files))

    # First load
    theme1 = service.load_theme("test-theme")
    assert theme1 is not None

    # Second load should come from cache
    theme2 = service.load_theme("test-theme")
    assert theme2 is theme1  # Same object reference


def test_load_theme_invalid_yaml(tmp_path):
    """Test loading theme with invalid YAML."""
    service = ThemeService(themes_dir=str(tmp_path))

    theme_dir = tmp_path / "bad-theme"
    theme_dir.mkdir()

    # Create invalid YAML
    theme_file = theme_dir / "theme.yaml"
    theme_file.write_text("invalid: yaml: content: [")

    theme = service.load_theme("bad-theme")
    assert theme is None


def test_load_theme_invalid_structure(tmp_path, valid_theme_data):
    """Test loading theme with invalid structure."""
    service = ThemeService(themes_dir=str(tmp_path))

    theme_dir = tmp_path / "invalid-theme"
    theme_dir.mkdir()

    # Create theme with missing required key
    invalid_data = valid_theme_data.copy()
    del invalid_data["colors"]

    theme_file = theme_dir / "theme.yaml"
    with theme_file.open("w", encoding="utf-8") as f:
        yaml.dump(invalid_data, f)

    theme = service.load_theme("invalid-theme")
    assert theme is None


def test_list_themes_empty(theme_service):
    """Test listing themes when directory is empty."""
    themes = theme_service.list_themes()
    assert themes == []


def test_list_themes_nonexistent_directory():
    """Test listing themes when directory doesn't exist."""
    service = ThemeService(themes_dir="/nonexistent/path")
    themes = service.list_themes()
    assert themes == []


def test_list_themes_multiple(tmp_path):
    """Test listing multiple themes."""
    service = ThemeService(themes_dir=str(tmp_path))

    # Create first theme
    theme1_dir = tmp_path / "theme1"
    theme1_dir.mkdir()
    theme1_file = theme1_dir / "theme.yaml"
    with theme1_file.open("w", encoding="utf-8") as f:
        yaml.dump(
            {
                "id": "theme1",
                "name": "B Theme",
                "description": "Second theme alphabetically",
            },
            f,
        )

    # Create second theme
    theme2_dir = tmp_path / "theme2"
    theme2_dir.mkdir()
    theme2_file = theme2_dir / "theme.yaml"
    with theme2_file.open("w", encoding="utf-8") as f:
        yaml.dump(
            {
                "id": "theme2",
                "name": "A Theme",
                "description": "First theme alphabetically",
            },
            f,
        )

    themes = service.list_themes()

    assert len(themes) == 2
    # Should be sorted by name
    assert themes[0]["name"] == "A Theme"
    assert themes[1]["name"] == "B Theme"


def test_list_themes_skips_files(tmp_path):
    """Test that list_themes skips non-directory files."""
    service = ThemeService(themes_dir=str(tmp_path))

    # Create a file (not directory)
    (tmp_path / "README.txt").write_text("readme")

    # Create a valid theme
    theme_dir = tmp_path / "valid-theme"
    theme_dir.mkdir()
    theme_file = theme_dir / "theme.yaml"
    with theme_file.open("w", encoding="utf-8") as f:
        yaml.dump(
            {
                "id": "valid-theme",
                "name": "Valid Theme",
                "description": "A valid theme",
            },
            f,
        )

    themes = service.list_themes()

    assert len(themes) == 1
    assert themes[0]["id"] == "valid-theme"


def test_theme_config_to_dict(valid_theme_data):
    """Test ThemeConfig to_dict method."""
    config = ThemeConfig(valid_theme_data)
    result = config.to_dict()

    assert result["id"] == "test-theme"
    assert result["name"] == "Test Theme"
    assert "colors" in result
    assert "typography" in result
    assert "terminology" in result
    assert "ui" in result
    assert "assets" in result


def test_get_default_theme():
    """Test getting default theme."""
    # Use absolute path from repository root
    themes_dir = Path(__file__).parent.parent.parent / "data" / "themes"
    service = ThemeService(themes_dir=str(themes_dir))
    theme = service.get_default_theme()

    assert theme is not None
    assert theme.id == "warhammer40k"


def test_get_default_theme_missing():
    """Test getting default theme when it doesn't exist."""
    service = ThemeService(themes_dir="/nonexistent")

    with pytest.raises(RuntimeError, match="Default theme"):
        service.get_default_theme()


def test_get_asset_path_success(theme_with_files):
    """Test getting asset path for existing asset."""
    service = ThemeService(themes_dir=str(theme_with_files))

    asset_path = service.get_asset_path("test-theme", "logo")

    assert asset_path is not None
    assert asset_path.exists()
    assert asset_path.name == "logo.png"


def test_get_asset_path_nonexistent_theme(theme_service):
    """Test getting asset path for nonexistent theme."""
    asset_path = theme_service.get_asset_path("nonexistent", "logo")
    assert asset_path is None


def test_get_asset_path_nonexistent_asset(theme_with_files):
    """Test getting asset path for nonexistent asset key."""
    service = ThemeService(themes_dir=str(theme_with_files))

    asset_path = service.get_asset_path("test-theme", "nonexistent")
    assert asset_path is None


def test_get_asset_path_missing_file(tmp_path, valid_theme_data):
    """Test getting asset path when file doesn't exist on disk."""
    service = ThemeService(themes_dir=str(tmp_path))

    theme_dir = tmp_path / "test-theme"
    theme_dir.mkdir()

    # Create theme.yaml but don't create the asset file
    theme_file = theme_dir / "theme.yaml"
    with theme_file.open("w", encoding="utf-8") as f:
        yaml.dump(valid_theme_data, f)

    # Create assets directory but not the file
    assets_dir = theme_dir / "assets"
    assets_dir.mkdir()

    asset_path = service.get_asset_path("test-theme", "logo")
    assert asset_path is None


def test_real_warhammer40k_theme():
    """Test loading the real warhammer40k theme."""
    # Use absolute path from repository root
    themes_dir = Path(__file__).parent.parent.parent / "data" / "themes"
    service = ThemeService(themes_dir=str(themes_dir))
    theme = service.load_theme("warhammer40k")

    assert theme is not None
    assert theme.id == "warhammer40k"
    assert theme.name == "Warhammer 40,000"
    assert theme.description == "Grimdark gothic sci-fi horror"
    assert theme.colors["primary"] == "#8B0000"
    assert theme.terminology["story"] == "Mission"
    assert theme.ui["welcome"] == "Enter the grim darkness of the far future"


def test_real_cyberpunk_theme():
    """Test loading the real cyberpunk theme."""
    # Use absolute path from repository root
    themes_dir = Path(__file__).parent.parent.parent / "data" / "themes"
    service = ThemeService(themes_dir=str(themes_dir))
    theme = service.load_theme("cyberpunk")

    assert theme is not None
    assert theme.id == "cyberpunk"
    assert theme.name == "Cyberpunk"
    assert theme.description == "High-tech dystopian future"
    assert theme.colors["primary"] == "#FF00FF"
    assert theme.terminology["story"] == "Run"
    assert theme.ui["welcome"] == "Jack in to the grid"


def test_list_real_themes():
    """Test listing real themes in data/themes."""
    # Use absolute path from repository root
    themes_dir = Path(__file__).parent.parent.parent / "data" / "themes"
    service = ThemeService(themes_dir=str(themes_dir))
    themes = service.list_themes()

    assert len(themes) >= 2
    theme_ids = [t["id"] for t in themes]
    assert "warhammer40k" in theme_ids
    assert "cyberpunk" in theme_ids
