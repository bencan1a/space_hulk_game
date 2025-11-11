"""Pydantic models for narrative map validation.

This module defines the schema for validating narrative map outputs including
scenes, connections, character moments, decision points, and character arcs.
"""

from pydantic import BaseModel, Field, field_validator


class CharacterMoment(BaseModel):
    """A significant character moment within a scene.

    Attributes:
        character: Name of the character experiencing the moment.
        moment: Description of what happens to the character in this scene.

    Example:
        >>> moment = CharacterMoment(
        ...     character="Brother-Captain Tyberius",
        ...     moment="Struggles to re-establish comms and locate his dispersed squad..."
        ... )
    """

    character: str = Field(..., min_length=1, max_length=200, description="Character name")
    moment: str = Field(..., min_length=20, description="Description of the character moment")


class Connection(BaseModel):
    """A connection from one scene to another.

    Attributes:
        target: ID of the target scene.
        description: Description of why/how the player transitions.
        condition: Optional condition that must be met for this connection.

    Example:
        >>> conn = Connection(
        ...     target="scene_whispers_in_the_dark",
        ...     description="Proceed deeper into the Hulk...",
        ...     condition=None
        ... )
    """

    target: str = Field(..., min_length=1, max_length=200, description="Target scene ID")
    description: str = Field(..., min_length=20, description="Description of the transition")
    condition: str | None = Field(
        default=None, max_length=500, description="Optional condition for this connection"
    )


class DecisionOption(BaseModel):
    """An option in a decision point.

    Attributes:
        choice: The text of the decision choice.
        outcome: What happens if this choice is selected.
        target_scene: The scene ID this choice leads to.

    Example:
        >>> option = DecisionOption(
        ...     choice="Initiate self-destruct sequence on the alien core",
        ...     outcome="The squad prepares for their final, desperate stand...",
        ...     target_scene="scene_climax_core_overload"
        ... )
    """

    choice: str = Field(..., min_length=10, description="The decision choice text")
    outcome: str = Field(..., min_length=20, description="What happens if this choice is selected")
    target_scene: str = Field(
        ..., min_length=1, max_length=200, description="Target scene ID for this choice"
    )


class DecisionPoint(BaseModel):
    """A decision point in the narrative.

    Attributes:
        id: Unique identifier for the decision point.
        prompt: The decision prompt presented to the player.
        options: List of available choices.

    Example:
        >>> decision = DecisionPoint(
        ...     id="decision_hulk_fate",
        ...     prompt="The Serpent's Coil must be stopped. How do you attempt to avert this catastrophe?",
        ...     options=[...]
        ... )
    """

    id: str = Field(
        ..., min_length=1, max_length=200, description="Unique decision point identifier"
    )
    prompt: str = Field(..., min_length=20, description="The decision prompt text")
    options: list[DecisionOption] = Field(
        ..., min_length=2, description="Available decision options (minimum 2)"
    )

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Ensure id follows naming convention."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "ID must contain only alphanumeric characters, underscores, and hyphens"
            )
        return v


class Scene(BaseModel):
    """A scene in the narrative map.

    Attributes:
        name: Human-readable scene name.
        description: Detailed description of what happens in the scene.
        connections: List of connections to other scenes.
        character_moments: Optional list of character moments in this scene.
        decision_points: Optional list of decision points in this scene.

    Example:
        >>> scene = Scene(
        ...     name="The Drop Pod Descent",
        ...     description="Deployed from the Battle Barge...",
        ...     connections=[...],
        ...     character_moments=[...]
        ... )
    """

    name: str = Field(..., min_length=1, max_length=200, description="Human-readable scene name")
    description: str = Field(..., min_length=50, description="Detailed scene description")
    connections: list[Connection] = Field(
        default_factory=list, description="Connections to other scenes"
    )
    character_moments: list[CharacterMoment] | None = Field(
        default=None, description="Character moments in this scene"
    )
    decision_points: list[DecisionPoint] | None = Field(
        default=None, description="Decision points in this scene"
    )


class CharacterArcStage(BaseModel):
    """A stage in a character's narrative arc.

    Attributes:
        stage: Name of the arc stage (e.g., 'Beginning', 'Development', 'Climax/Resolution').
        description: Description of the character's state at this stage.

    Example:
        >>> stage = CharacterArcStage(
        ...     stage="Beginning",
        ...     description="Jaded but fiercely loyal, carries the burden of command..."
        ... )
    """

    stage: str = Field(
        ..., min_length=1, max_length=200, description="Stage name in the character arc"
    )
    description: str = Field(
        ..., min_length=20, description="Description of character state at this stage"
    )


