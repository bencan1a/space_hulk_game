"""Pydantic models for puzzle design validation.

This module defines the schema for validating puzzle design outputs including
puzzles, artifacts, monsters, NPCs, and overall puzzle design structure.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class PuzzleStep(BaseModel):
    """A single step in solving a puzzle.
    
    This model accepts either a plain string or a dict with 'step' key
    to match the YAML format.
    
    Attributes:
        step: Description of the step to perform.
    
    Example:
        >>> step = PuzzleStep(
        ...     step="Locate the auxiliary power conduit junction..."
        ... )
    """
    
    step: str = Field(
        ...,
        min_length=10,
        description="Description of the puzzle step"
    )


class PuzzleSolution(BaseModel):
    """Solution structure for a puzzle.
    
    Attributes:
        type: Type of solution (e.g., 'multi-step', 'observation', 'timed').
        steps: List of steps to solve the puzzle.
    
    Example:
        >>> solution = PuzzleSolution(
        ...     type="multi-step_interaction_and_logic",
        ...     steps=[PuzzleStep(...), ...]
        ... )
    """
    
    type: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Type of puzzle solution"
    )
    steps: List[PuzzleStep] = Field(
        ...,
        min_length=1,
        description="Steps to solve the puzzle (at least 1)"
    )
    
    @field_validator('steps', mode='before')
    @classmethod
    def convert_string_steps(cls, v):
        """Convert plain string steps to PuzzleStep objects."""
        if isinstance(v, list):
            result = []
            for item in v:
                if isinstance(item, str):
                    result.append(PuzzleStep(step=item))
                elif isinstance(item, dict):
                    result.append(PuzzleStep(**item))
                else:
                    result.append(item)
            return result
        return v


class Puzzle(BaseModel):
    """A puzzle in the game.
    
    Attributes:
        id: Unique identifier for the puzzle.
        name: Human-readable puzzle name.
        description: Detailed description of the puzzle.
        location: Scene ID where the puzzle is located.
        narrative_purpose: Why this puzzle exists narratively.
        solution: Solution structure for the puzzle.
        difficulty: Difficulty level (e.g., 'easy', 'medium', 'hard').
    
    Example:
        >>> puzzle = Puzzle(
        ...     id="puzzle_comm_relay_restore",
        ...     name="Comm-Relay Restoration",
        ...     description="The damaged drop pod's auxiliary comm-relay...",
        ...     location="scene_drop_pod_descent",
        ...     narrative_purpose="Reinforces Tyberius's struggle...",
        ...     solution=PuzzleSolution(...),
        ...     difficulty="medium"
        ... )
    """
    
    id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Unique puzzle identifier"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Human-readable puzzle name"
    )
    description: str = Field(
        ...,
        min_length=50,
        description="Detailed puzzle description"
    )
    location: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Scene ID where puzzle is located"
    )
    narrative_purpose: str = Field(
        ...,
        min_length=20,
        description="Why this puzzle exists narratively"
    )
    solution: PuzzleSolution = Field(
        ...,
        description="Puzzle solution structure"
    )
    difficulty: str = Field(
        ...,
        pattern="^(easy|medium|hard)$",
        description="Difficulty level: easy, medium, or hard"
    )
    
    @field_validator('id')
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Ensure id follows naming convention."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                "ID must contain only alphanumeric characters, underscores, and hyphens"
            )
        return v


class ArtifactProperty(BaseModel):
    """A property of an artifact.
    
    Attributes:
        property: Description of the artifact property.
    
    Example:
        >>> prop = ArtifactProperty(
        ...     property="minor moral boost (if worn or kept)"
        ... )
    """
    
    property: str = Field(
        ...,
        min_length=5,
        description="Artifact property description"
    )


class Artifact(BaseModel):
    """An artifact that can be found in the game.
    
    Attributes:
        id: Unique identifier for the artifact.
        name: Human-readable artifact name.
        description: Detailed description of the artifact.
        location: Scene ID where the artifact is located.
        narrative_significance: Why this artifact is narratively important.
        properties: List of artifact properties or effects.
    
    Example:
        >>> artifact = Artifact(
        ...     id="artifact_blood_eagle_pendant",
        ...     name="Blood Eagle Pendant",
        ...     description="A tarnished, but resilient, bronze pendant...",
        ...     location="scene_whispers_in_the_dark",
        ...     narrative_significance="Serves as a grim reminder...",
        ...     properties=[ArtifactProperty(...)]
        ... )
    """
    
    id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Unique artifact identifier"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Human-readable artifact name"
    )
    description: str = Field(
        ...,
        min_length=20,
        description="Detailed artifact description"
    )
    location: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Scene ID where artifact is located"
    )
    narrative_significance: str = Field(
        ...,
        min_length=20,
        description="Narrative importance of this artifact"
    )
    properties: List[ArtifactProperty] = Field(
        ...,
        min_length=1,
        description="Artifact properties (at least 1)"
    )
    
    @field_validator('id')
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Ensure id follows naming convention."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                "ID must contain only alphanumeric characters, underscores, and hyphens"
            )
        return v


class Monster(BaseModel):
    """A monster or enemy in the game.
    
    Attributes:
        id: Unique identifier for the monster.
        name: Human-readable monster name.
        description: Detailed description of the monster.
        locations: List of scene IDs where this monster appears.
        narrative_role: The monster's role in the narrative.
        abilities: List of the monster's special abilities.
    
    Example:
        >>> monster = Monster(
        ...     id="monster_feral_genestealer",
        ...     name="Feral Genestealer",
        ...     description="The common Genestealer strain...",
        ...     locations=["scene_whispers_in_the_dark", ...],
        ...     narrative_role="The baseline, ever-present Xenos threat...",
        ...     abilities=["Fast Attack", "Rending Claws"]
        ... )
    """
    
    id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Unique monster identifier"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Human-readable monster name"
    )
    description: str = Field(
        ...,
        min_length=20,
        description="Detailed monster description"
    )
    locations: List[str] = Field(
        ...,
        min_length=1,
        description="Scene IDs where monster appears (at least 1)"
    )
    narrative_role: str = Field(
        ...,
        min_length=20,
        description="Monster's narrative role"
    )
    abilities: List[str] = Field(
        ...,
        min_length=1,
        description="Monster abilities (at least 1)"
    )
    
    @field_validator('id')
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Ensure id follows naming convention."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                "ID must contain only alphanumeric characters, underscores, and hyphens"
            )
        return v
    
    @field_validator('abilities')
    @classmethod
    def validate_abilities_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure all abilities are non-empty strings."""
        if not all(ability.strip() for ability in v):
            raise ValueError("All abilities must be non-empty strings")
        return v


