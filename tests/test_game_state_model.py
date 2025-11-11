"""
Unit tests for the game state data models.

Tests the GameState, Scene, Item, NPC, and Event classes to ensure they
work correctly and handle edge cases appropriately.
"""

import unittest

from space_hulk_game.engine import NPC, Event, GameState, Item, Scene


class TestGameState(unittest.TestCase):
    """Test cases for the GameState class."""

    def test_initialization_basic(self):
        """Test basic GameState initialization."""
        state = GameState(
            current_scene="entrance",
            inventory=["flashlight"],
            visited_scenes={"entrance"},
            game_flags={"door_open": True},
            health=80,
            max_health=100,
        )
        self.assertEqual(state.current_scene, "entrance")
        self.assertEqual(state.inventory, ["flashlight"])
        self.assertEqual(state.visited_scenes, {"entrance"})
        self.assertEqual(state.game_flags, {"door_open": True})
        self.assertEqual(state.health, 80)
        self.assertEqual(state.max_health, 100)

    def test_initialization_defaults(self):
        """Test GameState initialization with defaults."""
        state = GameState(current_scene="start")
        self.assertEqual(state.current_scene, "start")
        self.assertEqual(state.inventory, [])
        self.assertEqual(state.visited_scenes, set())
        self.assertEqual(state.game_flags, {})
        self.assertEqual(state.health, 100)
        self.assertEqual(state.max_health, 100)

    def test_validation_negative_health(self):
        """Test that negative health raises ValueError."""
        with self.assertRaises(ValueError):
            GameState(current_scene="test", health=-10)

    def test_validation_zero_max_health(self):
        """Test that zero max_health raises ValueError."""
        with self.assertRaises(ValueError):
            GameState(current_scene="test", max_health=0)

    def test_validation_health_exceeds_max(self):
        """Test that health > max_health raises ValueError."""
        with self.assertRaises(ValueError):
            GameState(current_scene="test", health=150, max_health=100)

    def test_validation_empty_current_scene(self):
        """Test that empty current_scene raises ValueError."""
        with self.assertRaises(ValueError):
            GameState(current_scene="")

    def test_add_item(self):
        """Test adding items to inventory."""
        state = GameState(current_scene="test")
        state.add_item("key")
        self.assertIn("key", state.inventory)

        # Adding same item again should not duplicate
        state.add_item("key")
        self.assertEqual(state.inventory.count("key"), 1)

    def test_remove_item(self):
        """Test removing items from inventory."""
        state = GameState(current_scene="test", inventory=["key", "sword"])

        result = state.remove_item("key")
        self.assertTrue(result)
        self.assertNotIn("key", state.inventory)

        result = state.remove_item("missing")
        self.assertFalse(result)

    def test_has_item(self):
        """Test checking for items in inventory."""
        state = GameState(current_scene="test", inventory=["key"])

        self.assertTrue(state.has_item("key"))
        self.assertFalse(state.has_item("sword"))

    def test_set_flag(self):
        """Test setting game flags."""
        state = GameState(current_scene="test")

        state.set_flag("door_open")
        self.assertTrue(state.game_flags["door_open"])

        state.set_flag("puzzle_solved", False)
        self.assertFalse(state.game_flags["puzzle_solved"])

    def test_get_flag(self):
        """Test getting game flags."""
        state = GameState(current_scene="test")
        state.set_flag("door_open", True)

        self.assertTrue(state.get_flag("door_open"))
        self.assertFalse(state.get_flag("missing_flag", False))
        self.assertTrue(state.get_flag("missing_flag", True))

    def test_visit_scene(self):
        """Test visiting a scene."""
        state = GameState(current_scene="start")

        state.visit_scene("next_room")
        self.assertEqual(state.current_scene, "next_room")
        self.assertIn("next_room", state.visited_scenes)

    def test_has_visited(self):
        """Test checking if a scene has been visited."""
        state = GameState(current_scene="test")
        state.visited_scenes.add("old_room")

        self.assertTrue(state.has_visited("old_room"))
        self.assertFalse(state.has_visited("new_room"))

    def test_take_damage(self):
        """Test taking damage."""
        state = GameState(current_scene="test", health=100)

        state.take_damage(30)
        self.assertEqual(state.health, 70)

        # Damage shouldn't go below 0
        state.take_damage(100)
        self.assertEqual(state.health, 0)

        # Negative damage should raise error
        with self.assertRaises(ValueError):
            state.take_damage(-10)

    def test_heal(self):
        """Test healing."""
        state = GameState(current_scene="test", health=50, max_health=100)

        state.heal(30)
        self.assertEqual(state.health, 80)

        # Healing shouldn't exceed max_health
        state.heal(50)
        self.assertEqual(state.health, 100)

        # Negative healing should raise error
        with self.assertRaises(ValueError):
            state.heal(-10)

    def test_is_alive(self):
        """Test checking if player is alive."""
        state = GameState(current_scene="test", health=50)
        self.assertTrue(state.is_alive())

        state.health = 0
        self.assertFalse(state.is_alive())

    def test_to_dict(self):
        """Test converting GameState to dictionary."""
        state = GameState(
            current_scene="test",
            inventory=["key"],
            visited_scenes={"test", "other"},
            game_flags={"flag1": True},
            health=80,
            max_health=100,
        )

        data = state.to_dict()
        self.assertEqual(data["current_scene"], "test")
        self.assertEqual(data["inventory"], ["key"])
        self.assertIn("test", data["visited_scenes"])
        self.assertEqual(data["game_flags"], {"flag1": True})
        self.assertEqual(data["health"], 80)
        self.assertEqual(data["max_health"], 100)

    def test_from_dict(self):
        """Test creating GameState from dictionary."""
        data = {
            "current_scene": "test",
            "inventory": ["item1"],
            "visited_scenes": ["test", "other"],
            "game_flags": {"flag1": True},
            "health": 80,
            "max_health": 100,
        }

        state = GameState.from_dict(data)
        self.assertEqual(state.current_scene, "test")
        self.assertEqual(state.inventory, ["item1"])
        self.assertIn("test", state.visited_scenes)
        self.assertEqual(state.game_flags, {"flag1": True})
        self.assertEqual(state.health, 80)
        self.assertEqual(state.max_health, 100)


