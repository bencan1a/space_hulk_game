"""
Game State Module

Defines the core GameState class that tracks the current state of a game session.
This includes player location, inventory, visited scenes, game flags, and health.

Example:
    >>> from space_hulk_game.engine import GameState
    >>> state = GameState(
    ...     current_scene="entrance",
    ...     inventory=["flashlight", "dataslate"],
    ...     visited_scenes={"entrance"},
    ...     game_flags={"door_unlocked": False},
    ...     health=100,
    ...     max_health=100
    ... )
    >>> state.current_scene
    'entrance'
    >>> state.health
    100
"""

from dataclasses import dataclass, field


@dataclass
class GameState:
    """
    Represents the current state of a game session.

    This class tracks all mutable state during gameplay, including player location,
    inventory, visited areas, game flags for puzzle/story progression, and health.

    Attributes:
        current_scene: The ID of the scene where the player is currently located.
        inventory: List of item IDs currently held by the player.
        visited_scenes: Set of scene IDs that the player has visited.
        game_flags: Dictionary of boolean flags for tracking game state
                   (e.g., puzzles solved, doors unlocked, NPCs encountered).
        health: Current health points of the player.
        max_health: Maximum health points the player can have.

    Examples:
        Create a new game state:
        >>> state = GameState(
        ...     current_scene="cargo_bay",
        ...     inventory=["bolt_pistol"],
        ...     visited_scenes={"cargo_bay"},
        ...     game_flags={"hull_breach_sealed": False},
        ...     health=100,
        ...     max_health=100
        ... )

        Update player location:
        >>> state.current_scene = "bridge"
        >>> state.visited_scenes.add("bridge")

        Modify inventory:
        >>> state.inventory.append("power_cell")

        Track puzzle progress:
        >>> state.game_flags["airlock_opened"] = True

        Manage health:
        >>> state.health -= 20  # Take damage
        >>> state.health = min(state.health + 30, state.max_health)  # Heal
    """

    current_scene: str
    inventory: list[str] = field(default_factory=list)
    visited_scenes: set[str] = field(default_factory=set)
    game_flags: dict[str, bool] = field(default_factory=dict)
    health: int = 100
    max_health: int = 100

    def __post_init__(self):
        """Validate the game state after initialization."""
        if self.health < 0:
            raise ValueError("Health cannot be negative")
        if self.max_health <= 0:
            raise ValueError("Max health must be positive")
        if self.health > self.max_health:
            raise ValueError("Health cannot exceed max_health")
        if not self.current_scene:
            raise ValueError("current_scene cannot be empty")

    def add_item(self, item_id: str) -> None:
        """
        Add an item to the player's inventory.

        Args:
            item_id: The ID of the item to add.

        Examples:
            >>> state = GameState(current_scene="test")
            >>> state.add_item("medkit")
            >>> "medkit" in state.inventory
            True
        """
        if item_id not in self.inventory:
            self.inventory.append(item_id)

    def remove_item(self, item_id: str) -> bool:
        """
        Remove an item from the player's inventory.

        Args:
            item_id: The ID of the item to remove.

        Returns:
            True if the item was removed, False if it wasn't in inventory.

        Examples:
            >>> state = GameState(current_scene="test", inventory=["key"])
            >>> state.remove_item("key")
            True
            >>> state.remove_item("key")
            False
        """
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            return True
        return False

    def has_item(self, item_id: str) -> bool:
        """
        Check if the player has a specific item.

        Args:
            item_id: The ID of the item to check.

        Returns:
            True if the player has the item, False otherwise.

        Examples:
            >>> state = GameState(current_scene="test", inventory=["sword"])
            >>> state.has_item("sword")
            True
            >>> state.has_item("shield")
            False
        """
        return item_id in self.inventory

    def set_flag(self, flag_name: str, value: bool = True) -> None:
        """
        Set a game flag to track story or puzzle progress.

        Args:
            flag_name: The name of the flag to set.
            value: The boolean value to set (default: True).

        Examples:
            >>> state = GameState(current_scene="test")
            >>> state.set_flag("door_opened")
            >>> state.game_flags["door_opened"]
            True
        """
        self.game_flags[flag_name] = value

    def get_flag(self, flag_name: str, default: bool = False) -> bool:
        """
        Get the value of a game flag.

        Args:
            flag_name: The name of the flag to retrieve.
            default: The default value if the flag doesn't exist.

        Returns:
            The boolean value of the flag, or the default if not set.

        Examples:
            >>> state = GameState(current_scene="test")
            >>> state.set_flag("puzzle_solved", True)
            >>> state.get_flag("puzzle_solved")
            True
            >>> state.get_flag("unknown_flag", False)
            False
        """
        return self.game_flags.get(flag_name, default)

    def visit_scene(self, scene_id: str) -> None:
        """
        Mark a scene as visited and update current location.

        Args:
            scene_id: The ID of the scene to visit.

        Examples:
            >>> state = GameState(current_scene="start")
            >>> state.visit_scene("next_room")
            >>> state.current_scene
            'next_room'
            >>> "next_room" in state.visited_scenes
            True
        """
        self.current_scene = scene_id
        self.visited_scenes.add(scene_id)

    def has_visited(self, scene_id: str) -> bool:
        """
        Check if the player has visited a specific scene.

        Args:
            scene_id: The ID of the scene to check.

        Returns:
            True if the scene has been visited, False otherwise.

        Examples:
            >>> state = GameState(current_scene="test")
            >>> state.visited_scenes.add("old_room")
            >>> state.has_visited("old_room")
            True
            >>> state.has_visited("new_room")
            False
        """
        return scene_id in self.visited_scenes

    def take_damage(self, amount: int) -> None:
        """
        Reduce player health by the specified amount.

        Args:
            amount: The amount of damage to take (must be non-negative).

        Examples:
            >>> state = GameState(current_scene="test", health=100)
            >>> state.take_damage(30)
            >>> state.health
            70
        """
        if amount < 0:
            raise ValueError("Damage amount must be non-negative")
        self.health = max(0, self.health - amount)

    def heal(self, amount: int) -> None:
        """
        Restore player health by the specified amount, up to max_health.

        Args:
            amount: The amount of health to restore (must be non-negative).

        Examples:
            >>> state = GameState(current_scene="test", health=50, max_health=100)
            >>> state.heal(30)
            >>> state.health
            80
            >>> state.heal(50)
            >>> state.health
            100
        """
        if amount < 0:
            raise ValueError("Heal amount must be non-negative")
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self) -> bool:
        """
        Check if the player is still alive.

        Returns:
            True if health > 0, False otherwise.

        Examples:
            >>> state = GameState(current_scene="test", health=50)
            >>> state.is_alive()
            True
            >>> state.health = 0
            >>> state.is_alive()
            False
        """
        return self.health > 0

    def to_dict(self) -> dict:
        """
        Convert the game state to a dictionary for serialization.

        Returns:
            Dictionary representation of the game state.

        Examples:
            >>> state = GameState(current_scene="test")
            >>> data = state.to_dict()
            >>> data['current_scene']
            'test'
        """
        return {
            "current_scene": self.current_scene,
            "inventory": list(self.inventory),
            "visited_scenes": list(self.visited_scenes),
            "game_flags": dict(self.game_flags),
            "health": self.health,
            "max_health": self.max_health,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """
        Create a GameState from a dictionary.

        Args:
            data: Dictionary containing game state data.

        Returns:
            A new GameState instance.

        Examples:
            >>> data = {
            ...     'current_scene': 'test',
            ...     'inventory': ['item1'],
            ...     'visited_scenes': ['test', 'other'],
            ...     'game_flags': {'flag1': True},
            ...     'health': 80,
            ...     'max_health': 100
            ... }
            >>> state = GameState.from_dict(data)
            >>> state.health
            80
        """
        return cls(
            current_scene=data["current_scene"],
            inventory=list(data.get("inventory", [])),
            visited_scenes=set(data.get("visited_scenes", [])),
            game_flags=dict(data.get("game_flags", {})),
            health=data.get("health", 100),
            max_health=data.get("max_health", 100),
        )
