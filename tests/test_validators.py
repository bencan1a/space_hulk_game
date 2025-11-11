"""Unit tests for YAML output validators.

This module tests the OutputValidator class to ensure it correctly
validates YAML outputs against Pydantic schemas.
"""

import unittest
from pathlib import Path

import yaml

from space_hulk_game.schemas.game_mechanics import GameMechanics
from space_hulk_game.schemas.narrative_map import NarrativeMap
from space_hulk_game.schemas.plot_outline import PlotOutline
from space_hulk_game.schemas.puzzle_design import PuzzleDesign
from space_hulk_game.schemas.scene_text import SceneTexts
from space_hulk_game.validation import OutputValidator, ValidationResult


class TestOutputValidator(unittest.TestCase):
    """Test cases for OutputValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = OutputValidator()

    def test_validator_initialization(self):
        """Test that validator initializes correctly."""
        self.assertIsInstance(self.validator, OutputValidator)

    def test_strip_markdown_fences_with_yaml_language(self):
        """Test stripping markdown fences with yaml language specifier."""
        yaml_with_fence = "```yaml\nkey: value\n```"
        result = self.validator._strip_markdown_fences(yaml_with_fence)
        self.assertEqual(result, "key: value")

    def test_strip_markdown_fences_without_language(self):
        """Test stripping markdown fences without language specifier."""
        yaml_with_fence = "```\nkey: value\n```"
        result = self.validator._strip_markdown_fences(yaml_with_fence)
        self.assertEqual(result, "key: value")

    def test_strip_markdown_fences_no_fences(self):
        """Test that content without fences is unchanged."""
        yaml_no_fence = "key: value"
        result = self.validator._strip_markdown_fences(yaml_no_fence)
        self.assertEqual(result, "key: value")

    def test_parse_yaml_valid(self):
        """Test parsing valid YAML."""
        yaml_str = "key: value\nnumber: 42"
        data, errors = self.validator._parse_yaml(yaml_str)
        self.assertEqual(data, {"key": "value", "number": 42})
        self.assertEqual(errors, [])

    def test_parse_yaml_empty(self):
        """Test parsing empty YAML."""
        yaml_str = ""
        data, errors = self.validator._parse_yaml(yaml_str)
        self.assertIsNone(data)
        self.assertEqual(len(errors), 1)
        self.assertIn("empty", errors[0].lower())

    def test_parse_yaml_invalid_syntax(self):
        """Test parsing YAML with syntax errors."""
        yaml_str = "key: value\n  bad indentation: here"
        data, errors = self.validator._parse_yaml(yaml_str)
        self.assertIsNone(data)
        self.assertEqual(len(errors), 1)
        self.assertIn("parsing error", errors[0].lower())

    def test_parse_yaml_not_dict(self):
        """Test parsing YAML that's not a dictionary."""
        yaml_str = "- item1\n- item2"
        data, errors = self.validator._parse_yaml(yaml_str)
        self.assertIsNone(data)
        self.assertEqual(len(errors), 1)
        self.assertIn("dictionary", errors[0].lower())


class TestPlotOutlineValidation(unittest.TestCase):
    """Test cases for plot outline validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = OutputValidator()

    def test_validate_plot_valid_minimal(self):
        """Test validating a minimal valid plot outline."""
        yaml_str = """
title: "Test Plot"
setting: "A dark and mysterious setting with lots of atmospheric detail and description to meet the minimum length requirement."
themes:
  - "survival"
  - "horror"
tone: "Dark and gritty atmosphere"
plot_points:
  - id: "pp_01"
    name: "Opening"
    description: "The opening scene where the characters arrive at the location and begin their investigation."
  - id: "pp_02"
    name: "Discovery"
    description: "The characters discover something terrible that changes everything they thought they knew."
  - id: "pp_03"
    name: "Climax"
    description: "The final confrontation where everything comes to a head and decisions must be made."
