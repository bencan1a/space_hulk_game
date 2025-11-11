"""
Unit tests for the command parser and action classes.

Tests the CommandParser class and all Action subclasses to ensure they
work correctly and handle various command formats, edge cases, and typos.
"""

import unittest

from space_hulk_game.engine import (
    NPC,
    Action,
    CommandParser,
    DropAction,
    GameState,
    HelpAction,
    InventoryAction,
    Item,
    LookAction,
    MoveAction,
    Scene,
    TakeAction,
    TalkAction,
    UnknownAction,
    UseAction,
)


class TestActionClasses(unittest.TestCase):
    """Test cases for Action classes."""

    def test_action_base_class(self):
        """Test the base Action class."""
        action = Action(raw_command="test")
        self.assertEqual(action.raw_command, "test")
        self.assertEqual(str(action), "Action()")

    def test_action_immutability(self):
        """Test that Action objects are immutable."""
        action = Action(raw_command="test")
        with self.assertRaises(Exception):  # FrozenInstanceError
            action.raw_command = "changed"

    def test_move_action(self):
        """Test MoveAction creation."""
        action = MoveAction(direction="north", raw_command="go north")
        self.assertEqual(action.direction, "north")
        self.assertEqual(action.raw_command, "go north")
        self.assertEqual(str(action), "MoveAction(direction='north')")

    def test_take_action(self):
        """Test TakeAction creation."""
        action = TakeAction(item_id="medkit", raw_command="take medkit")
        self.assertEqual(action.item_id, "medkit")
        self.assertEqual(action.raw_command, "take medkit")
        self.assertEqual(str(action), "TakeAction(item_id='medkit')")

    def test_drop_action(self):
        """Test DropAction creation."""
        action = DropAction(item_id="sword", raw_command="drop sword")
        self.assertEqual(action.item_id, "sword")
        self.assertEqual(str(action), "DropAction(item_id='sword')")

    def test_use_action_without_target(self):
        """Test UseAction without a target."""
        action = UseAction(item_id="medkit", raw_command="use medkit")
        self.assertEqual(action.item_id, "medkit")
        self.assertIsNone(action.target_id)
        self.assertEqual(str(action), "UseAction(item_id='medkit')")

    def test_use_action_with_target(self):
        """Test UseAction with a target."""
        action = UseAction(item_id="key", target_id="door", raw_command="use key on door")
        self.assertEqual(action.item_id, "key")
        self.assertEqual(action.target_id, "door")
        self.assertEqual(str(action), "UseAction(item_id='key', target_id='door')")

    def test_look_action_no_target(self):
        """Test LookAction without a target."""
        action = LookAction(raw_command="look")
        self.assertIsNone(action.target)
        self.assertEqual(str(action), "LookAction()")

    def test_look_action_with_target(self):
        """Test LookAction with a target."""
        action = LookAction(target="console", raw_command="examine console")
        self.assertEqual(action.target, "console")
        self.assertEqual(str(action), "LookAction(target='console')")

    def test_inventory_action(self):
        """Test InventoryAction creation."""
        action = InventoryAction(raw_command="inventory")
        self.assertEqual(str(action), "InventoryAction()")

    def test_talk_action_no_topic(self):
        """Test TalkAction without a topic."""
        action = TalkAction(npc_id="guard", raw_command="talk to guard")
        self.assertEqual(action.npc_id, "guard")
        self.assertIsNone(action.topic)
        self.assertEqual(str(action), "TalkAction(npc_id='guard')")

    def test_talk_action_with_topic(self):
        """Test TalkAction with a topic."""
        action = TalkAction(npc_id="guard", topic="quest", raw_command="ask guard about quest")
        self.assertEqual(action.npc_id, "guard")
        self.assertEqual(action.topic, "quest")
        self.assertEqual(str(action), "TalkAction(npc_id='guard', topic='quest')")

    def test_help_action(self):
        """Test HelpAction creation."""
        action = HelpAction(raw_command="help")
        self.assertEqual(str(action), "HelpAction()")

    def test_unknown_action_no_suggestion(self):
        """Test UnknownAction without a suggestion."""
        action = UnknownAction(raw_command="xyz")
        self.assertEqual(action.raw_command, "xyz")
        self.assertIsNone(action.suggestion)
        self.assertEqual(str(action), "UnknownAction()")

    def test_unknown_action_with_suggestion(self):
        """Test UnknownAction with a suggestion."""
        action = UnknownAction(raw_command="tak", suggestion="take")
        self.assertEqual(action.suggestion, "take")
        self.assertEqual(str(action), "UnknownAction(suggestion='take')")


