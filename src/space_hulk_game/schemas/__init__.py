"""Pydantic schema models for Space Hulk Game output validation.

This package contains comprehensive Pydantic models for validating all
generated game content including plot outlines, narrative maps, puzzles,
scene texts, and game mechanics.

Each model includes:
- Field-level validation with constraints (min/max length, patterns, etc.)
- Custom validators for complex business rules
- Type hints for all fields
- Google-style docstrings with examples
"""

from space_hulk_game.schemas.plot_outline import (
    PlotBranch,
    PlotPoint,
    Character,
    Conflict,
    PlotOutline,
)
from space_hulk_game.schemas.narrative_map import (
    Scene,
    Connection,
    CharacterMoment,
    DecisionPoint,
    DecisionOption,
    CharacterArcStage,
    CharacterArc,
    NarrativeMap,
)
from space_hulk_game.schemas.puzzle_design import (
    Puzzle,
    PuzzleSolution,
    PuzzleStep,
    Artifact,
    ArtifactProperty,
    Monster,
    NPC,
    PuzzleDesign,
)
from space_hulk_game.schemas.scene_text import (
    SceneDialogue,
    SceneText,
    SceneTexts,
)
from space_hulk_game.schemas.game_mechanics import (
    MovementSystem,
    InventorySystem,
    CombatSystem,
    CombatMechanic,
    InteractionSystem,
    GameSystems,
    TrackedVariable,
    WinCondition,
    LoseCondition,
    GameState,
    TechnicalRequirement,
    GameMechanics,
)

__all__ = [
    # Plot Outline models
    "PlotBranch",
    "PlotPoint",
    "Character",
    "Conflict",
    "PlotOutline",
    # Narrative Map models
    "Scene",
    "Connection",
    "CharacterMoment",
    "DecisionPoint",
    "DecisionOption",
    "CharacterArcStage",
    "CharacterArc",
    "NarrativeMap",
    # Puzzle Design models
    "Puzzle",
    "PuzzleSolution",
    "PuzzleStep",
    "Artifact",
    "ArtifactProperty",
    "Monster",
    "NPC",
    "PuzzleDesign",
    # Scene Text models
    "SceneDialogue",
    "SceneText",
    "SceneTexts",
    # Game Mechanics models
    "MovementSystem",
    "InventorySystem",
    "CombatSystem",
    "CombatMechanic",
    "InteractionSystem",
    "GameSystems",
    "TrackedVariable",
    "WinCondition",
    "LoseCondition",
    "GameState",
    "TechnicalRequirement",
    "GameMechanics",
]
