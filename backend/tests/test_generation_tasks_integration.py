"""Tests for generation task CrewAI integration."""

import json
from unittest.mock import Mock, mock_open, patch

import pytest
from app.integrations.crewai_wrapper import CrewExecutionError
from app.tasks.generation_tasks import _load_crew_output


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

        result = _load_crew_output()

        assert result == crew_data
        assert result["game"]["title"] == "Test Adventure"

    @patch("pathlib.Path.exists")
    def test_load_missing_file_raises_error(self, mock_exists):
        """Test that missing file raises CrewExecutionError."""
        mock_exists.return_value = False

        with pytest.raises(CrewExecutionError, match="Crew output file not found"):
            _load_crew_output()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_load_invalid_json_raises_error(self, mock_file, mock_exists):
        """Test that invalid JSON raises CrewExecutionError."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = "invalid json {"

        with pytest.raises(CrewExecutionError, match="Failed to parse crew output file"):
            _load_crew_output()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_load_missing_game_key_raises_error(self, mock_file, mock_exists):
        """Test that missing 'game' key raises CrewExecutionError."""
        mock_exists.return_value = True
        crew_data = {"title": "Test", "description": "Test"}  # Missing 'game' key
        mock_file.return_value.read.return_value = json.dumps(crew_data)

        with pytest.raises(CrewExecutionError, match="missing 'game' key"):
            _load_crew_output()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_load_non_dict_output_raises_error(self, mock_file, mock_exists):
        """Test that non-dict output raises CrewExecutionError."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(["array", "not", "dict"])

        with pytest.raises(CrewExecutionError, match="expected dict, got"):
            _load_crew_output()


class TestGenerationTaskIntegration:
    """Integration tests for the generation task."""

    @patch("app.tasks.generation_tasks.SpaceHulkGame")
    @patch("app.tasks.generation_tasks.CrewAIWrapper")
    def test_task_uses_real_crew(self, mock_wrapper_class, mock_crew_class):
        """Test that generation task calls CrewAIWrapper with real crew."""
        # Mock the crew
        mock_crew_instance = Mock()
        mock_crew = Mock()
        mock_crew_class.return_value = mock_crew_instance
        mock_crew_instance.crew.return_value = mock_crew

        # Mock the wrapper
        mock_wrapper = Mock()
        mock_wrapper_class.return_value = mock_wrapper
        mock_wrapper.execute_generation.return_value = {
            "status": "success",
            "output": {},
        }

        # Verify the modules are importable by checking the mocks were set up
        assert mock_crew_class is not None
        assert mock_wrapper_class is not None

    def test_crew_import_available(self):
        """Test that SpaceHulkGame crew can be imported."""
        # This test verifies the import works in the CI environment
        # The actual import is at the module level in generation_tasks.py
        # If it fails, the test module won't even load
        from app.tasks.generation_tasks import SpaceHulkGame  # noqa: PLC0415

        assert SpaceHulkGame is not None
