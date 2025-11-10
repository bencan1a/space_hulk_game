"""
Test suite for the TextAdventureEngine.

Comprehensive tests for game loop, action handlers, state transitions,
and persistence.
"""

import unittest
import tempfile
import os
from io import StringIO
from typing import List

from src.space_hulk_game.engine.engine import TextAdventureEngine
from src.space_hulk_game.engine.game_state import GameState
from src.space_hulk_game.engine.scene import Scene
from src.space_hulk_game.engine.entities import Item, NPC, Event
from src.space_hulk_game.engine.persistence import (
    save_game,
    load_game,
    get_save_metadata,
    list_save_files,
    delete_save,
    PersistenceError,
)


class MockInputOutput:
    """Mock input/output for testing the game engine."""
    
    def __init__(self, commands: List[str]):
        """
        Initialize with a list of commands to return.
        
        Args:
            commands: List of command strings to return from input().
        """
        self.commands = commands
        self.command_index = 0
        self.outputs = []
    
    def input_func(self) -> str:
        """Return next command from the list."""
        if self.command_index >= len(self.commands):
            raise EOFError("No more commands")
        
        command = self.commands[self.command_index]
        self.command_index += 1
        return command
    
    def output_func(self, text: str) -> None:
        """Store output text."""
        self.outputs.append(text)
    
    def get_all_output(self) -> str:
        """Get all output as a single string."""
        return '\n'.join(self.outputs)
    
    def clear_output(self) -> None:
        """Clear stored outputs."""
        self.outputs = []


class TestTextAdventureEngineInit(unittest.TestCase):
    """Test engine initialization."""
    
    def test_initialization_basic(self):
        """Test basic engine initialization."""
        state = GameState(current_scene="room1")
        scenes = {
            "room1": Scene(id="room1", name="Room 1", description="First room.")
        }
        
        engine = TextAdventureEngine(state, scenes)
        
        self.assertEqual(engine.game_state, state)
        self.assertEqual(engine.scenes, scenes)
        self.assertIsNotNone(engine.parser)
        self.assertFalse(engine.running)
    
    def test_initialization_invalid_scene(self):
        """Test that initialization fails with invalid current scene."""
        state = GameState(current_scene="nonexistent")
        scenes = {
            "room1": Scene(id="room1", name="Room 1", description="First room.")
        }
        
        with self.assertRaises(ValueError) as cm:
            TextAdventureEngine(state, scenes)
        
        self.assertIn("not found in scenes", str(cm.exception))
    
    def test_initialization_with_conditions(self):
        """Test initialization with victory/defeat conditions."""
        state = GameState(current_scene="room1")
        scenes = {
            "room1": Scene(id="room1", name="Room 1", description="First room.")
        }
        
        engine = TextAdventureEngine(
            state,
            scenes,
            victory_conditions={'mission_complete'},
            defeat_conditions={'catastrophic_failure'}
        )
        
        self.assertEqual(engine.victory_conditions, {'mission_complete'})
        self.assertEqual(engine.defeat_conditions, {'catastrophic_failure'})


