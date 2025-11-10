"""
Unit tests for the Game Validator module.

Tests the GameValidator's ability to detect playability issues in game content:
- Unreachable scenes
- Dead ends
- Invalid scene exits
- Missing required items
- Broken NPC dialogues
- Unsolvable puzzles
"""

import unittest
from space_hulk_game.engine import (
    GameValidator,
    ValidationResult,
    GameData,
    Scene,
    Item,
    NPC,
)


class TestValidationResult(unittest.TestCase):
    """Test cases for the ValidationResult class."""
    
    def test_initialization(self):
        """Test ValidationResult initialization."""
        result = ValidationResult()
        self.assertEqual(len(result.issues), 0)
        self.assertEqual(len(result.warnings), 0)
        self.assertEqual(len(result.suggestions), 0)
        self.assertTrue(result.is_valid())
    
    def test_is_valid_with_issues(self):
        """Test is_valid returns False when issues exist."""
        result = ValidationResult(issues=["Error 1"])
        self.assertFalse(result.is_valid())
    
    def test_is_valid_with_warnings_only(self):
        """Test is_valid returns True with only warnings."""
        result = ValidationResult(warnings=["Warning 1"])
        self.assertTrue(result.is_valid())
    
    def test_add_issue(self):
        """Test adding issues."""
        result = ValidationResult()
        result.add_issue("Critical error")
        self.assertEqual(len(result.issues), 1)
        self.assertIn("Critical error", result.issues)
        self.assertFalse(result.is_valid())
    
    def test_add_warning(self):
        """Test adding warnings."""
        result = ValidationResult()
        result.add_warning("Minor issue")
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("Minor issue", result.warnings)
        self.assertTrue(result.is_valid())
    
    def test_add_suggestion(self):
        """Test adding suggestions."""
        result = ValidationResult()
        result.add_suggestion("scene1", "Fix this")
        result.add_suggestion("scene1", "And this")
        result.add_suggestion("scene2", "Fix that")
        
        self.assertEqual(len(result.suggestions), 2)
        self.assertEqual(len(result.suggestions["scene1"]), 2)
        self.assertEqual(len(result.suggestions["scene2"]), 1)
    
    def test_get_summary(self):
        """Test get_summary generates readable output."""
        result = ValidationResult(
            issues=["Error 1"],
            warnings=["Warning 1"],
        )
        result.add_suggestion("scene1", "Fix it")
        result.stats = {"total_scenes": 5}
        
        summary = result.get_summary()
        self.assertIn("FAILED", summary)
        self.assertIn("Error 1", summary)
        self.assertIn("Warning 1", summary)
        self.assertIn("scene1", summary)
        self.assertIn("total_scenes", summary)


