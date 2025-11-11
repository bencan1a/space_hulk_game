"""Pydantic models for scene text validation.

This module defines the schema for validating scene text outputs including
scene descriptions, atmosphere, examination texts, dialogue, and narrative notes.
"""

from pydantic import BaseModel, Field, field_validator


class SceneDialogue(BaseModel):
    """A dialogue line in a scene.

    Attributes:
        speaker: Name of the character speaking.
        text: The dialogue text.
        emotion: Optional emotion or delivery style.
        context: Optional context for when this dialogue occurs.

    Example:
        >>> dialogue = SceneDialogue(
        ...     speaker="Brother-Captain Tyberius",
        ...     text="Status report! Comm-link non-responsive...",
        ...     emotion="Commanding, urgent",
        ...     context="As the drop pod shudders violently..."
        ... )
    """

    speaker: str = Field(..., min_length=1, max_length=200, description="Character name")
    text: str = Field(..., min_length=5, description="Dialogue text")
    emotion: str | None = Field(
        default=None, max_length=500, description="Optional emotion or delivery style"
    )
    context: str | None = Field(default=None, description="Optional context for the dialogue")


class SceneText(BaseModel):
    """Text content for a single scene.

    This includes all descriptive text, atmosphere, examination texts,
    dialogue, and narrative notes for a scene.

    Attributes:
        name: Human-readable scene name.
        description: Main scene description.
        atmosphere: Atmospheric tags or description.
        initial_text: Text shown when entering the scene.
        examination_texts: Dictionary of object names to examination descriptions.
        dialogue: List of dialogue in this scene.
        narrative_notes: Optional notes about the scene's narrative purpose.

    Example:
        >>> scene_text = SceneText(
        ...     name="The Drop Pod Descent",
        ...     description="The void screeches a cacophony of tortured metal...",
        ...     atmosphere="Chaotic, violent, disorienting, ominous",
        ...     initial_text="Impact imminent! Brace for uncontrolled descent!",
        ...     examination_texts={"comms_array": "The integral vox-caster array..."},
        ...     dialogue=[SceneDialogue(...), ...],
        ...     narrative_notes="This scene establishes the immediate chaos..."
        ... )
    """

    name: str = Field(..., min_length=1, max_length=200, description="Human-readable scene name")
    description: str = Field(..., min_length=50, description="Main scene description")
    atmosphere: str = Field(
        ..., min_length=10, max_length=500, description="Atmospheric description or tags"
    )
    initial_text: str = Field(..., min_length=10, description="Text shown when entering the scene")
    examination_texts: dict[str, str] = Field(
        default_factory=dict, description="Dictionary of examinable objects to descriptions"
    )
    dialogue: list[SceneDialogue] = Field(
        default_factory=list, description="List of dialogue in this scene"
    )
    narrative_notes: str | None = Field(
        default=None, min_length=20, description="Optional narrative purpose notes"
    )

    @field_validator("examination_texts")
    @classmethod
    def validate_examination_texts(cls, v: dict[str, str]) -> dict[str, str]:
        """Ensure all examination texts are non-empty."""
        for key, value in v.items():
            if not key.strip():
                raise ValueError("Examination text keys must be non-empty")
            if not value.strip() or len(value) < 10:
                raise ValueError(f"Examination text for '{key}' must be at least 10 characters")
        return v


