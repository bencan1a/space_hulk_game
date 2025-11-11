"""Unit tests for narrative_map schema models."""

import pytest
from pydantic import ValidationError

from space_hulk_game.schemas.narrative_map import (
    CharacterMoment,
    Connection,
    DecisionOption,
    DecisionPoint,
    Scene,
    CharacterArcStage,
    CharacterArc,
    NarrativeMap,
)


class TestConnection:
    """Tests for Connection model."""

    def test_valid_connection(self):
        """Test creating a valid connection."""
        conn = Connection(
            target="scene_test",
            description="Proceed to the next area",
        )
        assert conn.target == "scene_test"
        assert conn.condition is None

    def test_connection_with_condition(self):
        """Test connection with condition."""
        conn = Connection(
            target="scene_test",
            description="Proceed if condition met",
            condition="Broodlord defeated"
        )
        assert conn.condition == "Broodlord defeated"


class TestDecisionPoint:
    """Tests for DecisionPoint model."""

    def test_valid_decision_point(self):
        """Test creating a valid decision point."""
        dp = DecisionPoint(
            id="decision_test",
            prompt="What do you choose?" * 2,  # Min length 20
            options=[
                DecisionOption(
                    choice="Option 1 text here",
                    outcome="Outcome 1 text here",
                    target_scene="scene_1"
                ),
                DecisionOption(
                    choice="Option 2 text here",
                    outcome="Outcome 2 text here",
                    target_scene="scene_2"
                ),
            ]
        )
        assert dp.id == "decision_test"
        assert len(dp.options) == 2

    def test_minimum_two_options(self):
        """Test that decision points require at least 2 options."""
        with pytest.raises(ValidationError):
            DecisionPoint(
                id="decision_test",
                prompt="What do you choose?" * 2,
                options=[
                    DecisionOption(
                        choice="Only option",
                        outcome="Only outcome",
                        target_scene="scene_1"
                    )
                ]
            )


class TestNarrativeMap:
    """Tests for NarrativeMap model."""

    def test_valid_narrative_map(self):
        """Test creating a valid narrative map."""
        nm = NarrativeMap(
            start_scene="scene_start",
            scenes={
                "scene_start": Scene(
                    name="Start Scene",
                    description="A" * 50,
                    connections=[
                        Connection(target="scene_end", description="Go to end")
                    ]
                ),
                "scene_end": Scene(
                    name="End Scene",
                    description="A" * 50,
                    connections=[]
                )
            }
        )
        assert nm.start_scene == "scene_start"
        assert len(nm.scenes) == 2

    def test_connection_target_validation(self):
        """Test that connections must reference existing scenes."""
        with pytest.raises(ValidationError, match="non-existent"):
            NarrativeMap(
                start_scene="scene_start",
                scenes={
                    "scene_start": Scene(
                        name="Start",
                        description="A" * 50,
                        connections=[
                            Connection(target="scene_nonexistent", description="Invalid")
                        ]
                    )
                }
            )

    def test_decision_target_validation(self):
        """Test that decision options must reference existing scenes."""
        with pytest.raises(ValidationError, match="non-existent"):
            NarrativeMap(
                start_scene="scene_start",
                scenes={
                    "scene_start": Scene(
                        name="Start",
                        description="A" * 50,
                        connections=[],
                        decision_points=[
                            DecisionPoint(
                                id="decision_test",
                                prompt="Choose wisely" * 2,
                                options=[
                                    DecisionOption(
                                        choice="Option 1",
                                        outcome="Outcome 1",
                                        target_scene="scene_nonexistent"  # Invalid
                                    ),
                                    DecisionOption(
                                        choice="Option 2",
                                        outcome="Outcome 2",
                                        target_scene="scene_start"
                                    ),
                                ]
                            )
                        ]
                    )
                }
            )

    def test_character_arcs(self):
        """Test narrative map with character arcs."""
        nm = NarrativeMap(
            start_scene="scene_start",
            scenes={
                "scene_start": Scene(
                    name="Start",
                    description="A" * 50,
                    connections=[]
                )
            },
            character_arcs=[
                CharacterArc(
                    character="Test Character",
                    arc_stages=[
                        CharacterArcStage(
                            stage="Beginning",
                            description="Starting state"
                        ),
                        CharacterArcStage(
                            stage="Development",
                            description="Character grows"
                        )
                    ]
                )
            ]
        )
        assert len(nm.character_arcs) == 1
        assert len(nm.character_arcs[0].arc_stages) == 2