class TestItem(unittest.TestCase):
    """Test cases for the Item class."""

    def test_initialization(self):
        """Test basic Item initialization."""
        item = Item(
            id="key",
            name="Brass Key",
            description="An ornate brass key.",
            takeable=True,
            useable=True,
        )

        self.assertEqual(item.id, "key")
        self.assertEqual(item.name, "Brass Key")
        self.assertTrue(item.takeable)
        self.assertTrue(item.useable)

    def test_validation_empty_id(self):
        """Test that empty id raises ValueError."""
        with self.assertRaises(ValueError):
            Item(id="", name="Test", description="Test")

    def test_validation_empty_name(self):
        """Test that empty name raises ValueError."""
        with self.assertRaises(ValueError):
            Item(id="test", name="", description="Test")

    def test_validation_empty_description(self):
        """Test that empty description raises ValueError."""
        with self.assertRaises(ValueError):
            Item(id="test", name="Test", description="")

    def test_can_use_no_flag_required(self):
        """Test using an item with no flag requirement."""
        item = Item(id="medkit", name="Medkit", description="A medkit.", useable=True)

        self.assertTrue(item.can_use({}))

    def test_can_use_flag_required(self):
        """Test using an item with a flag requirement."""
        item = Item(
            id="console",
            name="Console",
            description="A console.",
            useable=True,
            required_flag="has_access",
        )

        self.assertFalse(item.can_use({}))
        self.assertFalse(item.can_use({"has_access": False}))
        self.assertTrue(item.can_use({"has_access": True}))

    def test_can_use_not_useable(self):
        """Test that non-useable items return False."""
        item = Item(id="decoration", name="Decoration", description="A decoration.", useable=False)

        self.assertFalse(item.can_use({}))

    def test_to_dict(self):
        """Test converting Item to dictionary."""
        item = Item(
            id="key", name="Key", description="A key.", takeable=True, effects={"unlock": "door"}
        )

        data = item.to_dict()
        self.assertEqual(data["id"], "key")
        self.assertEqual(data["name"], "Key")
        self.assertTrue(data["takeable"])
        self.assertEqual(data["effects"], {"unlock": "door"})

    def test_from_dict(self):
        """Test creating Item from dictionary."""
        data = {
            "id": "key",
            "name": "Key",
            "description": "A key.",
            "takeable": True,
            "useable": True,
            "effects": {"unlock": "door"},
        }

        item = Item.from_dict(data)
        self.assertEqual(item.id, "key")
        self.assertEqual(item.name, "Key")
        self.assertTrue(item.takeable)
        self.assertEqual(item.effects, {"unlock": "door"})


