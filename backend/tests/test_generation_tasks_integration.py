"""Tests for generation task CrewAI integration."""

import json
from unittest.mock import mock_open, patch

import pytest
from app.integrations.crewai_wrapper import CrewAIWrapper, CrewExecutionError


def get_load_crew_output():
    """Import _load_crew_output lazily to avoid triggering module-level import errors."""
    from app.tasks.generation_tasks import _load_crew_output  # noqa: PLC0415

    return _load_crew_output


class TestLoadCrewOutput:
    """Tests for _load_crew_output function."""

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_load_valid_crew_output(self, mock_file, mock_exists):
        """Test loading valid crew output from file."""
        mock_exists.return_value = True
        crew_data = {
            "game": {
                "title": "Test Adventure",
                "description": "A test game",
                "starting_scene": "scene_01",
                "scenes": {
                    "scene_01": {
                        "id": "scene_01",
                        "name": "Start",
                        "description": "The beginning",
                        "exits": {},
                        "items": [],
                        "npcs": [],
                    }
                },
            }
        }
        mock_file.return_value.read.return_value = json.dumps(crew_data)

        _load_crew_output = get_load_crew_output()
        result = _load_crew_output()

        assert result == crew_data
        assert result["game"]["title"] == "Test Adventure"

    @patch("pathlib.Path.exists")
    def test_load_missing_file_raises_error(self, mock_exists):
        """Test that missing file raises CrewExecutionError."""
        mock_exists.return_value = False

        _load_crew_output = get_load_crew_output()
        with pytest.raises(CrewExecutionError, match="Crew output file not found"):
            _load_crew_output()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_load_invalid_json_raises_error(self, mock_file, mock_exists):
        """Test that invalid JSON raises CrewExecutionError."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = "invalid json {"

        _load_crew_output = get_load_crew_output()
        with pytest.raises(CrewExecutionError, match="Failed to parse crew output file"):
            _load_crew_output()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_load_missing_game_key_raises_error(self, mock_file, mock_exists):
        """Test that missing 'game' key raises CrewExecutionError."""
        mock_exists.return_value = True
        crew_data = {"title": "Test", "description": "Test"}  # Missing 'game' key
        mock_file.return_value.read.return_value = json.dumps(crew_data)

        _load_crew_output = get_load_crew_output()
        with pytest.raises(CrewExecutionError, match="missing 'game' key"):
            _load_crew_output()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_load_non_dict_output_raises_error(self, mock_file, mock_exists):
        """Test that non-dict output raises CrewExecutionError."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(["array", "not", "dict"])

        _load_crew_output = get_load_crew_output()
        with pytest.raises(CrewExecutionError, match="expected dict, got"):
            _load_crew_output()


class TestGenerationTaskIntegration:
    """Integration tests for the generation task."""

    def test_crew_wrapper_import(self):
        """Test that CrewAIWrapper can be imported."""
        assert CrewAIWrapper is not None

    def test_crewai_wrapper_context_manager(self):
        """Test that CrewAIWrapper can be used as context manager."""
        # Verify the wrapper has context manager methods
        assert hasattr(CrewAIWrapper, "__enter__")
        assert hasattr(CrewAIWrapper, "__exit__")
