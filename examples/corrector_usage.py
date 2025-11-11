#!/usr/bin/env python
"""Example usage of OutputCorrector for fixing YAML validation errors.

This script demonstrates how to use the OutputCorrector class to automatically
fix common validation errors in AI-generated YAML outputs.
"""

from space_hulk_game.validation import OutputCorrector


def example_plot_correction():
    """Example: Correcting a plot outline with missing fields."""
    print("\n" + "=" * 80)
    print("Example 1: Correcting Plot Outline with Missing Fields")
    print("=" * 80)

    corrector = OutputCorrector()

    # Invalid plot YAML - missing plot_points
    invalid_plot = """
title: "The Lost Colony"
setting: "A mysterious abandoned colony ship drifting through deep space."
themes:
  - "isolation"
  - "mystery"
tone: "Dark and suspenseful"
characters:
  - name: "Captain Elena Rodriguez"
    role: "Ship Captain"
    backstory: "A veteran explorer haunted by past failures on deep space missions."
conflicts:
  - type: "Human vs. Unknown"
    description: "The crew must uncover what happened to the colony before it happens to them."
"""

    print("\nOriginal YAML (invalid - missing plot_points):")
    print(invalid_plot[:200] + "...")

    result = corrector.correct_plot(invalid_plot)

    print("\nCorrection Result:")
    print(f"  Success: {result.success}")
    print(f"  Corrections Applied: {len(result.corrections)}")
    for correction in result.corrections:
        print(f"    • {correction}")

    if result.success:
        print("\n✓ Plot outline successfully corrected!")
        print("\nCorrected YAML preview:")
        print(result.corrected_yaml[:300] + "...")
    else:
        print("\n✗ Correction failed. Remaining errors:")
        for error in result.validation_result.errors:
            print(f"    • {error}")


def example_narrative_map_correction():
    """Example: Correcting a narrative map with invalid IDs."""
    print("\n" + "=" * 80)
    print("Example 2: Correcting Narrative Map with Invalid Scene IDs")
    print("=" * 80)

    corrector = OutputCorrector()

    # Invalid narrative map - scene IDs have spaces and special characters
    invalid_map = """
start_scene: "Opening Scene!"
scenes:
  "Opening Scene!":
    name: "Opening Scene"
    description: >
      The player awakens in a dark corridor with flickering emergency lights
      casting eerie shadows.
    connections:
      - target: "Second Scene #2"
        description: "Proceed down the corridor"
  "Second Scene #2":
    name: "Second Scene"
    description: >
      A larger chamber filled with derelict machinery and strange alien
      artifacts scattered about.
    connections: []
"""

    print("\nOriginal YAML (invalid - bad scene IDs):")
    print(invalid_map[:250] + "...")

    result = corrector.correct_narrative_map(invalid_map)

    print("\nCorrection Result:")
    print(f"  Success: {result.success}")
    print(f"  Corrections Applied: {len(result.corrections)}")
    for correction in result.corrections:
        print(f"    • {correction}")

    if result.success:
        print("\n✓ Narrative map successfully corrected!")


def example_puzzle_design_correction():
    """Example: Correcting puzzle design with all missing fields."""
    print("\n" + "=" * 80)
    print("Example 3: Correcting Empty Puzzle Design")
    print("=" * 80)

    corrector = OutputCorrector()

    # Completely empty puzzle design
    invalid_puzzle = "{}"

    print("\nOriginal YAML (invalid - empty):")
    print(invalid_puzzle)

    result = corrector.correct_puzzle_design(invalid_puzzle)

    print("\nCorrection Result:")
    print(f"  Success: {result.success}")
    print(f"  Corrections Applied: {len(result.corrections)}")
    for correction in result.corrections:
        print(f"    • {correction}")

    if result.success:
        print("\n✓ Puzzle design successfully corrected with defaults!")
        print("\nCorrected YAML preview:")
        lines = result.corrected_yaml.split("\n")
        for line in lines[:20]:
            print(f"  {line}")
        if len(lines) > 20:
            print(f"  ... and {len(lines) - 20} more lines")


def example_scene_texts_correction():
    """Example: Correcting scene texts with descriptions too short."""
    print("\n" + "=" * 80)
    print("Example 4: Correcting Scene Texts with Short Descriptions")
    print("=" * 80)

    corrector = OutputCorrector()

    # Scene texts with descriptions that are too short
    invalid_scene = """
scenes:
  scene_entrance:
    name: "The Entrance"
    description: "Dark."
    atmosphere: "Scary."
    initial_text: "You enter."
    examination_texts:
      door: "A door."
    dialogue: []
"""

    print("\nOriginal YAML (invalid - descriptions too short):")
    print(invalid_scene)

    result = corrector.correct_scene_texts(invalid_scene)

    print("\nCorrection Result:")
    print(f"  Success: {result.success}")
    print(f"  Corrections Applied: {len(result.corrections)}")
    for correction in result.corrections:
        print(f"    • {correction}")

    if result.success:
        print("\n✓ Scene texts successfully corrected!")


def example_game_mechanics_correction():
    """Example: Correcting game mechanics with missing systems."""
    print("\n" + "=" * 80)
    print("Example 5: Correcting Game Mechanics with Missing Systems")
    print("=" * 80)

    corrector = OutputCorrector()

    # Game mechanics with only a title
    invalid_mechanics = """
game_title: "Space Adventure Game"
"""

    print("\nOriginal YAML (invalid - missing all systems):")
    print(invalid_mechanics)

    result = corrector.correct_game_mechanics(invalid_mechanics)

    print("\nCorrection Result:")
    print(f"  Success: {result.success}")
    print(f"  Corrections Applied: {len(result.corrections)}")
    for correction in result.corrections:
        print(f"    • {correction}")

    if result.success:
        print("\n✓ Game mechanics successfully corrected with all required systems!")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("OUTPUT CORRECTOR USAGE EXAMPLES")
    print("=" * 80)
    print("\nThe OutputCorrector automatically fixes common YAML validation errors:")
    print("  • Missing required fields")
    print("  • Invalid ID formats")
    print("  • Descriptions too short")
    print("  • YAML syntax errors")

    example_plot_correction()
    example_narrative_map_correction()
    example_puzzle_design_correction()
    example_scene_texts_correction()
    example_game_mechanics_correction()

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)
    print("\nFor more information, see:")
    print("  • src/space_hulk_game/validation/corrector.py")
    print("  • tests/test_corrector.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
