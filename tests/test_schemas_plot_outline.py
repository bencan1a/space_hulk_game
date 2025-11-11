"""Unit tests for plot_outline schema models."""

import pytest
from pydantic import ValidationError

from space_hulk_game.schemas.plot_outline import (
    Character,
    Conflict,
    PlotBranch,
    PlotOutline,
    PlotPoint,
)


class TestPlotPoint:
    """Tests for PlotPoint model."""

    def test_valid_plot_point(self):
        """Test creating a valid plot point."""
        pp = PlotPoint(
            id="pp_01_test",
            name="Test Plot Point",
            description="A" * 50  # Min length 50
        )
        assert pp.id == "pp_01_test"
        assert pp.name == "Test Plot Point"

    def test_plot_point_id_validation(self):
        """Test ID format validation."""
        # Valid IDs
        PlotPoint(id="pp_01", name="Name", description="A" * 50)
        PlotPoint(id="pp-01-test", name="Name", description="A" * 50)
        PlotPoint(id="pp_01_test", name="Name", description="A" * 50)

        # Invalid ID (special characters)
        with pytest.raises(ValidationError):
            PlotPoint(id="pp@01", name="Name", description="A" * 50)

    def test_plot_point_description_length(self):
        """Test description minimum length."""
        with pytest.raises(ValidationError):
            PlotPoint(id="pp_01", name="Name", description="Too short")


class TestCharacter:
    """Tests for Character model."""

    def test_valid_character(self):
        """Test creating a valid character."""
        char = Character(
            name="Brother-Captain Tyberius",
            role="Squad Leader",
            backstory="A" * 50  # Min length 50
        )
        assert char.name == "Brother-Captain Tyberius"
        assert char.role == "Squad Leader"
        assert char.conflicts is None

    def test_character_with_conflicts(self):
        """Test character with optional conflicts."""
        char = Character(
            name="Test Character",
            role="Test Role",
            backstory="A" * 50,
            conflicts=["Internal conflict", "External conflict"]
        )
        assert len(char.conflicts) == 2


class TestConflict:
    """Tests for Conflict model."""

    def test_valid_conflict(self):
        """Test creating a valid conflict."""
        conflict = Conflict(
            type="Man vs. Xenos",
            description="A" * 50  # Min length 50
        )
        assert conflict.type == "Man vs. Xenos"


class TestPlotBranch:
    """Tests for PlotBranch model."""

    def test_valid_plot_branch(self):
        """Test creating a valid plot branch."""
        branch = PlotBranch(
            path="heroic_sacrifice",
            description="A" * 50  # Min length 50
        )
        assert branch.path == "heroic_sacrifice"
        assert branch.decision_point is None

    def test_plot_branch_with_decision_point(self):
        """Test branch with decision point."""
        branch = PlotBranch(
            path="test_path",
            description="A" * 50,
            decision_point="decision_01"
        )
        assert branch.decision_point == "decision_01"


class TestPlotOutline:
    """Tests for PlotOutline model."""

    def test_valid_plot_outline(self):
        """Test creating a valid plot outline."""
        outline = PlotOutline(
            title="Test Title",
            setting="A" * 50,  # Min length 50
            themes=["Theme 1", "Theme 2"],
            tone="Dark and gritty",
            plot_points=[
                PlotPoint(id="pp_01", name="Point 1", description="A" * 50),
                PlotPoint(id="pp_02", name="Point 2", description="A" * 50),
                PlotPoint(id="pp_03", name="Point 3", description="A" * 50),
            ],
            characters=[
                Character(name="Char 1", role="Role 1", backstory="A" * 50)
            ],
            conflicts=[
                Conflict(type="Type 1", description="A" * 50)
            ]
        )
        assert outline.title == "Test Title"
        assert len(outline.plot_points) == 3
        assert len(outline.characters) == 1
        assert len(outline.conflicts) == 1

    def test_minimum_plot_points(self):
        """Test minimum plot points requirement."""
        with pytest.raises(ValidationError):
            PlotOutline(
                title="Test",
                setting="A" * 50,
                themes=["Theme"],
                tone="Tone",
                plot_points=[  # Only 2 plot points, need 3
                    PlotPoint(id="pp_01", name="Point 1", description="A" * 50),
                    PlotPoint(id="pp_02", name="Point 2", description="A" * 50),
                ],
                characters=[Character(name="C1", role="R1", backstory="A" * 50)],
                conflicts=[Conflict(type="T1", description="A" * 50)]
            )

    def test_unique_plot_point_ids(self):
        """Test plot point ID uniqueness validation."""
        with pytest.raises(ValidationError, match="unique"):
            PlotOutline(
                title="Test",
                setting="A" * 50,
                themes=["Theme"],
                tone="Tone",
                plot_points=[
                    PlotPoint(id="pp_01", name="Point 1", description="A" * 50),
                    PlotPoint(id="pp_01", name="Point 2", description="A" * 50),  # Duplicate ID
                    PlotPoint(id="pp_03", name="Point 3", description="A" * 50),
                ],
                characters=[Character(name="C1", role="R1", backstory="A" * 50)],
                conflicts=[Conflict(type="T1", description="A" * 50)]
            )

    def test_unique_character_names(self):
        """Test character name uniqueness validation."""
        with pytest.raises(ValidationError, match="unique"):
            PlotOutline(
                title="Test",
                setting="A" * 50,
                themes=["Theme"],
                tone="Tone",
                plot_points=[
                    PlotPoint(id="pp_01", name="Point 1", description="A" * 50),
                    PlotPoint(id="pp_02", name="Point 2", description="A" * 50),
                    PlotPoint(id="pp_03", name="Point 3", description="A" * 50),
                ],
                characters=[
                    Character(name="Duplicate", role="R1", backstory="A" * 50),
                    Character(name="Duplicate", role="R2", backstory="A" * 50),  # Duplicate name
                ],
                conflicts=[Conflict(type="T1", description="A" * 50)]
            )

    def test_empty_themes_validation(self):
        """Test that empty theme strings are rejected."""
        with pytest.raises(ValidationError, match="non-empty"):
            PlotOutline(
                title="Test",
                setting="A" * 50,
                themes=["Valid theme", "", "Another theme"],  # Empty string
                tone="Tone",
                plot_points=[
                    PlotPoint(id="pp_01", name="Point 1", description="A" * 50),
                    PlotPoint(id="pp_02", name="Point 2", description="A" * 50),
                    PlotPoint(id="pp_03", name="Point 3", description="A" * 50),
                ],
                characters=[Character(name="C1", role="R1", backstory="A" * 50)],
                conflicts=[Conflict(type="T1", description="A" * 50)]
            )

    def test_optional_plot_branches(self):
        """Test plot outline with optional branches."""
        outline = PlotOutline(
            title="Test",
            setting="A" * 50,
            themes=["Theme"],
            tone="Tone",
            plot_points=[
                PlotPoint(id="pp_01", name="Point 1", description="A" * 50),
                PlotPoint(id="pp_02", name="Point 2", description="A" * 50),
                PlotPoint(id="pp_03", name="Point 3", description="A" * 50),
            ],
            characters=[Character(name="C1", role="R1", backstory="A" * 50)],
            conflicts=[Conflict(type="T1", description="A" * 50)],
            plot_branches=[
                PlotBranch(path="branch_1", description="A" * 50)
            ]
        )
        assert len(outline.plot_branches) == 1