characters:
  - name: "Hero"
    role: "Protagonist"
    backstory: "A brave warrior with a dark past and many secrets that drive their actions."
conflicts:
  - type: "Man vs. Monster"
    description: "The primary conflict between the heroes and the terrible creatures that threaten them."
"""
        result = self.validator.validate_plot(yaml_str)
        self.assertTrue(result.valid)
        self.assertIsInstance(result.data, PlotOutline)
        self.assertEqual(result.data.title, "Test Plot")
        self.assertEqual(len(result.errors), 0)

    def test_validate_plot_with_markdown_fences(self):
        """Test validating plot outline with markdown fences."""
        yaml_str = """```yaml
title: "Test Plot"
setting: "A dark and mysterious setting with lots of atmospheric detail and description to meet the minimum length requirement."
themes:
  - "survival"
tone: "Dark and gritty atmosphere"
plot_points:
  - id: "pp_01"
    name: "Opening"
    description: "The opening scene where the characters arrive at the location and begin their investigation."
  - id: "pp_02"
    name: "Discovery"
    description: "The characters discover something terrible that changes everything they thought they knew."
  - id: "pp_03"
    name: "Climax"
    description: "The final confrontation where everything comes to a head and decisions must be made."
characters:
  - name: "Hero"
    role: "Protagonist"
    backstory: "A brave warrior with a dark past and many secrets that drive their actions."
conflicts:
  - type: "Man vs. Monster"
    description: "The primary conflict between the heroes and the terrible creatures that threaten them."
```"""
        result = self.validator.validate_plot(yaml_str)
        self.assertTrue(result.valid)
        self.assertIsInstance(result.data, PlotOutline)
        self.assertEqual(len(result.errors), 0)

    def test_validate_plot_missing_required_field(self):
        """Test validating plot outline with missing required field."""
        yaml_str = """
title: "Test Plot"
setting: "A setting"
themes:
  - "survival"
tone: "Dark"
plot_points: []
characters: []
"""
        # Missing 'conflicts' field
        result = self.validator.validate_plot(yaml_str)
        self.assertFalse(result.valid)
        self.assertIsNone(result.data)
        self.assertGreater(len(result.errors), 0)

    def test_validate_plot_invalid_plot_point_id(self):
        """Test validating plot outline with invalid plot point ID."""
        yaml_str = """
title: "Test Plot"
setting: "A dark and mysterious setting with lots of atmospheric detail and description."
themes:
  - "survival"
tone: "Dark and gritty"
plot_points:
  - id: "invalid id with spaces!"
    name: "Opening"
    description: "The opening scene where the characters arrive at the location."
  - id: "pp_02"
    name: "Discovery"
    description: "The characters discover something terrible that changes everything."
  - id: "pp_03"
    name: "Climax"
    description: "The final confrontation where everything comes to a head."
characters:
  - name: "Hero"
    role: "Protagonist"
    backstory: "A brave warrior with a dark past and many secrets that drive them."
conflicts:
  - type: "Man vs. Monster"
    description: "The primary conflict between the heroes and the monsters."
"""
        result = self.validator.validate_plot(yaml_str)
        self.assertFalse(result.valid)
        self.assertIsNone(result.data)
        self.assertGreater(len(result.errors), 0)
        # Check that error mentions ID validation
        error_str = " ".join(result.errors).lower()
        self.assertTrue("alphanumeric" in error_str or "id" in error_str)

    def test_validate_plot_duplicate_character_names(self):
        """Test validating plot outline with duplicate character names."""
        yaml_str = """
title: "Test Plot"
setting: "A dark and mysterious setting with lots of atmospheric detail."
themes:
  - "survival"
tone: "Dark"
plot_points:
  - id: "pp_01"
    name: "Opening"
    description: "The opening scene where the characters arrive at the location."
  - id: "pp_02"
    name: "Discovery"
    description: "The characters discover something terrible."
  - id: "pp_03"
    name: "Climax"
    description: "The final confrontation."
