"""
Tests for kloc-report.py script to ensure it works correctly and doesn't hang.
"""

import subprocess
import sys
import unittest
from pathlib import Path


class TestKlocReport(unittest.TestCase):
    """Test the KLOC report script."""

    def setUp(self):
        """Set up test fixtures."""
        self.script_path = Path(__file__).parent.parent / "tools" / "kloc-report.py"
        self.assertTrue(self.script_path.exists(), f"Script not found: {self.script_path}")

    def test_script_help_runs_without_hanging(self):
        """Test that --help runs quickly and doesn't hang."""
        # Run with timeout to ensure it doesn't hang
        result = subprocess.run(
            [sys.executable, str(self.script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,  # Should complete in under 5 seconds
        )

        self.assertEqual(result.returncode, 0, "Help command should succeed")
        self.assertIn("usage:", result.stdout.lower(), "Should show usage information")
        self.assertIn("--user", result.stdout, "Should show --user parameter")

    def test_script_syntax_is_valid(self):
        """Test that the Python script has valid syntax."""
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(self.script_path)],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        self.assertEqual(result.returncode, 0, f"Script should compile: {result.stderr}")

    def test_unbuffered_output_flag_works(self):
        """Test that -u flag for unbuffered output works with the script."""
        # Run with -u flag (unbuffered) to ensure it's compatible
        result = subprocess.run(
            [sys.executable, "-u", str(self.script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        self.assertEqual(result.returncode, 0, "Unbuffered mode should work")
        self.assertIn("usage:", result.stdout.lower(), "Should show usage with -u flag")

    def test_script_requires_user_parameter(self):
        """Test that script requires --user parameter."""
        result = subprocess.run(
            [sys.executable, str(self.script_path)],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        # Should fail without --user
        self.assertNotEqual(result.returncode, 0, "Should fail without --user")
        self.assertIn("--user", result.stderr, "Error should mention --user parameter")

    def test_script_has_flush_calls(self):
        """Test that the script contains sys.stdout.flush() calls."""
        with open(self.script_path, encoding="utf-8") as f:
            content = f.read()

        # Check for flush calls
        flush_count = content.count("sys.stdout.flush()")
        self.assertGreaterEqual(
            flush_count, 3, "Script should have at least 3 flush calls for unbuffered output"
        )

    def test_script_accepts_repos_parameter(self):
        """Test that script accepts --repos parameter."""
        result = subprocess.run(
            [sys.executable, str(self.script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("--repos", result.stdout, "Help should mention --repos parameter")
        self.assertIn(
            "repository names", result.stdout.lower(), "Help should explain --repos parameter"
        )

    def test_script_handles_missing_token_gracefully(self):
        """Test that script shows warning when GH_TOKEN is missing."""
        # This test runs without GH_TOKEN set, script should warn but not crash on --help
        import os

        env = os.environ.copy()
        env.pop("GH_TOKEN", None)
        env.pop("GITHUB_TOKEN", None)

        result = subprocess.run(
            [sys.executable, str(self.script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=5,
            env=env,
            check=False,
        )

        # Should still work for --help
        self.assertEqual(result.returncode, 0)
        # Should show warning about missing token
        combined_output = result.stdout + result.stderr
        self.assertIn("GH_TOKEN", combined_output, "Should mention GH_TOKEN")


if __name__ == "__main__":
    unittest.main()
