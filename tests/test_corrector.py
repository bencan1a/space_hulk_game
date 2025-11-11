"""Unit tests for YAML output auto-corrector.

This module tests the OutputCorrector class to ensure it correctly
fixes common validation errors in YAML outputs.
"""

import unittest

from space_hulk_game.validation import CorrectionResult, OutputCorrector


class TestOutputCorrector(unittest.TestCase):
    """Test cases for OutputCorrector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.corrector = OutputCorrector()

    def test_corrector_initialization(self):
        """Test that corrector initializes correctly."""
        self.assertIsInstance(self.corrector, OutputCorrector)
        self.assertIsNotNone(self.corrector.validator)

    def test_fix_id_format_lowercase(self):
        """Test ID format fixing converts to lowercase."""
        result = self.corrector._fix_id_format("MyScene")
        self.assertEqual(result, "myscene")

    def test_fix_id_format_spaces(self):
        """Test ID format fixing converts spaces to underscores."""
        result = self.corrector._fix_id_format("my scene id")
        self.assertEqual(result, "my_scene_id")

    def test_fix_id_format_special_chars(self):
        """Test ID format fixing removes special characters."""
        result = self.corrector._fix_id_format("my!scene@id#")
        self.assertEqual(result, "mysceneid")

    def test_fix_id_format_multiple_underscores(self):
        """Test ID format fixing normalizes multiple underscores."""
        result = self.corrector._fix_id_format("my___scene__id")
        self.assertEqual(result, "my_scene_id")

    def test_extend_short_description_no_change(self):
        """Test description extension when already long enough."""
        long_desc = "A" * 100
        result = self.corrector._extend_short_description(long_desc, 50)
        self.assertEqual(result, long_desc)

    def test_extend_short_description_extends(self):
        """Test description extension when too short."""
        short_desc = "Too short"
        result = self.corrector._extend_short_description(short_desc, 50)
        self.assertGreaterEqual(len(result), 50)
        self.assertTrue(result.startswith(short_desc))


class TestPlotCorrection(unittest.TestCase):
    """Test cases for plot outline correction."""

    def setUp(self):
        """Set up test fixtures."""
        self.corrector = OutputCorrector()

    def test_correct_plot_missing_plot_points(self):
        """Test correcting plot outline with missing plot_points."""
        yaml_str = """
title: "Test Plot"
setting: "A dark and mysterious setting with lots of atmospheric detail and description."
themes:
  - "survival"
tone: "Dark and gritty"
characters:
  - name: "Test Character"
    role: "Protagonist"
    backstory: "A backstory that is long enough to meet minimum requirements."
conflicts:
  - type: "Test Conflict"
    description: "A conflict description that meets minimum character requirements."
"""
        result = self.corrector.correct_plot(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)
        self.assertIn("plot_points", result.corrections[0].lower())

    def test_correct_plot_invalid_id(self):
        """Test correcting plot outline with invalid plot point ID."""
        yaml_str = """
title: "Test Plot"
setting: "A dark and mysterious setting with lots of atmospheric detail and description."
themes:
  - "survival"
tone: "Dark and gritty"
plot_points:
  - id: "Plot Point 1!"
    name: "Opening"
    description: "The opening scene where everything begins and sets the stage."
characters:
  - name: "Test Character"
    role: "Protagonist"
    backstory: "A backstory that is long enough to meet minimum requirements."
conflicts:
  - type: "Test Conflict"
    description: "A conflict description that meets minimum character requirements."
"""
        result = self.corrector.correct_plot(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(any("id format" in c.lower() for c in result.corrections))

    def test_correct_plot_short_description(self):
        """Test correcting plot outline with short description."""
        yaml_str = """
title: "Test Plot"
setting: "A dark and mysterious setting with lots of atmospheric detail and description."
themes:
  - "survival"
tone: "Dark and gritty"
plot_points:
  - id: "pp_01"
    name: "Opening"
    description: "Short"
characters:
  - name: "Test Character"
    role: "Protagonist"
    backstory: "A backstory that is long enough to meet minimum requirements."
conflicts:
  - type: "Test Conflict"
    description: "A conflict description that meets minimum character requirements."