class TestCommandParserBasic(unittest.TestCase):
    """Test basic command parsing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_parser_initialization(self):
        """Test that parser initializes correctly."""
        parser = CommandParser()
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser.COMMANDS, dict)
        self.assertEqual(parser.CUTOFF, 0.6)

    def test_empty_command(self):
        """Test parsing empty command."""
        action = self.parser.parse("")
        self.assertIsInstance(action, UnknownAction)
        self.assertEqual(action.raw_command, "")

    def test_whitespace_command(self):
        """Test parsing whitespace-only command."""
        action = self.parser.parse("   ")
        self.assertIsInstance(action, UnknownAction)

    def test_unknown_command(self):
        """Test parsing unknown command."""
        action = self.parser.parse("xyz123")
        self.assertIsInstance(action, UnknownAction)
        self.assertEqual(action.raw_command, "xyz123")


class TestCommandParserMove(unittest.TestCase):
    """Test movement command parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_move_north(self):
        """Test 'go north' command."""
        action = self.parser.parse("go north")
        self.assertIsInstance(action, MoveAction)
        self.assertEqual(action.direction, "north")

    def test_move_synonyms(self):
        """Test various movement command synonyms."""
        commands = [
            "walk south",
            "run east",
            "move west",
            "travel up",
            "head down",
        ]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, MoveAction, f"Failed for: {cmd}")

    def test_move_no_direction(self):
        """Test move command without direction."""
        action = self.parser.parse("go")
        self.assertIsInstance(action, UnknownAction)

    def test_move_with_scene_context(self):
        """Test move command with scene context."""
        scene = Scene(
            id="room",
            name="Room",
            description="A room.",
            exits={"north": "hallway", "east": "closet"},
        )

        action = self.parser.parse("go north", current_scene=scene)
        self.assertIsInstance(action, MoveAction)
        self.assertEqual(action.direction, "north")

    def test_move_fuzzy_match_with_context(self):
        """Test fuzzy matching for movement with scene context."""
        scene = Scene(
            id="room",
            name="Room",
            description="A room.",
            exits={"north": "hallway", "southwest": "exit"},
        )

        # Test typo in direction
        action = self.parser.parse("go nrth", current_scene=scene)
        self.assertIsInstance(action, MoveAction)
        self.assertEqual(action.direction, "north")