class CharacterArc(BaseModel):
    """Complete arc for a character across the narrative.

    Attributes:
        character: Name of the character.
        arc_stages: List of stages in the character's development.

    Example:
        >>> arc = CharacterArc(
        ...     character="Brother-Captain Tyberius",
        ...     arc_stages=[...]
        ... )
    """

    character: str = Field(..., min_length=1, max_length=200, description="Character name")
    arc_stages: list[CharacterArcStage] = Field(
        ..., min_length=1, description="Stages in the character's arc (at least 1)"
    )


class NarrativeMap(BaseModel):
    """Complete narrative map for a story.

    This is the top-level model representing the entire narrative structure
    including all scenes, connections, and character arcs.

    Attributes:
        start_scene: ID of the starting scene.
        scenes: Dictionary mapping scene IDs to Scene objects.
        character_arcs: Optional list of character development arcs.

    Example:
        >>> narrative_map = NarrativeMap(
        ...     start_scene="scene_drop_pod_descent",
        ...     scenes={
        ...         "scene_drop_pod_descent": Scene(...),
        ...         "scene_whispers_in_the_dark": Scene(...)
        ...     },
        ...     character_arcs=[...]
        ... )
    """

    start_scene: str = Field(
        ..., min_length=1, max_length=200, description="ID of the starting scene"
    )
    scenes: dict[str, Scene] = Field(
        ..., min_length=1, description="Dictionary of scene_id to Scene (minimum 1 scene)"
    )
    character_arcs: list[CharacterArc] | None = Field(
        default=None, description="Optional character development arcs"
    )

    @field_validator("start_scene")
    @classmethod
    def validate_start_scene_exists(cls, v: str, _info) -> str:
        """Ensure start_scene exists in scenes dictionary.

        Note: This validator runs before 'scenes' field is populated in Pydantic v2,
        so we can only do basic format validation here. Cross-field validation
        should be done via model_validator.
        """
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "start_scene must contain only alphanumeric characters, underscores, and hyphens"
            )
        return v

    @field_validator("scenes")
    @classmethod
    def validate_scene_ids(cls, v: dict[str, Scene]) -> dict[str, Scene]:
        """Ensure all scene IDs are valid and all connections reference existing scenes."""
        # Validate scene ID format
        for scene_id in v:
            if not scene_id.replace("_", "").replace("-", "").isalnum():
                raise ValueError(
                    f"Scene ID '{scene_id}' must contain only alphanumeric characters, "
                    f"underscores, and hyphens"
                )

        # Validate all connection targets exist
        all_scene_ids = set(v.keys())
        for scene_id, scene in v.items():
            for connection in scene.connections:
                if connection.target not in all_scene_ids:
                    raise ValueError(
                        f"Scene '{scene_id}' has connection to non-existent scene '{connection.target}'"
                    )

            # Validate decision point targets exist
            if scene.decision_points:
                for decision in scene.decision_points:
                    for option in decision.options:
                        if option.target_scene not in all_scene_ids:
                            raise ValueError(
                                f"Decision point '{decision.id}' in scene '{scene_id}' "
                                f"has option leading to non-existent scene '{option.target_scene}'"
                            )

        return v


# Example usage and validation
if __name__ == "__main__":
    # Example from the actual YAML file
    example_narrative_map = NarrativeMap(
        start_scene="scene_drop_pod_descent",
        scenes={
            "scene_drop_pod_descent": Scene(
                name="The Drop Pod Descent",
                description="Deployed from the Battle Barge, your Terminator squad crashes onto 'The Serpent's Coil'...",
                connections=[
                    Connection(
                        target="scene_whispers_in_the_dark",
                        description="Proceed deeper into the Hulk, seeking your scattered squadmates...",
                    )
                ],
                character_moments=[
                    CharacterMoment(
                        character="Brother-Captain Tyberius",
                        moment="Struggles to re-establish comms and locate his dispersed squad...",
                    )
                ],
            ),
            "scene_whispers_in_the_dark": Scene(
                name="Whispers in the Dark",
                description="Navigating twisted corridors, the flickering emergency lights reveal grotesque murals...",
                connections=[],
                character_moments=[],
            ),
        },
        character_arcs=[
            CharacterArc(
                character="Brother-Captain Tyberius",
                arc_stages=[
                    CharacterArcStage(
                        stage="Beginning",
                        description="Jaded but fiercely loyal, carries the burden of command...",
                    )
                ],
            )
        ],
    )

    print(f"✅ Narrative map validation successful: {len(example_narrative_map.scenes)} scenes")
