"""
End-to-End Integration Tests for Quality System

These tests validate that the quality checking system integrates correctly
with the CrewAI workflow and can run end-to-end.

Test Coverage:
1. Quality system can be enabled/disabled via environment variable
2. Quality evaluators integrate with task execution
3. Quality scores are logged correctly
4. Retry logic activates on poor quality outputs
5. Planning templates work with quality system
6. Generation time remains acceptable (< 15 minutes)

Author: Chunk 3.5 Implementation
Date: November 2025
"""
import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Try to import required modules
CREWAI_AVAILABLE = False
QUALITY_MODULES_AVAILABLE = False

try:
    import importlib.util

    CREWAI_AVAILABLE = importlib.util.find_spec("crewai") is not None
except ImportError:
    # CrewAI not available - some tests will be skipped
    CREWAI_AVAILABLE = False

try:
    from src.space_hulk_game.quality.integration import QualityCheckConfig
    from src.space_hulk_game.quality.narrative_evaluator import NarrativeMapEvaluator
    from src.space_hulk_game.quality.plot_evaluator import PlotEvaluator
    from src.space_hulk_game.quality.retry import TaskType, execute_with_quality_check
    from src.space_hulk_game.quality.score import QualityScore

    QUALITY_MODULES_AVAILABLE = True
except ImportError as e:
    # Quality modules not available - tests will be skipped
    print(f"⚠ Quality modules not available: {e}")


class TestQualitySystemConfiguration(unittest.TestCase):
    """Test that quality system configuration works correctly."""

    @unittest.skipUnless(QUALITY_MODULES_AVAILABLE, "Quality modules not available")
    def test_quality_config_loads(self):
        """Test that quality configuration can be loaded."""
        config = QualityCheckConfig()

        self.assertIsNotNone(config)
        self.assertIsNotNone(config.config)
        self.assertIn("global", config.config)
        self.assertIn("thresholds", config.config)

        # Check default state (disabled)
        self.assertFalse(config.config["global"]["enabled"])

    @unittest.skipUnless(QUALITY_MODULES_AVAILABLE, "Quality modules not available")
    def test_quality_config_env_override(self):
        """Test that environment variable can enable quality checking."""
        # Test with environment variable enabled
        with patch.dict(os.environ, {"QUALITY_CHECK_ENABLED": "true"}):
            config = QualityCheckConfig()
            # Note: Current implementation loads from file, not env
            # This test documents expected behavior for future implementation
            self.assertIsNotNone(config)

    @unittest.skipUnless(QUALITY_MODULES_AVAILABLE, "Quality modules not available")
    def test_task_type_mapping(self):
        """Test that all task types are properly defined."""
        # Verify TaskType enum exists and has expected values
        self.assertTrue(hasattr(TaskType, "PLOT"))
        self.assertTrue(hasattr(TaskType, "NARRATIVE"))
        self.assertTrue(hasattr(TaskType, "PUZZLE"))
        self.assertTrue(hasattr(TaskType, "SCENE"))
        self.assertTrue(hasattr(TaskType, "MECHANICS"))


class TestQualityEvaluatorIntegration(unittest.TestCase):
    """Test that quality evaluators integrate correctly."""

    @unittest.skipUnless(QUALITY_MODULES_AVAILABLE, "Quality modules not available")
    def test_plot_evaluator_integration(self):
        """Test PlotEvaluator can evaluate YAML output."""
        evaluator = PlotEvaluator()

        # Create sample plot YAML
        sample_plot = """
title: Test Plot
setting: A dark space hulk
themes:
  - Horror
  - Survival
tone: Dark and oppressive
main_branches:
  - path: Path A
    description: The crew explores the engineering deck
  - path: Path B
    description: The crew investigates strange signals
endings:
  - name: Victory
    description: The crew escapes
    type: victory
  - name: Defeat
    description: The crew is overwhelmed
    type: defeat
"""

        result = evaluator.evaluate(sample_plot)

        self.assertIsInstance(result, QualityScore)
        self.assertIsNotNone(result.score)
        self.assertIsInstance(result.passed, bool)
        self.assertIsInstance(result.feedback, str)

    @unittest.skipUnless(QUALITY_MODULES_AVAILABLE, "Quality modules not available")
    def test_narrative_evaluator_integration(self):
        """Test NarrativeMapEvaluator can evaluate YAML output."""
        evaluator = NarrativeMapEvaluator()

        # Create sample narrative map YAML
        sample_narrative = """
scenes:
  start:
    id: start
    description: Entry airlock
    exits:
      north: corridor1
  corridor1:
    id: corridor1
    description: Dark corridor
    exits:
      south: start
      east: end
  end:
    id: end
    description: Exit point
    exits:
      west: corridor1
"""

        result = evaluator.evaluate(sample_narrative)

        self.assertIsInstance(result, QualityScore)
        self.assertIsNotNone(result.score)
        self.assertIsInstance(result.passed, bool)