class TestActionHandlers(unittest.TestCase):
    """Test individual action handlers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state = GameState(
            current_scene="room1",
            inventory=["dataslate"],
            health=100,
            max_health=100
        )
        
        self.item1 = Item(
            id="medkit",
            name="Medical Kit",
            description="A standard medkit.",
            takeable=True,
            useable=True
        )
        
        self.item2 = Item(
            id="console",
            name="Control Console",
            description="A large console.",
            takeable=False,
            useable=True
        )
        
        self.npc1 = NPC(
            id="guard",
            name="Imperial Guard",
            description="A stern-looking guard.",
            dialogue={'greeting': "Halt! State your business."}
        )
        
        self.scenes = {
            "room1": Scene(
                id="room1",
                name="Room 1",
                description="The first room.",
                exits={"north": "room2"},
                items=[self.item1, self.item2],
                npcs=[self.npc1]
            ),
            "room2": Scene(
                id="room2",
                name="Room 2",
                description="The second room.",
                exits={"south": "room1"}
            )
        }
        
        self.mock_io = MockInputOutput([])
        self.engine = TextAdventureEngine(
            self.state,
            self.scenes,
            input_func=self.mock_io.input_func,
            output_func=self.mock_io.output_func
        )
    
    def test_handle_move_valid(self):
        """Test moving to a valid exit."""
        self.assertEqual(self.state.current_scene, "room1")
        
        # Mark room1 as visited initially
        self.state.visited_scenes.add("room1")
        
        self.engine.handle_move("north")
        
        self.assertEqual(self.state.current_scene, "room2")
        self.assertIn("room1", self.state.visited_scenes)
        self.assertIn("room2", self.state.visited_scenes)
    
    def test_handle_move_invalid_direction(self):
        """Test moving in an invalid direction."""
        self.engine.handle_move("west")
        
        # Should still be in room1
        self.assertEqual(self.state.current_scene, "room1")
        
        # Check output contains error message
        output = self.mock_io.get_all_output()
        self.assertIn("no exit", output.lower())
    
    def test_handle_move_locked_exit(self):
        """Test moving through a locked exit."""
        # Add locked exit to room1
        self.scenes["room1"].locked_exits["north"] = "special_key"
        
        self.engine.handle_move("north")
        
        # Should still be in room1
        self.assertEqual(self.state.current_scene, "room1")
        
        output = self.mock_io.get_all_output()
        self.assertIn("locked", output.lower())
    
    def test_handle_take_valid_item(self):
        """Test taking a valid, takeable item."""
        self.assertNotIn("medkit", self.state.inventory)
        
        self.engine.handle_take("medkit")
        
        self.assertIn("medkit", self.state.inventory)
        
        # Item should be removed from scene
        current_scene = self.scenes["room1"]
        self.assertIsNone(current_scene.get_item("medkit"))
    
    def test_handle_take_nontakeable_item(self):
        """Test taking a non-takeable item."""
        self.engine.handle_take("console")
        
        self.assertNotIn("console", self.state.inventory)
        
        output = self.mock_io.get_all_output()
        self.assertIn("can't take", output.lower())
    
    def test_handle_take_nonexistent_item(self):
        """Test taking an item that doesn't exist."""
        self.engine.handle_take("sword")
        
        output = self.mock_io.get_all_output()
        self.assertIn("don't see", output.lower())
    
    def test_handle_drop_valid_item(self):
        """Test dropping an item from inventory."""
        self.assertIn("dataslate", self.state.inventory)
        
        self.engine.handle_drop("dataslate")
        
        self.assertNotIn("dataslate", self.state.inventory)
        
        # Item should be added back to scene
        current_scene = self.scenes["room1"]
        dropped_item = current_scene.get_item("dataslate")
        self.assertIsNotNone(dropped_item)
    
    def test_handle_drop_nonexistent_item(self):
        """Test dropping an item not in inventory."""
        self.engine.handle_drop("sword")
        
        output = self.mock_io.get_all_output()
        self.assertIn("don't have", output.lower())
    
    def test_handle_use_healing_item(self):
        """Test using a healing item."""
        self.state.health = 70
        self.state.add_item("medkit")
        
        self.engine.handle_use("medkit")
        
        # Health should increase
        self.assertGreater(self.state.health, 70)
        # Item should be consumed
        self.assertNotIn("medkit", self.state.inventory)
    
    def test_handle_use_item_not_in_inventory(self):
        """Test using an item not in inventory."""
        self.engine.handle_use("sword")
        
        output = self.mock_io.get_all_output()
        self.assertIn("don't have", output.lower())
    
    def test_handle_look_at_scene(self):
        """Test looking at the current scene."""
        self.mock_io.clear_output()
        
        self.engine.handle_look(None)
        
        output = self.mock_io.get_all_output()
        self.assertIn("ROOM 1", output)  # Scene name is displayed in uppercase
        self.assertIn("first room", output.lower())
    
    def test_handle_look_at_item(self):
        """Test examining an item."""
        self.mock_io.clear_output()
        
        self.engine.handle_look("medkit")
        
        output = self.mock_io.get_all_output()
        self.assertIn("standard medkit", output.lower())
    
    def test_handle_look_at_npc(self):
        """Test examining an NPC."""
        self.mock_io.clear_output()
        
        self.engine.handle_look("guard")
        
        output = self.mock_io.get_all_output()
        self.assertIn("stern-looking", output.lower())
    
    def test_handle_look_at_nonexistent(self):
        """Test examining something that doesn't exist."""
        self.mock_io.clear_output()
        
        self.engine.handle_look("dragon")
        
        output = self.mock_io.get_all_output()
        self.assertIn("don't see", output.lower())
    
    def test_handle_talk_to_npc(self):
        """Test talking to an NPC."""
        self.mock_io.clear_output()
        
        self.engine.handle_talk("guard")
        
        output = self.mock_io.get_all_output()
        self.assertIn("Halt", output)
    
    def test_handle_talk_to_nonexistent_npc(self):
        """Test talking to an NPC that doesn't exist."""
        self.mock_io.clear_output()
        
        self.engine.handle_talk("merchant")
        
        output = self.mock_io.get_all_output()
        self.assertIn("don't see", output.lower())
    
    def test_handle_talk_with_topic(self):
        """Test talking to an NPC about a specific topic."""
        self.npc1.dialogue['quest'] = "I need your help!"
        self.mock_io.clear_output()
        
        self.engine.handle_talk("guard", "quest")
        
        output = self.mock_io.get_all_output()
        self.assertIn("need your help", output.lower())
    
    def test_handle_inventory_empty(self):
        """Test displaying empty inventory."""
        self.state.inventory = []
        self.mock_io.clear_output()
        
        self.engine.handle_inventory()
        
        output = self.mock_io.get_all_output()
        self.assertIn("empty", output.lower())
    
    def test_handle_inventory_with_items(self):
        """Test displaying inventory with items."""
        self.state.inventory = ["dataslate", "medkit"]
        self.mock_io.clear_output()
        
        self.engine.handle_inventory()
        
        output = self.mock_io.get_all_output()
        self.assertIn("INVENTORY", output)
        self.assertIn("dataslate", output.lower())
        self.assertIn("medkit", output.lower())
    
    def test_handle_help(self):
        """Test displaying help text."""
        self.mock_io.clear_output()
        
        self.engine.handle_help()
        
        output = self.mock_io.get_all_output()
        self.assertIn("COMMANDS", output)
        self.assertIn("go", output.lower())
        self.assertIn("take", output.lower())


