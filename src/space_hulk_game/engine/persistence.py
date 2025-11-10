"""
Persistence Module

Handles saving and loading game state to/from JSON files.
Provides validation and error handling for serialization.

Example:
    >>> from space_hulk_game.engine import GameState, Scene
    >>> from space_hulk_game.engine.persistence import save_game, load_game
    >>> state = GameState(current_scene="test")
    >>> scenes = {"test": Scene(id="test", name="Test", description="Test.")}
    >>> save_game("savegame.json", state, scenes)
    >>> loaded_state, loaded_scenes = load_game("savegame.json")
"""

import json
import logging
from pathlib import Path
from typing import Dict, Tuple, Any
from datetime import datetime

from .game_state import GameState
from .scene import Scene


# Configure logging
logger = logging.getLogger(__name__)


class PersistenceError(Exception):
    """Exception raised for errors during save/load operations."""
    pass


def save_game(
    filepath: str,
    game_state: GameState,
    scenes: Dict[str, Scene],
    metadata: Dict[str, Any] = None
) -> None:
    """
    Save the game state and scenes to a JSON file.
    
    This function serializes the game state and all scenes to a JSON file,
    allowing the game to be resumed later. It includes metadata about when
    the save was created.
    
    Args:
        filepath: Path to the save file.
        game_state: The current game state to save.
        scenes: Dictionary of all scenes in the game.
        metadata: Optional additional metadata to save.
        
    Raises:
        PersistenceError: If saving fails due to serialization or I/O error.
        
    Examples:
        >>> from space_hulk_game.engine import GameState, Scene
        >>> state = GameState(current_scene="room1")
        >>> scenes = {
        ...     "room1": Scene(id="room1", name="Room", description="A room.")
        ... }
        >>> save_game("mysave.json", state, scenes)
    """
    try:
        # Prepare save data
        save_data = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
            'game_state': game_state.to_dict(),
            'scenes': {
                scene_id: scene.to_dict()
                for scene_id, scene in scenes.items()
            }
        }
        
        # Ensure directory exists
        filepath_obj = Path(filepath)
        filepath_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to file with pretty formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Game saved to: {filepath}")
        
    except (OSError, IOError) as e:
        error_msg = f"Failed to save game: {e}"
        logger.error(error_msg)
        raise PersistenceError(error_msg) from e
    
    except (TypeError, ValueError) as e:
        error_msg = f"Failed to serialize game data: {e}"
        logger.error(error_msg)
        raise PersistenceError(error_msg) from e
    
    except Exception as e:
        error_msg = f"Unexpected error during save: {e}"
        logger.error(error_msg)
        raise PersistenceError(error_msg) from e


def load_game(filepath: str) -> Tuple[GameState, Dict[str, Scene]]:
    """
    Load a game state and scenes from a JSON file.
    
    This function deserializes a previously saved game, restoring the
    game state and all scenes. It validates the save file format and
    data integrity.
    
    Args:
        filepath: Path to the save file to load.
        
    Returns:
        A tuple of (GameState, scenes_dict).
        
    Raises:
        PersistenceError: If loading fails due to file not found,
                         invalid format, or data corruption.
        
    Examples:
        >>> state, scenes = load_game("mysave.json")
        >>> state.current_scene
        'room1'
    """
    try:
        # Check if file exists
        filepath_obj = Path(filepath)
        if not filepath_obj.exists():
            raise PersistenceError(f"Save file not found: {filepath}")
        
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # Validate save file structure
        _validate_save_data(save_data)
        
        # Deserialize game state
        game_state = GameState.from_dict(save_data['game_state'])
        
        # Deserialize scenes
        scenes = {}
        for scene_id, scene_data in save_data['scenes'].items():
            scenes[scene_id] = Scene.from_dict(scene_data)
        
        logger.info(f"Game loaded from: {filepath}")
        logger.debug(f"Loaded {len(scenes)} scenes")
        
        return game_state, scenes
        
    except PersistenceError:
        # Re-raise our own exceptions
        raise
    
    except (OSError, IOError) as e:
        error_msg = f"Failed to load game: {e}"
        logger.error(error_msg)
        raise PersistenceError(error_msg) from e
    
    except (json.JSONDecodeError, ValueError) as e:
        error_msg = f"Invalid save file format: {e}"
        logger.error(error_msg)
        raise PersistenceError(error_msg) from e
    
    except KeyError as e:
        error_msg = f"Missing required data in save file: {e}"
        logger.error(error_msg)
        raise PersistenceError(error_msg) from e
    
    except Exception as e:
        error_msg = f"Unexpected error during load: {e}"
        logger.error(error_msg)
        raise PersistenceError(error_msg) from e


