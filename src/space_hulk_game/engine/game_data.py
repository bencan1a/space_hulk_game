"""
Game Data Module

Defines the GameData class that holds all content loaded from generated YAML files.
This is the central data structure that bridges AI-generated content with the game engine.

The GameData class aggregates:
- Plot structure (from plot_outline.yaml)
- Scene graph (from narrative_map.yaml)
- Puzzles, artifacts, NPCs (from puzzle_design.yaml)
- Scene descriptions (from scene_texts.yaml)
- Game mechanics (from prd_document.yaml)

Example:
    >>> from space_hulk_game.engine import GameData, Scene
    >>> game_data = GameData(
    ...     title="Test Game",
    ...     scenes={"start": Scene(id="start", name="Start", description="Begin.")},
    ...     starting_scene="start"
    ... )
    >>> game_data.title
    'Test Game'
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from .scene import Scene
from .entities import Item, NPC


@dataclass
class GameData:
    """
    Holds all game content loaded from generated YAML files.
    
    This is the complete game definition, including all scenes, items, NPCs,
    game mechanics, and narrative structure. The TextAdventureEngine uses
    GameData to run the game.
    
    Attributes:
        title: The title of the game.
        description: Brief description of the game's premise.
        scenes: Dictionary mapping scene IDs to Scene objects.
        starting_scene: ID of the scene where the game begins.
        global_items: Dictionary of item definitions (not placed in any scene yet).
        global_npcs: Dictionary of NPC definitions (not placed in any scene yet).
        endings: List of possible game endings with their conditions.
        game_rules: Dictionary of game-specific mechanics and rules.
        themes: List of narrative themes.
        plot_points: List of major plot points.
        metadata: Additional metadata from the YAML files.
    
    Examples:
        Create minimal game data:
        >>> from space_hulk_game.engine import Scene
        >>> start_scene = Scene(
        ...     id="entrance",
        ...     name="Entrance Hall",
        ...     description="You are in the entrance."
        ... )
        >>> data = GameData(
        ...     title="Test Adventure",
        ...     description="A test game",
        ...     scenes={"entrance": start_scene},
        ...     starting_scene="entrance"
        ... )
        
        Access scenes:
        >>> scene = data.get_scene("entrance")
        >>> scene.name
        'Entrance Hall'
        
        Check for scenes:
        >>> data.has_scene("entrance")
        True
        >>> data.has_scene("unknown")
        False
    """
    
    title: str
    description: str
    scenes: Dict[str, Scene]
    starting_scene: str
    global_items: Dict[str, Item] = field(default_factory=dict)
    global_npcs: Dict[str, NPC] = field(default_factory=dict)
    endings: List[Dict[str, Any]] = field(default_factory=list)
    game_rules: Dict[str, Any] = field(default_factory=dict)
    themes: List[str] = field(default_factory=list)
    plot_points: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the game data after initialization."""
        if not self.title:
            raise ValueError("Game title cannot be empty")
        if not self.description:
            raise ValueError("Game description cannot be empty")
        if not self.scenes:
            raise ValueError("Game must have at least one scene")
        if not self.starting_scene:
            raise ValueError("Starting scene must be specified")
        if self.starting_scene not in self.scenes:
            raise ValueError(f"Starting scene '{self.starting_scene}' not found in scenes")
    
    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """
        Get a scene by its ID.
        
        Args:
            scene_id: The ID of the scene to retrieve.
            
        Returns:
            The Scene object if found, None otherwise.
            
        Examples:
            >>> from space_hulk_game.engine import Scene
            >>> scene = Scene(id="test", name="Test", description="Test scene")
            >>> data = GameData(
            ...     title="Test",
            ...     description="Test",
            ...     scenes={"test": scene},
            ...     starting_scene="test"
            ... )
            >>> found = data.get_scene("test")
            >>> found.name
            'Test'
            >>> data.get_scene("missing")
        """
        return self.scenes.get(scene_id)
    
    def has_scene(self, scene_id: str) -> bool:
        """
        Check if a scene exists.
        
        Args:
            scene_id: The ID of the scene to check.
            
        Returns:
            True if the scene exists, False otherwise.
            
        Examples:
            >>> from space_hulk_game.engine import Scene
            >>> scene = Scene(id="test", name="Test", description="Test")
            >>> data = GameData(
            ...     title="Test",
            ...     description="Test",
            ...     scenes={"test": scene},
            ...     starting_scene="test"
            ... )
            >>> data.has_scene("test")
            True
            >>> data.has_scene("unknown")
            False
        """
        return scene_id in self.scenes
    
    def get_item_definition(self, item_id: str) -> Optional[Item]:
        """
        Get a global item definition by ID.
        
        Args:
            item_id: The ID of the item to retrieve.
            
        Returns:
            The Item object if found, None otherwise.
            
        Examples:
            >>> from space_hulk_game.engine import Item, Scene
            >>> item = Item(id="key", name="Key", description="A key")
            >>> scene = Scene(id="start", name="Start", description="Start scene")
            >>> data = GameData(
            ...     title="Test",
            ...     description="Test",
            ...     scenes={"start": scene},
            ...     starting_scene="start",
            ...     global_items={"key": item}
            ... )
            >>> found = data.get_item_definition("key")
            >>> found.name
            'Key'
        """
        return self.global_items.get(item_id)
    
    def get_npc_definition(self, npc_id: str) -> Optional[NPC]:
        """
        Get a global NPC definition by ID.
        
        Args:
            npc_id: The ID of the NPC to retrieve.
            
        Returns:
            The NPC object if found, None otherwise.
            
        Examples:
            >>> from space_hulk_game.engine import NPC, Scene
            >>> npc = NPC(id="guard", name="Guard", description="A guard")
            >>> scene = Scene(id="start", name="Start", description="Start scene")
            >>> data = GameData(
            ...     title="Test",
            ...     description="Test",
            ...     scenes={"start": scene},
            ...     starting_scene="start",
            ...     global_npcs={"guard": npc}
            ... )
            >>> found = data.get_npc_definition("guard")
            >>> found.name
            'Guard'
        """
        return self.global_npcs.get(npc_id)
    
    def to_dict(self) -> Dict:
        """
        Convert the game data to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the game data.
        """
        return {
            'title': self.title,
            'description': self.description,
            'scenes': {sid: scene.to_dict() for sid, scene in self.scenes.items()},
            'starting_scene': self.starting_scene,
            'global_items': {iid: item.to_dict() for iid, item in self.global_items.items()},
            'global_npcs': {nid: npc.to_dict() for nid, npc in self.global_npcs.items()},
            'endings': self.endings,
            'game_rules': self.game_rules,
            'themes': self.themes,
            'plot_points': self.plot_points,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameData':
        """
        Create GameData from a dictionary.
        
        Args:
            data: Dictionary containing game data.
            
        Returns:
            A new GameData instance.
        """
        return cls(
            title=data['title'],
            description=data['description'],
            scenes={
                sid: Scene.from_dict(scene_data)
                for sid, scene_data in data.get('scenes', {}).items()
            },
            starting_scene=data['starting_scene'],
            global_items={
                iid: Item.from_dict(item_data)
                for iid, item_data in data.get('global_items', {}).items()
            },
            global_npcs={
                nid: NPC.from_dict(npc_data)
                for nid, npc_data in data.get('global_npcs', {}).items()
            },
            endings=data.get('endings', []),
            game_rules=data.get('game_rules', {}),
            themes=data.get('themes', []),
            plot_points=data.get('plot_points', []),
            metadata=data.get('metadata', {}),
        )