"""
        result = self.corrector.correct_plot(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(any("extended" in c.lower() for c in result.corrections))


class TestNarrativeMapCorrection(unittest.TestCase):
    """Test cases for narrative map correction."""

    def setUp(self):
        """Set up test fixtures."""
        self.corrector = OutputCorrector()

    def test_correct_narrative_map_missing_scenes(self):
        """Test correcting narrative map with missing scenes."""
        yaml_str = """
start_scene: "scene_1"
"""
        result = self.corrector.correct_narrative_map(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)
        self.assertIn("scenes", result.corrections[0].lower())

    def test_correct_narrative_map_invalid_scene_id(self):
        """Test correcting narrative map with invalid scene ID."""
        yaml_str = """
start_scene: "Scene One!"
scenes:
  "Scene One!":
    name: "Scene One"
    description: "A test scene with a long enough description to meet requirements."
    connections: []
"""
        result = self.corrector.correct_narrative_map(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)
        self.assertTrue(any("id format" in c.lower() for c in result.corrections))

    def test_correct_narrative_map_missing_start_scene(self):
        """Test correcting narrative map with missing start_scene."""
        yaml_str = """
scenes:
  scene_test:
    name: "Test Scene"
    description: "A test scene with a long enough description to meet requirements."
    connections: []
"""
        result = self.corrector.correct_narrative_map(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)
        self.assertTrue(any("start_scene" in c.lower() for c in result.corrections))


class TestPuzzleDesignCorrection(unittest.TestCase):
    """Test cases for puzzle design correction."""

    def setUp(self):
        """Set up test fixtures."""
        self.corrector = OutputCorrector()

    def test_correct_puzzle_design_all_missing(self):
        """Test correcting puzzle design with all fields missing."""
        yaml_str = "{}"
        result = self.corrector.correct_puzzle_design(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.corrections), 4)
        self.assertTrue(any("puzzles" in c.lower() for c in result.corrections))
        self.assertTrue(any("artifacts" in c.lower() for c in result.corrections))
        self.assertTrue(any("monsters" in c.lower() for c in result.corrections))
        self.assertTrue(any("npcs" in c.lower() for c in result.corrections))

    def test_correct_puzzle_design_invalid_puzzle_id(self):
        """Test correcting puzzle design with invalid puzzle ID."""
        yaml_str = """
puzzles:
  - id: "Puzzle One!"
    name: "Test Puzzle"
    description: "A puzzle description that is long enough to meet requirements."
    location: "scene_test"
    narrative_purpose: "Test narrative purpose"
    solution:
      type: "test"
      steps:
        - step: "Test step"
    difficulty: "medium"
artifacts:
  - id: "artifact_test"
    name: "Test Artifact"
    description: "Test description"
    location: "scene_test"
    narrative_significance: "Test significance"
    properties:
      - property: "Test property"
monsters:
  - id: "monster_test"
    name: "Test Monster"
    description: "Test description"
    locations: ["scene_test"]
    narrative_role: "Test role"
    abilities: ["Test ability"]
npcs:
  - id: "npc_test"
    name: "Test NPC"
    role: "Test role"
    description: "Test description"
    locations: ["scene_test"]
    dialogue_themes: ["Test theme"]
"""
        result = self.corrector.correct_puzzle_design(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(any("puzzle id format" in c.lower() for c in result.corrections))


class TestSceneTextsCorrection(unittest.TestCase):
    """Test cases for scene texts correction."""

    def setUp(self):
        """Set up test fixtures."""
        self.corrector = OutputCorrector()

    def test_correct_scene_texts_missing_scenes(self):
        """Test correcting scene texts with missing scenes."""
        yaml_str = "{}"
        result = self.corrector.correct_scene_texts(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)
        self.assertTrue(any("scenes" in c.lower() for c in result.corrections))

    def test_correct_scene_texts_short_description(self):
        """Test correcting scene texts with short description."""
        yaml_str = """
scenes:
  scene_test:
    name: "Test Scene"
    description: "Short"
    atmosphere: "Test"
    initial_text: "Test"
    examination_texts: {}
    dialogue: []