characters:
  - name: "Hero"
    role: "Protagonist"
    backstory: "A brave warrior with a dark past and many secrets."
  - name: "Hero"
    role: "Duplicate"
    backstory: "This is a duplicate name and should fail validation."
conflicts:
  - type: "Man vs. Monster"
    description: "The primary conflict between the heroes and the monsters."
"""
        result = self.validator.validate_plot(yaml_str)
        self.assertFalse(result.valid)
        self.assertIsNone(result.data)
        self.assertGreater(len(result.errors), 0)
        # Check that error mentions uniqueness
        error_str = " ".join(result.errors).lower()
        self.assertIn("unique", error_str)


class TestNarrativeMapValidation(unittest.TestCase):
    """Test cases for narrative map validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = OutputValidator()

    def test_validate_narrative_map_valid(self):
        """Test validating a valid narrative map."""
        yaml_str = """
start_scene: "scene_01"
scenes:
  scene_01:
    name: "Opening Scene"
    description: "A detailed description of the opening scene with lots of atmospheric detail and interesting elements."
    connections:
      - target: "scene_02"
        description: "The player moves to the next area after completing the first challenge."
  scene_02:
    name: "Second Scene"
    description: "The second scene where things get more intense and the plot thickens considerably."
    connections: []
"""
        result = self.validator.validate_narrative_map(yaml_str)
        self.assertTrue(result.valid)
        self.assertIsInstance(result.data, NarrativeMap)
        self.assertEqual(result.data.start_scene, "scene_01")
        self.assertEqual(len(result.data.scenes), 2)
        self.assertEqual(len(result.errors), 0)

    def test_validate_narrative_map_nonexistent_connection(self):
        """Test validating narrative map with connection to non-existent scene."""
        yaml_str = """
start_scene: "scene_01"
scenes:
  scene_01:
    name: "Opening Scene"
    description: "A detailed description of the opening scene with lots of detail."
    connections:
      - target: "scene_nonexistent"
        description: "This points to a scene that doesn't exist."
"""
        result = self.validator.validate_narrative_map(yaml_str)
        self.assertFalse(result.valid)
        self.assertIsNone(result.data)
        self.assertGreater(len(result.errors), 0)
        # Check that error mentions the non-existent scene
        error_str = " ".join(result.errors).lower()
        self.assertTrue("non-existent" in error_str or "nonexistent" in error_str)

    def test_validate_narrative_map_with_decision_points(self):
        """Test validating narrative map with decision points."""
        yaml_str = """
start_scene: "scene_01"
scenes:
  scene_01:
    name: "Decision Point"
    description: "A scene where the player must make an important choice that affects the outcome."
    connections: []
    decision_points:
      - id: "decision_01"
        prompt: "What path will you choose in this critical moment?"
        options:
          - choice: "Take the dangerous left path"
            outcome: "You take the dangerous path through the darkness."
            target_scene: "scene_02"
          - choice: "Take the safer right path"
            outcome: "You take the safer route but it takes longer."
            target_scene: "scene_02"
  scene_02:
    name: "Result"
    description: "The result of your previous choice becomes apparent as you continue forward."
    connections: []
"""
        result = self.validator.validate_narrative_map(yaml_str)
        self.assertTrue(result.valid)
        self.assertIsInstance(result.data, NarrativeMap)
        self.assertEqual(len(result.errors), 0)


class TestPuzzleDesignValidation(unittest.TestCase):
    """Test cases for puzzle design validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = OutputValidator()

    def test_validate_puzzle_design_valid(self):
        """Test validating a valid puzzle design."""
        yaml_str = """