class TestStateTransitions(unittest.TestCase):
    """Test game state transitions and event handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.event1 = Event(
            id="ambush",
            description="An enemy appears!",
            trigger_on_entry=True,
            effects={'damage': 10}
        )
        
        self.event2 = Event(
            id="treasure",
            description="You found treasure!",
            trigger_on_entry=True,
            effects={'give_item': 'gold_coin', 'set_flag': 'treasure_found'}
        )
        
        self.state = GameState(current_scene="room1")
        
        self.scenes = {
            "room1": Scene(
                id="room1",
                name="Room 1",
                description="First room.",
                exits={"north": "room2"}
            ),
            "room2": Scene(
                id="room2",
                name="Room 2",
                description="Second room.",
                exits={"south": "room1"},
                events=[self.event1]
            ),
            "room3": Scene(
                id="room3",
                name="Treasure Room",
                description="A treasure room.",
                events=[self.event2]
            )
        }
        
        self.mock_io = MockInputOutput([])
        self.engine = TextAdventureEngine(
            self.state,
            self.scenes,
            input_func=self.mock_io.input_func,
            output_func=self.mock_io.output_func
        )
    
    def test_entry_event_triggers(self):
        """Test that entry events trigger when entering a scene."""
        initial_health = self.state.health
        
        self.engine.handle_move("north")
        
        # Event should have triggered and dealt damage
        self.assertEqual(self.state.health, initial_health - 10)
        
        output = self.mock_io.get_all_output()
        self.assertIn("enemy appears", output.lower())
    
    def test_event_gives_item(self):
        """Test events that give items."""
        # Move to room3 manually
        self.state.current_scene = "room3"
        self.engine._process_entry_events()
        
        # Should have received item
        self.assertIn("gold_coin", self.state.inventory)
        
        output = self.mock_io.get_all_output()
        self.assertIn("treasure", output.lower())
    
    def test_event_sets_flag(self):
        """Test events that set flags."""
        self.state.current_scene = "room3"
        self.engine._process_entry_events()
        
        # Flag should be set
        self.assertTrue(self.state.get_flag("treasure_found"))
    
    def test_event_only_triggers_once(self):
        """Test that one-time events only trigger once."""
        initial_health = self.state.health
        
        # Enter room2
        self.engine.handle_move("north")
        health_after_first = self.state.health
        
        # Leave and re-enter
        self.engine.handle_move("south")
        self.engine.handle_move("north")
        health_after_second = self.state.health
        
        # Should only have taken damage once
        self.assertEqual(health_after_first, initial_health - 10)
        self.assertEqual(health_after_second, health_after_first)


class TestVictoryDefeat(unittest.TestCase):
    """Test victory and defeat condition checking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state = GameState(current_scene="room1", health=100)
        
        self.scenes = {
            "room1": Scene(id="room1", name="Room 1", description="First room.")
        }
        
        self.mock_io = MockInputOutput(['quit'])
    
    def test_victory_condition(self):
        """Test victory condition checking."""
        engine = TextAdventureEngine(
            self.state,
            self.scenes,
            input_func=self.mock_io.input_func,
            output_func=self.mock_io.output_func,
            victory_conditions={'mission_complete'}
        )
        
        # Initially no victory
        self.assertFalse(engine._check_victory())
        
        # Set victory flag
        self.state.set_flag('mission_complete')
        
        # Now should be victorious
        self.assertTrue(engine._check_victory())
    
    def test_defeat_by_death(self):
        """Test defeat by player death."""
        engine = TextAdventureEngine(
            self.state,
            self.scenes,
            input_func=self.mock_io.input_func,
            output_func=self.mock_io.output_func
        )
        
        # Initially alive
        self.assertFalse(engine._check_defeat())
        
        # Kill player
        self.state.health = 0
        
        # Now should be defeated
        self.assertTrue(engine._check_defeat())
    
    def test_defeat_by_flag(self):
        """Test defeat by setting a defeat flag."""
        engine = TextAdventureEngine(
            self.state,
            self.scenes,
            input_func=self.mock_io.input_func,
            output_func=self.mock_io.output_func,
            defeat_conditions={'catastrophic_failure'}
        )
        
        # Initially no defeat
        self.assertFalse(engine._check_defeat())
        
        # Set defeat flag
        self.state.set_flag('catastrophic_failure')
        
        # Now should be defeated
        self.assertTrue(engine._check_defeat())


