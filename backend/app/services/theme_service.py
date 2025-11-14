"""Service for managing themes."""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ThemeConfig:
    """Theme configuration data."""

    def __init__(self, data: dict[str, Any]):
        """
        Initialize theme config.

        Args:
            data: Theme configuration dictionary
        """
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.colors: dict[str, str] = data["colors"]
        self.typography: dict[str, Any] = data["typography"]
        self.terminology: dict[str, str] = data["terminology"]
        self.ui: dict[str, str] = data["ui"]
        self.assets: dict[str, str] = data["assets"]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "colors": self.colors,
            "typography": self.typography,
            "terminology": self.terminology,
            "ui": self.ui,
            "assets": self.assets,
        }


class ThemeService:
    """Service for loading and managing themes."""

    def __init__(self, themes_dir: str = "data/themes"):
        """
        Initialize theme service.

        Args:
            themes_dir: Path to themes directory
        """
        self.themes_dir = Path(themes_dir)
        self._cache: dict[str, ThemeConfig] = {}
        self.default_theme_id = "warhammer40k"

    def load_theme(self, theme_id: str) -> ThemeConfig | None:
        """
        Load theme configuration.

        Args:
            theme_id: Theme identifier

        Returns:
            Theme configuration or None if not found
        """
        # Check cache first
        if theme_id in self._cache:
            logger.debug(f"Theme '{theme_id}' loaded from cache")
            return self._cache[theme_id]

        # Load from file
        theme_file = self.themes_dir / theme_id / "theme.yaml"
        if not theme_file.exists():
            logger.warning(f"Theme file not found: {theme_file}")
            return None

        try:
            with theme_file.open(encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Validate theme
            if not self.validate_theme(data):
                logger.error(f"Invalid theme configuration: {theme_id}")
                return None

            # Create config and cache
            config = ThemeConfig(data)
            self._cache[theme_id] = config

            logger.info(f"Loaded theme: {theme_id}")
            return config

        except Exception as e:
            logger.error(f"Failed to load theme '{theme_id}': {e}")
            return None

    def list_themes(self) -> list[dict[str, str | None]]:
        """
        List all available themes.

        Returns:
            List of theme metadata (id, name, description)
        """
        themes: list[dict[str, str | None]] = []

        if not self.themes_dir.exists():
            logger.warning(f"Themes directory not found: {self.themes_dir}")
            return themes

        for theme_dir in self.themes_dir.iterdir():
            if not theme_dir.is_dir():
                continue

            theme_file = theme_dir / "theme.yaml"
            if not theme_file.exists():
                continue

            try:
                with theme_file.open(encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                themes.append(
                    {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "description": data.get("description"),
                    }
                )
            except Exception as e:
                logger.error(f"Failed to read theme metadata from {theme_file}: {e}")

        return sorted(themes, key=lambda x: x.get("name") or "")

    def validate_theme(self, data: dict[str, Any]) -> bool:
        """
        Validate theme configuration structure.

        Args:
            data: Theme configuration dictionary

        Returns:
            True if valid, False otherwise
        """
        required_keys = [
            "id",
            "name",
            "description",
            "colors",
            "typography",
            "terminology",
            "ui",
            "assets",
        ]

        for key in required_keys:
            if key not in data:
                logger.error(f"Missing required key in theme: {key}")
                return False

        # Validate colors
        required_colors = ["primary", "secondary", "background", "surface", "text"]
        for color in required_colors:
            if color not in data["colors"]:
                logger.error(f"Missing required color: {color}")
                return False

        return True

    def get_default_theme(self) -> ThemeConfig:
        """
        Get default theme (fallback).

        Returns:
            Default theme configuration
        """
        theme = self.load_theme(self.default_theme_id)
        if not theme:
            raise RuntimeError(f"Default theme '{self.default_theme_id}' not found")
        return theme

    def get_asset_path(self, theme_id: str, asset_key: str) -> Path | None:
        """
        Get absolute path to theme asset.

        Args:
            theme_id: Theme identifier
            asset_key: Asset key (e.g., 'logo', 'background')

        Returns:
            Absolute path to asset or None if not found
        """
        theme = self.load_theme(theme_id)
        if not theme or asset_key not in theme.assets:
            return None

        asset_path = self.themes_dir / theme_id / theme.assets[asset_key]
        return asset_path if asset_path.exists() else None
