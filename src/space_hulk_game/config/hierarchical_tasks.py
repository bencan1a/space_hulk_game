"""
Simplified task configurations for hierarchical mode.

These tasks have shorter descriptions to prevent LLM context overflow
when the manager creates delegation prompts.
"""

# Simplified tasks for hierarchical mode
HIERARCHICAL_TASKS = {
    "GenerateOverarchingPlot": {
        "name": "Generate Plot",
        "description": "Create a plot outline for a Space Hulk adventure game with branching paths and multiple endings.",
        "expected_output": "A plot outline in YAML format with title, setting, themes, and plot branches.",
        "agent": "PlotMasterAgent",
        "output_file": "game-config/plot_outline.yaml"
    },
    
    "CreateNarrativeMap": {
        "name": "Create Narrative Map",
        "description": "Based on the plot, create a map of scenes and connections showing how the story flows.",
        "expected_output": "A narrative map in YAML format showing scenes and their connections.",
        "agent": "NarrativeArchitectAgent",
        "output_file": "game-config/narrative_map.yaml",
        "context": ["GenerateOverarchingPlot"]
    },
    
    "DesignArtifactsAndPuzzles": {
        "name": "Design Puzzles",
        "description": "Design puzzles, artifacts, and challenges that fit the story and narrative map.",
        "expected_output": "Puzzle designs in YAML format including solutions and narrative integration.",
        "agent": "PuzzleSmithAgent",
        "output_file": "game-config/puzzle_design.yaml",
        "context": ["GenerateOverarchingPlot", "CreateNarrativeMap"]
    }
}