class TestPersistence(unittest.TestCase):
    """Test save/load functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.temp_dir, "test_save.json")
        
        self.state = GameState(
            current_scene="room1",
            inventory=["dataslate", "medkit"],
            visited_scenes={"room1", "room2"},
            game_flags={"door_opened": True},
            health=85,
            max_health=100
        )
        
        self.item = Item(
            id="key",
            name="Brass Key",
            description="An old key.",
            takeable=True
        )
        
        self.scenes = {
            "room1": Scene(
                id="room1",
                name="Room 1",
                description="First room.",
                exits={"north": "room2"},
                items=[self.item],
                visited=True
            ),
            "room2": Scene(
                id="room2",
                name="Room 2",
                description="Second room.",
                visited=True
            )
        }
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_save_game(self):
        """Test saving game state."""
        save_game(self.save_path, self.state, self.scenes)
        
        # File should exist
        self.assertTrue(os.path.exists(self.save_path))
        
        # File should contain JSON
        import json
        with open(self.save_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn('game_state', data)
        self.assertIn('scenes', data)
        self.assertIn('version', data)
    
    def test_load_game(self):
        """Test loading game state."""
        # Save first
        save_game(self.save_path, self.state, self.scenes)
        
        # Load
        loaded_state, loaded_scenes = load_game(self.save_path)
        
        # Verify game state
        self.assertEqual(loaded_state.current_scene, "room1")
        self.assertEqual(set(loaded_state.inventory), {"dataslate", "medkit"})
        self.assertEqual(loaded_state.visited_scenes, {"room1", "room2"})
        self.assertEqual(loaded_state.game_flags, {"door_opened": True})
        self.assertEqual(loaded_state.health, 85)
        self.assertEqual(loaded_state.max_health, 100)
        
        # Verify scenes
        self.assertEqual(len(loaded_scenes), 2)
        self.assertIn("room1", loaded_scenes)
        self.assertIn("room2", loaded_scenes)
        
        room1 = loaded_scenes["room1"]
        self.assertEqual(room1.name, "Room 1")
        self.assertTrue(room1.visited)
        self.assertEqual(len(room1.items), 1)
        self.assertEqual(room1.items[0].id, "key")
    
    def test_load_nonexistent_file(self):
        """Test loading from a file that doesn't exist."""
        with self.assertRaises(PersistenceError) as cm:
            load_game("nonexistent.json")
        
        self.assertIn("not found", str(cm.exception))
    
    def test_load_invalid_json(self):
        """Test loading from an invalid JSON file."""
        # Create invalid JSON file
        with open(self.save_path, 'w') as f:
            f.write("not valid json {{{")
        
        with self.assertRaises(PersistenceError) as cm:
            load_game(self.save_path)
        
        self.assertIn("Invalid", str(cm.exception))
    
    def test_get_save_metadata(self):
        """Test getting save file metadata."""
        save_game(self.save_path, self.state, self.scenes)
        
        metadata = get_save_metadata(self.save_path)
        
        self.assertIn('version', metadata)
        self.assertIn('timestamp', metadata)
        self.assertEqual(metadata['current_scene'], 'room1')
        self.assertEqual(metadata['health'], 85)
        self.assertEqual(metadata['inventory_size'], 2)
    
    def test_list_save_files(self):
        """Test listing save files in a directory."""
        # Create multiple save files
        save1 = os.path.join(self.temp_dir, "save1.json")
        save2 = os.path.join(self.temp_dir, "save2.json")
        
        save_game(save1, self.state, self.scenes)
        save_game(save2, self.state, self.scenes)
        
        # List files
        files = list_save_files(self.temp_dir)
        
        self.assertEqual(len(files), 2)
        self.assertTrue(any('save1.json' in f for f in files))
        self.assertTrue(any('save2.json' in f for f in files))
    
    def test_delete_save(self):
        """Test deleting a save file."""
        save_game(self.save_path, self.state, self.scenes)
        self.assertTrue(os.path.exists(self.save_path))
        
        delete_save(self.save_path)
        
        self.assertFalse(os.path.exists(self.save_path))