puzzles:
  - id: "puzzle_01"
    name: "The First Puzzle"
    description: "A challenging puzzle that requires careful observation and logical thinking to solve successfully."
    location: "scene_01"
    narrative_purpose: "This puzzle teaches the player about the game mechanics."
    solution:
      type: "multi-step"
      steps:
        - step: "First, examine the ancient control panel carefully."
        - step: "Then, locate the power conduit and activate it."
        - step: "Finally, input the correct sequence based on the clues."
    difficulty: "medium"
artifacts:
  - id: "artifact_01"
    name: "Ancient Key"
    description: "A mysterious key from a bygone era, covered in strange markings."
    location: "scene_01"
    narrative_significance: "This key unlocks the path to the truth about the past."
    properties:
      - property: "Opens ancient doors"
monsters:
  - id: "monster_01"
    name: "Shadow Beast"
    description: "A terrifying creature that lurks in the darkness, waiting to strike."
    locations:
      - "scene_02"
    narrative_role: "Represents the ever-present danger and fear in the environment."
    abilities:
      - "Stealth attack"
      - "Shadow form"
npcs:
  - id: "npc_01"
    name: "Old Sage"
    role: "Guide and mentor"
    description: "An ancient wise person who provides cryptic advice to the player."
    locations:
      - "scene_01"
    dialogue_themes:
      - "Ancient wisdom"
      - "Warnings about danger"
"""
        result = self.validator.validate_puzzle_design(yaml_str)
        self.assertTrue(result.valid)
        self.assertIsInstance(result.data, PuzzleDesign)
        self.assertEqual(len(result.data.puzzles), 1)
        self.assertEqual(len(result.data.artifacts), 1)
        self.assertEqual(len(result.data.monsters), 1)
        self.assertEqual(len(result.data.npcs), 1)
        self.assertEqual(len(result.errors), 0)

    def test_validate_puzzle_design_invalid_difficulty(self):
        """Test validating puzzle design with invalid difficulty."""
        yaml_str = """
puzzles:
  - id: "puzzle_01"
    name: "Test Puzzle"
    description: "A puzzle with an invalid difficulty level that should fail validation."
    location: "scene_01"
    narrative_purpose: "This puzzle tests validation."
    solution:
      type: "multi-step"
      steps:
        - step: "Complete the puzzle somehow."
    difficulty: "super-hard"
artifacts:
  - id: "artifact_01"
    name: "Test Artifact"
    description: "A test artifact"
    location: "scene_01"
    narrative_significance: "For testing purposes only"
    properties:
      - property: "Test property"
monsters:
  - id: "monster_01"
    name: "Test Monster"
    description: "A test monster"
    locations:
      - "scene_01"
    narrative_role: "Testing role"
    abilities:
      - "Test ability"
npcs:
  - id: "npc_01"
    name: "Test NPC"
    role: "Test role"
    description: "A test NPC character"
    locations:
      - "scene_01"
    dialogue_themes:
      - "Test theme"
"""
        result = self.validator.validate_puzzle_design(yaml_str)
        self.assertFalse(result.valid)
        self.assertIsNone(result.data)
        self.assertGreater(len(result.errors), 0)


class TestSceneTextsValidation(unittest.TestCase):
    """Test cases for scene texts validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = OutputValidator()

    def test_validate_scene_texts_valid(self):
        """Test validating valid scene texts."""
        yaml_str = """
scenes:
  scene_01:
    name: "The Dark Corridor"
    description: "A long, dark corridor stretches before you, lit only by flickering emergency lights that cast eerie shadows on the walls. The air is thick with the smell of decay and abandonment, and you can hear strange sounds echoing from somewhere deep within the darkness."
    atmosphere: "Oppressive, dark, foreboding, mysterious"
    initial_text: "You step into the corridor, your footsteps echoing ominously."
    examination_texts:
      door: "A heavy metal door, rusted but still intact and blocking your path forward."
      lights: "Emergency lights flicker weakly, their batteries nearly depleted after years of continuous operation."
    dialogue:
      - speaker: "Commander"
        text: "Stay alert. We don't know what's waiting for us in there."
        emotion: "Cautious, serious"
        context: "As the team enters the corridor"
"""
        result = self.validator.validate_scene_texts(yaml_str)
        self.assertTrue(result.valid)
        self.assertIsInstance(result.data, SceneTexts)
        self.assertEqual(len(result.data.scenes), 1)
        self.assertEqual(len(result.errors), 0)

    def test_validate_scene_texts_description_too_short(self):
        """Test validating scene texts with description that's too short."""
        yaml_str = """
scenes:
  scene_01:
    name: "Short Scene"
    description: "Too short."
    atmosphere: "Dark and moody"
    initial_text: "You enter the area."
    examination_texts: {}
    dialogue: []
"""
        result = self.validator.validate_scene_texts(yaml_str)
        self.assertFalse(result.valid)
        self.assertIsNone(result.data)
        self.assertGreater(len(result.errors), 0)


