"""
Game mechanics quality evaluator.

This module implements the evaluator for game mechanics content,
using MechanicsMetrics to score systems, rules clarity, and balance.
"""

import logging

from .evaluator import QualityEvaluator
from .mechanics_metrics import MechanicsMetrics
from .score import QualityScore

logger = logging.getLogger(__name__)


class MechanicsEvaluator(QualityEvaluator):
    """
    Evaluator for game mechanics content.

    Uses MechanicsMetrics to evaluate game mechanics against quality criteria
    including systems completeness, rules clarity, and balance.

    Example:
        >>> evaluator = MechanicsEvaluator()
        >>> score = evaluator.evaluate(mechanics_json_content)
        >>> print(f"Score: {score.score}/10")
        >>> print(score.feedback)
    """

    def __init__(self, pass_threshold: float = 6.0):
        """
        Initialize the mechanics evaluator.

        Args:
            pass_threshold: Minimum score required to pass (default: 6.0)
        """
        super().__init__(pass_threshold)
        logger.info(f"MechanicsEvaluator initialized with threshold {pass_threshold}")

    def evaluate(self, content: str) -> QualityScore:
        """
        Evaluate game mechanics content.

        Args:
            content: JSON string containing game mechanics

        Returns:
            QualityScore with evaluation results

        Raises:
            ValueError: If content cannot be parsed
        """
        try:
            # Parse JSON content using metrics class
            metrics = MechanicsMetrics.from_json_content(content)

            # Get score and check if passes threshold
            score = metrics.get_score()
            passed = score >= self.pass_threshold

            # Get failures for detailed feedback
            failures = metrics.get_failures()

            # Build feedback message
            feedback = self._build_feedback(score, failures)

            # Build details dictionary
            details = {
                "total_systems": metrics.total_systems,
                "systems_with_rules": metrics.systems_with_rules,
                "has_combat_system": metrics.has_combat_system,
                "has_movement_system": metrics.has_movement_system,
                "has_inventory_system": metrics.has_inventory_system,
                "has_progression_system": metrics.has_progression_system,
                "completeness_percentage": metrics.completeness_percentage,
                "average_rule_clarity": metrics.average_rule_clarity,
                "has_balance_notes": metrics.has_balance_notes,
                "total_word_count": 0,  # Can be computed if needed
                "systems_without_descriptions": [],
                "unclear_systems": [],
                "failures": failures,
                "threshold": self.pass_threshold,
            }

            logger.info(
                f"Mechanics evaluation complete: score={score:.1f}, passed={passed}, "
                f"systems={metrics.total_systems}, clarity={metrics.average_rule_clarity:.1f}"
            )

            return self._create_score(score, passed, feedback, details)

        except ValueError as e:
            logger.error(f"Failed to evaluate mechanics content: {e}")
            return self._create_score(
                score=0.0,
                passed=False,
                feedback=f"Failed to parse mechanics content: {e!s}",
                details={"error": str(e)},
            )
        except Exception as e:
            logger.exception(f"Unexpected error evaluating mechanics: {e}")
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
            content: JSON string containing game mechanics

        Returns:
            Multi-line feedback with specific suggestions
        """
        result = self.evaluate(content)

        lines = [
            f"Game Mechanics Quality Score: {result.score:.1f}/10.0",
            f"Status: {'PASS ✓' if result.passed else 'FAIL ✗'}",
            "",
        ]

        if result.passed:
            lines.append("The game mechanics meet all quality requirements!")
        else:
            lines.append("The game mechanics need improvement:")

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
        lines.append(f"System count: {details.get('total_systems', 0)} (min: 3)")
        lines.append(f"Systems with rules: {details.get('systems_with_rules', 0)}")
        lines.append(f"Completeness: {details.get('completeness_percentage', 0):.1f}%")
        lines.append(f"Average clarity: {details.get('average_rule_clarity', 0):.1f}/10")

        # Add positive feedback
        lines.append("")
        if details.get("has_combat_system"):
            lines.append("✓ Combat system described")
        if details.get("has_movement_system"):
            lines.append("✓ Movement system described")
        if details.get("has_inventory_system"):
            lines.append("✓ Inventory system described")
        if details.get("has_progression_system"):
            lines.append("✓ Progression system described")
        if details.get("average_rule_clarity", 0) >= 7.0:
            lines.append("✓ Rules are clear and well-explained")
        if details.get("has_balance_notes"):
            lines.append("✓ Difficulty/balance discussed")

        return "\n".join(lines)