class TestNPC(unittest.TestCase):
    """Test cases for the NPC class."""

    def test_initialization(self):
        """Test basic NPC initialization."""
        npc = NPC(
            id="guard",
            name="Imperial Guard",
            description="A stern guard.",
            dialogue={"greeting": "Halt!"},
            hostile=False,
            health=100,
        )

        self.assertEqual(npc.id, "guard")
        self.assertEqual(npc.name, "Imperial Guard")
        self.assertFalse(npc.hostile)
        self.assertEqual(npc.health, 100)

    def test_validation_empty_id(self):
        """Test that empty id raises ValueError."""
        with self.assertRaises(ValueError):
            NPC(id="", name="Test", description="Test")

    def test_validation_empty_name(self):
        """Test that empty name raises ValueError."""
        with self.assertRaises(ValueError):
            NPC(id="test", name="", description="Test")

    def test_validation_empty_description(self):
        """Test that empty description raises ValueError."""
        with self.assertRaises(ValueError):
            NPC(id="test", name="Test", description="")

    def test_validation_negative_health(self):
        """Test that negative health raises ValueError."""
        with self.assertRaises(ValueError):
            NPC(id="test", name="Test", description="Test", health=-10)

    def test_can_interact_no_flag(self):
        """Test interacting with NPC with no flag requirement."""
        npc = NPC(id="test", name="Test", description="Test")
        self.assertTrue(npc.can_interact({}))

    def test_can_interact_with_flag(self):
        """Test interacting with NPC with flag requirement."""
        npc = NPC(id="test", name="Test", description="Test", required_flag="friendly")

        self.assertFalse(npc.can_interact({}))
        self.assertTrue(npc.can_interact({"friendly": True}))

    def test_get_dialogue(self):
        """Test getting dialogue from NPC."""
        npc = NPC(id="test", name="Test", description="Test", dialogue={"hello": "Greetings!"})

        self.assertEqual(npc.get_dialogue("hello"), "Greetings!")
        self.assertEqual(npc.get_dialogue("missing"), "...")
        self.assertEqual(npc.get_dialogue("missing", "default"), "default")

    def test_is_alive(self):
        """Test checking if NPC is alive."""
        npc = NPC(id="test", name="Test", description="Test", health=50)
        self.assertTrue(npc.is_alive())

        npc.health = 0
        self.assertFalse(npc.is_alive())

    def test_to_dict(self):
        """Test converting NPC to dictionary."""
        npc = NPC(
            id="test",
            name="Test",
            description="Test",
            dialogue={"hi": "Hello"},
            hostile=True,
            health=50,
        )

        data = npc.to_dict()
        self.assertEqual(data["id"], "test")
        self.assertEqual(data["dialogue"], {"hi": "Hello"})
        self.assertTrue(data["hostile"])
        self.assertEqual(data["health"], 50)

    def test_from_dict(self):
        """Test creating NPC from dictionary."""
        data = {
            "id": "test",
            "name": "Test",
            "description": "Test",
            "dialogue": {"hi": "Hello"},
            "hostile": True,
            "health": 50,
        }

        npc = NPC.from_dict(data)
        self.assertEqual(npc.id, "test")
        self.assertEqual(npc.dialogue, {"hi": "Hello"})
        self.assertTrue(npc.hostile)
        self.assertEqual(npc.health, 50)