class TestGameValidator(unittest.TestCase):
    """Test cases for the GameValidator class."""
    
    def test_initialization(self):
        """Test GameValidator initialization."""
        validator = GameValidator()
        self.assertFalse(validator.strict_mode)
        
        validator_strict = GameValidator(strict_mode=True)
        self.assertTrue(validator_strict.strict_mode)
    
    def test_validate_simple_valid_game(self):
        """Test validation of a simple valid game."""
        scene = Scene(
            id="start",
            name="Starting Room",
            description="A simple starting room.",
            exits={}
        )
        
        game_data = GameData(
            title="Simple Game",
            description="A simple test game",
            scenes={"start": scene},
            starting_scene="start",
            endings=[{"scene_id": "start", "name": "The End"}]
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        # Should be valid (start scene with no exits is OK if it's an ending)
        self.assertTrue(result.is_valid())
        self.assertEqual(result.stats["total_scenes"], 1)
        self.assertEqual(result.stats["reachable_scenes"], 1)
    
    def test_validate_connected_game(self):
        """Test validation of a game with connected scenes."""
        scene1 = Scene(
            id="entrance",
            name="Entrance",
            description="The entrance hall.",
            exits={"north": "corridor"}
        )
        scene2 = Scene(
            id="corridor",
            name="Corridor",
            description="A long corridor.",
            exits={"south": "entrance", "east": "vault"}
        )
        scene3 = Scene(
            id="vault",
            name="Vault",
            description="The treasure vault.",
            exits={"west": "corridor"}
        )
        
        game_data = GameData(
            title="Connected Game",
            description="A game with connected scenes",
            scenes={
                "entrance": scene1,
                "corridor": scene2,
                "vault": scene3
            },
            starting_scene="entrance"
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        # All scenes are reachable
        self.assertTrue(result.is_valid())
        self.assertEqual(result.stats["reachable_scenes"], 3)
    
    def test_detect_unreachable_scenes(self):
        """Test detection of unreachable scenes."""
        scene1 = Scene(
            id="start",
            name="Start",
            description="Starting point.",
            exits={"north": "room1"}
        )
        scene2 = Scene(
            id="room1",
            name="Room 1",
            description="First room.",
            exits={"south": "start"}
        )
        # This scene is unreachable
        scene3 = Scene(
            id="orphan",
            name="Orphaned Room",
            description="Can't get here.",
            exits={"anywhere": "start"}
        )
        
        game_data = GameData(
            title="Broken Game",
            description="Game with unreachable scene",
            scenes={
                "start": scene1,
                "room1": scene2,
                "orphan": scene3
            },
            starting_scene="start"
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        # Should detect unreachable scene
        self.assertFalse(result.is_valid())
        self.assertTrue(any("orphan" in issue for issue in result.issues))
        self.assertEqual(result.stats["reachable_scenes"], 2)
        
        # Should suggest connection
        self.assertGreater(len(result.suggestions), 0)
    
    def test_detect_invalid_exits(self):
        """Test detection of exits pointing to non-existent scenes."""
        scene = Scene(
            id="start",
            name="Start",
            description="Starting point.",
            exits={"north": "missing_room"}
        )
        
        game_data = GameData(
            title="Invalid Exit Game",
            description="Game with invalid exit",
            scenes={"start": scene},
            starting_scene="start"
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        # Should detect invalid exit
        self.assertFalse(result.is_valid())
        self.assertTrue(
            any("invalid exit" in issue.lower() and "missing_room" in issue 
                for issue in result.issues)
        )
        
        # Should suggest fix
        self.assertIn("start", result.suggestions)
    
    def test_detect_dead_ends(self):
        """Test detection of dead-end scenes (not marked as endings)."""
        scene1 = Scene(
            id="start",
            name="Start",
            description="Starting point.",
            exits={"north": "dead_end"}
        )
        scene2 = Scene(
            id="dead_end",
            name="Dead End",
            description="No way out.",
            exits={}  # No exits!
        )
        
        game_data = GameData(
            title="Dead End Game",
            description="Game with dead end",
            scenes={
                "start": scene1,
                "dead_end": scene2
            },
            starting_scene="start",
            endings=[]  # No endings defined
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        # Should warn about dead end
        self.assertTrue(
            any("dead_end" in warning.lower() for warning in result.warnings) or
            any("dead_end" in issue.lower() for issue in result.issues)
        )
        
        # Should suggest adding exits
        if "dead_end" in result.suggestions:
            self.assertTrue(
                any("exit" in s.lower() for s in result.suggestions["dead_end"])
            )
    
    def test_dead_end_ok_if_ending(self):
        """Test that dead ends are OK if marked as endings."""
        scene1 = Scene(
            id="start",
            name="Start",
            description="Starting point.",
            exits={"north": "ending"}
        )
        scene2 = Scene(
            id="ending",
            name="The End",
            description="You win!",
            exits={}  # No exits, but this is OK
        )
        
        game_data = GameData(
            title="Proper Ending Game",
            description="Game with proper ending",
            scenes={
                "start": scene1,
                "ending": scene2
            },
            starting_scene="start",
            endings=[{"scene_id": "ending", "name": "Victory"}]
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        # Should be valid - ending scene can have no exits
        self.assertTrue(result.is_valid())
    
    def test_detect_missing_npc_item(self):
        """Test detection of NPCs giving non-existent items."""
        npc = NPC(
            id="merchant",
            name="Merchant",
            description="A trader.",
            gives_item="magic_sword"  # This item doesn't exist
        )
        
        scene = Scene(
            id="start",
            name="Start",
            description="Starting point.",
            npcs=[npc]
        )
        
        game_data = GameData(
            title="Missing Item Game",
            description="NPC gives missing item",
            scenes={"start": scene},
            starting_scene="start",
            endings=[{"scene_id": "start"}]
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        # Should detect missing item
        self.assertFalse(result.is_valid())
        self.assertTrue(
            any("magic_sword" in issue for issue in result.issues)
        )
    
    def test_npc_item_exists_globally(self):
        """Test that NPC items are OK if they exist in global items."""
        magic_sword = Item(
            id="magic_sword",
            name="Magic Sword",
            description="A legendary blade."
        )
        
        npc = NPC(
            id="merchant",
            name="Merchant",
            description="A trader.",
            gives_item="magic_sword"
        )
        
        scene = Scene(
            id="start",
            name="Start",
            description="Starting point.",
            npcs=[npc]
        )
        
        game_data = GameData(
            title="Valid NPC Item Game",
            description="NPC gives valid item",
            scenes={"start": scene},
            starting_scene="start",
            global_items={"magic_sword": magic_sword},
            endings=[{"scene_id": "start"}]
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        # Should be valid
        self.assertTrue(result.is_valid())
    
    def test_detect_npc_no_dialogue(self):
        """Test warning for NPCs with no dialogue."""
        npc = NPC(
            id="guard",
            name="Guard",
            description="A silent guard.",
            dialogue={}  # Empty dialogue
        )
        
        scene = Scene(
            id="start",
            name="Start",
            description="Starting point.",
            npcs=[npc]
        )
        
        game_data = GameData(
            title="Silent NPC Game",
            description="NPC with no dialogue",
            scenes={"start": scene},
            starting_scene="start",
            endings=[{"scene_id": "start"}]
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        # Should warn about missing dialogue
        self.assertTrue(
            any("dialogue" in warning.lower() for warning in result.warnings)
        )
    
    def test_complex_game_validation(self):
        """Test validation of a complex game with multiple issues."""
        item1 = Item(id="key", name="Key", description="A key", takeable=True)
        
        npc1 = NPC(
            id="guard",
            name="Guard",
            description="A guard.",
            dialogue={"greeting": "Hello"},
            gives_item="pass"  # This item exists
        )
        
        npc2 = NPC(
            id="merchant",
            name="Merchant",
            description="A merchant.",
            dialogue={},  # Empty dialogue - warning
            gives_item="missing_item"  # This doesn't exist - error
        )
        
        scene1 = Scene(
            id="start",
            name="Start",
            description="Start.",
            exits={"north": "room1", "east": "locked_room"},
            locked_exits={"east": "key"},
            items=[item1]
        )
        
        scene2 = Scene(
            id="room1",
            name="Room 1",
            description="First room.",
            exits={"south": "start", "west": "missing"},  # Invalid exit
            npcs=[npc1]
        )
        
        scene3 = Scene(
            id="locked_room",
            name="Locked Room",
            description="Locked.",
            exits={"west": "start"},
            npcs=[npc2]
        )
        
        scene4 = Scene(
            id="orphan",
            name="Orphan",
            description="Unreachable.",
            exits={}
        )
        
        pass_item = Item(id="pass", name="Pass", description="A pass")
        
        game_data = GameData(
            title="Complex Game",
            description="Complex test game",
            scenes={
                "start": scene1,
                "room1": scene2,
                "locked_room": scene3,
                "orphan": scene4
            },
            starting_scene="start",
            global_items={"pass": pass_item},
            endings=[{"scene_id": "orphan", "name": "Unreachable ending"}]
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        # Should have multiple issues
        self.assertFalse(result.is_valid())
        
        # Check for unreachable scene
        self.assertTrue(
            any("orphan" in issue.lower() for issue in result.issues)
        )
        
        # Check for invalid exit
        self.assertTrue(
            any("missing" in issue.lower() for issue in result.issues)
        )
        
        # Check for missing NPC item
        self.assertTrue(
            any("missing_item" in issue for issue in result.issues)
        )
        
        # Check for NPC dialogue warning
        self.assertTrue(
            any("dialogue" in warning.lower() for warning in result.warnings)
        )
        
        # Should have suggestions
        self.assertGreater(len(result.suggestions), 0)
    
    def test_find_reachable_scenes(self):
        """Test the BFS algorithm for finding reachable scenes."""
        scene1 = Scene(
            id="a",
            name="A",
            description="A",
            exits={"to_b": "b"}
        )
        scene2 = Scene(
            id="b",
            name="B",
            description="B",
            exits={"to_c": "c", "back": "a"}
        )
        scene3 = Scene(
            id="c",
            name="C",
            description="C",
            exits={"back": "b"}
        )
        scene4 = Scene(
            id="d",
            name="D",
            description="D (unreachable)",
            exits={}
        )
        
        scenes = {
            "a": scene1,
            "b": scene2,
            "c": scene3,
            "d": scene4
        }
        
        validator = GameValidator()
        reachable = validator._find_reachable_scenes(scenes, "a")
        
        self.assertEqual(len(reachable), 3)
        self.assertIn("a", reachable)
        self.assertIn("b", reachable)
        self.assertIn("c", reachable)
        self.assertNotIn("d", reachable)
    
    def test_locked_exit_validation(self):
        """Test validation of locked exits."""
        key = Item(id="key", name="Key", description="A key", takeable=True)
        
        scene1 = Scene(
            id="start",
            name="Start",
            description="Start.",
            exits={"north": "locked_room"},
            locked_exits={"north": "key"},
            items=[key]
        )
        
        scene2 = Scene(
            id="locked_room",
            name="Locked Room",
            description="A locked room.",
            exits={"south": "start"}
        )
        
        game_data = GameData(
            title="Locked Exit Game",
            description="Game with locked exit",
            scenes={
                "start": scene1,
                "locked_room": scene2
            },
            starting_scene="start"
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        # Should be valid - key is available
        self.assertTrue(result.is_valid())
    
    def test_stats_collection(self):
        """Test that validation collects proper statistics."""
        item = Item(id="item1", name="Item", description="An item")
        npc = NPC(id="npc1", name="NPC", description="An NPC")
        
        scene = Scene(
            id="start",
            name="Start",
            description="Start",
            items=[item],
            npcs=[npc]
        )
        
        game_data = GameData(
            title="Stats Game",
            description="Game for stats testing",
            scenes={"start": scene},
            starting_scene="start",
            global_items={"global_item": item},
            global_npcs={"global_npc": npc},
            endings=[{"scene_id": "start"}]
        )
        
        validator = GameValidator()
        result = validator.validate_game(game_data)
        
        self.assertEqual(result.stats["total_scenes"], 1)
        self.assertEqual(result.stats["total_items"], 1)
        self.assertEqual(result.stats["total_npcs"], 1)
        self.assertEqual(result.stats["starting_scene"], "start")
        self.assertEqual(result.stats["reachable_scenes"], 1)
    
    def test_strict_mode(self):
        """Test that strict_mode converts warnings to errors."""
        # Create game with NPC that has no dialogue (generates warning)
        npc = NPC(
            id="silent_npc",
            name="Silent NPC",
            description="A quiet character"
        )
        scene = Scene(
            id="start",
            name="Start",
            description="Starting room",
            exits={},
            npcs=[npc]
        )
        
        game_data = GameData(
            title="Test Game",
            description="Test",
            scenes={"start": scene},
            starting_scene="start",
            endings=[{"scene_id": "start"}]
        )
        
        # Normal mode - should have warning but no issues
        validator_normal = GameValidator(strict_mode=False)
        result_normal = validator_normal.validate_game(game_data)
        self.assertTrue(result_normal.is_valid())
        self.assertGreater(len(result_normal.warnings), 0)
        
        # Strict mode - warnings should become issues
        validator_strict = GameValidator(strict_mode=True)
        result_strict = validator_strict.validate_game(game_data)
        self.assertFalse(result_strict.is_valid())
        self.assertGreater(len(result_strict.issues), 0)
        self.assertEqual(len(result_strict.warnings), 0)


if __name__ == '__main__':
    unittest.main()