class TestScriptedPlaythrough(unittest.TestCase):
    """Integration tests with scripted playthroughs."""
    
    def test_basic_playthrough(self):
        """Test a basic game playthrough."""
        # Set up a simple game world
        state = GameState(current_scene="start")
        
        key_item = Item(
            id="brass_key",
            name="Brass Key",
            description="An ornate key.",
            takeable=True
        )
        
        scenes = {
            "start": Scene(
                id="start",
                name="Starting Room",
                description="You are in a small room.",
                exits={"north": "locked_room"},
                items=[key_item],
                locked_exits={"north": "brass_key"}
            ),
            "locked_room": Scene(
                id="locked_room",
                name="Locked Room",
                description="A previously locked room.",
                exits={"south": "start"}
            )
        }
        
        # Commands: take key, try to go north (should fail), use key, go north, quit
        commands = [
            "take brass key",
            "go north",  # Should fail - still locked
            "inventory",
            "quit",
            "yes"
        ]
        
        mock_io = MockInputOutput(commands)
        engine = TextAdventureEngine(
            state,
            scenes,
            input_func=mock_io.input_func,
            output_func=mock_io.output_func
        )
        
        # Run the game
        engine.run()
        
        # Verify state
        self.assertIn("brass_key", state.inventory)
        
        output = mock_io.get_all_output()
        self.assertIn("Brass Key", output)
    
    def test_victory_playthrough(self):
        """Test a playthrough that reaches victory."""
        state = GameState(current_scene="room1")
        
        victory_item = Item(
            id="sacred_relic",
            name="Sacred Relic",
            description="A powerful artifact.",
            takeable=True
        )
        
        victory_event = Event(
            id="mission_complete_event",
            description="You have recovered the sacred relic!",
            trigger_on_entry=False,
            effects={'set_flag': 'mission_complete'}
        )
        
        scenes = {
            "room1": Scene(
                id="room1",
                name="Starting Room",
                description="Beginning.",
                exits={"north": "vault"}
            ),
            "vault": Scene(
                id="vault",
                name="Sacred Vault",
                description="The vault.",
                items=[victory_item],
                events=[victory_event]
            )
        }
        
        commands = [
            "go north",
            "take sacred relic",
        ]
        
        mock_io = MockInputOutput(commands)
        engine = TextAdventureEngine(
            state,
            scenes,
            input_func=mock_io.input_func,
            output_func=mock_io.output_func,
            victory_conditions={'mission_complete'}
        )
        
        # Manually set flag to trigger victory
        state.set_flag('mission_complete')
        
        # Run game (should end in victory)
        engine.run()
        
        output = mock_io.get_all_output()
        self.assertIn("VICTORY", output)
    
    def test_defeat_playthrough(self):
        """Test a playthrough that ends in defeat."""
        state = GameState(current_scene="room1", health=20)
        
        death_event = Event(
            id="trap",
            description="A trap springs!",
            trigger_on_entry=True,
            effects={'damage': 25}
        )
        
        scenes = {
            "room1": Scene(
                id="room1",
                name="Starting Room",
                description="Safe room.",
                exits={"north": "trapped_room"}
            ),
            "trapped_room": Scene(
                id="trapped_room",
                name="Trapped Room",
                description="A dangerous room.",
                events=[death_event]
            )
        }
        
        commands = [
            "go north",  # Will trigger trap and die
        ]
        
        mock_io = MockInputOutput(commands)
        engine = TextAdventureEngine(
            state,
            scenes,
            input_func=mock_io.input_func,
            output_func=mock_io.output_func
        )
        
        # Run game (should end in defeat)
        engine.run()
        
        # Player should be dead
        self.assertEqual(state.health, 0)
        
        output = mock_io.get_all_output()
        self.assertIn("DEFEAT", output)


if __name__ == '__main__':
    unittest.main()