class TestGameMechanicsValidation(unittest.TestCase):
    """Test cases for game mechanics validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = OutputValidator()

    def test_validate_game_mechanics_valid(self):
        """Test validating valid game mechanics."""
        yaml_str = """
game_title: "Test Game"
game_systems:
  movement:
    description: "A tactical movement system where players navigate through grid-based environments with limited action points per turn."
    commands:
      - "move"
      - "run"
      - "crouch"
    narrative_purpose: "The movement system reinforces the tactical nature of the game and creates tension through limited mobility."
  inventory:
    description: "A limited inventory system where players must carefully manage their equipment and resources throughout the adventure."
    capacity: 10
    commands:
      - "take"
      - "drop"
      - "use"
    narrative_purpose: "Limited inventory creates resource scarcity and forces players to make meaningful choices about what to carry."
  combat:
    description: "A turn-based tactical combat system featuring cover mechanics and strategic positioning."
    mechanics:
      - name: "Cover System"
        rules: "Players can take cover behind objects to reduce incoming damage by 50 percent."
    narrative_purpose: "Combat reinforces the dangerous nature of the world and rewards careful planning and tactics."
  interaction:
    description: "An interaction system allowing players to examine objects and talk to NPCs for information."
    commands:
      - "examine"
      - "talk"
      - "use"
    narrative_purpose: "Interaction allows players to uncover lore and gather information needed to progress."
game_state:
  tracked_variables:
    - variable: "player_health"
      purpose: "Tracks the player's current health to determine when they are defeated."
  win_conditions:
    - condition: "Complete all objectives and reach the extraction point safely."
  lose_conditions:
    - condition: "Player health reaches zero and they are defeated in combat."
technical_requirements:
  - requirement: "Implement a robust save system that preserves game state."
    justification: "Players need to save their progress to avoid losing significant gameplay time."
"""
        result = self.validator.validate_game_mechanics(yaml_str)
        self.assertTrue(result.valid)
        self.assertIsInstance(result.data, GameMechanics)
        self.assertEqual(result.data.game_title, "Test Game")
        self.assertEqual(len(result.errors), 0)

    def test_validate_game_mechanics_invalid_inventory_capacity(self):
        """Test validating game mechanics with invalid inventory capacity."""
        yaml_str = """
game_title: "Test Game"
game_systems:
  movement:
    description: "A movement system with various commands for player navigation."
    commands:
      - "move"
    narrative_purpose: "Movement allows exploration of the game world."
  inventory:
    description: "An inventory system with invalid capacity."
    capacity: 0
    commands:
      - "take"
    narrative_purpose: "Inventory management is important."
  combat:
    description: "A combat system for engaging enemies in tactical battles."
    mechanics:
      - name: "Basic Attack"
        rules: "Players can perform basic attacks against enemies."
    narrative_purpose: "Combat creates challenge and excitement."
  interaction:
    description: "An interaction system for engaging with the world."
    commands:
      - "examine"
    narrative_purpose: "Interaction reveals information."
