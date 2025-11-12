"""Unit tests for game_mechanics schema models."""

import pytest
from pydantic import ValidationError

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


class TestInventorySystem:
    """Tests for InventorySystem model."""

    def test_valid_inventory_system(self):
        """Test creating valid inventory system."""
        inv = InventorySystem(
            description="A" * 50,
            capacity=5,
            commands=["take", "drop", "use"],
            narrative_purpose="B" * 50,
        )
        assert inv.capacity == 5
        assert len(inv.commands) == 3

    def test_inventory_capacity_constraints(self):
        """Test inventory capacity must be 1-100."""
        # Valid capacities
        InventorySystem(
            description="A" * 50, capacity=1, commands=["take"], narrative_purpose="B" * 50
        )
        InventorySystem(
            description="A" * 50, capacity=100, commands=["take"], narrative_purpose="B" * 50
        )

        # Invalid capacities
        with pytest.raises(ValidationError):
            InventorySystem(
                description="A" * 50,
                capacity=0,  # Too low
                commands=["take"],
                narrative_purpose="B" * 50,
            )
        with pytest.raises(ValidationError):
            InventorySystem(
                description="A" * 50,
                capacity=101,  # Too high
                commands=["take"],
                narrative_purpose="B" * 50,
            )


class TestCombatSystem:
    """Tests for CombatSystem model."""

    def test_valid_combat_system(self):
        """Test creating valid combat system."""
        combat = CombatSystem(
            description="A" * 50,
            mechanics=[
                CombatMechanic(name="Overwatch", rules="Set a character to fire upon enemies...")
            ],
            narrative_purpose="B" * 50,
        )
        assert len(combat.mechanics) == 1


class TestGameState:
    """Tests for GameState model."""

    def test_valid_game_state(self):
        """Test creating valid game state."""
        state = GameState(
            tracked_variables=[
                TrackedVariable(variable="squad_morale", purpose="Tracks mental state")
            ],
            win_conditions=[WinCondition(condition="Successfully complete the mission")],
            lose_conditions=[LoseCondition(condition="All squad members killed")],
        )
        assert len(state.tracked_variables) == 1
        assert len(state.win_conditions) == 1
        assert len(state.lose_conditions) == 1


class TestGameMechanics:
    """Tests for GameMechanics model."""

    def test_valid_game_mechanics(self):
        """Test creating valid game mechanics."""
        mechanics = GameMechanics(
            game_title="Test Game",
            game_systems=GameSystems(
                movement=MovementSystem(
                    description="A" * 50, commands=["move"], narrative_purpose="B" * 50
                ),
                inventory=InventorySystem(
                    description="A" * 50, capacity=5, commands=["take"], narrative_purpose="B" * 50
                ),
                combat=CombatSystem(
                    description="A" * 50,
                    mechanics=[CombatMechanic(name="Test", rules="Test rules here")],
                    narrative_purpose="B" * 50,
                ),
                interaction=InteractionSystem(
                    description="A" * 50, commands=["examine"], narrative_purpose="B" * 50
                ),
            ),
            game_state=GameState(
                tracked_variables=[TrackedVariable(variable="var1", purpose="Purpose here")],
                win_conditions=[WinCondition(condition="Win condition here")],
                lose_conditions=[LoseCondition(condition="Lose condition here")],
            ),
            technical_requirements=[
                TechnicalRequirement(
                    requirement="Requirement here", justification="Justification here"
                )
            ],
        )
        assert mechanics.game_title == "Test Game"
        assert mechanics.game_systems.inventory.capacity == 5
