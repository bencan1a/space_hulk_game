"""
Unit tests for the Content Loader module.

Tests ContentLoader's ability to load and parse YAML files,
handle errors gracefully, and convert AI-generated content into
engine-compatible GameData objects.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from space_hulk_game.engine import (
    NPC,
    ContentLoader,
    GameData,
    Item,
    LoaderError,
    Scene,
    YAMLParseError,
)


class TestGameData(unittest.TestCase):
    """Test cases for the GameData class."""

    def test_initialization_minimal(self):
        """Test GameData initialization with minimal required fields."""
        scene = Scene(id="start", name="Start", description="Starting room")
        data = GameData(
            title="Test Game",
            description="A test adventure",
            scenes={"start": scene},
            starting_scene="start",
        )

        self.assertEqual(data.title, "Test Game")
        self.assertEqual(data.description, "A test adventure")
        self.assertEqual(len(data.scenes), 1)
        self.assertEqual(data.starting_scene, "start")
        self.assertEqual(len(data.global_items), 0)
        self.assertEqual(len(data.global_npcs), 0)

    def test_initialization_complete(self):
        """Test GameData initialization with all fields."""
        scene = Scene(id="start", name="Start", description="Starting room")
        item = Item(id="key", name="Key", description="A key")
        npc = NPC(id="guard", name="Guard", description="A guard")

        data = GameData(
            title="Complete Game",
            description="A complete adventure",
            scenes={"start": scene},
            starting_scene="start",
            global_items={"key": item},
            global_npcs={"guard": npc},
            themes=["horror", "survival"],
            plot_points=[{"id": "p1", "name": "Point 1"}],
            endings=[{"id": "end1", "name": "Victory"}],
            game_rules={"combat": {"damage": 10}},
            metadata={"version": "1.0"},
        )

        self.assertEqual(len(data.global_items), 1)
        self.assertEqual(len(data.global_npcs), 1)
        self.assertEqual(len(data.themes), 2)
        self.assertEqual(len(data.plot_points), 1)
        self.assertEqual(len(data.endings), 1)
        self.assertIn("combat", data.game_rules)
        self.assertEqual(data.metadata["version"], "1.0")

    def test_validation_empty_title(self):
        """Test that empty title raises ValueError."""
        scene = Scene(id="start", name="Start", description="Start")
        with self.assertRaises(ValueError) as cm:
            GameData(title="", description="Test", scenes={"start": scene}, starting_scene="start")
        self.assertIn("title", str(cm.exception).lower())

    def test_validation_empty_description(self):
        """Test that empty description raises ValueError."""
        scene = Scene(id="start", name="Start", description="Start")
        with self.assertRaises(ValueError) as cm:
            GameData(title="Test", description="", scenes={"start": scene}, starting_scene="start")
        self.assertIn("description", str(cm.exception).lower())

    def test_validation_no_scenes(self):
        """Test that no scenes raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            GameData(title="Test", description="Test", scenes={}, starting_scene="start")
        self.assertIn("scene", str(cm.exception).lower())

    def test_validation_invalid_starting_scene(self):
        """Test that invalid starting scene raises ValueError."""
        scene = Scene(id="room1", name="Room", description="A room")
        with self.assertRaises(ValueError) as cm:
            GameData(
                title="Test",
                description="Test",
                scenes={"room1": scene},
                starting_scene="nonexistent",
            )
        self.assertIn("starting scene", str(cm.exception).lower())

    def test_get_scene_existing(self):
        """Test getting an existing scene."""
        scene = Scene(id="test", name="Test", description="Test")
        data = GameData(
            title="Test", description="Test", scenes={"test": scene}, starting_scene="test"
        )

        retrieved = data.get_scene("test")
        assert retrieved is not None
        self.assertEqual(retrieved.id, "test")

    def test_get_scene_nonexistent(self):
        """Test getting a nonexistent scene returns None."""
        scene = Scene(id="test", name="Test", description="Test")
        data = GameData(
            title="Test", description="Test", scenes={"test": scene}, starting_scene="test"
        )

        retrieved = data.get_scene("missing")
        self.assertIsNone(retrieved)

    def test_has_scene(self):
        """Test checking if scene exists."""
        scene = Scene(id="test", name="Test", description="Test")
        data = GameData(
            title="Test", description="Test", scenes={"test": scene}, starting_scene="test"
        )

        self.assertTrue(data.has_scene("test"))
        self.assertFalse(data.has_scene("missing"))

    def test_get_item_definition(self):
        """Test getting global item definitions."""
        scene = Scene(id="test", name="Test", description="Test")
        item = Item(id="sword", name="Sword", description="A sword")
        data = GameData(
            title="Test",
            description="Test",
            scenes={"test": scene},
            starting_scene="test",
            global_items={"sword": item},
        )

        retrieved = data.get_item_definition("sword")
        assert retrieved is not None
        self.assertEqual(retrieved.id, "sword")

        missing = data.get_item_definition("missing")
        self.assertIsNone(missing)

    def test_get_npc_definition(self):
        """Test getting global NPC definitions."""
        scene = Scene(id="test", name="Test", description="Test")
        npc = NPC(id="wizard", name="Wizard", description="A wizard")
        data = GameData(
            title="Test",
            description="Test",
            scenes={"test": scene},
            starting_scene="test",
            global_npcs={"wizard": npc},
        )

        retrieved = data.get_npc_definition("wizard")
        assert retrieved is not None
        self.assertEqual(retrieved.id, "wizard")

        missing = data.get_npc_definition("missing")
        self.assertIsNone(missing)

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        scene = Scene(id="test", name="Test", description="Test")
        item = Item(id="key", name="Key", description="A key")

        original = GameData(
            title="Test Game",
            description="Test",
            scenes={"test": scene},
            starting_scene="test",
            global_items={"key": item},
            themes=["horror"],
            metadata={"version": "1.0"},
        )

        # Convert to dict
        data_dict = original.to_dict()
        self.assertEqual(data_dict["title"], "Test Game")
        self.assertIn("test", data_dict["scenes"])

        # Convert back from dict
        restored = GameData.from_dict(data_dict)
        self.assertEqual(restored.title, original.title)
        self.assertEqual(restored.description, original.description)
        self.assertEqual(len(restored.scenes), len(original.scenes))
        self.assertEqual(len(restored.global_items), len(original.global_items))
        self.assertEqual(restored.themes, original.themes)


