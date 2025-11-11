"""
Text Adventure Engine Module

Main game engine for the Space Hulk text-based adventure game.
Handles the game loop, action execution, state transitions, and player I/O.

Example:
    >>> from space_hulk_game.engine import TextAdventureEngine, GameState, Scene
    >>> state = GameState(current_scene="start")
    >>> scenes = {"start": Scene(id="start", name="Start", description="Begin.")}
    >>> engine = TextAdventureEngine(state, scenes)
    >>> # engine.run()  # Start the game loop
"""

import logging
from collections.abc import Callable

from .actions import (
    Action,
    DropAction,
    HelpAction,
    InventoryAction,
    LookAction,
    MoveAction,
    TakeAction,
    TalkAction,
    UnknownAction,
    UseAction,
)
from .entities import Event, Item
from .game_state import GameState
from .parser import CommandParser
from .scene import Scene

# Configure logging
logger = logging.getLogger(__name__)


class TextAdventureEngine:
    """
    Main game engine for text-based adventure games.

    This class implements the core game loop and coordinates all game systems:
    - Command parsing and action execution
    - Scene management and state transitions
    - Event processing and triggering
    - Player input/output
    - Victory/defeat condition checking

    The engine follows the Facade pattern, providing a simple interface
    to the complex subsystems of the game (parser, state, scenes, etc.).

    Attributes:
        game_state: The current game state (player location, inventory, etc.).
        scenes: Dictionary mapping scene IDs to Scene objects.
        parser: CommandParser instance for processing player commands.
        running: Whether the game loop is currently running.
        victory_conditions: Set of game flags that trigger victory.
        defeat_conditions: Set of game flags that trigger defeat.
        input_func: Function for getting player input (for testing).
        output_func: Function for displaying output (for testing).

    Examples:
        Create and run a basic game:
        >>> from space_hulk_game.engine import (
        ...     TextAdventureEngine, GameState, Scene, Item
        ... )
        >>> state = GameState(current_scene="room1")
        >>> scenes = {
        ...     "room1": Scene(
        ...         id="room1",
        ...         name="Starting Room",
        ...         description="A simple room.",
        ...         exits={"north": "room2"}
        ...     ),
        ...     "room2": Scene(
        ...         id="room2",
        ...         name="Second Room",
        ...         description="Another room."
        ...     )
        ... }
        >>> engine = TextAdventureEngine(state, scenes)
        >>> # engine.run()  # Start the interactive game loop
    """

    def __init__(
        self,
        game_state: GameState,
        scenes: dict[str, Scene],
        input_func: Callable[[], str] | None = None,
        output_func: Callable[[str], None] | None = None,
        victory_conditions: set | None = None,
        defeat_conditions: set | None = None,
    ):
        """
        Initialize the text adventure engine.

        Args:
            game_state: Initial game state.
            scenes: Dictionary mapping scene IDs to Scene objects.
            input_func: Optional custom input function (default: input()).
            output_func: Optional custom output function (default: print()).
            victory_conditions: Optional set of flags that trigger victory.
            defeat_conditions: Optional set of flags that trigger defeat.

        Raises:
            ValueError: If current scene is not in scenes dict.
        """
        self.game_state = game_state
        self.scenes = scenes
        self.parser = CommandParser()
        self.running = False

        # I/O functions (allow injection for testing)
        self.input_func = input_func or input
        self.output_func = output_func or print

        # Win/loss conditions
        self.victory_conditions = victory_conditions or set()
        self.defeat_conditions = defeat_conditions or set()

        # Build item registry from all scenes
        self._item_registry: dict[str, Item] = {}
        for scene in scenes.values():
            for item in scene.items:
                self._item_registry[item.id] = item

        # Validate initial state
        if game_state.current_scene not in scenes:
            raise ValueError(f"Initial scene '{game_state.current_scene}' not found in scenes")

        logger.info(f"TextAdventureEngine initialized with {len(scenes)} scenes")

    def run(self) -> None:
        """
        Start the main game loop.

        This method handles:
        1. Initial scene display
        2. Player input collection
        3. Command parsing
        4. Action execution
        5. State updates
        6. Victory/defeat checking

        The loop continues until the player quits, wins, or loses.

        Examples:
            >>> engine = TextAdventureEngine(state, scenes)
            >>> # engine.run()  # Starts interactive game
        """
        self.running = True
        logger.info("Game loop started")

        # Display intro and current scene
        self._display_welcome()
        self._display_current_scene()
        self._process_entry_events()

        # Main game loop
        while self.running:
            try:
                # Check win/loss conditions
                if self._check_victory():
                    self._display_victory()
                    break

                if self._check_defeat():
                    self._display_defeat()
                    break

                # Get player input
                try:
                    command = self.input_func()
                except (EOFError, KeyboardInterrupt):
                    self._output("\n\nGoodbye!")
                    break

                if not command or not command.strip():
                    continue

                # Handle quit commands
                if command.strip().lower() in ["quit", "exit", "q"]:
                    if self._confirm_quit():
                        self._output("\nThanks for playing!")
                        break
                    continue

                # Parse and execute command
                current_scene = self.scenes[self.game_state.current_scene]
                action = self.parser.parse(command, self.game_state, current_scene)

                self._execute_action(action)

            except Exception as e:
                logger.exception("Error in game loop")
                self._output(f"\nAn error occurred: {e}")
                self._output("Please try another command.\n")

        self.running = False
        logger.info("Game loop ended")

    def _execute_action(self, action: Action) -> None:
        """
        Execute a parsed action and update game state.

        Args:
            action: The Action object to execute.
        """
        logger.debug(f"Executing action: {action}")

        # Route to appropriate handler
        if isinstance(action, MoveAction):
            self.handle_move(action.direction)
        elif isinstance(action, TakeAction):
            self.handle_take(action.item_id)
        elif isinstance(action, DropAction):
            self.handle_drop(action.item_id)
        elif isinstance(action, UseAction):
            self.handle_use(action.item_id, action.target_id)
        elif isinstance(action, LookAction):
            self.handle_look(action.target)
        elif isinstance(action, InventoryAction):
            self.handle_inventory()
        elif isinstance(action, TalkAction):
            self.handle_talk(action.npc_id, action.topic)
        elif isinstance(action, HelpAction):
            self.handle_help()
        elif isinstance(action, UnknownAction):
            self._handle_unknown(action)
        else:
            self._output("I don't understand that command.")
            logger.warning(f"Unknown action type: {type(action)}")

    def handle_move(self, direction: str) -> None:
        """
        Handle movement to another scene.

        Args:
            direction: The direction or exit name to move through.
        """
        current_scene = self.scenes[self.game_state.current_scene]

        # Check if exit exists and is accessible
        can_exit, reason = current_scene.can_exit(
            direction, self.game_state.inventory, self.game_state.game_flags
        )

        if not can_exit:
            self._output(f"\n{reason}\n")
            logger.debug(f"Move blocked: {reason}")
            return

        # Get destination scene
        destination_id = current_scene.exits[direction]

        if destination_id not in self.scenes:
            self._output(f"\nError: Destination '{destination_id}' not found.\n")
            logger.error(f"Invalid destination: {destination_id}")
            return

        # Move to new scene
        old_scene_id = self.game_state.current_scene
        self.game_state.visit_scene(destination_id)
        logger.info(f"Moved from {old_scene_id} to {destination_id}")

        # Display new scene
        self._output("")  # Blank line
        self._display_current_scene()

        # Process entry events
        self._process_entry_events()

    def handle_take(self, item_id: str) -> None:
        """
        Handle taking an item from the current scene.

        Args:
            item_id: The ID or name of the item to take.
        """
        current_scene = self.scenes[self.game_state.current_scene]

        # Find the item in the scene
        item = current_scene.get_item(item_id)

        if not item:
            self._output(f"\nYou don't see '{item_id}' here.\n")
            logger.debug(f"Item not found: {item_id}")
            return

        # Check if item is takeable
        if not item.takeable:
            self._output(f"\nYou can't take the {item.name}.\n")
            logger.debug(f"Item not takeable: {item_id}")
            return

        # Add to inventory and remove from scene
        self.game_state.add_item(item.id)
        current_scene.remove_item(item.id)

        # Register item in registry if not already there
        if item.id not in self._item_registry:
            self._item_registry[item.id] = item

        self._output(f"\nYou take the {item.name}.\n")
        logger.info(f"Took item: {item.id}")

    def handle_drop(self, item_id: str) -> None:
        """
        Handle dropping an item from inventory.

        Args:
            item_id: The ID or name of the item to drop.
        """
        if not self.game_state.has_item(item_id):
            self._output(f"\nYou don't have '{item_id}'.\n")
            logger.debug(f"Item not in inventory: {item_id}")
            return

        # Get the item from registry
        item = self._item_registry.get(item_id)
        if item is None:
            # Item not in registry - create a basic item as fallback
            item = Item(
                id=item_id,
                name=item_id.replace("_", " ").title(),
                description=f"A {item_id.replace('_', ' ')}.",
                takeable=True,
            )
            self._item_registry[item_id] = item

        # Remove from inventory
        self.game_state.remove_item(item_id)

        # Add to current scene
        current_scene = self.scenes[self.game_state.current_scene]
        current_scene.add_item(item)

        self._output(f"\nYou drop the {item.name}.\n")
        logger.info(f"Dropped item: {item_id}")

    def handle_use(self, item_id: str, target_id: str | None = None) -> None:
        """
        Handle using an item.

        Args:
            item_id: The ID of the item to use.
            target_id: Optional target for the item.
        """
        # Check if player has the item
        if not self.game_state.has_item(item_id):
            self._output(f"\nYou don't have '{item_id}'.\n")
            logger.debug(f"Item not in inventory: {item_id}")
            return

        # Get the item from registry
        item = self._item_registry.get(item_id)
        if item is None:
            self._output(f"\nYou can't use the {item_id}.\n")
            logger.warning(f"Item not in registry: {item_id}")
            return

        # Check if item is useable
        if not item.useable:
            self._output(f"\nYou can't use the {item.name}.\n")
            logger.debug(f"Item not useable: {item_id}")
            return

        # Check if item has required flag
        if item.required_flag and not self.game_state.get_flag(item.required_flag):
            self._output(f"\nYou can't use the {item.name} right now.\n")
            logger.debug(f"Missing required flag for item: {item.required_flag}")
            return

        # Display use text if available
        if item.use_text:
            self._output(f"\n{item.use_text}\n")

        # Apply item effects
        effects_applied = False

        # Handle healing effect
        if "heal" in item.effects:
            heal_amount = item.effects["heal"]
            self.game_state.heal(heal_amount)
            if not item.use_text:
                self._output(f"\nYou use the {item.name}. You feel better! (+{heal_amount} HP)\n")
            effects_applied = True
            # Remove consumable healing items
            self.game_state.remove_item(item_id)
            logger.info(f"Used healing item: {item_id}, healed {heal_amount} HP")

        # Handle unlock effect
        if "unlock" in item.effects:
            current_scene = self.scenes[self.game_state.current_scene]
            item.effects["unlock"]

            # Try to unlock the specified exit or any locked exit that requires this item
            unlocked = False
            for direction, locked_item in list(current_scene.locked_exits.items()):
                if locked_item == item_id or (target_id and direction == target_id):
                    current_scene.unlock_exit(direction)
                    if not item.use_text:
                        self._output(
                            f"\nYou use the {item.name}. You hear a click as the lock opens.\n"
                        )
                    logger.info(f"Unlocked exit: {direction}")
                    unlocked = True
                    effects_applied = True
                    break

            if not unlocked and not item.use_text:
                self._output(f"\nThe {item.name} doesn't seem to unlock anything here.\n")

        # Handle damage effect
        if "damage" in item.effects:
            damage_amount = item.effects["damage"]
            self.game_state.take_damage(damage_amount)
            if not item.use_text:
                self._output(f"\nYou use the {item.name}. It hurts! (-{damage_amount} HP)\n")
            effects_applied = True
            logger.info(f"Used damaging item: {item_id}, dealt {damage_amount} damage")

        # Handle flag setting effect
        if "set_flag" in item.effects:
            flag_name = item.effects["set_flag"]
            self.game_state.set_flag(flag_name, True)
            if not item.use_text:
                self._output(f"\nYou use the {item.name}.\n")
            effects_applied = True
            logger.info(f"Set flag from item use: {flag_name}")

        # If no effects were applied and no use_text, show generic message
        if not effects_applied and not item.use_text:
            self._output(f"\nYou use the {item.name}. Nothing happens.\n")
            logger.debug(f"Used item with no effects: {item_id}")

    def handle_look(self, target: str | None = None) -> None:
        """
        Handle examining the scene or an object.

        Args:
            target: Optional target to examine. If None, examine scene.
        """
        current_scene = self.scenes[self.game_state.current_scene]

        if not target:
            # Look at the scene
            self._output("")
            self._display_current_scene()
            return

        # Look for item in scene
        item = current_scene.get_item(target)
        if item:
            self._output(f"\n{item.description}\n")
            logger.debug(f"Examined item: {target}")
            return

        # Look for NPC in scene
        npc = current_scene.get_npc(target)
        if npc:
            self._output(f"\n{npc.description}\n")
            logger.debug(f"Examined NPC: {target}")
            return

        # Not found
        self._output(f"\nYou don't see '{target}' here.\n")
        logger.debug(f"Target not found: {target}")

    def handle_talk(self, npc_id: str, topic: str | None = None) -> None:
        """
        Handle talking to an NPC.

        Args:
            npc_id: The ID or name of the NPC to talk to.
            topic: Optional dialogue topic.
        """
        current_scene = self.scenes[self.game_state.current_scene]

        # Find the NPC
        npc = current_scene.get_npc(npc_id)

        if not npc:
            self._output(f"\nYou don't see '{npc_id}' here.\n")
            logger.debug(f"NPC not found: {npc_id}")
            return

        # Check if can interact
        if not npc.can_interact(self.game_state.game_flags):
            self._output(f"\nThe {npc.name} doesn't want to talk right now.\n")
            logger.debug(f"Cannot interact with NPC: {npc_id}")
            return

        # Get dialogue
        if topic:
            dialogue = npc.get_dialogue(topic, f"The {npc.name} has nothing to say about that.")
        else:
            # Try default greetings
            dialogue = npc.get_dialogue("greeting", None)
            if not dialogue:
                dialogue = npc.get_dialogue("default", f"The {npc.name} nods at you.")

        self._output(f'\n{npc.name}: "{dialogue}"\n')

        # Give item if configured
        if npc.gives_item and not self.game_state.has_item(npc.gives_item):
            self.game_state.add_item(npc.gives_item)
            self._output(f"The {npc.name} gives you: {npc.gives_item}\n")
            logger.info(f"Received item from NPC: {npc.gives_item}")

        logger.debug(f"Talked to NPC: {npc_id}, topic: {topic}")

    def handle_inventory(self) -> None:
        """
        Display the player's inventory.
        """
        if not self.game_state.inventory:
            self._output("\nYour inventory is empty.\n")
            return

        self._output("\n=== INVENTORY ===")
        for item_id in self.game_state.inventory:
            # Format item name nicely
            item_name = item_id.replace("_", " ").title()
            self._output(f"  - {item_name}")
        self._output("")

        logger.debug("Displayed inventory")

    def handle_help(self) -> None:
        """
        Display available commands and help text.
        """
        help_text = """
=== AVAILABLE COMMANDS ===

Movement:
  go <direction>     - Move in a direction (north, south, east, west, etc.)

Interaction:
  take <item>        - Pick up an item
  drop <item>        - Drop an item from your inventory
  use <item>         - Use an item
  use <item> on <target> - Use an item on a target
  look               - Look at the current scene
  look at <target>   - Examine an object or NPC
  talk to <npc>      - Talk to an NPC
  ask <npc> about <topic> - Ask an NPC about something

Inventory:
  inventory          - Show your inventory (or 'inv', 'i')

Other:
  help               - Show this help text (or 'h', '?')
  quit               - Quit the game (or 'exit', 'q')

Tips:
  - You can use synonyms for most commands (e.g., 'get' instead of 'take')
  - The parser is forgiving with typos and variations
  - Explore thoroughly and talk to everyone!
"""
        self._output(help_text)
        logger.debug("Displayed help")

    def _handle_unknown(self, action: UnknownAction) -> None:
        """
        Handle an unknown/unrecognized command.

        Args:
            action: The UnknownAction with optional suggestion.
        """
        self._output("\nI don't understand that command.")

        if action.suggestion:
            self._output(f"Did you mean '{action.suggestion}'?")

        self._output("Type 'help' for a list of commands.\n")
        logger.debug(f"Unknown command: {action.raw_command}")

    def _display_welcome(self) -> None:
        """Display welcome message."""
        welcome = """
╔═══════════════════════════════════════════════════════════╗
║           SPACE HULK: DERELICT OF THE VOID                ║
║                                                           ║
║  A Text Adventure in the Warhammer 40,000 Universe       ║
╚═══════════════════════════════════════════════════════════╝

In the grim darkness of the far future, there is only war...

Type 'help' for a list of commands. Type 'quit' to exit.
"""
        self._output(welcome)

    def _display_current_scene(self) -> None:
        """Display the current scene description."""
        current_scene = self.scenes[self.game_state.current_scene]

        # Scene header
        self._output("=" * 60)
        self._output(f"{current_scene.name.upper()}")
        self._output("=" * 60)

        # Scene description
        description = current_scene.get_full_description()
        self._output(f"\n{description}\n")

        # Available exits
        exit_desc = current_scene.get_exit_description()
        self._output(exit_desc)

        # Health status
        health_percent = (self.game_state.health / self.game_state.max_health) * 100
        health_bar = self._get_health_bar(health_percent)
        self._output(
            f"\nHealth: {health_bar} {self.game_state.health}/{self.game_state.max_health}"
        )
        self._output("")

        # Mark as visited
        current_scene.visited = True

    def _get_health_bar(self, percent: float) -> str:
        """
        Generate a visual health bar with status indicators.

        Args:
            percent: Health percentage (0-100).

        Returns:
            A string representing a health bar with status indicator.
        """
        bar_length = 20
        filled = int((percent / 100) * bar_length)
        empty = bar_length - filled

        bar = "█" * filled + "░" * empty

        # Add status indicators based on health
        if percent > 75:
            return f"[{bar}] (Good)"
        elif percent > 25:
            return f"[{bar}] (Warning)"
        else:
            return f"[{bar}] (CRITICAL)"

    def _process_entry_events(self) -> None:
        """Process events that trigger on entering the current scene."""
        current_scene = self.scenes[self.game_state.current_scene]

        entry_events = current_scene.get_entry_events(self.game_state.game_flags)

        for event in entry_events:
            self._trigger_event(event)

    def _trigger_event(self, event: Event) -> None:
        """
        Trigger an event and apply its effects.

        Args:
            event: The Event to trigger.
        """
        # Display event description
        self._output(f"\n>>> {event.description}\n")

        # Mark as triggered
        event.trigger()

        # Apply effects
        effects = event.effects

        if "damage" in effects:
            damage = effects["damage"]
            self.game_state.take_damage(damage)
            self._output(f"You take {damage} damage!\n")
            logger.info(f"Event damage: {damage}")

        if "heal" in effects:
            heal = effects["heal"]
            self.game_state.heal(heal)
            self._output(f"You recover {heal} health!\n")
            logger.info(f"Event heal: {heal}")

        if "set_flag" in effects:
            flag = effects["set_flag"]
            self.game_state.set_flag(flag)
            logger.info(f"Event set flag: {flag}")

        if "give_item" in effects:
            item_id = effects["give_item"]
            self.game_state.add_item(item_id)
            self._output(f"You receive: {item_id}\n")
            logger.info(f"Event gave item: {item_id}")

        logger.info(f"Triggered event: {event.id}")

    def _check_victory(self) -> bool:
        """
        Check if victory conditions are met.

        Returns:
            True if player has won, False otherwise.
        """
        if not self.victory_conditions:
            return False

        for flag in self.victory_conditions:
            if self.game_state.get_flag(flag):
                logger.info(f"Victory condition met: {flag}")
                return True

        return False

    def _check_defeat(self) -> bool:
        """
        Check if defeat conditions are met.

        Returns:
            True if player has lost, False otherwise.
        """
        # Check death
        if not self.game_state.is_alive():
            logger.info("Defeat: Player died")
            return True

        # Check defeat flags
        for flag in self.defeat_conditions:
            if self.game_state.get_flag(flag):
                logger.info(f"Defeat condition met: {flag}")
                return True

        return False

    def _display_victory(self) -> None:
        """Display victory message."""
        victory_text = """
╔═══════════════════════════════════════════════════════════╗
║                       VICTORY!                            ║
╚═══════════════════════════════════════════════════════════╝

Against all odds, you have succeeded in your mission!
The Emperor protects, and through your courage and skill,
you have brought honor to the Imperium.

May your name be remembered in the annals of history!
"""
        self._output(victory_text)

    def _display_defeat(self) -> None:
        """Display defeat message."""
        defeat_text = """
╔═══════════════════════════════════════════════════════════╗
║                       DEFEAT                              ║
╚═══════════════════════════════════════════════════════════╝

Your mission has ended in failure...

"""
        if not self.game_state.is_alive():
            defeat_text += "You have fallen in battle.\n"

        defeat_text += """
In the grim darkness of the far future, there is only war,
and not all battles can be won. Your sacrifice will be
remembered by those who come after.

Perhaps in another timeline, victory was possible...
"""
        self._output(defeat_text)

    def _confirm_quit(self) -> bool:
        """
        Ask player to confirm they want to quit.

        Returns:
            True if player confirms quit, False otherwise.
        """
        self._output("\nAre you sure you want to quit? (yes/no): ")
        try:
            response = self.input_func()
            return response.strip().lower() in ["yes", "y"]
        except (EOFError, KeyboardInterrupt):
            return True

    def _output(self, text: str) -> None:
        """
        Output text to the player.

        Args:
            text: The text to display.
        """
        self.output_func(text)