"""
        result = self.corrector.correct_scene_texts(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)
        self.assertTrue(any("extended" in c.lower() for c in result.corrections))


class TestGameMechanicsCorrection(unittest.TestCase):
    """Test cases for game mechanics correction."""

    def setUp(self):
        """Set up test fixtures."""
        self.corrector = OutputCorrector()

    def test_correct_game_mechanics_missing_systems(self):
        """Test correcting game mechanics with missing systems."""
        yaml_str = "game_title: Test Game"
        result = self.corrector.correct_game_mechanics(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)
        self.assertTrue(any("movement" in c.lower() for c in result.corrections))
        self.assertTrue(any("inventory" in c.lower() for c in result.corrections))
        self.assertTrue(any("combat" in c.lower() for c in result.corrections))
        self.assertTrue(any("interaction" in c.lower() for c in result.corrections))

    def test_correct_game_mechanics_all_missing(self):
        """Test correcting game mechanics with all fields missing."""
        yaml_str = "{}"
        result = self.corrector.correct_game_mechanics(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)
        self.assertTrue(any("game_title" in c.lower() for c in result.corrections))


class TestYAMLSyntaxCorrection(unittest.TestCase):
    """Test cases for YAML syntax error correction."""

    def setUp(self):
        """Set up test fixtures."""
        self.corrector = OutputCorrector()

    def test_correct_markdown_fences(self):
        """Test correcting YAML with markdown fences."""
        yaml_str = """```yaml
title: "Test Plot"
setting: "A dark and mysterious setting with lots of atmospheric detail and description."
themes:
  - "survival"
tone: "Dark and gritty"
plot_points:
  - id: "pp_01"
    name: "Opening"
    description: "The opening scene where everything begins and sets the stage for the narrative."
  - id: "pp_02"
    name: "Development"
    description: "The story develops as events unfold and tension builds."
  - id: "pp_03"
    name: "Conclusion"
    description: "The narrative reaches its conclusion and resolution."
characters:
  - name: "Test Character"
    role: "Protagonist"
    backstory: "A backstory that is long enough to meet minimum requirements."
conflicts:
  - type: "Test Conflict"
    description: "A conflict description that meets minimum character requirements."
```"""
        result = self.corrector.correct_plot(yaml_str)
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)


class TestMixedQuotesCorrection(unittest.TestCase):
    """Test cases for mixed quote delimiter correction."""

    def setUp(self):
        """Set up test fixtures."""
        self.corrector = OutputCorrector()

    def test_fix_mixed_quotes_double_to_single(self):
        """Test fixing quotes that start with double and end with single."""
        yaml_str = "starting_scene: \"entrance'"
        fixed = self.corrector._fix_mixed_quotes(yaml_str)
        self.assertEqual(fixed, 'starting_scene: "entrance"')

    def test_fix_mixed_quotes_single_to_double(self):
        """Test fixing quotes that start with single and end with double."""
        yaml_str = "south: 'corridor_1\""
        fixed = self.corrector._fix_mixed_quotes(yaml_str)
        self.assertEqual(fixed, "south: 'corridor_1'")

    def test_fix_mixed_quotes_multiple_lines(self):
        """Test fixing mixed quotes across multiple lines."""
        yaml_str = """starting_scene: "entrance'
  name: 'Main Corridor"
  description: "Test'"""
        fixed = self.corrector._fix_mixed_quotes(yaml_str)
        # All should be normalized to opening quote type
        self.assertIn('starting_scene: "entrance"', fixed)
        self.assertIn("name: 'Main Corridor'", fixed)
        self.assertIn('description: "Test"', fixed)

    def test_fix_mixed_quotes_in_narrative_map(self):
        """Test fixing mixed quotes from actual CI failure (narrative_map.yaml)."""
        yaml_str = """narrative_map:
  starting_scene: "entrance'
  scenes:
    entrance:
      name: 'Entrance Airlock"
      exits:
        north: 'corridor_1"
        east: "storage'"""
        fixed = self.corrector._fix_mixed_quotes(yaml_str)
        # Verify all quotes are normalized
        self.assertIn('starting_scene: "entrance"', fixed)
        self.assertIn("name: 'Entrance Airlock'", fixed)
        self.assertIn("north: 'corridor_1'", fixed)
        self.assertIn('east: "storage"', fixed)

    def test_fix_mixed_quotes_valid_yaml_output(self):
        """Test that fixed mixed quotes produce valid YAML."""
        yaml_str = """title: "Space Hulk: Lost Vessel'
setting: 'A derelict space station"
themes:
  - "horror'
  - 'survival"
tone: "Dark and foreboding'"""
        result = self.corrector.correct_plot(yaml_str)
        # Should be corrected and valid
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)


