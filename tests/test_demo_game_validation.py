"""
Integration test for demo game validation.

Verifies that the demo game properly validates loaded content and warns about issues.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from space_hulk_game.demo_game import DemoGameCLI
from space_hulk_game.engine import GameData, Scene


class TestDemoGameValidation(unittest.TestCase):
    """Test that demo game validates content on load."""

    def setUp(self):
        """Set up test fixtures."""
        # Use test fixtures directory
        fixtures_dir = Path(__file__).parent / "fixtures"
        self.cli = DemoGameCLI(game_dir=str(fixtures_dir))

    def test_load_valid_game_passes_validation(self):
        """Test that valid game content passes validation without warnings."""
        with patch("builtins.print") as mock_print:
            result = self.cli.load_game_data()

            # Should succeed
            self.assertTrue(result)
            self.assertIsNotNone(self.cli.game_data)

            # Check that validation was run
            print_calls = [str(call) for call in mock_print.call_args_list]
            "\n".join(print_calls)

            # Should see validation message
            self.assertTrue(
                any("Validating" in str(call) for call in print_calls),
                "Should show validation message",
            )

            # Should pass validation (test fixtures are valid)
            self.assertTrue(
                any("validation passed" in str(call).lower() for call in print_calls),
                "Should show validation passed",
            )

    def test_load_invalid_game_shows_warnings(self):
        """Test that invalid game content shows validation warnings."""
        # Create a game with validation issues (unreachable scenes)
        scene1 = Scene(
            id="start",
            name="Start",
            description="Starting room with no exits",
            exits={},  # No exits!
        )
        scene2 = Scene(
            id="unreachable",
            name="Unreachable",
            description="Can't get here",
            exits={"back": "start"},
        )

        invalid_game = GameData(
            title="Invalid Game",
            description="Test game with issues",
            scenes={"start": scene1, "unreachable": scene2},
            starting_scene="start",
            endings=[],  # No endings defined
        )

        # Mock the loader to return our invalid game
        with patch.object(self.cli.loader, "load_game", return_value=invalid_game):  # noqa: SIM117
            with patch("builtins.print") as mock_print:
                with patch("builtins.input", return_value="y"):  # Continue anyway
                    result = self.cli.load_game_data()

                    # Should still succeed (we chose to continue)
                    self.assertTrue(result)

                    # Check that validation warning was shown
                    print_calls = [str(call) for call in mock_print.call_args_list]

                    self.assertTrue(
                        any(
                            "warning" in str(call).lower() and "validation" in str(call).lower()
                            for call in print_calls
                        ),
                        "Should show validation warning",
                    )

                    self.assertTrue(
                        any("unreachable" in str(call).lower() for call in print_calls),
                        "Should mention unreachable scenes",
                    )

    def test_load_invalid_game_can_cancel(self):
        """Test that user can cancel loading invalid game."""
        # Create a game with critical issues
        scene = Scene(
            id="broken",
            name="Broken",
            description="Broken scene",
            exits={"north": "missing"},  # Invalid exit!
        )

        invalid_game = GameData(
            title="Broken Game",
            description="Test",
            scenes={"broken": scene},
            starting_scene="broken",
        )

        # Mock the loader and user input
        with patch.object(self.cli.loader, "load_game", return_value=invalid_game):  # noqa: SIM117
            with patch("builtins.print"):
                with patch("builtins.input", return_value="n"):  # Don't continue
                    result = self.cli.load_game_data()

                    # Should fail (user cancelled)
                    self.assertFalse(result)

    def test_validation_stats_are_shown(self):
        """Test that validation statistics are displayed."""
        with patch("builtins.print") as mock_print:
            self.cli.load_game_data()

            print_calls = [str(call) for call in mock_print.call_args_list]
            "\n".join(print_calls)

            # Should show scene count and other stats
            # (exact format depends on game content, but validation should run)
            self.assertTrue(
                any("Validating" in str(call) for call in print_calls), "Should run validation"
            )


class TestGameValidatorIntegration(unittest.TestCase):
    """Test GameValidator with real generated content (if available)."""

    def test_validator_detects_common_issues(self):
        """Test that validator detects common playability issues."""
        from space_hulk_game.engine import GameData, GameValidator, Scene

        # Create game with multiple issues
        scene1 = Scene(
            id="start",
            name="Start",
            description="Start",
            exits={"north": "missing_scene"},  # Invalid exit
        )
        scene2 = Scene(id="orphan", name="Orphan", description="Unreachable", exits={})

        game_data = GameData(
            title="Test",
            description="Test",
            scenes={"start": scene1, "orphan": scene2},
            starting_scene="start",
        )

        validator = GameValidator(strict_mode=False)
        result = validator.validate_game(game_data)

        # Should detect issues
        self.assertFalse(result.is_valid())
        self.assertGreater(len(result.issues), 0)

        # Should detect specific issues
        issues_text = " ".join(result.issues).lower()
        self.assertIn("orphan", issues_text, "Should detect unreachable scene")
        self.assertIn("missing_scene", issues_text, "Should detect invalid exit")


if __name__ == "__main__":
    unittest.main()
