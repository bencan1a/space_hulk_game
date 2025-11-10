"""
Command Parser Module

Natural language command parser for text-based adventure game.
Converts player text input into structured Action objects.

The parser uses a dictionary of command synonyms and fuzzy matching
to handle variations and typos in player input. It's context-aware,
considering available items, NPCs, and exits in the current scene.

Example:
    >>> from space_hulk_game.engine import CommandParser, GameState, Scene
    >>> parser = CommandParser()
    >>> action = parser.parse("go north")
    >>> action.direction
    'north'
"""

import difflib
import re
from typing import Dict, List, Optional, Set, Tuple
import logging

from .actions import (
    Action,
    MoveAction,
    TakeAction,
    DropAction,
    UseAction,
    LookAction,
    InventoryAction,
    TalkAction,
    HelpAction,
    UnknownAction,
)
from .game_state import GameState
from .scene import Scene
from .entities import Item, NPC


# Configure logging
logger = logging.getLogger(__name__)


class CommandParser:
    """
    Parses natural language commands into Action objects.
    
    This class implements a facade pattern for command parsing, providing
    a simple interface that hides the complexity of synonym matching,
    fuzzy matching, and context-aware parsing.
    
    The parser is designed to be forgiving and helpful, using fuzzy matching
    for typos and providing suggestions when commands aren't recognized.
    
    Attributes:
        COMMANDS: Dictionary mapping action types to lists of synonyms.
        CUTOFF: Minimum similarity score for fuzzy matching (0.0 to 1.0).
    
    Examples:
        Basic usage:
        >>> parser = CommandParser()
        >>> action = parser.parse("go north")
        >>> isinstance(action, MoveAction)
        True
        
        With context for better suggestions:
        >>> from space_hulk_game.engine import GameState, Scene
        >>> state = GameState(current_scene="room")
        >>> scene = Scene(id="room", name="Room", description="A room.", 
        ...               exits={"north": "hallway"})
        >>> action = parser.parse("go nrth", state, scene)  # typo
        >>> isinstance(action, MoveAction)
        True
    """
    
    # Command synonyms mapping
    COMMANDS: Dict[str, List[str]] = {
        'move': ['go', 'move', 'walk', 'run', 'travel', 'head', 'proceed', 'enter'],
        'take': ['take', 'get', 'grab', 'pick', 'pickup', 'acquire', 'collect'],
        'drop': ['drop', 'leave', 'discard', 'put down', 'release'],
        'use': ['use', 'activate', 'apply', 'employ', 'utilize', 'engage'],
        'look': ['look', 'examine', 'inspect', 'check', 'observe', 'search', 'view', 'l', 'x'],
        'inventory': ['inventory', 'inv', 'i', 'items', 'possessions', 'backpack', 'bag'],
        'talk': ['talk', 'speak', 'chat', 'converse', 'ask', 'tell', 'discuss'],
        'help': ['help', 'h', '?', 'commands', 'instructions'],
    }
    
    # Fuzzy matching threshold
    CUTOFF: float = 0.6
    
    def __init__(self):
        """Initialize the command parser."""
        # Build reverse mapping for fast lookup
        self._command_map: Dict[str, str] = {}
        for action_type, synonyms in self.COMMANDS.items():
            for synonym in synonyms:
                self._command_map[synonym.lower()] = action_type
        
        logger.debug(f"CommandParser initialized with {len(self._command_map)} command synonyms")
    
    def parse(
        self,
        command: str,
        game_state: Optional[GameState] = None,
        current_scene: Optional[Scene] = None
    ) -> Action:
        """
        Parse a text command into an Action object.
        
        This is the main entry point for command parsing. It handles:
        1. Text normalization and tokenization
        2. Command word identification (with fuzzy matching)
        3. Argument extraction
        4. Context-aware parsing
        5. Action object creation
        
        Args:
            command: The raw text command from the player.
            game_state: Optional current game state for context.
            current_scene: Optional current scene for context.
        
        Returns:
            An Action object representing the parsed command.
        
        Examples:
            >>> parser = CommandParser()
            >>> action = parser.parse("go north")
            >>> action.direction
            'north'
            
            >>> action = parser.parse("take medkit")
            >>> action.item_id
            'medkit'
            
            >>> action = parser.parse("look")
            >>> isinstance(action, LookAction)
            True
        """
        # Normalize input
        command = command.strip().lower()
        
        if not command:
            logger.debug("Empty command received")
            return UnknownAction(raw_command="")
        
        logger.debug(f"Parsing command: '{command}'")
        
        # Tokenize command
        tokens = self._tokenize(command)
        
        if not tokens:
            return UnknownAction(raw_command=command)
        
        # Identify command type
        action_type, command_word, remaining_tokens = self._identify_command(tokens)
        
        if not action_type:
            # Try to find a close match
            suggestion = self._suggest_command(command_word)
            logger.debug(f"Unknown command: '{command_word}', suggestion: '{suggestion}'")
            return UnknownAction(raw_command=command, suggestion=suggestion)
        
        # Parse based on action type
        logger.debug(f"Identified action type: {action_type}")
        
        if action_type == 'move':
            return self._parse_move(command, remaining_tokens, current_scene)
        elif action_type == 'take':
            return self._parse_take(command, remaining_tokens, current_scene)
        elif action_type == 'drop':
            return self._parse_drop(command, remaining_tokens, game_state)
        elif action_type == 'use':
            return self._parse_use(command, remaining_tokens, game_state, current_scene)
        elif action_type == 'look':
            return self._parse_look(command, remaining_tokens, current_scene)
        elif action_type == 'inventory':
            return InventoryAction(raw_command=command)
        elif action_type == 'talk':
            return self._parse_talk(command, remaining_tokens, current_scene)
        elif action_type == 'help':
            return HelpAction(raw_command=command)
        else:
            return UnknownAction(raw_command=command)
    
    def _tokenize(self, command: str) -> List[str]:
        """
        Tokenize a command into words.
        
        Args:
            command: The command string to tokenize.
        
        Returns:
            List of tokens (words).
        
        Examples:
            >>> parser = CommandParser()
            >>> parser._tokenize("go north")
            ['go', 'north']
            >>> parser._tokenize("  take   medkit  ")
            ['take', 'medkit']
        """
        # Split on whitespace and filter empty strings
        return [token for token in command.split() if token]
    
    def _identify_command(self, tokens: List[str]) -> Tuple[Optional[str], str, List[str]]:
        """
        Identify the command type from tokens.
        
        This method handles multi-word commands (e.g., "pick up") and
        uses fuzzy matching for typos.
        
        Args:
            tokens: List of command tokens.
        
        Returns:
            Tuple of (action_type, command_word, remaining_tokens).
            action_type is None if no match found.
        
        Examples:
            >>> parser = CommandParser()
            >>> parser._identify_command(['go', 'north'])
            ('move', 'go', ['north'])
            >>> parser._identify_command(['take', 'medkit'])
            ('take', 'take', ['medkit'])
        """
        if not tokens:
            return None, "", []
        
        # Try exact match for first word
        first_word = tokens[0]
        if first_word in self._command_map:
            return self._command_map[first_word], first_word, tokens[1:]
        
        # Try multi-word commands (e.g., "pick up", "put down")
        if len(tokens) >= 2:
            two_word = f"{tokens[0]} {tokens[1]}"
            if two_word in self._command_map:
                return self._command_map[two_word], two_word, tokens[2:]
        
        # Try fuzzy matching
        matches = difflib.get_close_matches(
            first_word,
            self._command_map.keys(),
            n=5,  # Get multiple matches to handle ties
            cutoff=self.CUTOFF
        )
        
        if matches:
            # If we have multiple matches, prefer certain command types
            # Priority: take > move > use > look > talk > drop > inventory > help
            priority_order = ['take', 'move', 'use', 'look', 'talk', 'drop', 'inventory', 'help']
            
            # Get action types for all matches
            match_action_types = [(match, self._command_map[match]) for match in matches]
            
            # Sort by priority
            for priority_type in priority_order:
                for match, action_type in match_action_types:
                    if action_type == priority_type:
                        logger.debug(f"Fuzzy match: '{first_word}' -> '{match}' (type: {action_type})")
                        return action_type, first_word, tokens[1:]
            
            # If no priority match, use first match
            matched_word = matches[0]
            logger.debug(f"Fuzzy match: '{first_word}' -> '{matched_word}'")
            return self._command_map[matched_word], first_word, tokens[1:]
        
        return None, first_word, tokens[1:]
    
    def _suggest_command(self, word: str) -> Optional[str]:
        """
        Suggest a command based on fuzzy matching.
        
        Args:
            word: The unrecognized word.
        
        Returns:
            A suggested command word, or None if no close match.
        
        Examples:
            >>> parser = CommandParser()
            >>> parser._suggest_command("tak")
            'take'
            >>> parser._suggest_command("examne")
            'examine'
        """
        matches = difflib.get_close_matches(
            word,
            self._command_map.keys(),
            n=1,
            cutoff=0.5  # Lower cutoff for suggestions
        )
        
        return matches[0] if matches else None
    
    def _parse_move(
        self,
        command: str,
        tokens: List[str],
        scene: Optional[Scene]
    ) -> Action:
        """
        Parse a movement command.
        
        Args:
            command: The raw command string.
            tokens: Remaining tokens after command word.
            scene: Optional current scene for context.
        
        Returns:
            A MoveAction or UnknownAction.
        
        Examples:
            >>> parser = CommandParser()
            >>> action = parser._parse_move("go north", ["north"], None)
            >>> action.direction
            'north'
        """
        if not tokens:
            logger.debug("Move command missing direction")
            return UnknownAction(
                raw_command=command,
                suggestion="go <direction>"
            )
        
        direction = tokens[0]
        
        # If we have scene context, validate and fuzzy match against available exits
        if scene and scene.exits:
            available_exits = list(scene.exits.keys())
            
            # Exact match
            if direction in available_exits:
                return MoveAction(direction=direction, raw_command=command)
            
            # Fuzzy match
            matches = difflib.get_close_matches(
                direction,
                available_exits,
                n=1,
                cutoff=self.CUTOFF
            )
            
            if matches:
                matched_direction = matches[0]
                logger.debug(f"Fuzzy matched direction: '{direction}' -> '{matched_direction}'")
                return MoveAction(direction=matched_direction, raw_command=command)
        
        # No context or no match, return as-is
        return MoveAction(direction=direction, raw_command=command)
    
    def _parse_take(
        self,
        command: str,
        tokens: List[str],
        scene: Optional[Scene]
    ) -> Action:
        """
        Parse a take/get command.
        
        Args:
            command: The raw command string.
            tokens: Remaining tokens after command word.
            scene: Optional current scene for context.
        
        Returns:
            A TakeAction or UnknownAction.
        
        Examples:
            >>> parser = CommandParser()
            >>> action = parser._parse_take("take medkit", ["medkit"], None)
            >>> action.item_id
            'medkit'
        """
        if not tokens:
            logger.debug("Take command missing item")
            return UnknownAction(
                raw_command=command,
                suggestion="take <item>"
            )
        
        item_name = ' '.join(tokens)
        
        # If we have scene context, try to match against available items
        if scene and scene.items:
            item = self._find_item_in_scene(item_name, scene)
            if item:
                return TakeAction(item_id=item.id, raw_command=command)
        
        # No context or no match, use the name as-is
        return TakeAction(item_id=item_name, raw_command=command)
    
    def _parse_drop(
        self,
        command: str,
        tokens: List[str],
        game_state: Optional[GameState]
    ) -> Action:
        """
        Parse a drop command.
        
        Args:
            command: The raw command string.
            tokens: Remaining tokens after command word.
            game_state: Optional game state for inventory context.
        
        Returns:
            A DropAction or UnknownAction.
        
        Examples:
            >>> parser = CommandParser()
            >>> action = parser._parse_drop("drop sword", ["sword"], None)
            >>> action.item_id
            'sword'
        """
        if not tokens:
            logger.debug("Drop command missing item")
            return UnknownAction(
                raw_command=command,
                suggestion="drop <item>"
            )
        
        item_name = ' '.join(tokens)
        
        # If we have game state, try to match against inventory
        if game_state and game_state.inventory:
            matches = difflib.get_close_matches(
                item_name,
                game_state.inventory,
                n=1,
                cutoff=self.CUTOFF
            )
            if matches:
                matched_item = matches[0]
                logger.debug(f"Fuzzy matched inventory item: '{item_name}' -> '{matched_item}'")
                return DropAction(item_id=matched_item, raw_command=command)
        
        # No context or no match, use the name as-is
        return DropAction(item_id=item_name, raw_command=command)
    
    def _parse_use(
        self,
        command: str,
        tokens: List[str],
        game_state: Optional[GameState],
        scene: Optional[Scene]
    ) -> Action:
        """
        Parse a use command.
        
        Handles both "use item" and "use item on target" formats.
        
        Args:
            command: The raw command string.
            tokens: Remaining tokens after command word.
            game_state: Optional game state for inventory context.
            scene: Optional current scene for context.
        
        Returns:
            A UseAction or UnknownAction.
        
        Examples:
            >>> parser = CommandParser()
            >>> action = parser._parse_use("use medkit", ["medkit"], None, None)
            >>> action.item_id
            'medkit'
            
            >>> action = parser._parse_use("use key on door", ["key", "on", "door"], None, None)
            >>> action.item_id
            'key'
            >>> action.target_id
            'door'
        """
        if not tokens:
            logger.debug("Use command missing item")
            return UnknownAction(
                raw_command=command,
                suggestion="use <item> [on <target>]"
            )
        
        # Look for "on" or "with" to separate item from target
        item_tokens = []
        target_tokens = []
        found_separator = False
        
        for i, token in enumerate(tokens):
            if token in ['on', 'with', 'to']:
                found_separator = True
                item_tokens = tokens[:i]
                target_tokens = tokens[i+1:]
                break
        
        if not found_separator:
            item_tokens = tokens
        
        item_name = ' '.join(item_tokens)
        target_name = ' '.join(target_tokens) if target_tokens else None
        
        # Try to match item against inventory if we have game state
        item_id = item_name
        if game_state and game_state.inventory:
            matches = difflib.get_close_matches(
                item_name,
                game_state.inventory,
                n=1,
                cutoff=self.CUTOFF
            )
            if matches:
                item_id = matches[0]
                logger.debug(f"Fuzzy matched use item: '{item_name}' -> '{item_id}'")
        
        # Try to match target against scene items/NPCs if we have scene
        target_id = target_name
        if target_name and scene:
            # Check items
            if scene.items:
                item = self._find_item_in_scene(target_name, scene)
                if item:
                    target_id = item.id
            # Check NPCs
            if scene.npcs and target_id == target_name:
                npc = self._find_npc_in_scene(target_name, scene)
                if npc:
                    target_id = npc.id
        
        return UseAction(item_id=item_id, target_id=target_id, raw_command=command)
    
    def _parse_look(
        self,
        command: str,
        tokens: List[str],
        scene: Optional[Scene]
    ) -> Action:
        """
        Parse a look/examine command.
        
        Args:
            command: The raw command string.
            tokens: Remaining tokens after command word.
            scene: Optional current scene for context.
        
        Returns:
            A LookAction.
        
        Examples:
            >>> parser = CommandParser()
            >>> action = parser._parse_look("look", [], None)
            >>> action.target is None
            True
            
            >>> action = parser._parse_look("examine console", ["console"], None)
            >>> action.target
            'console'
        """
        if not tokens:
            # Just "look" - examine the scene
            return LookAction(raw_command=command)
        
        # Filter out common words
        filter_words = {'at', 'the', 'a', 'an'}
        filtered_tokens = [t for t in tokens if t not in filter_words]
        
        if not filtered_tokens:
            return LookAction(raw_command=command)
        
        target_name = ' '.join(filtered_tokens)
        
        # Try to match against scene items/NPCs if we have scene
        target_id = target_name
        if scene:
            # Check items
            if scene.items:
                item = self._find_item_in_scene(target_name, scene)
                if item:
                    target_id = item.id
            # Check NPCs
            if scene.npcs and target_id == target_name:
                npc = self._find_npc_in_scene(target_name, scene)
                if npc:
                    target_id = npc.id
        
        return LookAction(target=target_id, raw_command=command)
    
    def _parse_talk(
        self,
        command: str,
        tokens: List[str],
        scene: Optional[Scene]
    ) -> Action:
        """
        Parse a talk command.
        
        Handles formats like:
        - "talk to guard"
        - "ask guard about quest"
        - "tell guard about problem"
        
        Args:
            command: The raw command string.
            tokens: Remaining tokens after command word.
            scene: Optional current scene for context.
        
        Returns:
            A TalkAction or UnknownAction.
        
        Examples:
            >>> parser = CommandParser()
            >>> action = parser._parse_talk("talk to guard", ["to", "guard"], None)
            >>> action.npc_id
            'guard'
            
            >>> action = parser._parse_talk("ask guard about quest", ["guard", "about", "quest"], None)
            >>> action.npc_id
            'guard'
            >>> action.topic
            'quest'
        """
        if not tokens:
            logger.debug("Talk command missing NPC")
            return UnknownAction(
                raw_command=command,
                suggestion="talk to <NPC>"
            )
        
        # Remove common prepositions
        filter_words = {'to', 'with'}
        filtered_tokens = [t for t in tokens if t not in filter_words]
        
        if not filtered_tokens:
            return UnknownAction(
                raw_command=command,
                suggestion="talk to <NPC>"
            )
        
        # Look for "about" to separate NPC from topic
        npc_tokens = []
        topic_tokens = []
        found_about = False
        
        for i, token in enumerate(filtered_tokens):
            if token == 'about':
                found_about = True
                npc_tokens = filtered_tokens[:i]
                topic_tokens = filtered_tokens[i+1:]
                break
        
        if not found_about:
            npc_tokens = filtered_tokens
        
        npc_name = ' '.join(npc_tokens)
        topic = ' '.join(topic_tokens) if topic_tokens else None
        
        # Try to match NPC against scene NPCs if we have scene
        npc_id = npc_name
        if scene and scene.npcs:
            npc = self._find_npc_in_scene(npc_name, scene)
            if npc:
                npc_id = npc.id
                logger.debug(f"Matched NPC: '{npc_name}' -> '{npc_id}'")
        
        return TalkAction(npc_id=npc_id, topic=topic, raw_command=command)
    
    def _find_item_in_scene(self, item_name: str, scene: Scene) -> Optional[Item]:
        """
        Find an item in the scene by name or ID using fuzzy matching.
        
        Args:
            item_name: The name or ID to search for.
            scene: The scene to search in.
        
        Returns:
            The matching Item object, or None if not found.
        
        Examples:
            >>> from space_hulk_game.engine import Scene, Item
            >>> item = Item(id="medkit", name="Medical Kit", description="A medkit.")
            >>> scene = Scene(id="room", name="Room", description="A room.", items=[item])
            >>> parser = CommandParser()
            >>> found = parser._find_item_in_scene("medkit", scene)
            >>> found.id
            'medkit'
        """
        # Try exact match on ID first
        for item in scene.items:
            if item.id.lower() == item_name.lower():
                return item
        
        # Try exact match on name
        for item in scene.items:
            if item.name.lower() == item_name.lower():
                return item
        
        # Try fuzzy match on ID
        item_ids = [item.id.lower() for item in scene.items]
        matches = difflib.get_close_matches(
            item_name.lower(),
            item_ids,
            n=1,
            cutoff=self.CUTOFF
        )
        
        if matches:
            for item in scene.items:
                if item.id.lower() == matches[0]:
                    logger.debug(f"Fuzzy matched item ID: '{item_name}' -> '{item.id}'")
                    return item
        
        # Try fuzzy match on name
        item_names = [item.name.lower() for item in scene.items]
        matches = difflib.get_close_matches(
            item_name.lower(),
            item_names,
            n=1,
            cutoff=self.CUTOFF
        )
        
        if matches:
            for item in scene.items:
                if item.name.lower() == matches[0]:
                    logger.debug(f"Fuzzy matched item name: '{item_name}' -> '{item.name}'")
                    return item
        
        return None
    
    def _find_npc_in_scene(self, npc_name: str, scene: Scene) -> Optional[NPC]:
        """
        Find an NPC in the scene by name or ID using fuzzy matching.
        
        Args:
            npc_name: The name or ID to search for.
            scene: The scene to search in.
        
        Returns:
            The matching NPC object, or None if not found.
        
        Examples:
            >>> from space_hulk_game.engine import Scene, NPC
            >>> npc = NPC(id="guard", name="Imperial Guard", description="A guard.")
            >>> scene = Scene(id="room", name="Room", description="A room.", npcs=[npc])
            >>> parser = CommandParser()
            >>> found = parser._find_npc_in_scene("guard", scene)
            >>> found.id
            'guard'
        """
        # Try exact match on ID first
        for npc in scene.npcs:
            if npc.id.lower() == npc_name.lower():
                return npc
        
        # Try exact match on name
        for npc in scene.npcs:
            if npc.name.lower() == npc_name.lower():
                return npc
        
        # Try fuzzy match on ID
        npc_ids = [npc.id.lower() for npc in scene.npcs]
        matches = difflib.get_close_matches(
            npc_name.lower(),
            npc_ids,
            n=1,
            cutoff=self.CUTOFF
        )
        
        if matches:
            for npc in scene.npcs:
                if npc.id.lower() == matches[0]:
                    logger.debug(f"Fuzzy matched NPC ID: '{npc_name}' -> '{npc.id}'")
                    return npc
        
        # Try fuzzy match on name
        npc_names = [npc.name.lower() for npc in scene.npcs]
        matches = difflib.get_close_matches(
            npc_name.lower(),
            npc_names,
            n=1,
            cutoff=self.CUTOFF
        )
        
        if matches:
            for npc in scene.npcs:
                if npc.name.lower() == matches[0]:
                    logger.debug(f"Fuzzy matched NPC name: '{npc_name}' -> '{npc.name}'")
                    return npc
        
        return None
