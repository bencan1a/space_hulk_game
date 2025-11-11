"""Pydantic models for game mechanics validation.

This module defines the schema for validating game mechanics outputs including
game systems, state management, win/lose conditions, and technical requirements.
"""


from pydantic import BaseModel, Field, field_validator


class GameSystemCommands(BaseModel):
    """Commands available in a game system.

    This is a simple wrapper to ensure commands are valid.
    """

    commands: list[str] = Field(
        ...,
        min_length=1,
        description="List of available commands (at least 1)"
    )

    @field_validator('commands')
    @classmethod
    def validate_commands_not_empty(cls, v: list[str]) -> list[str]:
        """Ensure all commands are non-empty strings."""
        if not all(cmd.strip() for cmd in v):
            raise ValueError("All commands must be non-empty strings")
        return v


class CombatMechanic(BaseModel):
    """A specific combat mechanic or rule.

    Attributes:
        name: Name of the combat mechanic.
        rules: Description of how the mechanic works.

    Example:
        >>> mechanic = CombatMechanic(
        ...     name="Overwatch",
        ...     rules="Set a character to fire upon enemies entering their line of sight..."
        ... )
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Mechanic name"
    )
    rules: str = Field(
        ...,
        min_length=20,
        description="Description of mechanic rules"
    )


class MovementSystem(BaseModel):
    """Movement system configuration.

    Attributes:
        description: Description of how movement works.
        commands: List of movement commands.
        narrative_purpose: Why this system exists narratively.

    Example:
        >>> movement = MovementSystem(
        ...     description="Tactical grid-based movement with limited action points...",
        ...     commands=["move", "brace", "breach"],
        ...     narrative_purpose="Reinforces the claustrophobic and dangerous environment..."
        ... )
    """

    description: str = Field(
        ...,
        min_length=50,
        description="Description of movement system"
    )
    commands: list[str] = Field(
        ...,
        min_length=1,
        description="Movement commands (at least 1)"
    )
    narrative_purpose: str = Field(
        ...,
        min_length=50,
        description="Narrative purpose of movement system"
    )


class InventorySystem(BaseModel):
    """Inventory system configuration.

    Attributes:
        description: Description of how inventory works.
        capacity: Maximum number of items that can be carried.
        commands: List of inventory commands.
        narrative_purpose: Why this system exists narratively.

    Example:
        >>> inventory = InventorySystem(
        ...     description="Limited capacity inventory for each Space Marine...",
        ...     capacity=5,
        ...     commands=["take", "drop", "use"],
        ...     narrative_purpose="Scarcity of resources drives the survival theme..."
        ... )
    """

    description: str = Field(
        ...,
        min_length=50,
        description="Description of inventory system"
    )
    capacity: int = Field(
        ...,
        ge=1,
        le=100,
        description="Maximum inventory capacity (1-100)"
    )
    commands: list[str] = Field(
        ...,
        min_length=1,
        description="Inventory commands (at least 1)"
    )
    narrative_purpose: str = Field(
        ...,
        min_length=50,
        description="Narrative purpose of inventory system"
    )


class CombatSystem(BaseModel):
    """Combat system configuration.

    Attributes:
        description: Description of how combat works.
        mechanics: List of specific combat mechanics.
        narrative_purpose: Why this system exists narratively.

    Example:
        >>> combat = CombatSystem(
        ...     description="Turn-based tactical combat. Features cover systems...",
        ...     mechanics=[CombatMechanic(...), ...],
        ...     narrative_purpose="The tactical, turn-based nature supports survival theme..."
        ... )
    """

    description: str = Field(
        ...,
        min_length=50,
        description="Description of combat system"
    )
    mechanics: list[CombatMechanic] = Field(
        ...,
        min_length=1,
        description="Combat mechanics (at least 1)"
    )
    narrative_purpose: str = Field(
        ...,
        min_length=50,
        description="Narrative purpose of combat system"
    )


class InteractionSystem(BaseModel):
    """Interaction system configuration.

    Attributes:
        description: Description of how interaction works.
        commands: List of interaction commands.
        narrative_purpose: Why this system exists narratively.

    Example:
        >>> interaction = InteractionSystem(
        ...     description="Allows players to interact with objects, environments...",
        ...     commands=["examine", "talk", "use", "analyze"],
        ...     narrative_purpose="'Examine' allows players to uncover crucial lore..."
        ... )
    """

    description: str = Field(
        ...,
        min_length=50,
        description="Description of interaction system"
    )
    commands: list[str] = Field(
        ...,
        min_length=1,
        description="Interaction commands (at least 1)"
    )
    narrative_purpose: str = Field(
        ...,
        min_length=50,
        description="Narrative purpose of interaction system"
    )


class GameSystems(BaseModel):
    """All game systems configuration.

    Attributes:
        movement: Movement system configuration.
        inventory: Inventory system configuration.
        combat: Combat system configuration.
        interaction: Interaction system configuration.

    Example:
        >>> systems = GameSystems(
        ...     movement=MovementSystem(...),
        ...     inventory=InventorySystem(...),
        ...     combat=CombatSystem(...),
        ...     interaction=InteractionSystem(...)
        ... )
    """

    movement: MovementSystem = Field(..., description="Movement system")
    inventory: InventorySystem = Field(..., description="Inventory system")
    combat: CombatSystem = Field(..., description="Combat system")
    interaction: InteractionSystem = Field(..., description="Interaction system")


class TrackedVariable(BaseModel):
    """A tracked game state variable.

    Attributes:
        variable: Name of the variable being tracked.
        purpose: Description of what the variable tracks and why.

    Example:
        >>> var = TrackedVariable(
        ...     variable="squad_morale",
        ...     purpose="Tracks the overall mental state of the squad..."
        ... )
    """

    variable: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Variable name"
    )
    purpose: str = Field(
        ...,
        min_length=20,
        description="Purpose and impact of the variable"
    )


class WinCondition(BaseModel):
    """A win condition for the game.

    Attributes:
        condition: Description of the win condition.

    Example:
        >>> win = WinCondition(
        ...     condition="Successfully neutralize the threat posed by 'The Serpent's Coil'..."
        ... )
    """

    condition: str = Field(
        ...,
        min_length=20,
        description="Description of the win condition"
    )


class LoseCondition(BaseModel):
    """A lose condition for the game.

    Attributes:
        condition: Description of the lose condition.

    Example:
        >>> lose = LoseCondition(
        ...     condition="All squad members are incapacitated or killed in combat."
        ... )
    """

    condition: str = Field(
        ...,
        min_length=20,
        description="Description of the lose condition"
    )


class GameState(BaseModel):
    """Game state management configuration.

    Attributes:
        tracked_variables: List of variables being tracked.
        win_conditions: List of win conditions.
        lose_conditions: List of lose conditions.

    Example:
        >>> state = GameState(
        ...     tracked_variables=[TrackedVariable(...), ...],
        ...     win_conditions=[WinCondition(...), ...],
        ...     lose_conditions=[LoseCondition(...), ...]
        ... )
    """

    tracked_variables: list[TrackedVariable] = Field(
        ...,
        min_length=1,
        description="Tracked variables (at least 1)"
    )
    win_conditions: list[WinCondition] = Field(
        ...,
        min_length=1,
        description="Win conditions (at least 1)"
    )
    lose_conditions: list[LoseCondition] = Field(
        ...,
        min_length=1,
        description="Lose conditions (at least 1)"
    )


class TechnicalRequirement(BaseModel):
    """A technical requirement for the game.

    Attributes:
        requirement: Description of the technical requirement.
        justification: Why this requirement is necessary.

    Example:
        >>> req = TechnicalRequirement(
        ...     requirement="Robust AI for diverse enemy types...",
        ...     justification="Crucial for making combat challenging and varied..."
        ... )
    """

    requirement: str = Field(
        ...,
        min_length=20,
        description="Technical requirement description"
    )
    justification: str = Field(
        ...,
        min_length=20,
        description="Justification for the requirement"
    )


class GameMechanics(BaseModel):
    """Complete game mechanics and design document.

    This is the top-level model representing the entire game mechanics
    specification including systems, state management, and technical requirements.

    Attributes:
        game_title: Title of the game.
        game_systems: All game systems configuration.
        game_state: Game state management configuration.
        technical_requirements: List of technical requirements.

    Example:
        >>> mechanics = GameMechanics(
        ...     game_title="Space Hulk: Echoes of the Void",
        ...     game_systems=GameSystems(...),
        ...     game_state=GameState(...),
        ...     technical_requirements=[TechnicalRequirement(...), ...]
        ... )
    """

    game_title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Title of the game"
    )
    game_systems: GameSystems = Field(
        ...,
        description="Game systems configuration"
    )
    game_state: GameState = Field(
        ...,
        description="Game state management"
    )
    technical_requirements: list[TechnicalRequirement] = Field(
        ...,
        min_length=1,
        description="Technical requirements (at least 1)"
    )


# Example usage and validation
if __name__ == "__main__":
    # Example from the actual YAML file
    example_game_mechanics = GameMechanics(
        game_title="Space Hulk: Echoes of the Void",
        game_systems=GameSystems(
            movement=MovementSystem(
                description="Tactical grid-based movement with limited action points per turn. Incorporates environmental hazards...",
                commands=["move", "brace", "breach"],
                narrative_purpose="Reinforces the claustrophobic and dangerous environment of the Space Hulk..."
            ),
            inventory=InventorySystem(
                description="Limited capacity inventory for each Space Marine, reflecting their Terminator armor's storage...",
                capacity=5,
                commands=["take", "drop", "use"],
                narrative_purpose="Scarcity of resources (ammo, medkits) drives the 'Survival against overwhelming odds'..."
            ),
            combat=CombatSystem(
                description="Turn-based tactical combat. Features cover systems, line of sight...",
                mechanics=[
                    CombatMechanic(
                        name="Overwatch",
                        rules="Set a character to fire upon enemies entering their line of sight during the enemy turn..."
                    )
                ],
                narrative_purpose="The tactical, turn-based nature, coupled with overwhelming odds..."
            ),
            interaction=InteractionSystem(
                description="Allows players to interact with objects, environments, and even character-specific internal thoughts...",
                commands=["examine", "talk", "use", "analyze"],
                narrative_purpose="'Examine' and 'Analyze' allow players to uncover crucial lore..."
            )
        ),
        game_state=GameState(
            tracked_variables=[
                TrackedVariable(
                    variable="squad_morale",
                    purpose="Tracks the overall mental state of the squad, influenced by combat outcomes..."
                )
            ],
            win_conditions=[
                WinCondition(
                    condition="Successfully neutralize the threat posed by 'The Serpent's Coil'..."
                )
            ],
            lose_conditions=[
                LoseCondition(
                    condition="All squad members are incapacitated or killed in combat."
                )
            ]
        ),
        technical_requirements=[
            TechnicalRequirement(
                requirement="Robust AI for diverse enemy types with distinct attack patterns...",
                justification="Crucial for making combat challenging and varied, reinforcing themes..."
            )
        ]
    )

    print(f"✅ Game mechanics validation successful: {example_game_mechanics.game_title}")
