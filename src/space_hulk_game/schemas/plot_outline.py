"""Pydantic models for plot outline validation.

This module defines the schema for validating plot outline outputs including
narrative foundation elements such as plot points, characters, conflicts,
and overall story structure.
"""

from pydantic import BaseModel, Field, field_validator


class PlotPoint(BaseModel):
    """A significant event or milestone in the narrative.

    Attributes:
        id: Unique identifier for the plot point (e.g., 'pp_01_insertion').
        name: Short, descriptive name for the plot point.
        description: Detailed description of what happens in this plot point.

    Example:
        >>> plot_point = PlotPoint(
        ...     id="pp_01_insertion",
        ...     name="The Drop Pod Descent",
        ...     description="A squad of elite Space Marine Terminators..."
        ... )
    """

    id: str = Field(
        ..., min_length=1, max_length=100, description="Unique identifier for the plot point"
    )
    name: str = Field(..., min_length=1, max_length=200, description="Short descriptive name")
    description: str = Field(
        ..., min_length=50, description="Detailed description of the plot point"
    )

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Ensure id follows naming convention (lowercase, underscores)."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "ID must contain only alphanumeric characters, underscores, and hyphens"
            )
        return v


class Character(BaseModel):
    """A character in the narrative.

    Attributes:
        name: Full name of the character.
        role: The character's role or position in the story.
        backstory: Background and history of the character.
        conflicts: Optional list of internal or external conflicts.

    Example:
        >>> character = Character(
        ...     name="Brother-Captain Tyberius",
        ...     role="Squad Leader, Blood Angels Terminator",
        ...     backstory="Tyberius has seen entire worlds fall..."
        ... )
    """

    name: str = Field(..., min_length=1, max_length=200, description="Full name of the character")
    role: str = Field(..., min_length=1, max_length=300, description="Character's role or position")
    backstory: str = Field(..., min_length=50, description="Character background and history")
    conflicts: list[str] | None = Field(
        default=None, description="Optional character-specific conflicts"
    )


class Conflict(BaseModel):
    """A conflict or tension in the narrative.

    Attributes:
        type: Type of conflict (e.g., 'Man vs. Xenos', 'Man vs. Self').
        description: Detailed description of the conflict.

    Example:
        >>> conflict = Conflict(
        ...     type="Man vs. Xenos",
        ...     description="The primary and most immediate conflict..."
        ... )
    """

    type: str = Field(..., min_length=1, max_length=200, description="Type or category of conflict")
    description: str = Field(..., min_length=50, description="Detailed description of the conflict")


class PlotBranch(BaseModel):
    """A branching path in the narrative structure.

    This represents a decision point or alternative story path that
    diverges from the main narrative.

    Attributes:
        path: Identifier for the branch path.
        description: Description of what happens on this branch.
        decision_point: Optional plot point ID where the branch occurs.

    Example:
        >>> branch = PlotBranch(
        ...     path="heroic_sacrifice",
        ...     description="The squad chooses to destroy the core...",
        ...     decision_point="decision_hulk_fate"
        ... )
    """

    path: str = Field(..., min_length=1, max_length=200, description="Branch path identifier")
    description: str = Field(..., min_length=50, description="Description of the branch narrative")
    decision_point: str | None = Field(
        default=None, description="ID of the plot point where this branch occurs"
    )


class PlotOutline(BaseModel):
    """Complete plot outline for a narrative.

    This is the top-level model representing the entire narrative foundation
    including title, setting, themes, plot points, characters, and conflicts.

    Attributes:
        title: Title of the narrative.
        setting: Description of the setting/world.
        themes: List of major themes explored.
        tone: Overall tone and atmosphere.
        plot_points: Chronological list of major plot events.
        characters: List of major characters.
        conflicts: List of major conflicts in the narrative.
        plot_branches: Optional list of alternative narrative paths.

    Example:
        >>> outline = PlotOutline(
        ...     title="Space Hulk: Echoes of the Void",
        ...     setting="The grimdark universe of Warhammer 40,000...",
        ...     themes=["Survival against overwhelming odds", "Duty versus conscience"],
        ...     tone="Bleak, claustrophobic, survival horror",
        ...     plot_points=[...],
        ...     characters=[...],
        ...     conflicts=[...]
        ... )
    """

    title: str = Field(..., min_length=1, max_length=200, description="Title of the narrative")
    setting: str = Field(
        ..., min_length=50, description="Detailed description of the setting and world"
    )
    themes: list[str] = Field(
        ..., min_length=1, description="List of major themes (at least 1 required)"
    )
    tone: str = Field(..., min_length=10, max_length=500, description="Overall tone and atmosphere")
    plot_points: list[PlotPoint] = Field(
        ..., min_length=3, description="Chronological list of major plot events (minimum 3)"
    )
    characters: list[Character] = Field(
        ..., min_length=1, description="List of major characters (at least 1 required)"
    )
    conflicts: list[Conflict] = Field(
        ..., min_length=1, description="List of major conflicts (at least 1 required)"
    )
    plot_branches: list[PlotBranch] | None = Field(
        default=None, description="Optional alternative narrative paths"
    )

    @field_validator("themes")
    @classmethod
    def validate_themes_not_empty(cls, v: list[str]) -> list[str]:
        """Ensure all themes are non-empty strings."""
        if not all(theme.strip() for theme in v):
            raise ValueError("All themes must be non-empty strings")
        return v

    @field_validator("plot_points")
    @classmethod
    def validate_plot_point_ids_unique(cls, v: list[PlotPoint]) -> list[PlotPoint]:
        """Ensure all plot point IDs are unique."""
        ids = [pp.id for pp in v]
        if len(ids) != len(set(ids)):
            raise ValueError("All plot point IDs must be unique")
        return v

    @field_validator("characters")
    @classmethod
    def validate_character_names_unique(cls, v: list[Character]) -> list[Character]:
        """Ensure all character names are unique."""
        names = [char.name for char in v]
        if len(names) != len(set(names)):
            raise ValueError("All character names must be unique")
        return v


# Example usage and validation
if __name__ == "__main__":
    # Example from the actual YAML file
    example_plot_outline = PlotOutline(
        title="Space Hulk: Echoes of the Void",
        setting="The grimdark universe of Warhammer 40,000. Players are thrust into the claustrophobic confines...",
        themes=[
            "Survival against overwhelming odds",
            "The corrupting influence of the Warp and the unknown",
            "Duty versus conscience",
        ],
        tone="Bleak, claustrophobic, survival horror, grimdark, desperate",
        plot_points=[
            PlotPoint(
                id="pp_01_insertion",
                name="The Drop Pod Descent",
                description="A squad of elite Space Marine Terminators is deployed onto 'The Serpent's Coil'...",
            ),
            PlotPoint(
                id="pp_02_first_contact",
                name="Whispers in the Dark",
                description="The scattered Terminators encounter the first Genestealers...",
            ),
            PlotPoint(
                id="pp_03_squad_recon",
                name="The Labyrinth's Embrace",
                description="The squad attempts to regroup and establish a perimeter...",
            ),
        ],
        characters=[
            Character(
                name="Brother-Captain Tyberius",
                role="Squad Leader, Blood Angels Terminator",
                backstory="Tyberius has seen entire worlds fall. His faith in the Emperor is unwavering...",
            )
        ],
        conflicts=[
            Conflict(
                type="Man vs. Xenos",
                description="The primary and most immediate conflict: the relentless battle against the Genestealer cult...",
            )
        ],
    )

    print(f"✅ Plot outline validation successful: {example_plot_outline.title}")
