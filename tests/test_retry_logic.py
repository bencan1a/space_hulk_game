"""
Unit tests for retry logic with quality feedback.

Tests the retry mechanism for tasks that fail quality checks,
including feedback integration, retry limits, and quality score logging.
"""

import logging
import unittest

from src.space_hulk_game.quality.retry import (
    TaskType,
    TaskWithQualityCheck,
    create_quality_config,
    execute_with_quality_check,
)


class TestTaskType(unittest.TestCase):
    """Test TaskType enum."""

    def test_task_type_values(self):
        """Test that all task types have correct values."""
        self.assertEqual(TaskType.PLOT.value, "plot")
        self.assertEqual(TaskType.NARRATIVE.value, "narrative")
        self.assertEqual(TaskType.PUZZLE.value, "puzzle")
        self.assertEqual(TaskType.SCENE.value, "scene")
        self.assertEqual(TaskType.MECHANICS.value, "mechanics")


class TestTaskWithQualityCheck(unittest.TestCase):
    """Test TaskWithQualityCheck wrapper class."""

    def test_initialization(self):
        """Test wrapper initializes correctly."""
        wrapper = TaskWithQualityCheck(task_type=TaskType.PLOT, pass_threshold=7.0, max_retries=3)

        self.assertEqual(wrapper.task_type, TaskType.PLOT)
        self.assertEqual(wrapper.pass_threshold, 7.0)
        self.assertEqual(wrapper.max_retries, 3)
        self.assertIsNotNone(wrapper.evaluator)

    def test_invalid_threshold(self):
        """Test that invalid threshold raises ValueError."""
        with self.assertRaises(ValueError) as context:
            TaskWithQualityCheck(
                task_type=TaskType.PLOT,
                pass_threshold=11.0,  # Invalid: > 10.0
            )
        self.assertIn("Pass threshold must be between", str(context.exception))

    def test_invalid_max_retries(self):
        """Test that invalid max_retries raises ValueError."""
        with self.assertRaises(ValueError) as context:
            TaskWithQualityCheck(
                task_type=TaskType.PLOT,
                max_retries=0,  # Invalid: must be >= 1
            )
        self.assertIn("Max retries must be at least 1", str(context.exception))

    def test_creates_correct_evaluator(self):
        """Test that correct evaluator is created for each task type."""
        from src.space_hulk_game.quality.mechanics_evaluator import MechanicsEvaluator
        from src.space_hulk_game.quality.narrative_evaluator import NarrativeMapEvaluator
        from src.space_hulk_game.quality.plot_evaluator import PlotEvaluator
        from src.space_hulk_game.quality.puzzle_evaluator import PuzzleEvaluator
        from src.space_hulk_game.quality.scene_evaluator import SceneEvaluator

        test_cases = [
            (TaskType.PLOT, PlotEvaluator),
            (TaskType.NARRATIVE, NarrativeMapEvaluator),
            (TaskType.PUZZLE, PuzzleEvaluator),
            (TaskType.SCENE, SceneEvaluator),
            (TaskType.MECHANICS, MechanicsEvaluator),
        ]

        for task_type, expected_class in test_cases:
            wrapper = TaskWithQualityCheck(task_type=task_type)
            self.assertIsInstance(wrapper.evaluator, expected_class)

    def test_execute_passes_first_attempt(self):
        """Test successful execution on first attempt."""

        # Create a task function that returns good quality output
        def good_task(**kwargs):
            return """
{
  "title": "Excellent Adventure",
  "setting": "A detailed and immersive setting description with rich atmosphere and clear stakes.",
  "themes": ["survival", "mystery", "horror"],
  "tone": "Dark, tense, and atmospheric",
  "main_branches": [
    {
      "path": "Investigation Path",
      "description": "Search for clues about what happened to the crew"
    },
    {
      "path": "Escape Path",
      "description": "Find a way to escape the derelict vessel"
    },
    {
      "path": "Combat Path",
      "description": "Fight through hostile entities"
    }
  ],
  "endings": [
    {
      "name": "Victory",
      "description": "Successfully escape with critical intelligence",
      "type": "victory"
    },
    {
      "name": "Defeat",
      "description": "Overwhelmed by the hostile forces",
      "type": "defeat"
    },
    {
      "name": "Sacrifice",
      "description": "Sacrifice yourself to save others",
      "type": "neutral"
    }
  ]
}
"""

        wrapper = TaskWithQualityCheck(task_type=TaskType.PLOT, pass_threshold=6.0, max_retries=3)

        output, quality, attempts = wrapper.execute(task_function=good_task, task_name="Test Plot")

        self.assertIn("Excellent Adventure", output)
        self.assertTrue(quality.passed)
        self.assertGreaterEqual(quality.score, 6.0)
        self.assertEqual(attempts, 1)

    def test_execute_retries_on_failure(self):
        """Test retry behavior when quality check fails."""
        # Create a mock task that improves over attempts
        call_count = [0]

        def improving_task(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First attempt: poor quality (minimal content)
                return '{"title": "Test", "setting": "Bad"}'
            else:
                # Second attempt: good quality
                return """
{
  "title": "Improved Plot",
  "setting": "A detailed and well-developed setting with clear atmosphere and stakes.",
  "themes": ["mystery", "horror"],
  "tone": "Dark and atmospheric",
  "main_branches": [
    {
      "path": "Path A",
      "description": "A detailed branching path with clear choices and consequences"
    },
    {
      "path": "Path B",
      "description": "An alternative path with different challenges"
    }
  ],
  "endings": [
    {
      "name": "Victory",
      "description": "A satisfying victory ending",
      "type": "victory"
    },
    {
      "name": "Defeat",
      "description": "A dramatic defeat ending",
      "type": "defeat"
    }
  ]
}
"""

        wrapper = TaskWithQualityCheck(task_type=TaskType.PLOT, pass_threshold=6.0, max_retries=3)

        output, quality, attempts = wrapper.execute(
            task_function=improving_task, task_name="Test Plot"
        )

        self.assertIn("Improved Plot", output)
        self.assertTrue(quality.passed)
        self.assertEqual(attempts, 2)
        self.assertEqual(call_count[0], 2)

    def test_execute_reaches_max_retries(self):
        """Test that execution stops after max retries."""

        # Create a task that always fails quality checks
        def failing_task(**kwargs):
            return '{"title": "Bad", "setting": "Poor"}'

        wrapper = TaskWithQualityCheck(task_type=TaskType.PLOT, pass_threshold=6.0, max_retries=3)

        with self.assertLogs(level=logging.WARNING) as log:
            output, quality, attempts = wrapper.execute(
                task_function=failing_task, task_name="Test Plot"
            )

        # Should return output even if it doesn't pass
        self.assertIn('"title": "Bad"', output)
        self.assertFalse(quality.passed)
        self.assertEqual(attempts, 3)

        # Check that warning was logged
        self.assertTrue(any("Max retries" in message for message in log.output))

    def test_feedback_history_accumulated(self):
        """Test that feedback history is accumulated across retries."""
        call_count = [0]
        feedback_received = []

        def task_with_feedback(**kwargs):
            call_count[0] += 1
            # Store feedback from previous attempts
            if "feedback_history" in kwargs:
                # Make a copy to avoid reference issues
                feedback_received.append(list(kwargs["feedback_history"]))

            # Always return poor quality to test feedback accumulation
            return '{"title": "Test", "setting": "Bad"}'

        wrapper = TaskWithQualityCheck(task_type=TaskType.PLOT, pass_threshold=6.0, max_retries=3)

        _, _, _attempts = wrapper.execute(task_function=task_with_feedback, task_name="Test Plot")

        # Should have been called 3 times
        self.assertEqual(call_count[0], 3)

        # Feedback should accumulate (attempts 2 and 3 receive feedback)
        self.assertGreaterEqual(len(feedback_received), 2)

        # Verify feedback items are present
        if len(feedback_received) >= 2:
            # Each feedback item should have attempt number
            for feedback_list in feedback_received:
                for feedback_item in feedback_list:
                    self.assertIn("attempt", feedback_item)
                    self.assertIn("score", feedback_item)
                    self.assertIn("feedback", feedback_item)

    def test_execute_handles_task_exception(self):
        """Test handling of exceptions during task execution."""
        call_count = [0]

        def failing_then_succeeding_task(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("Simulated task failure")
            # Second attempt succeeds with high quality output
            return """
{
  "title": "Recovery Test: A Comprehensive Adventure",
  "setting": "A detailed and richly described setting after recovery from error, with atmospheric details and clear stakes that draw the player into the narrative.",
  "themes": ["recovery", "resilience", "redemption"],
  "tone": "Hopeful yet tense",
  "main_branches": [
    {
      "path": "Success Path",
      "description": "A detailed path to success after failure with clear challenges and rewards"
    },
    {
      "path": "Alternative Route",
      "description": "An alternative approach with different consequences and opportunities"
    },
    {
      "path": "Risk and Reward",
      "description": "A high-risk, high-reward path for bold adventurers"
    }
  ],
  "endings": [
    {
      "name": "Victory",
      "description": "Overcame the challenge through perseverance and skill",
      "type": "victory"
    },
    {
      "name": "Pyrrhic Victory",
      "description": "Success but at great cost",
      "type": "neutral"
    },
    {
      "name": "Learning Experience",
      "description": "Failure that teaches valuable lessons",
      "type": "defeat"
    }
  ]
}
"""

        wrapper = TaskWithQualityCheck(task_type=TaskType.PLOT, pass_threshold=6.0, max_retries=3)

        output, quality, attempts = wrapper.execute(
            task_function=failing_then_succeeding_task, task_name="Test Plot"
        )

        # Should succeed on second attempt
        self.assertIn("Recovery Test", output)
        self.assertTrue(quality.passed)
        self.assertEqual(attempts, 2)

    def test_execute_raises_on_persistent_exception(self):
        """Test that persistent exceptions are raised after max retries."""

        def always_failing_task(**kwargs):
            raise RuntimeError("Persistent failure")

        wrapper = TaskWithQualityCheck(task_type=TaskType.PLOT, pass_threshold=6.0, max_retries=3)

        with self.assertRaises(RuntimeError) as context:
            wrapper.execute(task_function=always_failing_task, task_name="Test Plot")

        self.assertIn("Persistent failure", str(context.exception))

    def test_execute_handles_evaluation_exception(self):
        """Test handling of evaluation errors."""

        def task_with_bad_output(**kwargs):
            # Return output that causes evaluation error
            return '{ "invalid": "json", "unclosed": ['

        wrapper = TaskWithQualityCheck(
            task_type=TaskType.PLOT,
            pass_threshold=6.0,
            max_retries=1,  # Only 1 attempt to speed up test
        )

        output, quality, attempts = wrapper.execute(
            task_function=task_with_bad_output, task_name="Test Plot"
        )

        # Should return output even if evaluation fails
        self.assertIn("invalid", output)
        self.assertFalse(quality.passed)
        self.assertEqual(quality.score, 0.0)
        # The feedback contains the parse error message
        self.assertIn("Failed to parse", quality.feedback)
        self.assertEqual(attempts, 1)


class TestExecuteWithQualityCheck(unittest.TestCase):
    """Test execute_with_quality_check functional interface."""

    def test_functional_interface(self):
        """Test that functional interface works correctly."""

        def good_task(**kwargs):
            return """
{
  "title": "Good Plot",
  "setting": "A well-developed setting with clear details and atmosphere.",
  "themes": ["adventure"],
  "tone": "Exciting",
  "main_branches": [
    {
      "path": "Path A",
      "description": "First branching path"
    },
    {
      "path": "Path B",
      "description": "Second branching path"
    }
  ],
  "endings": [
    {
      "name": "Victory",
      "description": "Success ending",
      "type": "victory"
    },
    {
      "name": "Defeat",
      "description": "Failure ending",
      "type": "defeat"
    }
  ]
}
"""

        output, quality, attempts = execute_with_quality_check(
            task_function=good_task,
            task_type=TaskType.PLOT,
            task_name="Test Plot",
            pass_threshold=6.0,
            max_retries=3,
        )

        self.assertIn("Good Plot", output)
        self.assertTrue(quality.passed)
        self.assertGreaterEqual(quality.score, 6.0)
        self.assertEqual(attempts, 1)

    def test_functional_with_custom_threshold(self):
        """Test functional interface with custom threshold."""

        def average_task(**kwargs):
            return """
{
  "title": "Average Plot",
  "setting": "A basic setting description.",
  "themes": ["action"],
  "tone": "Standard",
  "main_branches": [
    {
      "path": "Path",
      "description": "A path"
    }
  ],
  "endings": [
    {
      "name": "End",
      "description": "An ending",
      "type": "victory"
    }
  ]
}
"""

        # With higher threshold, might not pass
        output, _quality, attempts = execute_with_quality_check(
            task_function=average_task,
            task_type=TaskType.PLOT,
            task_name="Test Plot",
            pass_threshold=8.0,  # Higher threshold
            max_retries=1,
        )

        self.assertIn("Average Plot", output)
        # May or may not pass depending on score, but should complete
        self.assertEqual(attempts, 1)


class TestCreateQualityConfig(unittest.TestCase):
    """Test create_quality_config helper function."""

    def test_creates_config_with_defaults(self):
        """Test creating config with default values."""
        config = create_quality_config()

        # Should have all task types
        self.assertEqual(len(config), 5)
        self.assertIn(TaskType.PLOT, config)
        self.assertIn(TaskType.NARRATIVE, config)
        self.assertIn(TaskType.PUZZLE, config)
        self.assertIn(TaskType.SCENE, config)
        self.assertIn(TaskType.MECHANICS, config)

        # Check default values
        for _task_type, task_config in config.items():
            self.assertEqual(task_config["pass_threshold"], 6.0)
            self.assertEqual(task_config["max_retries"], 3)

    def test_creates_config_with_custom_values(self):
        """Test creating config with custom values."""
        config = create_quality_config(
            plot_threshold=7.0,
            narrative_threshold=8.0,
            puzzle_threshold=6.5,
            scene_threshold=7.5,
            mechanics_threshold=6.0,
            max_retries=5,
        )

        self.assertEqual(config[TaskType.PLOT]["pass_threshold"], 7.0)
        self.assertEqual(config[TaskType.NARRATIVE]["pass_threshold"], 8.0)
        self.assertEqual(config[TaskType.PUZZLE]["pass_threshold"], 6.5)
        self.assertEqual(config[TaskType.SCENE]["pass_threshold"], 7.5)
        self.assertEqual(config[TaskType.MECHANICS]["pass_threshold"], 6.0)

        # All should have same max_retries
        for task_config in config.values():
            self.assertEqual(task_config["max_retries"], 5)

    def test_config_can_be_used_with_wrapper(self):
        """Test that generated config can be used with TaskWithQualityCheck."""
        config = create_quality_config(plot_threshold=7.5, max_retries=2)

        plot_config = config[TaskType.PLOT]

        wrapper = TaskWithQualityCheck(
            task_type=TaskType.PLOT,
            pass_threshold=plot_config["pass_threshold"],
            max_retries=plot_config["max_retries"],
        )

        self.assertEqual(wrapper.pass_threshold, 7.5)
        self.assertEqual(wrapper.max_retries, 2)


class TestRetryLoggingIntegration(unittest.TestCase):
    """Test that retry logic logs appropriately."""

    def test_logs_quality_scores(self):
        """Test that quality scores are logged."""

        def good_task(**kwargs):
            return """
{
  "title": "Test",
  "setting": "A detailed setting with proper description and atmosphere.",
  "themes": ["test"],
  "tone": "Test",
  "main_branches": [
    {
      "path": "A",
      "description": "Path description"
    }
  ],
  "endings": [
    {
      "name": "End",
      "description": "Ending",
      "type": "victory"
    }
  ]
}
"""

        wrapper = TaskWithQualityCheck(task_type=TaskType.PLOT, pass_threshold=6.0, max_retries=3)

        with self.assertLogs(level=logging.INFO) as log:
            wrapper.execute(good_task, task_name="Test Plot")

        # Check that quality score was logged
        self.assertTrue(
            any(
                "Quality score" in message or "quality" in message.lower() for message in log.output
            )
        )

    def test_logs_retry_attempts(self):
        """Test that retry attempts are logged."""
        call_count = [0]

        def improving_task(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return '{"title": "Bad", "setting": "Poor"}'
            return """
{
  "title": "Better",
  "setting": "An improved setting with good details and atmosphere.",
  "themes": ["improvement"],
  "tone": "Better",
  "main_branches": [
    {
      "path": "A",
      "description": "Path"
    }
  ],
  "endings": [
    {
      "name": "End",
      "description": "End",
      "type": "victory"
    }
  ]
}
"""

        wrapper = TaskWithQualityCheck(task_type=TaskType.PLOT, pass_threshold=6.0, max_retries=3)

        with self.assertLogs(level=logging.INFO) as log:
            wrapper.execute(improving_task, task_name="Test Plot")

        # Check that both attempts were logged
        log_output = " ".join(log.output)
        self.assertIn("Attempt 1", log_output)
        self.assertIn("Attempt 2", log_output)


if __name__ == "__main__":
    unittest.main()
