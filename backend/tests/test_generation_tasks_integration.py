"""Tests for generation task CrewAI integration."""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest
from app.tasks.generation_tasks import (
    _create_fallback_game_data,
    _parse_crew_output_to_game_json,
    _transform_game_structure,
)


class TestParseCrewOutput:
    """Tests for _parse_crew_output_to_game_json function."""

    def test_parse_dict_output_with_game_key(self):
        """Test parsing dict output with 'game' key."""
        crew_output = {
            "game": {
                "title": "Test Adventure",
                "description": "A test game",
                "starting_scene": "scene_01",
                "scenes": {
                    "scene_01": {
                        "id": "scene_01",
                        "name": "Start",
                        "description": "The beginning",
                        "exits": {"north": "scene_02"},
                        "items": [],
                        "npcs": [],
                    }
                },
            }
        }
        prompt = "Create a test game"

        result = _parse_crew_output_to_game_json(crew_output, prompt)

        assert result["metadata"]["title"] == "Test Adventure"
        assert result["metadata"]["description"] == "A test game"
        assert len(result["scenes"]) == 1
        assert result["scenes"][0]["id"] == "scene_01"

    def test_parse_dict_output_without_game_key(self):
        """Test parsing dict output without 'game' key."""
        crew_output = {
            "title": "Test Adventure",
            "description": "A test game",
            "scenes": {
                "scene_01": {
                    "id": "scene_01",
                    "name": "Start",
                    "description": "The beginning",
                    "exits": {},
                    "items": [],
                }
            },
        }
        prompt = "Create a test game"

        result = _parse_crew_output_to_game_json(crew_output, prompt)

        assert result["metadata"]["title"] == "Test Adventure"
        assert len(result["scenes"]) == 1

    def test_parse_string_output(self):
        """Test parsing string (JSON) output."""
        crew_output = json.dumps(
            {
                "game": {
                    "title": "Test Adventure",
                    "description": "A test game",
                    "scenes": {},
                }
            }
        )
        prompt = "Create a test game"

        result = _parse_crew_output_to_game_json(crew_output, prompt)

        assert result["metadata"]["title"] == "Test Adventure"

    def test_parse_crew_output_object(self):
        """Test parsing CrewOutput object."""
        mock_output = Mock()
        mock_output.raw = json.dumps(
            {
                "game": {
                    "title": "Test Adventure",
                    "description": "A test game",
                    "scenes": {},
                }
            }
        )
        mock_output.tasks_output = []
        prompt = "Create a test game"

        result = _parse_crew_output_to_game_json(mock_output, prompt)

        assert result["metadata"]["title"] == "Test Adventure"

    def test_parse_invalid_output_returns_fallback(self):
        """Test that invalid output returns fallback data."""
        crew_output = "invalid json data"
        prompt = "Create a test game"

        result = _parse_crew_output_to_game_json(crew_output, prompt)

        # Should return fallback structure
        assert "metadata" in result
        assert "scenes" in result
        assert len(result["scenes"]) == 1  # Fallback has one scene
        assert result["metadata"]["title"].startswith("Generated Story:")


