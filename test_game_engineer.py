#!/usr/bin/env python3
"""
Quick test of the GameEngineerAgent transformation.

This script manually tests the GameEngineerAgent's ability to transform
existing narrative content into playable game structure.
"""

import json
import logging
from pathlib import Path
from typing import Any, cast

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_json(filepath: Path) -> dict[str, Any]:
    """Load JSON file."""
    with filepath.open() as f:
        return cast("dict[str, Any]", json.load(f))


def test_transformation():
    """Test transforming narrative content to game structure."""

    logger.info("Loading existing narrative content...")

    # Load existing generated content
    game_config_dir = Path("game-config")

    narrative_map = load_json(game_config_dir / "narrative_map.json")
    scene_texts = load_json(game_config_dir / "scene_texts.json")

    logger.info(f"Loaded narrative map with {len(narrative_map['narrative_map']['scenes'])} scenes")
    logger.info(f"Loaded scene texts with {len(scene_texts['scene_texts']['scenes'])} scenes")

    # Transform to game structure (manual simulation)
    logger.info("\nTransforming to game structure...")

    game_structure = {
        "game": {
            "title": "Space Hulk: Echoes of the Void",
            "description": "A text-based adventure in the Warhammer 40K universe",
            "starting_scene": narrative_map["narrative_map"]["start_scene"],
            "scenes": {},
            "global_items": {},
            "global_npcs": {},
            "endings": [],
        }
    }

    # Transform each scene
    for scene_id, narrative_scene in narrative_map["narrative_map"]["scenes"].items():
        logger.info(f"  Processing scene: {scene_id}")

        # Get full description from scene_texts
        scene_text = scene_texts["scene_texts"]["scenes"].get(scene_id, {})

        # Convert connections to exits
        exits = {}
        for idx, connection in enumerate(narrative_scene.get("connections", [])):
            target = connection.get("target")
            if target:
                # Simple mapping: use ordinal directions or "forward"
                direction = ["forward", "north", "east", "south", "west"][idx % 5]
                exits[direction] = target

        # Extract NPCs from character moments and dialogue
        npcs = []
        for dialogue_entry in scene_text.get("dialogue", []):
            speaker = dialogue_entry.get("speaker")
            if speaker and speaker not in [npc["name"] for npc in npcs]:
                npc_id = f"npc_{speaker.lower().replace(' ', '_').replace('-', '_')}"
                npcs.append(
                    {
                        "id": npc_id,
                        "name": speaker,
                        "description": f"{speaker} is present in this scene",
                        "dialogue": {"greeting": dialogue_entry.get("text", "...")},
                    }
                )

        # Create scene object
        game_scene = {
            "id": scene_id,
            "name": narrative_scene.get("name", "Unknown"),
            "description": scene_text.get("description", narrative_scene.get("description", "")),
            "exits": exits,
            "items": [],  # Would extract from puzzle_design
            "npcs": npcs,
            "events": [],
            "dark": False,
            "locked_exits": {},
        }

        game_structure["game"]["scenes"][scene_id] = game_scene

    # Add ending scene to endings array
    final_scene_id = "scene_010_desperate_escape"
    if final_scene_id in game_structure["game"]["scenes"]:
        game_structure["game"]["endings"].append(
            {
                "id": "ending_escape",
                "scene_id": final_scene_id,
                "name": "Desperate Escape",
                "description": "Final push for extraction",
                "ending_type": "victory",
            }
        )

    logger.info(f"\nTransformed {len(game_structure['game']['scenes'])} scenes")
    logger.info(
        f"Created {sum(len(s['npcs']) for s in game_structure['game']['scenes'].values())} NPCs"
    )
    logger.info(f"Created {len(game_structure['game']['endings'])} endings")

    # Save result
    output_file = game_config_dir / "playable_game_test.json"
    with output_file.open("w") as f:
        json.dump(game_structure, f, indent=2)

    logger.info(f"\n✅ Saved playable game structure to: {output_file}")

    # Validate structure
    logger.info("\nValidating game structure...")
    starting_scene = game_structure["game"]["starting_scene"]
    scenes = game_structure["game"]["scenes"]

    if starting_scene not in scenes:
        logger.error(f"❌ Starting scene '{starting_scene}' not found in scenes!")
    else:
        logger.info(f"✅ Starting scene '{starting_scene}' exists")

    # Check reachability (simple)
    reachable = {starting_scene}
    to_visit = [starting_scene]

    while to_visit:
        current = to_visit.pop(0)
        for exit_target in scenes[current]["exits"].values():
            if exit_target not in reachable and exit_target in scenes:
                reachable.add(exit_target)
                to_visit.append(exit_target)

    unreachable = set(scenes.keys()) - reachable

    if unreachable:
        logger.warning(f"⚠️  Unreachable scenes: {unreachable}")
    else:
        logger.info(f"✅ All {len(scenes)} scenes are reachable!")

    return game_structure


if __name__ == "__main__":
    test_transformation()