class TestCommandParserTake(unittest.TestCase):
    """Test take command parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_take_item(self):
        """Test 'take medkit' command."""
        action = self.parser.parse("take medkit")
        self.assertIsInstance(action, TakeAction)
        self.assertEqual(action.item_id, "medkit")

    def test_take_synonyms(self):
        """Test various take command synonyms."""
        commands = [
            "get key",
            "grab sword",
            "pick flashlight",
            "pickup dataslate",
        ]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, TakeAction, f"Failed for: {cmd}")

    def test_take_multi_word_item(self):
        """Test taking item with multi-word name."""
        action = self.parser.parse("take medical kit")
        self.assertIsInstance(action, TakeAction)
        self.assertEqual(action.item_id, "medical kit")

    def test_take_no_item(self):
        """Test take command without item."""
        action = self.parser.parse("take")
        self.assertIsInstance(action, UnknownAction)

    def test_take_with_scene_context(self):
        """Test take command with scene context."""
        medkit = Item(
            id="medkit_01", name="Medical Kit", description="A medical kit.", takeable=True
        )
        scene = Scene(id="room", name="Room", description="A room.", items=[medkit])

        action = self.parser.parse("take medical kit", current_scene=scene)
        self.assertIsInstance(action, TakeAction)
        self.assertEqual(action.item_id, "medkit_01")

    def test_take_fuzzy_match_with_context(self):
        """Test fuzzy matching for take with scene context."""
        medkit = Item(id="medkit", name="Medical Kit", description="A medical kit.", takeable=True)
        scene = Scene(id="room", name="Room", description="A room.", items=[medkit])

        # Test typo in item name
        action = self.parser.parse("take medkt", current_scene=scene)
        self.assertIsInstance(action, TakeAction)
        self.assertEqual(action.item_id, "medkit")


class TestCommandParserDrop(unittest.TestCase):
    """Test drop command parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_drop_item(self):
        """Test 'drop sword' command."""
        action = self.parser.parse("drop sword")
        self.assertIsInstance(action, DropAction)
        self.assertEqual(action.item_id, "sword")

    def test_drop_synonyms(self):
        """Test various drop command synonyms."""
        commands = [
            "drop key",
            "leave flashlight",
            "discard dataslate",
        ]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, DropAction, f"Failed for: {cmd}")

    def test_drop_no_item(self):
        """Test drop command without item."""
        action = self.parser.parse("drop")
        self.assertIsInstance(action, UnknownAction)

    def test_drop_with_game_state(self):
        """Test drop command with game state context."""
        state = GameState(current_scene="room", inventory=["medkit", "sword", "key"])

        action = self.parser.parse("drop sword", game_state=state)
        self.assertIsInstance(action, DropAction)
        self.assertEqual(action.item_id, "sword")

    def test_drop_fuzzy_match_with_context(self):
        """Test fuzzy matching for drop with game state."""
        state = GameState(current_scene="room", inventory=["medkit"])

        # Test typo in item name
        action = self.parser.parse("drop medkt", game_state=state)
        self.assertIsInstance(action, DropAction)
        self.assertEqual(action.item_id, "medkit")


class TestCommandParserUse(unittest.TestCase):
    """Test use command parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_use_item(self):
        """Test 'use medkit' command."""
        action = self.parser.parse("use medkit")
        self.assertIsInstance(action, UseAction)
        self.assertEqual(action.item_id, "medkit")
        self.assertIsNone(action.target_id)

    def test_use_item_on_target(self):
        """Test 'use key on door' command."""
        action = self.parser.parse("use key on door")
        self.assertIsInstance(action, UseAction)
        self.assertEqual(action.item_id, "key")
        self.assertEqual(action.target_id, "door")

    def test_use_item_with_target(self):
        """Test 'use rope with hook' command."""
        action = self.parser.parse("use rope with hook")
        self.assertIsInstance(action, UseAction)
        self.assertEqual(action.item_id, "rope")
        self.assertEqual(action.target_id, "hook")

    def test_use_synonyms(self):
        """Test various use command synonyms."""
        commands = [
            "activate console",
            "apply bandage",
            "engage thruster",
        ]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, UseAction, f"Failed for: {cmd}")

    def test_use_no_item(self):
        """Test use command without item."""
        action = self.parser.parse("use")
        self.assertIsInstance(action, UnknownAction)

    def test_use_with_context(self):
        """Test use command with game state and scene context."""
        state = GameState(current_scene="room", inventory=["brass_key"])

        door = Item(id="vault_door", name="Vault Door", description="A heavy door.", takeable=False)
        scene = Scene(id="room", name="Room", description="A room.", items=[door])

        action = self.parser.parse(
            "use brass key on vault door", game_state=state, current_scene=scene
        )
        self.assertIsInstance(action, UseAction)
        self.assertEqual(action.item_id, "brass_key")
        self.assertEqual(action.target_id, "vault_door")


class TestCommandParserLook(unittest.TestCase):
    """Test look/examine command parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_look(self):
        """Test simple 'look' command."""
        action = self.parser.parse("look")
        self.assertIsInstance(action, LookAction)
        self.assertIsNone(action.target)

    def test_look_at_object(self):
        """Test 'look at console' command."""
        action = self.parser.parse("look at console")
        self.assertIsInstance(action, LookAction)
        self.assertEqual(action.target, "console")

    def test_examine_object(self):
        """Test 'examine console' command."""
        action = self.parser.parse("examine console")
        self.assertIsInstance(action, LookAction)
        self.assertEqual(action.target, "console")

    def test_look_synonyms(self):
        """Test various look command synonyms."""
        commands = [
            "inspect key",
            "check door",
            "observe npc",
            "x console",
            "l",
        ]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, LookAction, f"Failed for: {cmd}")

    def test_look_with_articles(self):
        """Test look command with articles."""
        action = self.parser.parse("look at the console")
        self.assertIsInstance(action, LookAction)
        self.assertEqual(action.target, "console")

    def test_look_with_scene_context(self):
        """Test look command with scene context."""
        console = Item(
            id="control_console", name="Control Console", description="A console.", takeable=False
        )
        scene = Scene(id="room", name="Room", description="A room.", items=[console])

        action = self.parser.parse("examine control console", current_scene=scene)
        self.assertIsInstance(action, LookAction)
        self.assertEqual(action.target, "control_console")


