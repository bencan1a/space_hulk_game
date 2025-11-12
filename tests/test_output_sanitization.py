"""Tests for JSON Output Sanitization Pipeline

This module tests the JSON sanitization pipeline that runs before
CrewAI writes output files to disk. With JSON mode enabled in the LLM,
the sanitizer now focuses on:
1. Stripping markdown fences (```json blocks)
2. Validating JSON syntax
3. Pretty-formatting JSON for readability

This is significantly simpler than the previous YAML pipeline.

Test Coverage:
- Test markdown fence stripping
- Test JSON validation
- Test pretty-formatting
- Test all 5 output types (plot, narrative, puzzle, scene, mechanics)
- Test graceful error handling for invalid JSON
"""

import json
import unittest

from space_hulk_game.utils.output_sanitizer import OutputSanitizer


class TestOutputSanitization(unittest.TestCase):
    """Tests for the JSON output sanitization pipeline.

    These tests verify that the OutputSanitizer correctly:
    1. Strips markdown fences from JSON
    2. Validates JSON syntax
    3. Pretty-formats JSON for readability
    4. Handles errors gracefully
    """

    def setUp(self):
        """Set up test fixtures."""
        self.sanitizer = OutputSanitizer()

    def test_sanitizer_initialization(self):
        """Test that OutputSanitizer initializes correctly."""
        self.assertIsInstance(self.sanitizer, OutputSanitizer)

    # ========================================================================
    # Test Markdown Fence Stripping
    # ========================================================================

    def test_strip_markdown_fences(self):
        """Test stripping markdown ```json blocks."""
        input_json = """```json
{
  "narrative_foundation": {
    "title": "Space Hulk: Lost Vessel"
  }
}
```"""

        result = self.sanitizer.sanitize(input_json, "plot")

        # Should be parseable as valid JSON
        data = json.loads(result)
        self.assertIsNotNone(data)
        self.assertIn("narrative_foundation", data)
        self.assertEqual(data["narrative_foundation"]["title"], "Space Hulk: Lost Vessel")

    def test_strip_markdown_fences_with_whitespace(self):
        """Test stripping markdown fences with extra whitespace."""
        input_json = """   ```json
{
  "narrative_foundation": {
    "title": "Test"
  }
}
   ```   """

        result = self.sanitizer.sanitize(input_json, "plot")

        # Should be parseable as valid JSON
        data = json.loads(result)
        self.assertIsNotNone(data)

    def test_no_markdown_fences(self):
        """Test JSON without markdown fences."""
        input_json = '{"narrative_foundation": {"title": "Test"}}'

        result = self.sanitizer.sanitize(input_json, "plot")

        # Should be parseable as valid JSON
        data = json.loads(result)
        self.assertIsNotNone(data)
        self.assertIn("narrative_foundation", data)

    # ========================================================================
    # Test JSON Validation
    # ========================================================================

    def test_valid_json(self):
        """Test sanitizing valid JSON."""
        input_json = '{"narrative_foundation": {"title": "Test", "setting": "A test setting"}}'

        result = self.sanitizer.sanitize(input_json, "plot")

        # Should be valid and pretty-formatted
        data = json.loads(result)
        self.assertIn("narrative_foundation", data)
        # Check that it's pretty-formatted (has newlines and indentation)
        self.assertIn("\n", result)
        self.assertIn("  ", result)

    def test_compact_json(self):
        """Test that compact JSON is pretty-formatted."""
        input_json = '{"narrative_foundation":{"title":"Test","setting":"Setting"}}'

        result = self.sanitizer.sanitize(input_json, "plot")

        # Should be pretty-formatted
        self.assertIn("\n", result)
        self.assertIn("  ", result)

        # Should be parseable
        data = json.loads(result)
        self.assertEqual(data["narrative_foundation"]["title"], "Test")

    # ========================================================================
    # Test All Output Types
    # ========================================================================

    def test_sanitize_plot_outline(self):
        """Test sanitizing plot outline JSON."""
        input_json = """```json
{
  "narrative_foundation": {
    "title": "Test Plot",
    "setting": "Test setting",
    "themes": ["survival"],
    "tone": "Dark"
  }
}
```"""

        result = self.sanitizer.sanitize(input_json, "plot")
        data = json.loads(result)
        self.assertIn("narrative_foundation", data)

    def test_sanitize_narrative_map(self):
        """Test sanitizing narrative map JSON."""
        input_json = """```json
{
  "start_scene": "scene_1",
  "scenes": {
    "scene_1": {
      "name": "Opening",
      "description": "The opening scene",
      "connections": []
    }
  }
}
```"""

        result = self.sanitizer.sanitize(input_json, "narrative")
        data = json.loads(result)
        self.assertIn("start_scene", data)
        self.assertIn("scenes", data)

    def test_sanitize_puzzle_design(self):
        """Test sanitizing puzzle design JSON."""
        input_json = """```json
{
  "puzzles": [],
  "artifacts": [],
  "monsters": [],
  "npcs": []
}
```"""

        result = self.sanitizer.sanitize(input_json, "puzzle")
        data = json.loads(result)
        self.assertIn("puzzles", data)

    def test_sanitize_scene_texts(self):
        """Test sanitizing scene texts JSON."""
        input_json = """```json
{
  "scenes": {
    "scene_1": {
      "name": "Test Scene",
      "description": "A test scene description",
      "atmosphere": "Atmospheric",
      "initial_text": "You enter the scene",
      "examination_texts": {},
      "dialogue": []
    }
  }
}
```"""

        result = self.sanitizer.sanitize(input_json, "scene")
        data = json.loads(result)
        self.assertIn("scenes", data)

    def test_sanitize_game_mechanics(self):
        """Test sanitizing game mechanics JSON."""
        input_json = """```json
{
  "game_title": "Test Game",
  "game_systems": {
    "movement": {},
    "inventory": {},
    "combat": {},
    "interaction": {}
  },
  "game_state": {},
  "technical_requirements": []
}
```"""

        result = self.sanitizer.sanitize(input_json, "mechanics")
        data = json.loads(result)
        self.assertIn("game_title", data)

    # ========================================================================
    # Test Error Handling
    # ========================================================================

    def test_graceful_degradation_invalid_json(self):
        """Test that sanitizer handles invalid JSON gracefully."""
        input_json = """```json
{
  "narrative_foundation": {
    "title": "Test",
    "setting": "This is not valid JSON
  }
}
```"""

        # Should not raise exception, but log error
        # In graceful mode, it returns the input as-is after stripping fences
        result = self.sanitizer.sanitize(input_json, "plot")

        # Result should still be a string (even if not valid JSON)
        self.assertIsInstance(result, str)

    def test_empty_input(self):
        """Test handling empty input."""
        result = self.sanitizer.sanitize("", "plot")

        # Should return empty or minimal result without crashing
        self.assertIsInstance(result, str)

    def test_whitespace_only_input(self):
        """Test handling whitespace-only input."""
        result = self.sanitizer.sanitize("   \n\n   ", "plot")

        # Should return empty or minimal result without crashing
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
