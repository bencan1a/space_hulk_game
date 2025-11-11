"""
Scene Module

Defines the Scene class that represents a location in the game world.
Scenes contain descriptions, exits to other scenes, items, NPCs, and events.

Example:
    >>> from space_hulk_game.engine import Scene, Item, NPC, Event
    >>> scene = Scene(
    ...     id="cargo_bay",
    ...     name="Cargo Bay Alpha",
    ...     description="A vast cargo hold filled with ancient crates.",
    ...     exits={"north": "corridor_1", "east": "airlock"},
    ...     items=[],
    ...     npcs=[],
    ...     events=[]
    ... )
"""

from dataclasses import dataclass, field

from .entities import NPC, Event, Item


@dataclass
class Scene:
    """
    Represents a location/room in the game world.

    Scenes are the primary spatial units in the game. Each scene has a description,
    connections to other scenes (exits), and can contain items, NPCs, and events.
    Players navigate between scenes to progress through the story.

    Attributes:
        id: Unique identifier for the scene.
        name: Display name of the scene.
        description: Detailed text description of the scene.
        exits: Dictionary mapping direction names to scene IDs
              (e.g., {"north": "corridor_1", "east": "airlock"}).
        items: List of Item objects present in this scene.
        npcs: List of NPC objects present in this scene.
        events: List of Event objects that can trigger in this scene.
        visited: Whether the player has visited this scene before.
        dark: Whether the scene is dark (requires light source).
        locked_exits: Dictionary of locked exits requiring items or flags
                     (e.g., {"north": "brass_key"}).

    Examples:
        Create a simple scene:
        >>> entrance = Scene(
        ...     id="entrance_hall",
        ...     name="Entrance Hall",
        ...     description="A grand hall with vaulted ceilings.",
        ...     exits={"north": "main_corridor", "south": "exterior"}
        ... )

        Create a scene with items and NPCs:
        >>> from space_hulk_game.engine import Item, NPC
        >>> medkit = Item(id="medkit", name="Medkit", description="A medkit.")
        >>> guard = NPC(id="guard", name="Guard", description="A guard.")
        >>> armory = Scene(
        ...     id="armory",
        ...     name="Armory",
        ...     description="Weapons line the walls.",
        ...     exits={"west": "corridor"},
        ...     items=[medkit],
        ...     npcs=[guard]
        ... )

        Create a scene with locked exits:
        >>> vault = Scene(
        ...     id="vault",
        ...     name="Secure Vault",
        ...     description="A heavily secured vault.",
        ...     exits={"north": "corridor", "vault_door": "treasure_room"},
        ...     locked_exits={"vault_door": "vault_key"}
        ... )

        Create a dark scene:
        >>> dark_corridor = Scene(
        ...     id="dark_corridor",
        ...     name="Dark Corridor",
        ...     description="A pitch-black corridor.",
        ...     exits={"east": "light_room", "west": "another_room"},
        ...     dark=True
        ... )
    """

    id: str
    name: str
    description: str
    exits: dict[str, str] = field(default_factory=dict)
    items: list[Item] = field(default_factory=list)
    npcs: list[NPC] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    visited: bool = False
    dark: bool = False
    locked_exits: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validate the scene after initialization."""
        if not self.id:
            raise ValueError("Scene id cannot be empty")
        if not self.name:
            raise ValueError("Scene name cannot be empty")
        if not self.description:
            raise ValueError("Scene description cannot be empty")

    def get_full_description(self) -> str:
        """
        Get the complete description of the scene, including items and NPCs.

        Returns:
            A formatted string describing the scene and its contents.

        Examples:
            >>> item = Item(id="key", name="Brass Key", description="A key.")
            >>> scene = Scene(
            ...     id="room",
            ...     name="Test Room",
            ...     description="A test room.",
            ...     items=[item]
            ... )
            >>> desc = scene.get_full_description()
            >>> "Brass Key" in desc
            True
        """
        parts = [self.description]

        if self.items:
            item_names = [item.name for item in self.items]
            parts.append(f"\n\nYou see: {', '.join(item_names)}.")

        if self.npcs:
            npc_descriptions = [npc.description for npc in self.npcs]
            parts.append(f"\n\n{' '.join(npc_descriptions)}")

        return "".join(parts)

    def get_exit_description(self) -> str:
        """
        Get a description of available exits.

        Returns:
            A formatted string describing available exits.

        Examples:
            >>> scene = Scene(
            ...     id="room",
            ...     name="Room",
            ...     description="A room.",
            ...     exits={"north": "hallway", "east": "closet"}
            ... )
            >>> desc = scene.get_exit_description()
            >>> "north" in desc and "east" in desc
            True
        """
        if not self.exits:
            return "There are no obvious exits."

        exit_names = list(self.exits.keys())
        if len(exit_names) == 1:
            return f"There is an exit to the {exit_names[0]}."
        else:
            exits_str = ", ".join(exit_names[:-1]) + f" and {exit_names[-1]}"
            return f"There are exits to the {exits_str}."

    def can_exit(
        self, direction: str, inventory: list[str], game_flags: dict[str, bool]
    ) -> tuple[bool, str | None]:
        """
        Check if the player can use a specific exit.

        Args:
            direction: The direction/exit name to check.
            inventory: Player's current inventory.
            game_flags: Current game flags.

        Returns:
            A tuple of (can_exit: bool, reason: Optional[str]).
            If can_exit is False, reason contains an explanation.

        Examples:
            >>> scene = Scene(
            ...     id="room",
            ...     name="Room",
            ...     description="A room.",
            ...     exits={"north": "hallway"},
            ...     locked_exits={"north": "key"}
            ... )
            >>> scene.can_exit("north", [], {})
            (False, 'The exit to the north is locked. You need: key')
            >>> scene.can_exit("north", ["key"], {})
            (True, None)
            >>> scene.can_exit("south", ["key"], {})
            (False, 'There is no exit in that direction.')
        """
        if direction not in self.exits:
            return False, "There is no exit in that direction."

        if direction in self.locked_exits:
            required = self.locked_exits[direction]

            # Check if it's an item requirement
            if required in inventory:
                return True, None

            # Check if it's a flag requirement
            if game_flags.get(required, False):
                return True, None

            return False, f"The exit to the {direction} is locked. You need: {required}"

        return True, None

    def get_item(self, item_id: str) -> Item | None:
        """
        Get an item from the scene by ID.

        Args:
            item_id: The ID of the item to retrieve.

        Returns:
            The Item object if found, None otherwise.

        Examples:
            >>> item = Item(id="key", name="Key", description="A key.")
            >>> scene = Scene(
            ...     id="room",
            ...     name="Room",
            ...     description="A room.",
            ...     items=[item]
            ... )
            >>> found = scene.get_item("key")
            >>> found.name
            'Key'
            >>> scene.get_item("missing")
        """
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def remove_item(self, item_id: str) -> bool:
        """
        Remove an item from the scene.

        Args:
            item_id: The ID of the item to remove.

        Returns:
            True if the item was removed, False if not found.

        Examples:
            >>> item = Item(id="key", name="Key", description="A key.")
            >>> scene = Scene(
            ...     id="room",
            ...     name="Room",
            ...     description="A room.",
            ...     items=[item]
            ... )
            >>> scene.remove_item("key")
            True
            >>> len(scene.items)
            0
            >>> scene.remove_item("key")
            False
        """
        for i, item in enumerate(self.items):
            if item.id == item_id:
                self.items.pop(i)
                return True
        return False

    def add_item(self, item: Item) -> None:
        """
        Add an item to the scene.

        Args:
            item: The Item object to add.

        Examples:
            >>> item = Item(id="key", name="Key", description="A key.")
            >>> scene = Scene(id="room", name="Room", description="A room.")
            >>> scene.add_item(item)
            >>> len(scene.items)
            1
        """
        self.items.append(item)

    def get_npc(self, npc_id: str) -> NPC | None:
        """
        Get an NPC from the scene by ID.

        Args:
            npc_id: The ID of the NPC to retrieve.

        Returns:
            The NPC object if found, None otherwise.

        Examples:
            >>> npc = NPC(id="guard", name="Guard", description="A guard.")
            >>> scene = Scene(
            ...     id="room",
            ...     name="Room",
            ...     description="A room.",
            ...     npcs=[npc]
            ... )
            >>> found = scene.get_npc("guard")
            >>> found.name
            'Guard'
        """
        for npc in self.npcs:
            if npc.id == npc_id:
                return npc
        return None

    def get_entry_events(self, game_flags: dict[str, bool]) -> list[Event]:
        """
        Get all events that should trigger when entering this scene.

        Args:
            game_flags: Current game flags.

        Returns:
            List of Event objects that can trigger.

        Examples:
            >>> event = Event(
            ...     id="ambush",
            ...     description="An ambush!",
            ...     trigger_on_entry=True
            ... )
            >>> scene = Scene(
            ...     id="room",
            ...     name="Room",
            ...     description="A room.",
            ...     events=[event]
            ... )
            >>> events = scene.get_entry_events({})
            >>> len(events)
            1
        """
        return [
            event
            for event in self.events
            if event.trigger_on_entry and event.can_trigger(game_flags)
        ]

    def unlock_exit(self, direction: str) -> bool:
        """
        Unlock an exit, making it passable.

        Args:
            direction: The direction/exit to unlock.

        Returns:
            True if the exit was unlocked, False if it wasn't locked.

        Examples:
            >>> scene = Scene(
            ...     id="room",
            ...     name="Room",
            ...     description="A room.",
            ...     exits={"north": "hallway"},
            ...     locked_exits={"north": "key"}
            ... )
            >>> scene.unlock_exit("north")
            True
            >>> "north" in scene.locked_exits
            False
        """
        if direction in self.locked_exits:
            del self.locked_exits[direction]
            return True
        return False

    def to_dict(self) -> dict:
        """
        Convert the scene to a dictionary for serialization.

        Returns:
            Dictionary representation of the scene.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "exits": self.exits,
            "items": [item.to_dict() for item in self.items],
            "npcs": [npc.to_dict() for npc in self.npcs],
            "events": [event.to_dict() for event in self.events],
            "visited": self.visited,
            "dark": self.dark,
            "locked_exits": self.locked_exits,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Scene":
        """
        Create a Scene from a dictionary.

        Args:
            data: Dictionary containing scene data.

        Returns:
            A new Scene instance.
        """
        scene = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            exits=data.get("exits", {}),
            items=[Item.from_dict(item_data) for item_data in data.get("items", [])],
            npcs=[NPC.from_dict(npc_data) for npc_data in data.get("npcs", [])],
            events=[Event.from_dict(event_data) for event_data in data.get("events", [])],
            dark=data.get("dark", False),
            locked_exits=data.get("locked_exits", {}),
        )
        scene.visited = data.get("visited", False)
        return scene