class TestInvalidListMarkersCorrection(unittest.TestCase):
    """Test cases for invalid list marker correction."""

    def setUp(self):
        """Set up test fixtures."""
        self.corrector = OutputCorrector()

    def test_fix_invalid_list_markers_simple(self):
        """Test fixing simple invalid list markers."""
        yaml_str = """items:
  ---------------- flashlight"""
        fixed = self.corrector._fix_invalid_list_markers(yaml_str)
        self.assertEqual(
            fixed,
            """items:
  - flashlight""",
        )

    def test_fix_invalid_list_markers_multiple_items(self):
        """Test fixing multiple invalid list markers."""
        yaml_str = """items:
  ---------------- flashlight
  ---------------- medkit
  ---------------- dataslate"""
        fixed = self.corrector._fix_invalid_list_markers(yaml_str)
        expected = """items:
  - flashlight
  - medkit
  - dataslate"""
        self.assertEqual(fixed, expected)

    def test_fix_invalid_list_markers_nested(self):
        """Test fixing invalid list markers with different indentation levels."""
        yaml_str = """scenes:
  entrance:
    items:
      ---------------- flashlight
      ---------------- medkit
    npcs:
      ---------------- servitor_wreck"""
        fixed = self.corrector._fix_invalid_list_markers(yaml_str)
        # Should fix all levels
        self.assertIn("- flashlight", fixed)
        self.assertIn("- medkit", fixed)
        self.assertIn("- servitor_wreck", fixed)
        self.assertNotIn("----------------", fixed)

    def test_fix_invalid_list_markers_from_ci_failure(self):
        """Test fixing invalid list markers from actual CI failure."""
        yaml_str = """narrative_map:
  scenes:
    entrance:
      items:
        ---------------- flashlight
      npcs: []
    storage:
      items:
        ---------------- medkit
        ---------------- bridge_key"""
        fixed = self.corrector._fix_invalid_list_markers(yaml_str)
        # Verify all invalid markers are fixed
        self.assertNotIn("----------------", fixed)
        self.assertIn("- flashlight", fixed)
        self.assertIn("- medkit", fixed)
        self.assertIn("- bridge_key", fixed)

    def test_fix_invalid_list_markers_valid_yaml_output(self):
        """Test that fixed list markers produce valid YAML."""
        yaml_str = """scenes:
  scene_test:
    name: "Test Scene"
    description: "A test scene with a long enough description to meet requirements."
    items:
      ---------------- item1
      ---------------- item2
    connections: []"""
        result = self.corrector.correct_narrative_map(yaml_str)
        # Should be corrected and valid
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)