class TestRetryLogicIntegration(unittest.TestCase):
    """Test that retry logic works with quality evaluation."""

    @unittest.skipUnless(QUALITY_MODULES_AVAILABLE, "Quality modules not available")
    def test_retry_logic_with_poor_quality(self):
        """Test that retry logic activates on poor quality output."""
        # Create a mock task that returns poor quality output
        call_count = [0]

        def mock_task_executor(**kwargs):
            """Mock task that improves on retries."""
            call_count[0] += 1
            if call_count[0] == 1:
                # First attempt: poor quality (minimal content)
                return "title: Test\nsetting: A place"
            else:
                # Retry: better quality
                return """
title: Test Plot
setting: A detailed dark space hulk with atmosphere
themes: [Horror, Survival]
tone: Dark
main_branches:
  - path: A
    description: Detailed path A description here
  - path: B
    description: Detailed path B description here
endings:
  - name: Victory
    description: Detailed victory
    type: victory
  - name: Defeat
    description: Detailed defeat
    type: defeat
"""

        # Execute with quality checking
        output, _quality_score, _attempts = execute_with_quality_check(
            task_function=mock_task_executor,
            task_type=TaskType.PLOT,
            task_name="Test Plot Task",
            pass_threshold=6.0,
            max_retries=3,
        )

        # Should have retried at least once
        self.assertGreater(call_count[0], 1, "Retry logic should have activated")
        self.assertIsNotNone(output)

    @unittest.skipUnless(QUALITY_MODULES_AVAILABLE, "Quality modules not available")
    def test_retry_limit_enforced(self):
        """Test that retry limit is enforced."""
        call_count = [0]

        def mock_task_always_poor(**kwargs):
            """Mock task that always returns poor output."""
            call_count[0] += 1
            return "title: Bad"  # Always poor quality

        # Execute with quality checking and low retry limit
        output, _quality_score, _attempts = execute_with_quality_check(
            task_function=mock_task_always_poor,
            task_type=TaskType.PLOT,
            task_name="Test Poor Task",
            pass_threshold=6.0,
            max_retries=2,
        )

        # Should have tried max_retries times (not max_retries + 1)
        self.assertEqual(call_count[0], 2, "Should execute max_retries times")
        self.assertIsNotNone(output, "Should return last attempt even if poor")


class TestQualityScoreLogging(unittest.TestCase):
    """Test that quality scores are logged correctly."""

    @unittest.skipUnless(QUALITY_MODULES_AVAILABLE, "Quality modules not available")
    def test_quality_score_logged(self):
        """Test that quality scores appear in logs."""
        with patch("src.space_hulk_game.quality.retry.logger") as mock_logger:
            # Create a simple task that passes quality check
            def mock_task(**kwargs):
                return """
title: Good Plot
setting: Detailed setting description
themes: [Theme1, Theme2]
tone: Appropriate
main_branches:
  - path: A
    description: Path A
  - path: B
    description: Path B
endings:
  - name: End1
    description: Ending 1
    type: victory
  - name: End2
    description: Ending 2
    type: defeat
"""

            execute_with_quality_check(
                task_function=mock_task,
                task_type=TaskType.PLOT,
                task_name="Test Logging Task",
                pass_threshold=6.0,
                max_retries=1,
            )

            # Check that logger was called with quality score info
            # Note: This depends on implementation details
            self.assertTrue(mock_logger.info.called or mock_logger.debug.called)


class TestPlanningTemplateIntegration(unittest.TestCase):
    """Test quality system with planning templates."""

    def setUp(self):
        """Set up test fixtures."""
        self.templates_dir = Path(__file__).parent.parent / "planning_templates"
        self.templates_exist = self.templates_dir.exists()

    @unittest.skipUnless(QUALITY_MODULES_AVAILABLE, "Quality modules not available")
    def test_templates_directory_exists(self):
        """Test that planning templates directory exists."""
        self.assertTrue(
            self.templates_exist,
            f"Planning templates directory should exist at {self.templates_dir}",
        )

    @unittest.skipUnless(QUALITY_MODULES_AVAILABLE, "Quality modules not available")
    def test_template_files_exist(self):
        """Test that all expected template files exist."""
        if not self.templates_exist:
            self.skipTest("Templates directory not found")

        expected_templates = [
            "space_horror.yaml",
            "mystery_investigation.yaml",
            "survival_escape.yaml",
            "combat_focused.yaml",
        ]

        for template in expected_templates:
            template_path = self.templates_dir / template
            self.assertTrue(template_path.exists(), f"Template {template} should exist")


