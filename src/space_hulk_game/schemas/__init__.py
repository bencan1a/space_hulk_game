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

from space_hulk_game.schemas.game_mechanics import (
    CombatMechanic,
    CombatSystem,
    GameMechanics,
    GameState,
    GameSystems,
    InteractionSystem,
    InventorySystem,
    LoseCondition,
    MovementSystem,
    TechnicalRequirement,
    TrackedVariable,
    WinCondition,
)
from space_hulk_game.schemas.narrative_map import (
    CharacterArc,
    CharacterArcStage,
    CharacterMoment,
    Connection,
    DecisionOption,
    DecisionPoint,
    NarrativeMap,
    Scene,
)
from space_hulk_game.schemas.plot_outline import (
    Character,
    Conflict,
    PlotBranch,
    PlotOutline,
    PlotPoint,
)
from space_hulk_game.schemas.puzzle_design import (
    NPC,
    Artifact,
    ArtifactProperty,
    Monster,
    Puzzle,
    PuzzleDesign,
    PuzzleSolution,
    PuzzleStep,
)
from space_hulk_game.schemas.scene_text import (
    SceneDialogue,
    SceneText,
    SceneTexts,
)

__all__ = [
    "NPC",
    "Artifact",
    "ArtifactProperty",
    "Character",
    "CharacterArc",
    "CharacterArcStage",
    "CharacterMoment",
    "CombatMechanic",
    "CombatSystem",
    "Conflict",
    "Connection",
    "DecisionOption",
    "DecisionPoint",
    "GameMechanics",
    "GameState",
    "GameSystems",
    "InteractionSystem",
    "InventorySystem",
    "LoseCondition",
    "Monster",
    # Game Mechanics models
    "MovementSystem",
    "NarrativeMap",
    # Plot Outline models
    "PlotBranch",
    "PlotOutline",
    "PlotPoint",
    # Puzzle Design models
    "Puzzle",
    "PuzzleDesign",
    "PuzzleSolution",
    "PuzzleStep",
    # Narrative Map models
    "Scene",
    # Scene Text models
    "SceneDialogue",
    "SceneText",
    "SceneTexts",
    "TechnicalRequirement",
    "TrackedVariable",
    "WinCondition",
]