class TestEvent(unittest.TestCase):
    """Test cases for the Event class."""

    def test_initialization(self):
        """Test basic Event initialization."""
        event = Event(id="ambush", description="An ambush!", trigger_on_entry=True, one_time=True)

        self.assertEqual(event.id, "ambush")
        self.assertEqual(event.description, "An ambush!")
        self.assertTrue(event.trigger_on_entry)
        self.assertTrue(event.one_time)
        self.assertFalse(event.triggered)

    def test_validation_empty_id(self):
        """Test that empty id raises ValueError."""
        with self.assertRaises(ValueError):
            Event(id="", description="Test")

    def test_validation_empty_description(self):
        """Test that empty description raises ValueError."""
        with self.assertRaises(ValueError):
            Event(id="test", description="")

    def test_can_trigger_no_flag(self):
        """Test triggering event with no flag requirement."""
        event = Event(id="test", description="Test")
        self.assertTrue(event.can_trigger({}))

    def test_can_trigger_with_flag(self):
        """Test triggering event with flag requirement."""
        event = Event(id="test", description="Test", required_flag="condition_met")

        self.assertFalse(event.can_trigger({}))
        self.assertTrue(event.can_trigger({"condition_met": True}))

    def test_can_trigger_one_time(self):
        """Test one-time event triggering."""
        event = Event(id="test", description="Test", one_time=True)

        self.assertTrue(event.can_trigger({}))

        event.trigger()
        self.assertFalse(event.can_trigger({}))

    def test_can_trigger_repeatable(self):
        """Test repeatable event triggering."""
        event = Event(id="test", description="Test", one_time=False)

        self.assertTrue(event.can_trigger({}))

        event.trigger()
        self.assertTrue(event.can_trigger({}))

    def test_trigger(self):
        """Test triggering an event."""
        event = Event(id="test", description="Test")

        self.assertFalse(event.triggered)
        event.trigger()
        self.assertTrue(event.triggered)

    def test_reset(self):
        """Test resetting an event."""
        event = Event(id="test", description="Test")

        event.trigger()
        self.assertTrue(event.triggered)

        event.reset()
        self.assertFalse(event.triggered)

    def test_to_dict(self):
        """Test converting Event to dictionary."""
        event = Event(id="test", description="Test", trigger_on_entry=True, effects={"damage": 10})
        event.trigger()

        data = event.to_dict()
        self.assertEqual(data["id"], "test")
        self.assertTrue(data["trigger_on_entry"])
        self.assertEqual(data["effects"], {"damage": 10})
        self.assertTrue(data["triggered"])

    def test_from_dict(self):
        """Test creating Event from dictionary."""
        data = {
            "id": "test",
            "description": "Test",
            "trigger_on_entry": True,
            "effects": {"damage": 10},
            "triggered": True,
        }

        event = Event.from_dict(data)
        self.assertEqual(event.id, "test")
        self.assertTrue(event.trigger_on_entry)
        self.assertEqual(event.effects, {"damage": 10})
        self.assertTrue(event.triggered)