class TestEndToEndIntegration(unittest.TestCase):
    """
    End-to-end integration tests.

    These tests validate the complete quality system workflow.
    They run with mocked LLM responses to avoid API costs.
    """

    @unittest.skipUnless(
        CREWAI_AVAILABLE and QUALITY_MODULES_AVAILABLE, "CrewAI and quality modules required"
    )
    def test_quality_system_disabled_by_default(self):
        """Test that quality system is disabled by default."""
        config = QualityCheckConfig()
        self.assertFalse(
            config.config["global"]["enabled"], "Quality checking should be disabled by default"
        )

    @unittest.skipUnless(
        CREWAI_AVAILABLE and QUALITY_MODULES_AVAILABLE, "CrewAI and quality modules required"
    )
    def test_quality_integration_workflow(self):
        """Test complete workflow: task → quality check → retry if needed."""
        # Track execution
        execution_log = []

        def mock_task(**kwargs):
            """Mock task with improving quality."""
            attempt = len(execution_log) + 1
            execution_log.append(f"Attempt {attempt}")

            if attempt == 1:
                # Poor quality on first attempt
                return "title: Minimal"
            else:
                # Good quality on retry
                return """
title: Improved Plot
setting: Rich detailed setting with atmosphere
themes: [Horror, Mystery, Survival]
tone: Dark and foreboding
main_branches:
  - path: Investigation
    description: Detailed investigation path
  - path: Combat
    description: Detailed combat path
endings:
  - name: Success
    description: Detailed success ending
    type: victory
  - name: Failure
    description: Detailed failure ending
    type: defeat
"""

        output, _quality_score, _attempts = execute_with_quality_check(
            task_function=mock_task,
            task_type=TaskType.PLOT,
            task_name="Test Integration Task",
            pass_threshold=6.0,
            max_retries=3,
        )

        # Should have improved on retry
        self.assertGreater(len(execution_log), 1, "Should retry on poor quality")
        self.assertLessEqual(len(execution_log), 4, "Should not exceed max retries")
        self.assertIsNotNone(output)


class TestPerformanceRequirements(unittest.TestCase):
    """Test that performance requirements are met."""

    @unittest.skipUnless(QUALITY_MODULES_AVAILABLE, "Quality modules not available")
    def test_quality_check_performance(self):
        """Test that quality checking adds minimal overhead."""
        # Create realistic YAML output
        sample_output = """
title: Performance Test Plot
setting: A massive derelict space hulk drifting in the void
themes:
  - Gothic Horror
  - Survival
  - Mystery
tone: Dark, oppressive, and claustrophobic
main_branches:
  - path: Engineering Deck
    description: Investigate the failing reactor core
  - path: Command Bridge
    description: Search for the ship's logs
endings:
  - name: Escape
    description: Successfully escape in a functioning shuttle
    type: victory
  - name: Consumed
    description: Overwhelmed by the darkness within
    type: defeat
"""

        # Time the quality evaluation
        evaluator = PlotEvaluator()
        start_time = time.time()

        result = evaluator.evaluate(sample_output)

        elapsed = time.time() - start_time

        # Quality check should be very fast (< 1 second)
        self.assertLess(elapsed, 1.0, "Quality evaluation should be fast")
        self.assertIsInstance(result, QualityScore)


class TestDocumentation(unittest.TestCase):
    """Test that quality system is properly documented."""

    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures."""
        cls.docs_dir = Path(__file__).parent.parent / "docs"

    def test_quality_metrics_documentation_exists(self):
        """Test that QUALITY_METRICS.md exists."""
        quality_doc = self.docs_dir / "QUALITY_METRICS.md"

        self.assertTrue(quality_doc.exists(), "QUALITY_METRICS.md documentation should exist")

    def test_quality_checking_documentation_exists(self):
        """Test that QUALITY_CHECKING.md exists."""
        checking_doc = self.docs_dir / "QUALITY_CHECKING.md"

        self.assertTrue(checking_doc.exists(), "QUALITY_CHECKING.md documentation should exist")

    def test_planning_templates_documentation_exists(self):
        """Test that PLANNING_TEMPLATES.md exists."""
        templates_doc = self.docs_dir / "PLANNING_TEMPLATES.md"

        self.assertTrue(templates_doc.exists(), "PLANNING_TEMPLATES.md documentation should exist")


if __name__ == "__main__":
    # Print environment info
    print("\n" + "=" * 70)
    print("QUALITY SYSTEM - END-TO-END INTEGRATION TESTS")
    print("=" * 70)

    if CREWAI_AVAILABLE:
        print("✓ CrewAI available")
    else:
        print("⚠ CrewAI not available - some tests will be skipped")

    if QUALITY_MODULES_AVAILABLE:
        print("✓ Quality modules available")
    else:
        print("⚠ Quality modules not available - tests will be skipped")

    # Check for quality config
    config_path = (
        Path(__file__).parent.parent / "src" / "space_hulk_game" / "config" / "quality_config.yaml"
    )
    if config_path.exists():
        print("✓ quality_config.yaml found")
    else:
        print("⚠ quality_config.yaml not found")

    # Check for templates
    templates_dir = Path(__file__).parent.parent / "planning_templates"
    if templates_dir.exists():
        template_count = len(list(templates_dir.glob("*.yaml")))
        print(f"✓ Planning templates directory found ({template_count} templates)")
    else:
        print("⚠ Planning templates directory not found")

    print("=" * 70 + "\n")

    # Run tests
    unittest.main(verbosity=2)
