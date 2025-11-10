"""
Entity Classes Module

Defines the Item, NPC, and Event classes used in game scenes.
These represent interactive elements that players can encounter during gameplay.

Example:
    >>> from space_hulk_game.engine import Item, NPC, Event
    >>> item = Item(
    ...     id="dataslate",
    ...     name="Ancient Dataslate",
    ...     description="A cracked dataslate with flickering text.",
    ...     takeable=True,
    ...     useable=True
    ... )
    >>> npc = NPC(
    ...     id="tech_priest",
    ...     name="Tech-Priest Var'kun",
    ...     description="A red-robed Tech-Priest tending to ancient machines.",
    ...     dialogue={"greeting": "The Omnissiah provides..."}
    ... )
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any


@dataclass
class Item:
    """
    Represents an interactive item in the game world.
    
    Items can be picked up, examined, or used to solve puzzles and progress
    the story. They can have associated effects when used.
    
    Attributes:
        id: Unique identifier for the item.
        name: Display name of the item.
        description: Text description shown when examining the item.
        takeable: Whether the item can be added to inventory.
        useable: Whether the item can be used/activated.
        use_text: Text displayed when the item is used.
        required_flag: Optional game flag required to use this item.
        effects: Dictionary of effects applied when item is used
                (e.g., {'unlock_door': 'door_id', 'heal': 20}).
    
    Examples:
        Create a simple takeable item:
        >>> medkit = Item(
        ...     id="medkit",
        ...     name="Medical Kit",
        ...     description="A standard Imperial Guard medical kit.",
        ...     takeable=True,
        ...     useable=True,
        ...     use_text="You use the medkit and feel your wounds close.",
        ...     effects={'heal': 30}
        ... )
        
        Create a key item for puzzles:
        >>> key = Item(
        ...     id="brass_key",
        ...     name="Brass Key",
        ...     description="An ornate brass key with strange markings.",
        ...     takeable=True,
        ...     useable=True,
        ...     use_text="You insert the key and hear a satisfying click.",
        ...     effects={'unlock_door': 'vault_door'}
        ... )
        
        Create a scenery item:
        >>> console = Item(
        ...     id="control_console",
        ...     name="Control Console",
        ...     description="A massive control console covered in blinking lights.",
        ...     takeable=False,
        ...     useable=True,
        ...     required_flag="has_access_card"
        ... )
    """
    
    id: str
    name: str
    description: str
    takeable: bool = False
    useable: bool = False
    use_text: Optional[str] = None
    required_flag: Optional[str] = None
    effects: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the item after initialization."""
        if not self.id:
            raise ValueError("Item id cannot be empty")
        if not self.name:
            raise ValueError("Item name cannot be empty")
        if not self.description:
            raise ValueError("Item description cannot be empty")
    
    def can_use(self, game_flags: Dict[str, bool]) -> bool:
        """
        Check if the item can be used given current game flags.
        
        Args:
            game_flags: Dictionary of current game flags.
            
        Returns:
            True if the item can be used, False otherwise.
            
        Examples:
            >>> item = Item(id="locked_box", name="Box", description="A locked box.",
            ...             required_flag="has_key")
            >>> item.can_use({})
            False
            >>> item.can_use({"has_key": True})
            True
        """
        if not self.useable:
            return False
        if self.required_flag:
            return game_flags.get(self.required_flag, False)
        return True
    
    def to_dict(self) -> Dict:
        """
        Convert the item to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the item.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'takeable': self.takeable,
            'useable': self.useable,
            'use_text': self.use_text,
            'required_flag': self.required_flag,
            'effects': self.effects,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """
        Create an Item from a dictionary.
        
        Args:
            data: Dictionary containing item data.
            
        Returns:
            A new Item instance.
        """
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            takeable=data.get('takeable', False),
            useable=data.get('useable', False),
            use_text=data.get('use_text'),
            required_flag=data.get('required_flag'),
            effects=data.get('effects', {}),
        )


@dataclass
class NPC:
    """
    Represents a non-player character in the game.
    
    NPCs can provide dialogue, quests, information, and interact with the player
    in various ways. They can have multiple dialogue options and react to
    game state.
    
    Attributes:
        id: Unique identifier for the NPC.
        name: Display name of the NPC.
        description: Text description of the NPC's appearance.
        dialogue: Dictionary mapping dialogue keys to text responses.
        hostile: Whether the NPC is hostile to the player.
        health: NPC health points (for combat).
        gives_item: Optional item ID that the NPC gives to the player.
        required_flag: Optional game flag required to interact with this NPC.
    
    Examples:
        Create a friendly NPC:
        >>> trader = NPC(
        ...     id="merchant",
        ...     name="Rogue Trader Jin",
        ...     description="A weathered trader in worn void armor.",
        ...     dialogue={
        ...         'greeting': "Looking to trade, stranger?",
        ...         'help': "I can offer you supplies... for a price.",
        ...         'goodbye': "Emperor protects, traveler."
        ...     }
        ... )
        
        Create a quest-giving NPC:
        >>> survivor = NPC(
        ...     id="survivor_kane",
        ...     name="Guardsman Kane",
        ...     description="A wounded Imperial Guardsman.",
        ...     dialogue={
        ...         'greeting': "Thank the Emperor! You must warn the others!",
        ...         'quest': "There's a genestealer nest in the cargo hold!"
        ...     },
        ...     gives_item="access_card"
        ... )
        
        Create a hostile NPC:
        >>> cultist = NPC(
        ...     id="chaos_cultist",
        ...     name="Chaos Cultist",
        ...     description="A twisted figure covered in profane symbols.",
        ...     hostile=True,
        ...     health=50
        ... )
    """
    
    id: str
    name: str
    description: str
    dialogue: Dict[str, str] = field(default_factory=dict)
    hostile: bool = False
    health: int = 100
    gives_item: Optional[str] = None
    required_flag: Optional[str] = None
    
    def __post_init__(self):
        """Validate the NPC after initialization."""
        if not self.id:
            raise ValueError("NPC id cannot be empty")
        if not self.name:
            raise ValueError("NPC name cannot be empty")
        if not self.description:
            raise ValueError("NPC description cannot be empty")
        if self.health < 0:
            raise ValueError("NPC health cannot be negative")
    
    def can_interact(self, game_flags: Dict[str, bool]) -> bool:
        """
        Check if the player can interact with this NPC.
        
        Args:
            game_flags: Dictionary of current game flags.
            
        Returns:
            True if interaction is possible, False otherwise.
            
        Examples:
            >>> npc = NPC(id="guard", name="Guard", description="A guard.",
            ...           required_flag="guard_friendly")
            >>> npc.can_interact({})
            False
            >>> npc.can_interact({"guard_friendly": True})
            True
        """
        if self.required_flag:
            return game_flags.get(self.required_flag, False)
        return True
    
    def get_dialogue(self, key: str, default: str = "...") -> str:
        """
        Get dialogue text for a specific key.
        
        Args:
            key: The dialogue key to retrieve.
            default: Default text if the key doesn't exist.
            
        Returns:
            The dialogue text.
            
        Examples:
            >>> npc = NPC(id="test", name="Test", description="Test",
            ...           dialogue={"hello": "Greetings!"})
            >>> npc.get_dialogue("hello")
            'Greetings!'
            >>> npc.get_dialogue("unknown")
            '...'
        """
        return self.dialogue.get(key, default)
    
    def is_alive(self) -> bool:
        """
        Check if the NPC is still alive.
        
        Returns:
            True if health > 0, False otherwise.
            
        Examples:
            >>> npc = NPC(id="test", name="Test", description="Test", health=50)
            >>> npc.is_alive()
            True
            >>> npc.health = 0
            >>> npc.is_alive()
            False
        """
        return self.health > 0
    
    def to_dict(self) -> Dict:
        """
        Convert the NPC to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the NPC.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'dialogue': self.dialogue,
            'hostile': self.hostile,
            'health': self.health,
            'gives_item': self.gives_item,
            'required_flag': self.required_flag,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        """
        Create an NPC from a dictionary.
        
        Args:
            data: Dictionary containing NPC data.
            
        Returns:
            A new NPC instance.
        """
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            dialogue=data.get('dialogue', {}),
            hostile=data.get('hostile', False),
            health=data.get('health', 100),
            gives_item=data.get('gives_item'),
            required_flag=data.get('required_flag'),
        )