class TestContentLoaderBasics(unittest.TestCase):
    """Test basic ContentLoader functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = ContentLoader()
        self.strict_loader = ContentLoader(strict_mode=True)

        # Get path to test fixtures
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def test_initialization(self):
        """Test ContentLoader initialization."""
        loader1 = ContentLoader()
        self.assertFalse(loader1.strict_mode)

        loader2 = ContentLoader(strict_mode=True)
        self.assertTrue(loader2.strict_mode)

    def test_load_yaml_valid_file(self):
        """Test loading a valid YAML file."""
        plot_file = self.fixtures_dir / "plot_outline.yaml"
        data = self.loader.load_yaml(str(plot_file))

        self.assertIsInstance(data, dict)
        self.assertIn("narrative_foundation", data)
        self.assertEqual(data["narrative_foundation"]["title"], "Test Space Hulk Adventure")

    def test_load_yaml_missing_file_lenient(self):
        """Test loading missing file in lenient mode."""
        data = self.loader.load_yaml("nonexistent.yaml")
        self.assertEqual(data, {})

    def test_load_yaml_missing_file_strict(self):
        """Test loading missing file in strict mode raises error."""
        with self.assertRaises(LoaderError):
            self.strict_loader.load_yaml("nonexistent.yaml")

    def test_clean_yaml_content_with_markdown(self):
        """Test cleaning YAML content with markdown fences."""
        content_with_fence = """```yaml
key: value
nested:
  item: data
```"""
        cleaned = self.loader._clean_yaml_content(content_with_fence)
        self.assertNotIn("```", cleaned)
        self.assertIn("key: value", cleaned)

    def test_clean_yaml_content_without_markdown(self):
        """Test cleaning YAML content without markdown."""
        content = "key: value\nnested:\n  item: data"
        cleaned = self.loader._clean_yaml_content(content)
        self.assertEqual(cleaned.strip(), content.strip())


class TestContentLoaderIntegration(unittest.TestCase):
    """Test ContentLoader integration with complete YAML files."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = ContentLoader()
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def test_load_game_complete(self):
        """Test loading a complete game from fixtures."""
        game_data = self.loader.load_game(str(self.fixtures_dir))

        # Verify basic properties
        self.assertEqual(game_data.title, "Test Space Hulk Adventure")
        self.assertIn("derelict spacecraft", game_data.description.lower())

        # Verify scenes were loaded
        self.assertGreater(len(game_data.scenes), 0)
        self.assertIn("entrance", game_data.scenes)
        self.assertEqual(game_data.starting_scene, "entrance")

        # Verify scene details
        entrance = game_data.get_scene("entrance")
        assert entrance is not None
        self.assertEqual(entrance.name, "Entrance Airlock")
        self.assertIn("north", entrance.exits)
        self.assertEqual(entrance.exits["north"], "corridor_1")

    def test_load_game_scenes_structure(self):
        """Test that scenes are properly structured."""
        game_data = self.loader.load_game(str(self.fixtures_dir))

        # Check corridor scene
        corridor = game_data.get_scene("corridor_1")
        assert corridor is not None
        self.assertEqual(corridor.name, "Main Corridor")
        self.assertTrue(corridor.dark)
        self.assertIn("north", corridor.locked_exits)
        self.assertEqual(corridor.locked_exits["north"], "bridge_key")

    def test_load_game_items(self):
        """Test that items are properly loaded."""
        game_data = self.loader.load_game(str(self.fixtures_dir))

        # Check global items
        self.assertGreater(len(game_data.global_items), 0)

        flashlight = game_data.get_item_definition("flashlight")
        assert flashlight is not None
        self.assertEqual(flashlight.name, "Lumen Globe")
        self.assertTrue(flashlight.takeable)
        self.assertTrue(flashlight.useable)

    def test_load_game_npcs(self):
        """Test that NPCs are properly loaded."""
        game_data = self.loader.load_game(str(self.fixtures_dir))

        # Check global NPCs
        self.assertGreater(len(game_data.global_npcs), 0)

        survivor = game_data.get_npc_definition("survivor")
        assert survivor is not None
        self.assertEqual(survivor.name, "Guardsman Kane")
        self.assertFalse(survivor.hostile)
        self.assertIn("greeting", survivor.dialogue)

    def test_load_game_themes(self):
        """Test that themes are extracted."""
        game_data = self.loader.load_game(str(self.fixtures_dir))

        self.assertGreater(len(game_data.themes), 0)
        self.assertIn("isolation", game_data.themes)
        self.assertIn("survival", game_data.themes)

    def test_load_game_plot_points(self):
        """Test that plot points are extracted."""
        game_data = self.loader.load_game(str(self.fixtures_dir))

        self.assertGreater(len(game_data.plot_points), 0)
        # Find discovery plot point
        discovery = next((p for p in game_data.plot_points if p["id"] == "discovery"), None)
        assert discovery is not None
        self.assertEqual(discovery["name"], "Discovery of the Hulk")

    def test_load_game_endings(self):
        """Test that endings are extracted."""
        game_data = self.loader.load_game(str(self.fixtures_dir))

        self.assertGreater(len(game_data.endings), 0)
        # Find victory ending
        victory = next((e for e in game_data.endings if e["id"] == "victory"), None)
        assert victory is not None
        self.assertEqual(victory["name"], "Victorious Escape")

    def test_load_game_mechanics(self):
        """Test that game mechanics are extracted."""
        game_data = self.loader.load_game(str(self.fixtures_dir))

        self.assertGreater(len(game_data.game_rules), 0)
        self.assertIn("mechanics", game_data.game_rules)