class NPC(BaseModel):
    """A non-player character in the game.
    
    Attributes:
        id: Unique identifier for the NPC.
        name: Human-readable NPC name.
        role: The NPC's role in the game.
        description: Detailed description of the NPC.
        locations: List of scene IDs where this NPC appears.
        dialogue_themes: List of themes or topics the NPC discusses.
    
    Example:
        >>> npc = NPC(
        ...     id="npc_brother_captain_tyberius",
        ...     name="Brother-Captain Tyberius",
        ...     role="Player Character / Squad Leader",
        ...     description="The player embodies Tyberius...",
        ...     locations=["all_scenes"],
        ...     dialogue_themes=["Duty and Sacrifice", "The Burden of Command"]
        ... )
    """
    
    id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Unique NPC identifier"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Human-readable NPC name"
    )
    role: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="NPC's role in the game"
    )
    description: str = Field(
        ...,
        min_length=20,
        description="Detailed NPC description"
    )
    locations: List[str] = Field(
        ...,
        min_length=1,
        description="Scene IDs where NPC appears (at least 1)"
    )
    dialogue_themes: List[str] = Field(
        ...,
        min_length=1,
        description="Dialogue themes (at least 1)"
    )
    
    @field_validator('id')
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Ensure id follows naming convention."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                "ID must contain only alphanumeric characters, underscores, and hyphens"
            )
        return v
    
    @field_validator('dialogue_themes')
    @classmethod
    def validate_themes_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure all dialogue themes are non-empty strings."""
        if not all(theme.strip() for theme in v):
            raise ValueError("All dialogue themes must be non-empty strings")
        return v


class PuzzleDesign(BaseModel):
    """Complete puzzle design for a game.
    
    This is the top-level model representing all puzzles, artifacts,
    monsters, and NPCs in the game.
    
    Attributes:
        puzzles: List of puzzles in the game.
        artifacts: List of artifacts that can be found.
        monsters: List of monsters/enemies in the game.
        npcs: List of non-player characters.
    
    Example:
        >>> puzzle_design = PuzzleDesign(
        ...     puzzles=[Puzzle(...), ...],
        ...     artifacts=[Artifact(...), ...],
        ...     monsters=[Monster(...), ...],
        ...     npcs=[NPC(...), ...]
        ... )
    """
    
    puzzles: List[Puzzle] = Field(
        ...,
        min_length=1,
        description="Puzzles in the game (at least 1)"
    )
    artifacts: List[Artifact] = Field(
        ...,
        min_length=1,
        description="Artifacts in the game (at least 1)"
    )
    monsters: List[Monster] = Field(
        ...,
        min_length=1,
        description="Monsters in the game (at least 1)"
    )
    npcs: List[NPC] = Field(
        ...,
        min_length=1,
        description="NPCs in the game (at least 1)"
    )
    
    @field_validator('puzzles')
    @classmethod
    def validate_puzzle_ids_unique(cls, v: List[Puzzle]) -> List[Puzzle]:
        """Ensure all puzzle IDs are unique."""
        ids = [puzzle.id for puzzle in v]
        if len(ids) != len(set(ids)):
            raise ValueError("All puzzle IDs must be unique")
        return v
    
    @field_validator('artifacts')
    @classmethod
    def validate_artifact_ids_unique(cls, v: List[Artifact]) -> List[Artifact]:
        """Ensure all artifact IDs are unique."""
        ids = [artifact.id for artifact in v]
        if len(ids) != len(set(ids)):
            raise ValueError("All artifact IDs must be unique")
        return v
    
    @field_validator('monsters')
    @classmethod
    def validate_monster_ids_unique(cls, v: List[Monster]) -> List[Monster]:
        """Ensure all monster IDs are unique."""
        ids = [monster.id for monster in v]
        if len(ids) != len(set(ids)):
            raise ValueError("All monster IDs must be unique")
        return v
    
    @field_validator('npcs')
    @classmethod
    def validate_npc_ids_unique(cls, v: List[NPC]) -> List[NPC]:
        """Ensure all NPC IDs are unique."""
        ids = [npc.id for npc in v]
        if len(ids) != len(set(ids)):
            raise ValueError("All NPC IDs must be unique")
        return v


# Example usage and validation
if __name__ == "__main__":
    # Example from the actual YAML file
    example_puzzle_design = PuzzleDesign(
        puzzles=[
            Puzzle(
                id="puzzle_comm_relay_restore",
                name="Comm-Relay Restoration",
                description="The damaged drop pod's auxiliary comm-relay needs manual recalibration...",
                location="scene_drop_pod_descent",
                narrative_purpose="Reinforces Tyberius's struggle with command...",
                solution=PuzzleSolution(
                    type="multi-step_interaction_and_logic",
                    steps=[
                        PuzzleStep(step_text="Locate the auxiliary power conduit junction...")
                    ]
                ),
                difficulty="medium"
            )
        ],
        artifacts=[
            Artifact(
                id="artifact_blood_eagle_pendant",
                name="Blood Eagle Pendant",
                description="A tarnished, but resilient, bronze pendant...",
                location="scene_whispers_in_the_dark",
                narrative_significance="Serves as a grim reminder of previous failures...",
                properties=[
                    ArtifactProperty(property="minor moral boost (if worn or kept)")
                ]
            )
        ],
        monsters=[
            Monster(
                id="monster_feral_genestealer",
                name="Feral Genestealer",
                description="The common Genestealer strain. Swift, multi-limbed...",
                locations=["scene_whispers_in_the_dark"],
                narrative_role="The baseline, ever-present Xenos threat...",
                abilities=["Fast Attack", "Rending Claws", "Stealthy Ambush"]
            )
        ],
        npcs=[
            NPC(
                id="npc_brother_captain_tyberius",
                name="Brother-Captain Tyberius",
                role="Player Character / Squad Leader",
                description="The player embodies Tyberius. A veteran of countless campaigns...",
                locations=["all_scenes"],
                dialogue_themes=["Duty and Sacrifice", "The Burden of Command"]
            )
        ]
    )
    
    print(f"✅ Puzzle design validation successful: {len(example_puzzle_design.puzzles)} puzzles")