class TestUnescapedApostrophesCorrection(unittest.TestCase):
    """Test cases for unescaped apostrophe correction."""

    def setUp(self):
        """Set up test fixtures."""
        self.corrector = OutputCorrector()

    def test_fix_unescaped_apostrophes_ships_bridge(self):
        """Test fixing apostrophes in 'Ship's Bridge'."""
        yaml_str = "name: 'Ship's Bridge'"
        fixed = self.corrector._fix_unescaped_apostrophes(yaml_str)
        # Should be converted to double quotes
        self.assertEqual(fixed, 'name: "Ship\'s Bridge"')

    def test_fix_unescaped_apostrophes_captains_quarters(self):
        """Test fixing apostrophes in 'The captain's quarters'."""
        yaml_str = "description: 'The captain's quarters'"
        fixed = self.corrector._fix_unescaped_apostrophes(yaml_str)
        # Should be converted to double quotes
        self.assertEqual(fixed, 'description: "The captain\'s quarters"')

    def test_fix_unescaped_apostrophes_multiple_lines(self):
        """Test fixing apostrophes across multiple lines."""
        yaml_str = """bridge:
  name: 'Ship's Bridge'
  description: 'The captain's quarters'
  note: 'It's a dark place'"""
        fixed = self.corrector._fix_unescaped_apostrophes(yaml_str)
        # All should be converted to double quotes
        self.assertIn('name: "Ship\'s Bridge"', fixed)
        self.assertIn('description: "The captain\'s quarters"', fixed)
        self.assertIn('note: "It\'s a dark place"', fixed)

    def test_fix_unescaped_apostrophes_no_change_if_no_apostrophe(self):
        """Test that strings without apostrophes are left unchanged."""
        yaml_str = "name: 'Simple Name'"
        fixed = self.corrector._fix_unescaped_apostrophes(yaml_str)
        # Should remain single-quoted (no apostrophe inside)
        self.assertEqual(fixed, "name: 'Simple Name'")

    def test_fix_unescaped_apostrophes_from_ci_failure(self):
        """Test fixing unescaped apostrophes from actual CI failure."""
        yaml_str = """narrative_map:
  scenes:
    bridge:
      name: 'Ship's Bridge'
      description: 'The vessel's command center'
      note: 'It's sealed'"""
        fixed = self.corrector._fix_unescaped_apostrophes(yaml_str)
        # Verify all apostrophes are handled
        self.assertIn('name: "Ship\'s Bridge"', fixed)
        self.assertIn('description: "The vessel\'s command center"', fixed)
        self.assertIn('note: "It\'s sealed"', fixed)

    def test_fix_unescaped_apostrophes_valid_yaml_output(self):
        """Test that fixed apostrophes produce valid YAML."""
        yaml_str = """scenes:
  bridge:
    name: 'Ship's Bridge'
    description: 'The captain's quarters with long description to meet minimum requirements.'
    connections: []"""
        result = self.corrector.correct_narrative_map(yaml_str)
        # Should be corrected and valid
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)


class TestCombinedSyntaxCorrection(unittest.TestCase):
    """Test cases for combined syntax error correction."""

    def setUp(self):
        """Set up test fixtures."""
        self.corrector = OutputCorrector()

    def test_fix_all_three_error_types_together(self):
        """Test fixing mixed quotes, invalid list markers, and apostrophes together."""
        yaml_str = """narrative_map:
  starting_scene: "entrance'
  scenes:
    entrance:
      name: 'Entrance Airlock"
      description: 'A dark airlock chamber with corroded walls'
      items:
        ---------------- flashlight
        ---------------- medkit
    bridge:
      name: 'Ship's Bridge'
      description: "The captain's quarters'
      items:
        ---------------- dataslate"""
        result = self.corrector.correct_narrative_map(yaml_str)
        # Should fix all errors and produce valid YAML
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)
        # Verify the YAML can be parsed
        self.assertIsNotNone(result.validation_result.data)

    def test_fix_real_ci_failure_scenario(self):
        """Test fixing a realistic CI failure scenario with all error types."""
        yaml_str = """title: "Space Hulk: Lost Vessel'
setting: 'A derelict Imperial vessel drifting through the void"
themes:
  ---------------- gothic horror
  ---------------- survival
  ---------------- isolation
tone: "Dark and foreboding'
plot_points:
  - id: "pp_01"
    name: 'Initial Breach"
    description: "The team's entry point into the derelict vessel. Long enough description."
  - id: "pp_02"
    name: "Discovery'
    description: 'The team discovers the ship's dark secrets here with sufficient detail.'
  - id: "pp_03"
    name: 'Resolution"
    description: "The final confrontation and resolution of the narrative with detail.'
characters:
  - name: 'Brother Sergeant"
    role: 'Team Leader'
    backstory: "A veteran warrior with enough backstory to meet requirements.'
conflicts:
  - type: "Main Conflict'
    description: "The primary conflict driving the narrative with sufficient length here.'"""
        result = self.corrector.correct_plot(yaml_str)
        # Should fix all errors and produce valid YAML
        self.assertIsInstance(result, CorrectionResult)
        self.assertTrue(result.success)
        # Verify the YAML can be parsed
        self.assertIsNotNone(result.validation_result.data)


if __name__ == "__main__":
    unittest.main()
