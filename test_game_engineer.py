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
        # Define direction pairs for bidirectional mapping
        DIRECTION_PAIRS = {
            "forward": "backward",
            "backward": "forward",
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east",
        }
        DIRECTIONS = ["forward", "north", "east", "south", "west"]
        for idx, connection in enumerate(narrative_scene.get("connections", [])):
            target = connection.get("target")
            if target:
                direction = DIRECTIONS[idx % len(DIRECTIONS)]
                exits[direction] = target
                # Ensure bidirectional exit in the target scene
                # Initialize target scene in game_structure if not already present
                if target not in game_structure["game"]["scenes"]:
                    # Try to get the narrative and text for the target scene
                    target_narrative = narrative_map["narrative_map"]["scenes"].get(target, {})
                    target_text = scene_texts["scene_texts"]["scenes"].get(target, {})
                    game_structure["game"]["scenes"][target] = {
                        "id": target,
                        "name": target_narrative.get("name", "Unknown"),
                        "description": target_text.get(
                            "description", target_narrative.get("description", "")
                        ),
                        "exits": {},
                        "items": [],
                        "npcs": [],
                        "events": [],
                        "dark": False,
                        "locked_exits": {},
                    }
                # Add the reverse exit to the target scene
                reverse_direction = DIRECTION_PAIRS.get(direction)
                if reverse_direction:
                    target_exits = game_structure["game"]["scenes"][target].setdefault("exits", {})
                    # Only add if not already present to avoid overwriting
                    if reverse_direction not in target_exits:
                        target_exits[reverse_direction] = scene_id

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
    # Dynamically determine the final scene ID
    # Try to find a scene marked as final, else pick the last scene by sorted order
    scenes_dict = game_structure["game"]["scenes"]
    # Option 1: Look for a scene with a name or property indicating it's the final scene
    final_scene_id = None
    for sid, scene in scenes_dict.items():
        if (
            "final" in scene["name"].lower()
            or "confrontation" in scene["name"].lower()
            or "escape" in scene["name"].lower()
        ):
            final_scene_id = sid
            break
    # Option 2: Fallback to last scene by sorted order if not found
    if not final_scene_id:
        final_scene_id = sorted(scenes_dict.keys())[-1]
    if final_scene_id in scenes_dict:
        game_structure["game"]["endings"].append(
            {
                "id": "ending_escape",
                "scene_id": final_scene_id,
                "name": scenes_dict[final_scene_id]["name"],
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