class SceneTexts(BaseModel):
    """Collection of all scene texts in the game.

    This is the top-level model representing all scene text content
    organized by scene ID.

    Attributes:
        scenes: Dictionary mapping scene IDs to SceneText objects.

    Example:
        >>> scene_texts = SceneTexts(
        ...     scenes={
        ...         "scene_drop_pod_descent": SceneText(...),
        ...         "scene_whispers_in_the_dark": SceneText(...)
        ...     }
        ... )
    """

    scenes: dict[str, SceneText] = Field(
        ..., min_length=1, description="Dictionary of scene_id to SceneText (minimum 1 scene)"
    )

    @field_validator("scenes")
    @classmethod
    def validate_scene_ids(cls, v: dict[str, SceneText]) -> dict[str, SceneText]:
        """Ensure all scene IDs follow naming convention."""
        for scene_id in v:
            if not scene_id.replace("_", "").replace("-", "").isalnum():
                raise ValueError(
                    f"Scene ID '{scene_id}' must contain only alphanumeric characters, "
                    f"underscores, and hyphens"
                )
        return v

    @field_validator("scenes")
    @classmethod
    def validate_scene_names_match_keys(cls, v: dict[str, SceneText]) -> dict[str, SceneText]:
        """Validate that scene texts are properly structured.

        This ensures scenes have sufficient content and quality.
        """
        for scene_id, scene_text in v.items():
            # Ensure description is substantive
            if len(scene_text.description) < 100:
                raise ValueError(
                    f"Scene '{scene_id}' description should be at least 100 characters for immersion"
                )

            # Ensure initial text is meaningful
            if len(scene_text.initial_text) < 20:
                raise ValueError(
                    f"Scene '{scene_id}' initial_text should be at least 20 characters"
                )

        return v


# Example usage and validation
if __name__ == "__main__":
    # Example from the actual YAML file
    example_scene_texts = SceneTexts(
        scenes={
            "scene_drop_pod_descent": SceneText(
                name="The Drop Pod Descent",
                description="The void screeches a cacophony of tortured metal and strained ceramite as the drop pod lances through the orbital debris...",
                atmosphere="Chaotic, violent, disorienting, ominous, foreboding.",
                initial_text="Impact imminent! Brace for uncontrolled descent!",
                examination_texts={
                    "comms_array": "The integral vox-caster array is spitting static, an angry electrical current buzzing against your gauntlet. Severely damaged, only faint, distorted whispers pierce the din.",
                    "drop_pod_hatch": "The massive ceramite hatch is buckled inwards at one corner, scorch marks marring its integrity. It remains sealed for now, a flimsy barrier against the void and whatever primordial horrors await.",
                },
                dialogue=[
                    SceneDialogue(
                        speaker="Brother-Captain Tyberius",
                        text="Status report! Comm-link non-responsive. Valerius, Xylos, Theron, confirm vitals!",
                        emotion="Commanding, urgent",
                        context="As the drop pod shudders violently from impacts.",
                    ),
                    SceneDialogue(
                        speaker="Brother Valerius",
                        text="All systems nominal, Captain! Eager for contact! Let the Xenos come!",
                        emotion="Anticipatory, aggressive",
                        context="A growl in his voice, even through the vox.",
                    ),
                ],
                narrative_notes="This scene establishes the immediate chaos and danger of the insertion. It introduces the squad members and their initial reactions, sets the claustrophobic and grimdark tone, and immediately highlights the isolation and the pervasive Warp influence.",
            ),
            "scene_whispers_in_the_dark": SceneText(
                name="Whispers in the Dark",
                description="The emergency lights, ancient and feeble, bleed weak pools of amber light into the oppressive gloom of the Hulk's corridors. They flicker erratically, casting elongated, dancing shadows that seem to writhe with malevolent life...",
                atmosphere="Ominous, horrifying, tense, claustrophobic, grim.",
                initial_text="The darkness presses in, alive with unseen horrors. The stench of decay and something far fouler fills the air.",
                examination_texts={
                    "grotesque_murals": "Crude, yet disturbingly detailed, charnel-house art. They depict Xenos worshipped as gods, their vile forms rendered with disturbing reverence by mutated hands. A perversion of faith."
                },
                dialogue=[],
                narrative_notes="This scene introduces the primary Xenos threat (Genestealers) and establishes their brutality. The decaying remains of previous expeditions reinforce the overwhelming odds and grim nature of the mission.",
            ),
        }
    )

    print(f"✅ Scene texts validation successful: {len(example_scene_texts.scenes)} scenes")
