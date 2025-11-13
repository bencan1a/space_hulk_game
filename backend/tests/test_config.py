"""Tests for configuration management."""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Settings


def test_config_defaults() -> None:
    """Test config has sensible defaults."""
    settings = Settings()
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.api_environment == "development"
    assert settings.log_level == "INFO"


def test_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test config loads from environment variables."""
    monkeypatch.setenv("API_PORT", "9000")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()
    assert settings.api_port == 9000
    assert settings.log_level == "DEBUG"