game_state:
  tracked_variables:
    - variable: "test"
      purpose: "Testing variable tracking."
  win_conditions:
    - condition: "Win the game by completing objectives."
  lose_conditions:
    - condition: "Lose by failing objectives."
technical_requirements:
  - requirement: "Basic technical requirements."
    justification: "Required for game to function."
"""
        result = self.validator.validate_game_mechanics(yaml_str)
        self.assertFalse(result.valid)
        self.assertIsNone(result.data)
        self.assertGreater(len(result.errors), 0)


class TestRealFileValidation(unittest.TestCase):
    """Test validation against real YAML files in game-config/."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = OutputValidator()
        # Get path to game-config directory relative to this test file
        test_dir = Path(__file__).parent
        self.game_config_dir = test_dir.parent / "game-config"

    def test_validate_real_plot_outline(self):
        """Test validation against real plot_outline.yaml file."""
        try:
            plot_file = self.game_config_dir / "plot_outline.yaml"
            with open(plot_file) as f:
                yaml_content = f.read()

            # The real file has a 'narrative_foundation' wrapper, extract it
            data = yaml.safe_load(yaml_content)
            if "narrative_foundation" in data:
                # Re-serialize just the narrative_foundation part
                yaml_content = yaml.dump(data["narrative_foundation"])

            result = self.validator.validate_plot(yaml_content)

            # The file may not validate perfectly if it's a template
            # Just check that we can process it without crashing
            self.assertIsInstance(result, ValidationResult)

            if not result.valid:
                print(f"\nNote: Real plot_outline.yaml has {len(result.errors)} validation errors:")
                for error in result.errors[:5]:  # Print first 5 errors
                    print(f"  - {error}")

        except FileNotFoundError:
            self.skipTest("Real plot_outline.yaml file not found")

    def test_validate_real_narrative_map(self):
        """Test validation against real narrative_map.yaml file."""
        try:
            narrative_file = self.game_config_dir / "narrative_map.yaml"
            with open(narrative_file) as f:
                yaml_content = f.read()

            result = self.validator.validate_narrative_map(yaml_content)

            # Just check that we can process it
            self.assertIsInstance(result, ValidationResult)

            if not result.valid:
                print(
                    f"\nNote: Real narrative_map.yaml has {len(result.errors)} validation errors:"
                )
                for error in result.errors[:5]:
                    print(f"  - {error}")

        except FileNotFoundError:
            self.skipTest("Real narrative_map.yaml file not found")

    def test_validate_real_puzzle_design(self):
        """Test validation against real puzzle_design.yaml file."""
        try:
            puzzle_file = self.game_config_dir / "puzzle_design.yaml"
            with open(puzzle_file) as f:
                yaml_content = f.read()

            result = self.validator.validate_puzzle_design(yaml_content)

            # Just check that we can process it
            self.assertIsInstance(result, ValidationResult)

            if not result.valid:
                print(
                    f"\nNote: Real puzzle_design.yaml has {len(result.errors)} validation errors:"
                )
                for error in result.errors[:5]:
                    print(f"  - {error}")

        except FileNotFoundError:
            self.skipTest("Real puzzle_design.yaml file not found")

    def test_validate_real_scene_texts(self):
        """Test validation against real scene_texts.yaml file."""
        try:
            scene_file = self.game_config_dir / "scene_texts.yaml"
            with open(scene_file) as f:
                yaml_content = f.read()

            result = self.validator.validate_scene_texts(yaml_content)

            # Just check that we can process it
            self.assertIsInstance(result, ValidationResult)

            if not result.valid:
                print(f"\nNote: Real scene_texts.yaml has {len(result.errors)} validation errors:")
                for error in result.errors[:5]:
                    print(f"  - {error}")

        except FileNotFoundError:
            self.skipTest("Real scene_texts.yaml file not found")


if __name__ == "__main__":
    unittest.main()
