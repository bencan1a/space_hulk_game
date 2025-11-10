#!/usr/bin/env python
"""
Demo script showing ContentLoader integration with TextAdventureEngine.

This demonstrates the complete pipeline from AI-generated YAML files
to a playable text adventure game.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from space_hulk_game.engine import ContentLoader, TextAdventureEngine, GameState


def main():
    """Run the demo."""
    print("=" * 70)
    print("Space Hulk Game - Content Loader Demo")
    print("=" * 70)
    print()
    
    # Load game data from fixtures
    fixtures_dir = Path(__file__).parent / "fixtures"
    print(f"Loading game content from: {fixtures_dir}")
    print()
    
    loader = ContentLoader()
    try:
        game_data = loader.load_game(str(fixtures_dir))
    except Exception as e:
        print(f"Error loading game: {e}")
        return 1
    
    # Display game information
    print("Game Loaded Successfully!")
    print("-" * 70)
    print(f"Title: {game_data.title}")
    print(f"Description: {game_data.description[:100]}...")
    print()
    print(f"Scenes: {len(game_data.scenes)}")
    for scene_id, scene in list(game_data.scenes.items())[:3]:
        print(f"  - {scene.name} ({scene_id})")
    if len(game_data.scenes) > 3:
        print(f"  ... and {len(game_data.scenes) - 3} more")
    print()
    print(f"Themes: {', '.join(game_data.themes)}")
    print(f"Plot Points: {len(game_data.plot_points)}")
    print(f"Possible Endings: {len(game_data.endings)}")
    print()
    print(f"Global Items: {len(game_data.global_items)}")
    print(f"Global NPCs: {len(game_data.global_npcs)}")
    print()
    
    # Show scene connectivity
    print("Scene Graph:")
    print("-" * 70)
    for scene_id, scene in game_data.scenes.items():
        exits_str = ", ".join(
            f"{dir}->{target}" for dir, target in scene.exits.items()
        ) if scene.exits else "none"
        dark_marker = " [DARK]" if scene.dark else ""
        locked_marker = f" [LOCKED: {', '.join(scene.locked_exits.keys())}]" if scene.locked_exits else ""
        print(f"{scene.name}{dark_marker}{locked_marker}")
        print(f"  Exits: {exits_str}")
        if scene.items:
            items_str = ", ".join(item.name for item in scene.items)
            print(f"  Items: {items_str}")
        if scene.npcs:
            npcs_str = ", ".join(npc.name for npc in scene.npcs)
            print(f"  NPCs: {npcs_str}")
        print()
    
    # Show that it integrates with TextAdventureEngine
    print("Integration with TextAdventureEngine:")
    print("-" * 70)
    
    # Create initial game state
    initial_state = GameState(
        current_scene=game_data.starting_scene,
        visited_scenes={game_data.starting_scene}
    )
    
    # Create engine
    engine = TextAdventureEngine(initial_state, game_data.scenes)
    
    print(f"Engine initialized with {len(game_data.scenes)} scenes")
    print(f"Starting scene: {game_data.starting_scene}")
    print()
    
    # Show starting scene description
    starting_scene = game_data.get_scene(game_data.starting_scene)
    print("Starting Scene Description:")
    print(starting_scene.get_full_description())
    print()
    print(starting_scene.get_exit_description())
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print()
    print("The ContentLoader successfully:")
    print("  ✓ Loaded all 5 YAML files")
    print("  ✓ Converted YAML to engine objects (Scene, Item, NPC)")
    print("  ✓ Created playable GameData structure")
    print("  ✓ Integrated with TextAdventureEngine")
    print()
    print("Game Statistics:")
    print(f"  - {len(game_data.scenes)} scenes with {sum(len(s.exits) for s in game_data.scenes.values())} connections")
    print(f"  - {len(game_data.global_items)} items")
    print(f"  - {len(game_data.global_npcs)} NPCs")
    print(f"  - {len(game_data.themes)} narrative themes")
    print(f"  - {len(game_data.endings)} possible endings")
    print()
    print("Next steps:")
    print("  - Run AI agents to generate new content")
    print("  - Load generated content with ContentLoader")
    print("  - Play the generated game with engine.run()!")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