def _validate_save_data(save_data: Dict) -> None:
    """
    Validate the structure of save file data.
    
    Args:
        save_data: The loaded save data dictionary.
        
    Raises:
        PersistenceError: If the save data is invalid.
    """
    required_keys = ['version', 'game_state', 'scenes']
    
    for key in required_keys:
        if key not in save_data:
            raise PersistenceError(f"Save file missing required key: {key}")
    
    # Validate version (for future compatibility)
    version = save_data['version']
    if not isinstance(version, str):
        raise PersistenceError("Invalid version format")
    
    # Validate version format and check compatibility
    try:
        version_parts = version.split('.')
        if len(version_parts) < 1:
            raise PersistenceError(f"Invalid version format: {version}")
        major_version = version_parts[0]
        if not major_version.isdigit():
            raise PersistenceError(f"Invalid version format: {version}")
        if major_version != '1':
            logger.warning(f"Loading save file from different version: {version}")
    except (AttributeError, IndexError) as e:
        raise PersistenceError(f"Invalid version format: {version}") from e
    
    # Validate game_state structure
    if not isinstance(save_data['game_state'], dict):
        raise PersistenceError("Invalid game_state format")
    
    # Validate scenes structure
    if not isinstance(save_data['scenes'], dict):
        raise PersistenceError("Invalid scenes format")
    
    logger.debug("Save data validation passed")


def get_save_metadata(filepath: str) -> Dict[str, Any]:
    """
    Get metadata from a save file without loading the full game.
    
    This is useful for displaying save file information in a load menu.
    
    Args:
        filepath: Path to the save file.
        
    Returns:
        Dictionary containing save metadata (timestamp, version, etc.).
        
    Raises:
        PersistenceError: If reading metadata fails.
        
    Examples:
        >>> metadata = get_save_metadata("mysave.json")
        >>> print(metadata['timestamp'])
        '2024-01-15T14:30:00'
    """
    try:
        filepath_obj = Path(filepath)
        if not filepath_obj.exists():
            raise PersistenceError(f"Save file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        metadata = {
            'version': save_data.get('version', 'unknown'),
            'timestamp': save_data.get('timestamp', 'unknown'),
            'current_scene': save_data.get('game_state', {}).get('current_scene', 'unknown'),
            'health': save_data.get('game_state', {}).get('health', 0),
            'inventory_size': len(save_data.get('game_state', {}).get('inventory', [])),
        }
        
        # Include custom metadata if present
        if 'metadata' in save_data:
            metadata.update(save_data['metadata'])
        
        return metadata
        
    except Exception as e:
        error_msg = f"Failed to read save metadata: {e}"
        logger.error(error_msg)
        raise PersistenceError(error_msg) from e


def list_save_files(save_directory: str = "saves") -> list:
    """
    List all save files in a directory.
    
    Args:
        save_directory: Directory to search for save files.
        
    Returns:
        List of save file paths.
        
    Examples:
        >>> saves = list_save_files("saves")
        >>> for save in saves:
        ...     print(save)
        saves/autosave.json
        saves/mysave.json
    """
    try:
        save_dir = Path(save_directory)
        if not save_dir.exists():
            return []
        
        # Use a list to avoid multiple stat() calls
        save_files = []
        for file_path in save_dir.glob("*.json"):
            save_files.append((file_path, file_path.stat().st_mtime))
        
        # Sort by modification time (newest first)
        save_files.sort(key=lambda x: x[1], reverse=True)
        
        return [str(f[0]) for f in save_files]
        
    except Exception as e:
        logger.error(f"Failed to list save files: {e}")
        return []


def delete_save(filepath: str) -> None:
    """
    Delete a save file.
    
    Args:
        filepath: Path to the save file to delete.
        
    Raises:
        PersistenceError: If deletion fails.
        
    Examples:
        >>> delete_save("mysave.json")
    """
    try:
        filepath_obj = Path(filepath)
        if filepath_obj.exists():
            filepath_obj.unlink()
            logger.info(f"Deleted save file: {filepath}")
        else:
            raise PersistenceError(f"Save file not found: {filepath}")
            
    except Exception as e:
        error_msg = f"Failed to delete save file: {e}"
        logger.error(error_msg)
        raise PersistenceError(error_msg) from e