class TestScene(unittest.TestCase):
    """Test cases for the Scene class."""

    def test_initialization(self):
        """Test basic Scene initialization."""
        scene = Scene(
            id="entrance",
            name="Entrance Hall",
            description="A grand entrance.",
            exits={"north": "corridor"},
            dark=False,
        )

        self.assertEqual(scene.id, "entrance")
        self.assertEqual(scene.name, "Entrance Hall")
        self.assertEqual(scene.exits, {"north": "corridor"})
        self.assertFalse(scene.dark)
        self.assertFalse(scene.visited)

    def test_validation_empty_id(self):
        """Test that empty id raises ValueError."""
        with self.assertRaises(ValueError):
            Scene(id="", name="Test", description="Test")

    def test_validation_empty_name(self):
        """Test that empty name raises ValueError."""
        with self.assertRaises(ValueError):
            Scene(id="test", name="", description="Test")

    def test_validation_empty_description(self):
        """Test that empty description raises ValueError."""
        with self.assertRaises(ValueError):
            Scene(id="test", name="Test", description="")

    def test_get_full_description(self):
        """Test getting full scene description."""
        item = Item(id="key", name="Brass Key", description="A key.")
        npc = NPC(id="guard", name="Guard", description="A stern guard stands here.")

        scene = Scene(id="room", name="Room", description="A test room.", items=[item], npcs=[npc])

        desc = scene.get_full_description()
        self.assertIn("A test room.", desc)
        self.assertIn("Brass Key", desc)
        self.assertIn("stern guard", desc)

    def test_get_exit_description(self):
        """Test getting exit description."""
        scene1 = Scene(id="room1", name="Room", description="A room.", exits={})
        self.assertIn("no obvious exits", scene1.get_exit_description())

        scene2 = Scene(id="room2", name="Room", description="A room.", exits={"north": "hallway"})
        desc = scene2.get_exit_description()
        self.assertIn("north", desc)

        scene3 = Scene(
            id="room3",
            name="Room",
            description="A room.",
            exits={"north": "hallway", "east": "closet"},
        )
        desc = scene3.get_exit_description()
        self.assertIn("north", desc)
        self.assertIn("east", desc)

    def test_can_exit_valid(self):
        """Test checking valid exits."""
        scene = Scene(id="room", name="Room", description="A room.", exits={"north": "hallway"})

        can_exit, reason = scene.can_exit("north", [], {})
        self.assertTrue(can_exit)
        self.assertIsNone(reason)

    def test_can_exit_invalid_direction(self):
        """Test checking invalid exit direction."""
        scene = Scene(id="room", name="Room", description="A room.", exits={"north": "hallway"})

        can_exit, reason = scene.can_exit("south", [], {})
        self.assertFalse(can_exit)
        self.assertIsNotNone(reason)
        assert reason is not None  # Type narrowing for Pylance
        self.assertIn("no exit", reason)

    def test_can_exit_locked_with_item(self):
        """Test locked exit that requires an item."""
        scene = Scene(
            id="room",
            name="Room",
            description="A room.",
            exits={"north": "vault"},
            locked_exits={"north": "key"},
        )

        # Without key
        can_exit, reason = scene.can_exit("north", [], {})
        self.assertFalse(can_exit)
        self.assertIsNotNone(reason)
        assert reason is not None  # Type narrowing for Pylance
        self.assertIn("locked", reason)

        # With key
        can_exit, reason = scene.can_exit("north", ["key"], {})
        self.assertTrue(can_exit)
        self.assertIsNone(reason)

    def test_can_exit_locked_with_flag(self):
        """Test locked exit that requires a flag."""
        scene = Scene(
            id="room",
            name="Room",
            description="A room.",
            exits={"north": "vault"},
            locked_exits={"north": "door_unlocked"},
        )

        # Without flag
        can_exit, reason = scene.can_exit("north", [], {})
        self.assertFalse(can_exit)

        # With flag
        can_exit, _reason = scene.can_exit("north", [], {"door_unlocked": True})
        self.assertTrue(can_exit)

    def test_get_item(self):
        """Test getting an item from the scene."""
        item = Item(id="key", name="Key", description="A key.")
        scene = Scene(id="room", name="Room", description="A room.", items=[item])

        found = scene.get_item("key")
        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found.name, "Key")

        not_found = scene.get_item("missing")
        self.assertIsNone(not_found)

    def test_remove_item(self):
        """Test removing an item from the scene."""
        item = Item(id="key", name="Key", description="A key.")
        scene = Scene(id="room", name="Room", description="A room.", items=[item])

        result = scene.remove_item("key")
        self.assertTrue(result)
        self.assertEqual(len(scene.items), 0)

        result = scene.remove_item("key")
        self.assertFalse(result)

    def test_add_item(self):
        """Test adding an item to the scene."""
        scene = Scene(id="room", name="Room", description="A room.")
        item = Item(id="key", name="Key", description="A key.")

        scene.add_item(item)
        self.assertEqual(len(scene.items), 1)
        self.assertEqual(scene.items[0].id, "key")

    def test_get_npc(self):
        """Test getting an NPC from the scene."""
        npc = NPC(id="guard", name="Guard", description="A guard.")
        scene = Scene(id="room", name="Room", description="A room.", npcs=[npc])

        found = scene.get_npc("guard")
        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found.name, "Guard")

        not_found = scene.get_npc("missing")
        self.assertIsNone(not_found)

    def test_get_entry_events(self):
        """Test getting entry events."""
        event1 = Event(id="ambush", description="An ambush!", trigger_on_entry=True)
        event2 = Event(id="clue", description="You find a clue.", trigger_on_entry=False)
        event3 = Event(
            id="conditional",
            description="Something happens.",
            trigger_on_entry=True,
            required_flag="condition_met",
        )

        scene = Scene(
            id="room", name="Room", description="A room.", events=[event1, event2, event3]
        )

        # Without flag
        events = scene.get_entry_events({})
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].id, "ambush")

        # With flag
        events = scene.get_entry_events({"condition_met": True})
        self.assertEqual(len(events), 2)

    def test_unlock_exit(self):
        """Test unlocking an exit."""
        scene = Scene(
            id="room",
            name="Room",
            description="A room.",
            exits={"north": "vault"},
            locked_exits={"north": "key"},
        )

        result = scene.unlock_exit("north")
        self.assertTrue(result)
        self.assertNotIn("north", scene.locked_exits)

        result = scene.unlock_exit("north")
        self.assertFalse(result)

    def test_to_dict(self):
        """Test converting Scene to dictionary."""
        item = Item(id="key", name="Key", description="A key.")
        scene = Scene(
            id="room",
            name="Room",
            description="A room.",
            exits={"north": "hallway"},
            items=[item],
            dark=True,
        )

        data = scene.to_dict()
        self.assertEqual(data["id"], "room")
        self.assertEqual(data["exits"], {"north": "hallway"})
        self.assertEqual(len(data["items"]), 1)
        self.assertTrue(data["dark"])

    def test_from_dict(self):
        """Test creating Scene from dictionary."""
        data = {
            "id": "room",
            "name": "Room",
            "description": "A room.",
            "exits": {"north": "hallway"},
            "items": [{"id": "key", "name": "Key", "description": "A key."}],
            "npcs": [],
            "events": [],
            "dark": True,
            "visited": True,
        }

        scene = Scene.from_dict(data)
        self.assertEqual(scene.id, "room")
        self.assertEqual(scene.exits, {"north": "hallway"})
        self.assertEqual(len(scene.items), 1)
        self.assertTrue(scene.dark)
        self.assertTrue(scene.visited)