class TestCommandParserInventory(unittest.TestCase):
    """Test inventory command parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_inventory(self):
        """Test 'inventory' command."""
        action = self.parser.parse("inventory")
        self.assertIsInstance(action, InventoryAction)

    def test_inventory_synonyms(self):
        """Test various inventory command synonyms."""
        commands = ["inv", "i", "items", "possessions"]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, InventoryAction, f"Failed for: {cmd}")


class TestCommandParserTalk(unittest.TestCase):
    """Test talk command parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_talk_to_npc(self):
        """Test 'talk to guard' command."""
        action = self.parser.parse("talk to guard")
        self.assertIsInstance(action, TalkAction)
        self.assertEqual(action.npc_id, "guard")
        self.assertIsNone(action.topic)

    def test_talk_synonyms(self):
        """Test various talk command synonyms."""
        commands = [
            "speak to merchant",
            "chat with guard",
            "converse with npc",
        ]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, TalkAction, f"Failed for: {cmd}")

    def test_ask_about_topic(self):
        """Test 'ask guard about quest' command."""
        action = self.parser.parse("ask guard about quest")
        self.assertIsInstance(action, TalkAction)
        self.assertEqual(action.npc_id, "guard")
        self.assertEqual(action.topic, "quest")

    def test_talk_no_npc(self):
        """Test talk command without NPC."""
        action = self.parser.parse("talk")
        self.assertIsInstance(action, UnknownAction)

    def test_talk_with_scene_context(self):
        """Test talk command with scene context."""
        guard = NPC(
            id="imperial_guard",
            name="Imperial Guard",
            description="A stern guard.",
            dialogue={"greeting": "Halt!"},
        )
        scene = Scene(id="room", name="Room", description="A room.", npcs=[guard])

        action = self.parser.parse("talk to imperial guard", current_scene=scene)
        self.assertIsInstance(action, TalkAction)
        self.assertEqual(action.npc_id, "imperial_guard")

    def test_talk_fuzzy_match_with_context(self):
        """Test fuzzy matching for talk with scene context."""
        guard = NPC(id="guard", name="Guard", description="A guard.", dialogue={})
        scene = Scene(id="room", name="Room", description="A room.", npcs=[guard])

        # Test typo in NPC name
        action = self.parser.parse("talk to gard", current_scene=scene)
        self.assertIsInstance(action, TalkAction)
        self.assertEqual(action.npc_id, "guard")