class TestContentLoaderErrorHandling(unittest.TestCase):
    """Test ContentLoader error handling."""

    def setUp(self):
        """Set up temporary test directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = ContentLoader(strict_mode=False)
        self.strict_loader = ContentLoader(strict_mode=True)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_load_yaml_invalid_syntax_lenient(self):
        """Test loading YAML with invalid syntax in lenient mode."""
        invalid_yaml = os.path.join(self.temp_dir, "invalid.yaml")
        with open(invalid_yaml, "w") as f:
            f.write("key: value\n  invalid: indent\nbroken")

        # Should return empty dict in lenient mode
        data = self.loader.load_yaml(invalid_yaml)
        self.assertEqual(data, {})

    def test_load_yaml_invalid_syntax_strict(self):
        """Test loading YAML with invalid syntax in strict mode."""
        invalid_yaml = os.path.join(self.temp_dir, "invalid.yaml")
        with open(invalid_yaml, "w") as f:
            f.write("key: value\n  invalid: indent\nbroken")

        # Should raise YAMLParseError in strict mode
        with self.assertRaises(YAMLParseError):
            self.strict_loader.load_yaml(invalid_yaml)

    def test_load_yaml_empty_file(self):
        """Test loading an empty YAML file."""
        empty_yaml = os.path.join(self.temp_dir, "empty.yaml")
        with open(empty_yaml, "w") as f:
            f.write("")

        data = self.loader.load_yaml(empty_yaml)
        self.assertEqual(data, {})

    def test_load_game_missing_scenes_lenient(self):
        """Test loading game with missing scenes in lenient mode."""
        # Create minimal YAMLs with no scenes
        for filename in [
            "plot_outline.yaml",
            "narrative_map.yaml",
            "puzzle_design.yaml",
            "scene_texts.yaml",
            "prd_document.yaml",
        ]:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, "w") as f:
                f.write("empty: {}")

        # Should create a default scene
        game_data = self.loader.load_game(self.temp_dir)
        self.assertGreater(len(game_data.scenes), 0)
        self.assertEqual(game_data.starting_scene, "start")

    def test_extract_exits_from_list(self):
        """Test extracting exits when provided as list."""
        scene_data = {
            "exits": [
                {"direction": "north", "target": "room1"},
                {"direction": "south", "target": "room2"},
            ]
        }
        exits = self.loader._extract_exits(scene_data)
        self.assertEqual(exits["north"], "room1")
        self.assertEqual(exits["south"], "room2")

    def test_extract_exits_from_dict(self):
        """Test extracting exits when provided as dict."""
        scene_data = {"exits": {"north": "room1", "south": "room2"}}
        exits = self.loader._extract_exits(scene_data)
        self.assertEqual(exits["north"], "room1")
        self.assertEqual(exits["south"], "room2")

    def test_extract_exits_missing(self):
        """Test extracting exits when not provided."""
        scene_data = {}
        exits = self.loader._extract_exits(scene_data)
        self.assertEqual(exits, {})


class TestContentLoaderEdgeCases(unittest.TestCase):
    """Test ContentLoader edge cases and format variations."""

    def setUp(self):
        """Set up test loader."""
        self.loader = ContentLoader()

    def test_extract_title_from_plot(self):
        """Test title extraction from plot data."""
        plot = {"narrative_foundation": {"title": "Epic Adventure"}}
        narrative = {}
        mechanics = {}

        title = self.loader._extract_title(plot, narrative, mechanics)
        self.assertEqual(title, "Epic Adventure")

    def test_extract_title_from_mechanics(self):
        """Test title extraction from mechanics data."""
        plot = {}
        narrative = {}
        mechanics = {"game_title": "Mechanical Adventure"}

        title = self.loader._extract_title(plot, narrative, mechanics)
        self.assertEqual(title, "Mechanical Adventure")

    def test_extract_title_fallback(self):
        """Test title extraction with fallback."""
        plot = {}
        narrative = {}
        mechanics = {}

        title = self.loader._extract_title(plot, narrative, mechanics)
        self.assertIn("Space Hulk", title)

    def test_extract_themes_as_list(self):
        """Test extracting themes as list."""
        plot = {"narrative_foundation": {"themes": ["horror", "survival"]}}
        themes = self.loader._extract_themes(plot)
        self.assertEqual(len(themes), 2)
        self.assertIn("horror", themes)

    def test_extract_themes_as_string(self):
        """Test extracting single theme as string."""
        plot = {"narrative_foundation": {"themes": "horror"}}
        themes = self.loader._extract_themes(plot)
        self.assertEqual(len(themes), 1)
        self.assertEqual(themes[0], "horror")

    def test_build_item_minimal(self):
        """Test building item with minimal data."""
        item = self.loader._build_item("test_item", {"name": "Test"})
        self.assertEqual(item.id, "test_item")
        self.assertEqual(item.name, "Test")
        # Default is takeable=True
        self.assertTrue(item.takeable)

    def test_build_item_complete(self):
        """Test building item with complete data."""
        item_def = {
            "name": "Magic Sword",
            "description": "A powerful weapon",
            "takeable": True,
            "useable": True,
            "use_text": "You swing the sword",
            "effects": {"damage": 50},
        }
        item = self.loader._build_item("sword", item_def)
        self.assertEqual(item.name, "Magic Sword")
        self.assertTrue(item.takeable)
        self.assertTrue(item.useable)
        self.assertEqual(item.effects["damage"], 50)

    def test_build_npc_minimal(self):
        """Test building NPC with minimal data."""
        npc = self.loader._build_npc("test_npc", {"name": "Guard"})
        self.assertEqual(npc.id, "test_npc")
        self.assertEqual(npc.name, "Guard")
        self.assertFalse(npc.hostile)

    def test_build_npc_complete(self):
        """Test building NPC with complete data."""
        npc_def = {
            "name": "Evil Wizard",
            "description": "A dark sorcerer",
            "dialogue": {"greeting": "Muahaha!"},
            "hostile": True,
            "health": 150,
            "gives_item": "magic_staff",
        }
        npc = self.loader._build_npc("wizard", npc_def)
        self.assertEqual(npc.name, "Evil Wizard")
        self.assertTrue(npc.hostile)
        self.assertEqual(npc.health, 150)
        self.assertEqual(npc.gives_item, "magic_staff")


if __name__ == "__main__":
    unittest.main()