class TestIntegration(unittest.TestCase):
    """Integration tests for the game state models."""

    def test_complete_game_scenario(self):
        """Test a complete game scenario with all components."""
        # Create game state
        state = GameState(current_scene="entrance")

        # Create items
        key = Item(
            id="brass_key",
            name="Brass Key",
            description="An ornate brass key.",
            takeable=True,
            useable=True,
            effects={"unlock": "vault_door"},
        )

        medkit = Item(
            id="medkit",
            name="Medical Kit",
            description="A medical kit.",
            takeable=True,
            useable=True,
            effects={"heal": 30},
        )

        # Create NPC
        guard = NPC(
            id="guard",
            name="Imperial Guard",
            description="A guard watches the entrance.",
            dialogue={
                "greeting": "Halt! State your business.",
                "help": "The vault key is in the armory.",
            },
            gives_item="brass_key",
        )

        # Create event
        ambush = Event(
            id="ambush",
            description="Enemies attack!",
            trigger_on_entry=True,
            one_time=True,
            effects={"damage": 20},
        )

        # Create scenes
        entrance = Scene(
            id="entrance",
            name="Entrance Hall",
            description="A grand entrance hall.",
            exits={"north": "armory", "vault": "vault"},
            npcs=[guard],
            locked_exits={"vault": "brass_key"},
        )

        armory = Scene(
            id="armory",
            name="Armory",
            description="Weapons line the walls.",
            exits={"south": "entrance"},
            items=[key, medkit],
            events=[ambush],
        )

        # Simulate gameplay
        # 1. Player is at entrance
        self.assertEqual(state.current_scene, "entrance")

        # 2. Player talks to guard
        guard_npc = entrance.get_npc("guard")
        self.assertIsNotNone(guard_npc)
        assert guard_npc is not None  # Type narrowing for Pylance
        greeting = guard_npc.get_dialogue("greeting")
        self.assertIsNotNone(greeting)
        assert greeting is not None  # Type narrowing for Pylance
        self.assertIn("Halt", greeting)

        # 3. Player moves to armory
        state.visit_scene("armory")
        self.assertEqual(state.current_scene, "armory")
        self.assertTrue(state.has_visited("armory"))

        # 4. Entry event triggers (ambush)
        entry_events = armory.get_entry_events({})
        self.assertEqual(len(entry_events), 1)
        event = entry_events[0]
        event.trigger()

        # Apply damage from event
        state.take_damage(event.effects["damage"])
        self.assertEqual(state.health, 80)

        # 5. Player takes items
        key_item = armory.get_item("brass_key")
        self.assertIsNotNone(key_item)
        armory.remove_item("brass_key")
        state.add_item("brass_key")

        medkit_item = armory.get_item("medkit")
        self.assertIsNotNone(medkit_item)
        assert medkit_item is not None
        armory.remove_item("medkit")
        state.add_item("medkit")

        # 6. Player uses medkit
        self.assertTrue(state.has_item("medkit"))
        state.heal(medkit_item.effects["heal"])
        self.assertEqual(state.health, 100)
        state.remove_item("medkit")

        # 7. Player returns to entrance
        state.visit_scene("entrance")

        # 8. Player tries to enter vault
        can_exit, _reason = entrance.can_exit("vault", state.inventory, state.game_flags)
        self.assertTrue(can_exit)

        # Verify complete state
        self.assertEqual(len(state.inventory), 1)
        self.assertEqual(state.inventory[0], "brass_key")
        self.assertEqual(len(state.visited_scenes), 2)
        self.assertTrue(state.is_alive())


if __name__ == "__main__":
    unittest.main()
