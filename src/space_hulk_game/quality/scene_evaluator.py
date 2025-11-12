"""
Scene text quality evaluator.

This module implements the evaluator for scene text content,
using SceneMetrics to score text quality, dialogue, and tone.
"""

import logging

from .evaluator import QualityEvaluator
from .scene_metrics import SceneMetrics
from .score import QualityScore

logger = logging.getLogger(__name__)


class SceneEvaluator(QualityEvaluator):
    """
    Evaluator for scene text content.

    Uses SceneMetrics to evaluate scene texts against quality criteria
    including vivid descriptions, dialogue presence, tone consistency,
    and sensory details.

    Example:
        >>> evaluator = SceneEvaluator()
        >>> score = evaluator.evaluate(scene_json_content)
        >>> print(f"Score: {score.score}/10")
        >>> print(score.feedback)
    """

    def __init__(self, pass_threshold: float = 6.0):
        """
        Initialize the scene evaluator.

        Args:
            pass_threshold: Minimum score required to pass (default: 6.0)
        """
        super().__init__(pass_threshold)
        logger.info(f"SceneEvaluator initialized with threshold {pass_threshold}")

    def evaluate(self, content: str) -> QualityScore:
        """
        Evaluate scene text content.

        Args:
            content: JSON string containing scene texts

        Returns:
            QualityScore with evaluation results

        Raises:
            ValueError: If content cannot be parsed
        """
        try:
            # Parse JSON content using metrics class
            metrics = SceneMetrics.from_json_content(content)

            # Get score and check if passes threshold
            score = metrics.get_score()
            passed = score >= self.pass_threshold

            # Get failures for detailed feedback
            failures = metrics.get_failures()

            # Build feedback message
            feedback = self._build_feedback(score, failures)

            # Build details dictionary
            details = {
                "total_scenes": metrics.total_scenes,
                "scenes_with_vivid_descriptions": metrics.scenes_with_vivid_descriptions,
                "scenes_with_dialogue": metrics.scenes_with_dialogue,
                "average_description_length": metrics.average_description_length,
                "tone_consistency_score": metrics.tone_consistency_score,
                "has_sensory_details": metrics.has_sensory_details,
                "total_word_count": metrics.average_description_length * metrics.total_scenes
                if metrics.total_scenes > 0
                else 0,
                "scenes_without_descriptions": [],  # Can be computed if needed
                "scenes_with_short_descriptions": [],
                "failures": failures,
                "threshold": self.pass_threshold,
            }

            logger.info(
                f"Scene evaluation complete: score={score:.1f}, passed={passed}, "
                f"scenes={metrics.total_scenes}, avg_length={metrics.average_description_length:.0f}"
            )

            return self._create_score(score, passed, feedback, details)

        except ValueError as e:
            logger.error(f"Failed to evaluate scene content: {e}")
            return self._create_score(
                score=0.0,
                passed=False,
                feedback=f"Failed to parse scene content: {e!s}",
                details={"error": str(e)},
            )
        except Exception as e:
            logger.exception(f"Unexpected error evaluating scene: {e}")
            return self._create_score(
                score=0.0,
                passed=False,
                feedback=f"Unexpected error during evaluation: {e!s}",
                details={"error": str(e)},
            )

    def generate_detailed_feedback(self, content: str) -> str:
        """
        Generate detailed, actionable feedback for improvement.

        Args:
            content: JSON string containing scene texts

        Returns:
            Multi-line feedback with specific suggestions
        """
        result = self.evaluate(content)

        lines = [
            f"Scene Text Quality Score: {result.score:.1f}/10.0",
            f"Status: {'PASS ✓' if result.passed else 'FAIL ✗'}",
            "",
        ]

        if result.passed:
            lines.append("The scene texts meet all quality requirements!")
        else:
            lines.append("The scene texts need improvement:")

        lines.append("")

        # Add specific findings
        details = result.details
        failures = details.get("failures", [])

        if failures:
            lines.append("Issues to address:")
            for failure in failures:
                lines.append(f"  • {failure}")
            lines.append("")

        # Add content statistics
        lines.append(f"Scene count: {details.get('total_scenes', 0)} (min: 5)")
        lines.append(f"Total word count: {details.get('total_word_count', 0):.0f}")
        lines.append(
            f"Average description length: {details.get('average_description_length', 0):.0f} words"
        )
        lines.append(
            f"Scenes with vivid descriptions: {details.get('scenes_with_vivid_descriptions', 0)}"
        )
        lines.append(f"Scenes with dialogue: {details.get('scenes_with_dialogue', 0)}")

        # Add positive feedback
        lines.append("")
        if details.get("scenes_with_vivid_descriptions", 0) > 0:
            lines.append("✓ Vivid, detailed descriptions present")
        if details.get("scenes_with_dialogue", 0) > 0:
            lines.append("✓ Dialogue present where appropriate")
        if details.get("tone_consistency_score", 0) >= 7.0:
            lines.append("✓ Consistent tone throughout")
        if details.get("has_sensory_details"):
            lines.append("✓ Rich sensory details included")

        return "\n".join(lines)