class TestCommandParserHelp(unittest.TestCase):
    """Test help command parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_help(self):
        """Test 'help' command."""
        action = self.parser.parse("help")
        self.assertIsInstance(action, HelpAction)

    def test_help_synonyms(self):
        """Test various help command synonyms."""
        commands = ["h", "?", "commands"]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, HelpAction, f"Failed for: {cmd}")


class TestCommandParserFuzzyMatching(unittest.TestCase):
    """Test fuzzy matching for typos."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_fuzzy_match_command_word(self):
        """Test fuzzy matching on command word."""
        # "tak" should match "take"
        action = self.parser.parse("tak medkit")
        self.assertIsInstance(action, TakeAction)

    def test_fuzzy_match_with_low_cutoff(self):
        """Test that very different words don't match."""
        action = self.parser.parse("xyz medkit")
        self.assertIsInstance(action, UnknownAction)

    def test_suggestion_for_unknown_command(self):
        """Test that fuzzy matching auto-corrects close matches."""
        # "examne" is close enough to "examine" that we auto-correct it
        action = self.parser.parse("examne")
        self.assertIsInstance(action, LookAction)  # examine is a look synonym

        # Very different words should still be unknown with suggestions
        action2 = self.parser.parse("exzzz")
        self.assertIsInstance(action2, UnknownAction)
        # May or may not have a suggestion depending on how different

    def test_multi_word_command_fuzzy_match(self):
        """Test fuzzy matching for multi-word commands."""
        # "pik up" should match "pick up"
        action = self.parser.parse("pickup medkit")
        self.assertIsInstance(action, TakeAction)


class TestCommandParserEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_case_insensitive(self):
        """Test that parsing is case-insensitive."""
        commands = [
            "GO NORTH",
            "Go North",
            "go north",
            "gO NoRtH",
        ]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, MoveAction, f"Failed for: {cmd}")
            self.assertEqual(action.direction, "north")

    def test_extra_whitespace(self):
        """Test handling of extra whitespace."""
        action = self.parser.parse("  go    north  ")
        self.assertIsInstance(action, MoveAction)
        self.assertEqual(action.direction, "north")

    def test_command_with_punctuation(self):
        """Test commands with punctuation."""
        action = self.parser.parse("help!")
        # Should still work (punctuation will be part of token)
        self.assertIsInstance(action, (HelpAction, UnknownAction))

    def test_very_long_command(self):
        """Test very long command."""
        long_item = "this is a very long item name with many words"
        action = self.parser.parse(f"take {long_item}")
        self.assertIsInstance(action, TakeAction)
        self.assertEqual(action.item_id, long_item)

    def test_tokenize_method(self):
        """Test the tokenize method directly."""
        tokens = self.parser._tokenize("go north quickly")
        self.assertEqual(tokens, ["go", "north", "quickly"])

        tokens = self.parser._tokenize("  multiple   spaces  ")
        self.assertEqual(tokens, ["multiple", "spaces"])

    def test_identify_command_method(self):
        """Test the identify_command method directly."""
        action_type, word, remaining = self.parser._identify_command(["go", "north"])
        self.assertEqual(action_type, "move")
        self.assertEqual(word, "go")
        self.assertEqual(remaining, ["north"])

        action_type, word, remaining = self.parser._identify_command(["xyz", "abc"])
        self.assertIsNone(action_type)
        self.assertEqual(word, "xyz")

    def test_suggest_command_method(self):
        """Test the suggest_command method directly."""
        suggestion = self.parser._suggest_command("tak")
        self.assertIsNotNone(suggestion)
        self.assertIn(suggestion, ["take", "talk"])

        suggestion = self.parser._suggest_command("examne")
        self.assertEqual(suggestion, "examine")