@dataclass
class Event:
    """
    Represents a triggerable event in a scene.
    
    Events are scripted occurrences that can happen when the player enters
    a scene, performs an action, or meets certain conditions. They can
    modify game state, trigger dialogue, or cause other effects.
    
    Attributes:
        id: Unique identifier for the event.
        description: Text description of what happens.
        trigger_on_entry: Whether the event triggers when entering the scene.
        required_flag: Optional game flag required to trigger this event.
        one_time: Whether the event can only trigger once.
        effects: Dictionary of effects applied when event triggers.
    
    Examples:
        Create an entry event:
        >>> ambush = Event(
        ...     id="genestealer_ambush",
        ...     description="A genestealer drops from the ceiling!",
        ...     trigger_on_entry=True,
        ...     effects={'spawn_enemy': 'genestealer', 'damage': 20}
        ... )
        
        Create a conditional event:
        >>> discovery = Event(
        ...     id="find_clue",
        ...     description="You notice strange markings on the wall.",
        ...     required_flag="has_enhanced_vision",
        ...     one_time=True,
        ...     effects={'set_flag': 'clue_found'}
        ... )
        
        Create a narrative event:
        >>> flashback = Event(
        ...     id="vision",
        ...     description="A psychic vision overwhelms you...",
        ...     trigger_on_entry=True,
        ...     one_time=True,
        ...     effects={'set_flag': 'vision_seen', 'damage': 5}
        ... )
    """
    
    id: str
    description: str
    trigger_on_entry: bool = False
    required_flag: Optional[str] = None
    one_time: bool = True
    effects: Dict[str, Any] = field(default_factory=dict)
    triggered: bool = False
    
    def __post_init__(self):
        """Validate the event after initialization."""
        if not self.id:
            raise ValueError("Event id cannot be empty")
        if not self.description:
            raise ValueError("Event description cannot be empty")
    
    def can_trigger(self, game_flags: Dict[str, bool]) -> bool:
        """
        Check if the event can trigger given current game flags.
        
        Args:
            game_flags: Dictionary of current game flags.
            
        Returns:
            True if the event can trigger, False otherwise.
            
        Examples:
            >>> event = Event(id="test", description="Test event",
            ...               required_flag="key_found", one_time=True)
            >>> event.can_trigger({})
            False
            >>> event.can_trigger({"key_found": True})
            True
            >>> event.triggered = True
            >>> event.can_trigger({"key_found": True})
            False
        """
        if self.one_time and self.triggered:
            return False
        if self.required_flag:
            return game_flags.get(self.required_flag, False)
        return True
    
    def trigger(self) -> None:
        """
        Mark the event as triggered.
        
        Examples:
            >>> event = Event(id="test", description="Test", one_time=True)
            >>> event.triggered
            False
            >>> event.trigger()
            >>> event.triggered
            True
        """
        self.triggered = True
    
    def reset(self) -> None:
        """
        Reset the event so it can trigger again.
        
        Examples:
            >>> event = Event(id="test", description="Test")
            >>> event.trigger()
            >>> event.triggered
            True
            >>> event.reset()
            >>> event.triggered
            False
        """
        self.triggered = False
    
    def to_dict(self) -> Dict:
        """
        Convert the event to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the event.
        """
        return {
            'id': self.id,
            'description': self.description,
            'trigger_on_entry': self.trigger_on_entry,
            'required_flag': self.required_flag,
            'one_time': self.one_time,
            'effects': self.effects,
            'triggered': self.triggered,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Event':
        """
        Create an Event from a dictionary.
        
        Args:
            data: Dictionary containing event data.
            
        Returns:
            A new Event instance.
        """
        event = cls(
            id=data['id'],
            description=data['description'],
            trigger_on_entry=data.get('trigger_on_entry', False),
            required_flag=data.get('required_flag'),
            one_time=data.get('one_time', True),
            effects=data.get('effects', {}),
        )
        event.triggered = data.get('triggered', False)
        return event