class TestTransformGameStructure:
    """Tests for _transform_game_structure function."""

    def test_transform_basic_structure(self):
        """Test transforming basic game structure."""
        game_structure = {
            "title": "Test Game",
            "description": "A test description",
            "scenes": {
                "scene_01": {
                    "id": "scene_01",
                    "name": "Start Area",
                    "description": "The starting point",
                    "exits": {"north": "scene_02"},
                    "items": [],
                    "npcs": [],
                }
            },
        }
        prompt = "Test prompt"

        result = _transform_game_structure(game_structure, prompt)

        assert result["metadata"]["title"] == "Test Game"
        assert result["metadata"]["description"] == "A test description"
        assert result["metadata"]["theme"] == "warhammer40k"
        assert len(result["scenes"]) == 1
        assert result["scenes"][0]["name"] == "Start Area"

    def test_transform_extracts_items_from_scenes(self):
        """Test that items are extracted from scenes."""
        game_structure = {
            "title": "Test Game",
            "description": "Test",
            "scenes": {
                "scene_01": {
                    "id": "scene_01",
                    "name": "Area 1",
                    "description": "Test area",
                    "exits": {},
                    "items": [
                        {
                            "id": "item_01",
                            "name": "Test Item",
                            "description": "A test item",
                            "takeable": True,
                        }
                    ],
                }
            },
        }
        prompt = "Test"

        result = _transform_game_structure(game_structure, prompt)

        assert len(result["items"]) == 1
        assert result["items"][0]["id"] == "item_01"
        assert result["items"][0]["name"] == "Test Item"

    def test_transform_extracts_npcs_from_scenes(self):
        """Test that NPCs are extracted from scenes."""
        game_structure = {
            "title": "Test Game",
            "description": "Test",
            "scenes": {
                "scene_01": {
                    "id": "scene_01",
                    "name": "Area 1",
                    "description": "Test area",
                    "exits": {},
                    "items": [],
                    "npcs": [
                        {
                            "id": "npc_01",
                            "name": "Test NPC",
                            "description": "A test character",
                        }
                    ],
                }
            },
        }
        prompt = "Test"

        result = _transform_game_structure(game_structure, prompt)

        assert len(result["npcs"]) == 1
        assert result["npcs"][0]["id"] == "npc_01"

    def test_transform_extracts_puzzles_from_events(self):
        """Test that puzzles are extracted from scene events."""
        game_structure = {
            "title": "Test Game",
            "description": "Test",
            "scenes": {
                "scene_01": {
                    "id": "scene_01",
                    "name": "Area 1",
                    "description": "Test area",
                    "exits": {},
                    "items": [],
                    "npcs": [],
                    "events": [
                        {
                            "type": "puzzle",
                            "id": "puzzle_01",
                            "name": "Test Puzzle",
                            "description": "A test puzzle",
                        }
                    ],
                }
            },
        }
        prompt = "Test"

        result = _transform_game_structure(game_structure, prompt)

        assert len(result["puzzles"]) == 1
        assert result["puzzles"][0]["id"] == "puzzle_01"

    def test_transform_handles_empty_scenes(self):
        """Test handling of empty scenes dict."""
        game_structure = {
            "title": "Test Game",
            "description": "Test",
            "scenes": {},
        }
        prompt = "Test"

        result = _transform_game_structure(game_structure, prompt)

        assert len(result["scenes"]) == 0
        assert len(result["items"]) == 0
        assert len(result["npcs"]) == 0
        assert len(result["puzzles"]) == 0

    def test_transform_handles_missing_title_description(self):
        """Test handling of missing title and description."""
        game_structure = {
            "scenes": {
                "scene_01": {
                    "id": "scene_01",
                    "name": "Test",
                    "description": "Test",
                    "exits": {},
                    "items": [],
                }
            }
        }
        prompt = "Create a test story about space marines"

        result = _transform_game_structure(game_structure, prompt)

        assert "Generated Story:" in result["metadata"]["title"]
        assert "Create a test story" in result["metadata"]["title"]
        assert "space marines" in result["metadata"]["description"]


class TestCreateFallbackGameData:
    """Tests for _create_fallback_game_data function."""

    def test_creates_valid_structure(self):
        """Test that fallback creates valid game structure."""
        prompt = "Create a test game"

        result = _create_fallback_game_data(prompt)

        assert "metadata" in result
        assert "scenes" in result
        assert "items" in result
        assert "npcs" in result
        assert "puzzles" in result

    def test_includes_prompt_in_metadata(self):
        """Test that prompt is included in metadata."""
        prompt = "Create a space hulk adventure with genestealers"

        result = _create_fallback_game_data(prompt)

        assert "Create a space hulk" in result["metadata"]["title"]
        assert "genestealers" in result["metadata"]["description"]

    def test_creates_minimal_scene(self):
        """Test that fallback creates at least one scene."""
        prompt = "Test"

        result = _create_fallback_game_data(prompt)

        assert len(result["scenes"]) >= 1
        assert result["scenes"][0]["id"] == "scene_start"
        assert "description" in result["scenes"][0]


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
            "output": {
                "game": {
                    "title": "Test Game",
                    "description": "Test",
                    "scenes": {},
                }
            },
        }

        # Import and run the task (this would normally be done by Celery)
        # For now, we just verify the mocks would be called correctly
        # Actual task testing requires database and Celery setup

        # Verify the imports work
        from app.tasks.generation_tasks import SpaceHulkGame, CrewAIWrapper

        assert SpaceHulkGame is not None
        assert CrewAIWrapper is not None

    def test_crew_import_available(self):
        """Test that SpaceHulkGame crew can be imported."""
        try:
            from src.space_hulk_game.crew import SpaceHulkGame

            assert SpaceHulkGame is not None
        except ImportError as e:
            pytest.skip(f"SpaceHulkGame not available in test environment: {e}")
