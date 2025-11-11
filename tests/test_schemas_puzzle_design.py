"""Unit tests for puzzle_design schema models."""

import pytest
from pydantic import ValidationError

from space_hulk_game.schemas.puzzle_design import (
    PuzzleStep,
    PuzzleSolution,
    Puzzle,
    ArtifactProperty,
    Artifact,
    Monster,
    NPC,
    PuzzleDesign,
)


class TestPuzzle:
    """Tests for Puzzle model."""

    def test_valid_puzzle(self):
        """Test creating a valid puzzle."""
        puzzle = Puzzle(
            id="puzzle_test",
            name="Test Puzzle",
            description="A" * 50,
            location="scene_test",
            narrative_purpose="Test purpose for narrative",
            solution=PuzzleSolution(
                type="multi-step",
                steps=[PuzzleStep(step="Step 1 description here")]
            ),
            difficulty="medium"
        )
        assert puzzle.id == "puzzle_test"
        assert puzzle.difficulty == "medium"

    def test_difficulty_validation(self):
        """Test difficulty must be easy, medium, or hard."""
        with pytest.raises(ValidationError):
            Puzzle(
                id="puzzle_test",
                name="Test",
                description="A" * 50,
                location="scene_test",
                narrative_purpose="Test purpose for narrative",
                solution=PuzzleSolution(
                    type="test",
                    steps=[PuzzleStep(step="Step description here")]
                ),
                difficulty="extreme"  # Invalid difficulty
            )


class TestMonster:
    """Tests for Monster model."""

    def test_valid_monster(self):
        """Test creating a valid monster."""
        monster = Monster(
            id="monster_test",
            name="Test Monster",
            description="A terrifying creature",
            locations=["scene_1", "scene_2"],
            narrative_role="Primary antagonist for testing",
            abilities=["Fast Attack", "Rending Claws"]
        )
        assert len(monster.abilities) == 2
        assert len(monster.locations) == 2

    def test_empty_abilities_validation(self):
        """Test that empty ability strings are rejected."""
        with pytest.raises(ValidationError, match="non-empty"):
            Monster(
                id="monster_test",
                name="Test",
                description="Description here",
                locations=["scene_1"],
                narrative_role="Role description here",
                abilities=["Valid ability", "", "Another ability"]  # Empty string
            )


class TestNPC:
    """Tests for NPC model."""

    def test_valid_npc(self):
        """Test creating a valid NPC."""
        npc = NPC(
            id="npc_test",
            name="Test NPC",
            role="Test Role in game",
            description="NPC description here",
            locations=["scene_1"],
            dialogue_themes=["Theme 1", "Theme 2"]
        )
        assert len(npc.dialogue_themes) == 2

    def test_empty_dialogue_themes_validation(self):
        """Test that empty dialogue theme strings are rejected."""
        with pytest.raises(ValidationError, match="non-empty"):
            NPC(
                id="npc_test",
                name="Test",
                role="Role",
                description="Description here",
                locations=["scene_1"],
                dialogue_themes=["Valid theme", "  "]  # Whitespace-only string
            )


class TestPuzzleDesign:
    """Tests for PuzzleDesign model."""

    def test_valid_puzzle_design(self):
        """Test creating a valid puzzle design."""
        pd = PuzzleDesign(
            puzzles=[
                Puzzle(
                    id="puzzle_1",
                    name="Puzzle 1",
                    description="A" * 50,
                    location="scene_1",
                    narrative_purpose="Purpose description here",
                    solution=PuzzleSolution(
                        type="test",
                        steps=[PuzzleStep(step="Step description")]
                    ),
                    difficulty="easy"
                )
            ],
            artifacts=[
                Artifact(
                    id="artifact_1",
                    name="Artifact 1",
                    description="Artifact description",
                    location="scene_1",
                    narrative_significance="Significance description here",
                    properties=[ArtifactProperty(property="prop1")]
                )
            ],
            monsters=[
                Monster(
                    id="monster_1",
                    name="Monster 1",
                    description="Monster description",
                    locations=["scene_1"],
                    narrative_role="Role description here",
                    abilities=["ability1"]
                )
            ],
            npcs=[
                NPC(
                    id="npc_1",
                    name="NPC 1",
                    role="Role",
                    description="NPC description here",
                    locations=["scene_1"],
                    dialogue_themes=["theme1"]
                )
            ]
        )
        assert len(pd.puzzles) == 1
        assert len(pd.artifacts) == 1
        assert len(pd.monsters) == 1
        assert len(pd.npcs) == 1

    def test_unique_puzzle_ids(self):
        """Test puzzle ID uniqueness validation."""
        with pytest.raises(ValidationError, match="unique"):
            PuzzleDesign(
                puzzles=[
                    Puzzle(
                        id="puzzle_duplicate",
                        name="P1",
                        description="A" * 50,
                        location="s1",
                        narrative_purpose="Purpose here",
                        solution=PuzzleSolution(type="t", steps=[PuzzleStep(step="s" * 10)]),
                        difficulty="easy"
                    ),
                    Puzzle(
                        id="puzzle_duplicate",  # Duplicate
                        name="P2",
                        description="A" * 50,
                        location="s1",
                        narrative_purpose="Purpose here",
                        solution=PuzzleSolution(type="t", steps=[PuzzleStep(step="s" * 10)]),
                        difficulty="easy"
                    ),
                ],
                artifacts=[
                    Artifact(
                        id="a1", name="A1", description="d", location="s1",
                        narrative_significance="s" * 20, properties=[ArtifactProperty(property="p")]
                    )
                ],
                monsters=[
                    Monster(
                        id="m1", name="M1", description="d", locations=["s1"],
                        narrative_role="r" * 20, abilities=["a"]
                    )
                ],
                npcs=[
                    NPC(
                        id="n1", name="N1", role="r", description="A grizzled veteran of the Imperial Guard, haunted by past battles.",
                        locations=["s1"], dialogue_themes=["t"]
                    )
                ]
            )

    def test_unique_artifact_ids(self):
        """Test artifact ID uniqueness validation."""
        with pytest.raises(ValidationError, match="unique"):
            PuzzleDesign(
                puzzles=[
                    Puzzle(
                        id="p1", name="P1", description="A" * 50, location="s1",
                        narrative_purpose="Purpose here",
                        solution=PuzzleSolution(type="t", steps=[PuzzleStep(step="s" * 10)]),
                        difficulty="easy"
                    )
                ],
                artifacts=[
                    Artifact(
                        id="artifact_dup", name="A1", description="d", location="s1",
                        narrative_significance="s" * 20, properties=[ArtifactProperty(property="p")]
                    ),
                    Artifact(
                        id="artifact_dup", name="A2", description="d", location="s1",  # Duplicate
                        narrative_significance="s" * 20, properties=[ArtifactProperty(property="p")]
                    ),
                ],
                monsters=[
                    Monster(
                        id="m1", name="M1", description="d", locations=["s1"],
                        narrative_role="r" * 20, abilities=["a"]
                    )
                ],
                npcs=[
                    NPC(
                        id="n1", name="N1", role="r", description="A grizzled veteran of the Imperial Guard, haunted by past battles.",
                        locations=["s1"], dialogue_themes=["t"]
                    )
                ]
            )
