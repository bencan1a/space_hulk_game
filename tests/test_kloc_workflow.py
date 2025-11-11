"""
Tests for GitHub Actions workflow files.
"""

import unittest
from pathlib import Path

import yaml


class TestWorkflows(unittest.TestCase):
    """Test GitHub Actions workflow configurations."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflows_dir = Path(__file__).parent.parent / ".github" / "workflows"
        self.assertTrue(
            self.workflows_dir.exists(), f"Workflows directory not found: {self.workflows_dir}"
        )

    def test_kloc_workflow_is_valid_yaml(self):
        """Test that run-kloc-report.yml is valid YAML."""
        workflow_path = self.workflows_dir / "run-kloc-report.yml"
        self.assertTrue(workflow_path.exists(), f"Workflow not found: {workflow_path}")

        with open(workflow_path, encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        self.assertIsNotNone(workflow, "Workflow should parse as YAML")
        self.assertIn("name", workflow, "Workflow should have a name")
        self.assertIn("jobs", workflow, "Workflow should have jobs")

    def test_kloc_workflow_has_timeout(self):
        """Test that kloc workflow job step has timeout configured."""
        workflow_path = self.workflows_dir / "run-kloc-report.yml"

        with open(workflow_path, encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        # Find the run-kloc-report job
        jobs = workflow.get("jobs", {})
        kloc_job = jobs.get("run-kloc-report")
        self.assertIsNotNone(kloc_job, "Should have run-kloc-report job")

        # Check for timeout in the run step
        steps = kloc_job.get("steps", [])
        run_kloc_step = None
        for step in steps:
            if step.get("name") == "Run KLOC report script":
                run_kloc_step = step
                break

        self.assertIsNotNone(run_kloc_step, "Should have 'Run KLOC report script' step")
        assert run_kloc_step is not None  # Type narrowing for type checker
        self.assertIn("timeout-minutes", run_kloc_step, "Run step should have timeout-minutes")

        timeout = run_kloc_step["timeout-minutes"]
        self.assertEqual(timeout, 360, "Timeout should be 360 minutes (6 hours)")

    def test_kloc_workflow_uses_unbuffered_python(self):
        """Test that kloc workflow uses python -u for unbuffered output."""
        workflow_path = self.workflows_dir / "run-kloc-report.yml"

        with open(workflow_path, encoding="utf-8") as f:
            content = f.read()

        # Check that python -u is used
        self.assertIn("python -u", content, "Workflow should use 'python -u' for unbuffered output")
        self.assertIn("kloc-report.py", content, "Workflow should run kloc-report.py")

    def test_kloc_workflow_uses_specific_repos(self):
        """Test that kloc workflow uses --repos for faster execution."""
        workflow_path = self.workflows_dir / "run-kloc-report.yml"

        with open(workflow_path, encoding="utf-8") as f:
            content = f.read()

        # Check that --repos is used
        self.assertIn("--repos", content, "Workflow should use --repos parameter")
        # Check for at least some of the expected repos
        self.assertIn("CalendarBot", content, "Workflow should include CalendarBot repo")
        self.assertIn("space_hulk_game", content, "Workflow should include space_hulk_game repo")

    def test_kloc_workflow_checks_exit_code(self):
        """Test that kloc workflow checks script exit code."""
        workflow_path = self.workflows_dir / "run-kloc-report.yml"

        with open(workflow_path, encoding="utf-8") as f:
            content = f.read()

        # Check for PIPESTATUS check
        self.assertIn("PIPESTATUS", content, "Workflow should check PIPESTATUS for tee'd command")
        self.assertIn("SCRIPT_EXIT", content, "Workflow should save script exit code")

    def test_kloc_workflow_has_required_permissions(self):
        """Test that kloc workflow has required permissions."""
        workflow_path = self.workflows_dir / "run-kloc-report.yml"

        with open(workflow_path, encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        jobs = workflow.get("jobs", {})
        kloc_job = jobs.get("run-kloc-report")

        permissions = kloc_job.get("permissions", {})
        self.assertIn("contents", permissions, "Should have contents permission")
        self.assertEqual(permissions["contents"], "read", "Should have read access to contents")

        # Check for PR write permission (needed for comments)
        self.assertIn("pull-requests", permissions, "Should have pull-requests permission")
        self.assertEqual(permissions["pull-requests"], "write", "Should have write access to PRs")


if __name__ == "__main__":
    unittest.main()
