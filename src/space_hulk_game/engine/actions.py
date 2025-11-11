"""
Action Classes Module

Defines the action class hierarchy for representing player commands.
Actions encapsulate player intent and are created by the CommandParser.

Example:
    >>> from space_hulk_game.engine import MoveAction, TakeAction
    >>> move = MoveAction(direction="north")
    >>> take = TakeAction(item_id="medkit")
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    """
    Base class for all player actions.

    Actions represent the player's intent after parsing their command.
    They are immutable and contain all information needed to execute
    the action in the game engine.

    This follows the Command Pattern from Gang of Four design patterns,
    encapsulating requests as objects.

    Attributes:
        raw_command: The original text command from the player.

    Examples:
        Actions are typically created by CommandParser, not directly:
        >>> action = Action(raw_command="look around")
        >>> action.raw_command
        'look around'
    """

    raw_command: str = ""

    def __str__(self) -> str:
        """Return a string representation of the action."""
        return f"{self.__class__.__name__}()"


@dataclass(frozen=True)
class MoveAction(Action):
    """
    Represents a movement action to another scene.

    Attributes:
        direction: The direction to move (e.g., "north", "south", "door").
        raw_command: The original text command from the player.

    Examples:
        >>> action = MoveAction(direction="north", raw_command="go north")
        >>> action.direction
        'north'
    """

    direction: str = ""

    def __str__(self) -> str:
        """Return a string representation of the action."""
        return f"MoveAction(direction='{self.direction}')"


@dataclass(frozen=True)
class TakeAction(Action):
    """
    Represents taking/picking up an item.

    Attributes:
        item_id: The ID or name of the item to take.
        raw_command: The original text command from the player.

    Examples:
        >>> action = TakeAction(item_id="medkit", raw_command="take medkit")
        >>> action.item_id
        'medkit'
    """

    item_id: str = ""

    def __str__(self) -> str:
        """Return a string representation of the action."""
        return f"TakeAction(item_id='{self.item_id}')"


@dataclass(frozen=True)
class DropAction(Action):
    """
    Represents dropping an item from inventory.

    Attributes:
        item_id: The ID or name of the item to drop.
        raw_command: The original text command from the player.

    Examples:
        >>> action = DropAction(item_id="sword", raw_command="drop sword")
        >>> action.item_id
        'sword'
    """

    item_id: str = ""

    def __str__(self) -> str:
        """Return a string representation of the action."""
        return f"DropAction(item_id='{self.item_id}')"


@dataclass(frozen=True)
class UseAction(Action):
    """
    Represents using an item.

    Attributes:
        item_id: The ID or name of the item to use.
        target_id: Optional target for the item (e.g., "use key on door").
        raw_command: The original text command from the player.

    Examples:
        >>> action = UseAction(item_id="medkit", raw_command="use medkit")
        >>> action.item_id
        'medkit'

        >>> action2 = UseAction(item_id="key", target_id="door", raw_command="use key on door")
        >>> action2.target_id
        'door'
    """

    item_id: str = ""
    target_id: str | None = None

    def __str__(self) -> str:
        """Return a string representation of the action."""
        if self.target_id:
            return f"UseAction(item_id='{self.item_id}', target_id='{self.target_id}')"
        return f"UseAction(item_id='{self.item_id}')"


@dataclass(frozen=True)
class LookAction(Action):
    """
    Represents examining the scene or an object.

    Attributes:
        target: Optional target to examine (if None, examine current scene).
        raw_command: The original text command from the player.

    Examples:
        >>> action = LookAction(raw_command="look")
        >>> action.target is None
        True

        >>> action2 = LookAction(target="console", raw_command="examine console")
        >>> action2.target
        'console'
    """

    target: str | None = None

    def __str__(self) -> str:
        """Return a string representation of the action."""
        if self.target:
            return f"LookAction(target='{self.target}')"
        return "LookAction()"


@dataclass(frozen=True)
class InventoryAction(Action):
    """
    Represents checking the player's inventory.

    Attributes:
        raw_command: The original text command from the player.

    Examples:
        >>> action = InventoryAction(raw_command="inventory")
        >>> str(action)
        'InventoryAction()'
    """

    def __str__(self) -> str:
        """Return a string representation of the action."""
        return "InventoryAction()"


@dataclass(frozen=True)
class TalkAction(Action):
    """
    Represents talking to an NPC.

    Attributes:
        npc_id: The ID or name of the NPC to talk to.
        topic: Optional dialogue topic or key.
        raw_command: The original text command from the player.

    Examples:
        >>> action = TalkAction(npc_id="guard", raw_command="talk to guard")
        >>> action.npc_id
        'guard'

        >>> action2 = TalkAction(npc_id="guard", topic="quest", raw_command="ask guard about quest")
        >>> action2.topic
        'quest'
    """

    npc_id: str = ""
    topic: str | None = None

    def __str__(self) -> str:
        """Return a string representation of the action."""
        if self.topic:
            return f"TalkAction(npc_id='{self.npc_id}', topic='{self.topic}')"
        return f"TalkAction(npc_id='{self.npc_id}')"


@dataclass(frozen=True)
class HelpAction(Action):
    """
    Represents requesting help or available commands.

    Attributes:
        raw_command: The original text command from the player.

    Examples:
        >>> action = HelpAction(raw_command="help")
        >>> str(action)
        'HelpAction()'
    """

    def __str__(self) -> str:
        """Return a string representation of the action."""
        return "HelpAction()"


@dataclass(frozen=True)
class UnknownAction(Action):
    """
    Represents an unrecognized command.

    Attributes:
        raw_command: The original text command from the player.
        suggestion: Optional suggestion for what the player might have meant.

    Examples:
        >>> action = UnknownAction(raw_command="xyz", suggestion="examine")
        >>> action.suggestion
        'examine'
    """

    suggestion: str | None = None

    def __str__(self) -> str:
        """Return a string representation of the action."""
        if self.suggestion:
            return f"UnknownAction(suggestion='{self.suggestion}')"
        return "UnknownAction()"