class SaveSystem:
    """
    High-level save/load system with simplified interface.
    
    This class provides an object-oriented interface to the persistence
    functions, managing save directory and file naming conventions.
    
    Attributes:
        save_dir: Directory where save files are stored.
    
    Examples:
        Create a save system:
        >>> save_system = SaveSystem("saves/")
        >>> save_system.save(game_state, "mysave")
        >>> loaded_state = save_system.load("mysave")
        >>> saves = save_system.list_saves()
    """
    
    def __init__(self, save_dir: str = "saves"):
        """
        Initialize the save system.
        
        Args:
            save_dir: Directory for save files (created if it doesn't exist).
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"SaveSystem initialized (save_dir={self.save_dir})")
    
    def save(
        self,
        game_state: GameState,
        save_name: str,
        scenes: Dict[str, Scene] = None,
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Save a game state.
        
        Args:
            game_state: Game state to save.
            save_name: Name for the save (without .json extension).
            scenes: Optional scenes dict (not needed for state-only saves).
            metadata: Optional metadata to include.
            
        Raises:
            PersistenceError: If save fails.
        """
        # Add .json extension if not present
        if not save_name.endswith('.json'):
            save_name = f"{save_name}.json"
        
        filepath = self.save_dir / save_name
        
        # For simplified saves, we only save the game state
        # Scenes will be loaded from the original game files
        save_data = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
            'game_state': game_state.to_dict(),
        }
        
        # If scenes provided, save them too (for compatibility)
        if scenes:
            save_data['scenes'] = {
                scene_id: scene.to_dict()
                for scene_id, scene in scenes.items()
            }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Game saved to: {filepath}")
            
        except Exception as e:
            error_msg = f"Failed to save game: {e}"
            logger.error(error_msg)
            raise PersistenceError(error_msg) from e
    
    def load(self, save_name: str) -> GameState:
        """
        Load a game state.
        
        Args:
            save_name: Name of the save to load (with or without .json).
            
        Returns:
            Loaded game state.
            
        Raises:
            PersistenceError: If load fails.
        """
        # Add .json extension if not present
        if not save_name.endswith('.json'):
            save_name = f"{save_name}.json"
        
        filepath = self.save_dir / save_name
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Validate basic structure
            if 'game_state' not in save_data:
                raise PersistenceError("Invalid save file: missing game_state")
            
            # Deserialize game state
            game_state = GameState.from_dict(save_data['game_state'])
            
            logger.info(f"Game loaded from: {filepath}")
            return game_state
            
        except FileNotFoundError:
            raise PersistenceError(f"Save file not found: {save_name}")
        except Exception as e:
            error_msg = f"Failed to load game: {e}"
            logger.error(error_msg)
            raise PersistenceError(error_msg) from e
    
    def list_saves(self) -> list:
        """
        List all available save files.
        
        Returns:
            List of save names (without .json extension).
        """
        try:
            save_files = []
            for file_path in self.save_dir.glob("*.json"):
                # Return just the stem (filename without extension)
                save_files.append((file_path.stem, file_path.stat().st_mtime))
            
            # Sort by modification time (newest first)
            save_files.sort(key=lambda x: x[1], reverse=True)
            
            return [f[0] for f in save_files]
            
        except Exception as e:
            logger.error(f"Failed to list save files: {e}")
            return []
    
    def delete(self, save_name: str) -> None:
        """
        Delete a save file.
        
        Args:
            save_name: Name of the save to delete (with or without .json).
            
        Raises:
            PersistenceError: If deletion fails.
        """
        # Add .json extension if not present
        if not save_name.endswith('.json'):
            save_name = f"{save_name}.json"
        
        filepath = self.save_dir / save_name
        delete_save(str(filepath))
    
    def get_metadata(self, save_name: str) -> Dict[str, Any]:
        """
        Get metadata for a save file.
        
        Args:
            save_name: Name of the save (with or without .json).
            
        Returns:
            Dictionary of metadata.
            
        Raises:
            PersistenceError: If reading metadata fails.
        """
        # Add .json extension if not present
        if not save_name.endswith('.json'):
            save_name = f"{save_name}.json"
        
        filepath = self.save_dir / save_name
        return get_save_metadata(str(filepath))
