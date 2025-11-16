# Game Configuration

This directory contains game design configuration files that define examples and guidelines for the AI agents when generating game content.

## Contents

These JSON files serve as **product code** - they define the structure and examples that guide the CrewAI agents in creating consistent, high-quality game content:

- **plot_outline.json** - Example plot structure with branching narratives and multiple endings
- **narrative_map.json** - Example scene structure showing how scenes connect and flow
- **puzzle_design.json** - Example puzzle, artifact, NPC, and monster designs
- **scene_texts.json** - Example scene descriptions and dialogue formatting
- **prd_document.json** - Product requirements defining game mechanics and systems

## Purpose

These files are **not** generated outputs to be ignored. They are:

1. **Configuration templates** that agents use to understand the expected format
2. **Example content** showing the quality and style expected
3. **Guidelines** for maintaining consistency across generated content
4. **Product specifications** that define what the game should contain

## For Developers

When working with the CrewAI system:

- Agents read these files to understand output format requirements
- The files define the structure of agent-generated content
- Changes to these files affect how agents generate game content
- These files should be version controlled and reviewed like other code

## Relationship to tasks.yaml

The `src/space_hulk_game/config/tasks.yaml` file references these files in `output_file` settings, telling agents where to write their generated content based on these templates. The agents generate JSON output files instead of YAML for the game engine to load.