class TestCommandParserIntegration(unittest.TestCase):
    """Integration tests with full game context."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

        # Create a rich game context
        self.medkit = Item(
            id="medkit_01",
            name="Medical Kit",
            description="A medical kit.",
            takeable=True,
            useable=True,
        )

        self.key = Item(
            id="brass_key",
            name="Brass Key",
            description="An ornate key.",
            takeable=True,
            useable=True,
        )

        self.console = Item(
            id="control_console",
            name="Control Console",
            description="A complex console.",
            takeable=False,
            useable=True,
        )

        self.guard = NPC(
            id="imperial_guard",
            name="Imperial Guard",
            description="A stern guard.",
            dialogue={"greeting": "Halt!"},
        )

        self.scene = Scene(
            id="entrance",
            name="Entrance Hall",
            description="A grand entrance.",
            exits={"north": "corridor", "east": "armory"},
            items=[self.medkit, self.console],
            npcs=[self.guard],
        )

        self.state = GameState(
            current_scene="entrance",
            inventory=["brass_key", "flashlight"],
            visited_scenes={"entrance"},
            health=80,
        )

    def test_move_with_full_context(self):
        """Test movement with full game context."""
        action = self.parser.parse("go north", self.state, self.scene)
        self.assertIsInstance(action, MoveAction)
        self.assertEqual(action.direction, "north")

    def test_take_item_from_scene(self):
        """Test taking an item that exists in the scene."""
        action = self.parser.parse("take medical kit", self.state, self.scene)
        self.assertIsInstance(action, TakeAction)
        self.assertEqual(action.item_id, "medkit_01")

    def test_drop_item_from_inventory(self):
        """Test dropping an item from inventory."""
        action = self.parser.parse("drop flashlight", self.state, self.scene)
        self.assertIsInstance(action, DropAction)
        self.assertEqual(action.item_id, "flashlight")

    def test_use_item_from_inventory_on_scene_item(self):
        """Test using an inventory item on a scene item."""
        action = self.parser.parse("use brass key on control console", self.state, self.scene)
        self.assertIsInstance(action, UseAction)
        self.assertEqual(action.item_id, "brass_key")
        self.assertEqual(action.target_id, "control_console")

    def test_examine_scene_item(self):
        """Test examining an item in the scene."""
        action = self.parser.parse("examine control console", self.state, self.scene)
        self.assertIsInstance(action, LookAction)
        self.assertEqual(action.target, "control_console")

    def test_talk_to_npc_in_scene(self):
        """Test talking to an NPC in the scene."""
        action = self.parser.parse("talk to imperial guard", self.state, self.scene)
        self.assertIsInstance(action, TalkAction)
        self.assertEqual(action.npc_id, "imperial_guard")

    def test_multiple_commands_sequence(self):
        """Test parsing multiple commands in sequence."""
        commands = [
            ("look", LookAction),
            ("inventory", InventoryAction),
            ("take medkit", TakeAction),
            ("go north", MoveAction),
            ("talk to guard", TalkAction),
            ("help", HelpAction),
        ]

        for cmd, expected_type in commands:
            action = self.parser.parse(cmd, self.state, self.scene)
            self.assertIsInstance(action, expected_type, f"Failed for: {cmd}")

    def test_typo_correction_with_context(self):
        """Test that typos are corrected when context is available."""
        # Typo in direction
        action = self.parser.parse("go nrth", self.state, self.scene)
        self.assertIsInstance(action, MoveAction)
        self.assertEqual(action.direction, "north")

        # Typo in item name
        action = self.parser.parse("take medcal kit", self.state, self.scene)
        self.assertIsInstance(action, TakeAction)
        self.assertEqual(action.item_id, "medkit_01")

        # Typo in NPC name
        action = self.parser.parse("talk to imperil guard", self.state, self.scene)
        self.assertIsInstance(action, TalkAction)
        self.assertEqual(action.npc_id, "imperial_guard")


class TestCommandParserNaturalLanguage(unittest.TestCase):
    """Test natural language variations."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CommandParser()

    def test_natural_variations_move(self):
        """Test natural language variations for movement."""
        commands = [
            "go north",
            "walk north",
            "run north",
            "move north",
            "travel north",
            "head north",
        ]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, MoveAction, f"Failed for: {cmd}")
            self.assertEqual(action.direction, "north")

    def test_natural_variations_take(self):
        """Test natural language variations for taking items."""
        commands = [
            "take medkit",
            "get medkit",
            "grab medkit",
            "pick medkit",
            "pickup medkit",
        ]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, TakeAction, f"Failed for: {cmd}")

    def test_natural_variations_look(self):
        """Test natural language variations for looking."""
        commands = [
            "look at console",
            "examine console",
            "inspect console",
            "check console",
            "observe console",
        ]

        for cmd in commands:
            action = self.parser.parse(cmd)
            self.assertIsInstance(action, LookAction, f"Failed for: {cmd}")
            self.assertEqual(action.target, "console")


if __name__ == "__main__":
    unittest.main()
