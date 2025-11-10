"""
Narrative map quality evaluator.

This module implements the evaluator for narrative map content,
using NarrativeMetrics to score and validate scene graph structure.
"""

import logging

from .evaluator import QualityEvaluator
from .narrative_metrics import NarrativeMetrics
from .score import QualityScore

logger = logging.getLogger(__name__)


class NarrativeMapEvaluator(QualityEvaluator):
    """
    Evaluator for narrative map content.

    Uses NarrativeMetrics to evaluate narrative maps against quality criteria
    including scene connectivity, completeness, and orphan detection.

    Example:
        >>> evaluator = NarrativeMapEvaluator()
        >>> score = evaluator.evaluate(narrative_yaml_content)
        >>> print(f"Score: {score.score}/10")
        >>> print(score.feedback)
    """

    def __init__(self, pass_threshold: float = 6.0):
        """
        Initialize the narrative map evaluator.

        Args:
            pass_threshold: Minimum score required to pass (default: 6.0)
        """
        super().__init__(pass_threshold)
        logger.info(f"NarrativeMapEvaluator initialized with threshold {pass_threshold}")

    def evaluate(self, content: str) -> QualityScore:
        """
        Evaluate narrative map content.

        Args:
            content: YAML string containing narrative map

        Returns:
            QualityScore with evaluation results

        Raises:
            ValueError: If content cannot be parsed
        """
        try:
            # Parse YAML content using metrics class
            metrics = NarrativeMetrics.from_yaml_content(content)

            # Get score and check if passes threshold
            score = metrics.get_score()
            passed = score >= self.pass_threshold

            # Get failures for detailed feedback
            failures = metrics.get_failures()

            # Build feedback message
            feedback = self._build_feedback(score, failures)

            # Build details dictionary
            details = {
                'total_scenes': metrics.total_scenes,
                'scenes_with_descriptions': metrics.scenes_with_descriptions,
                'all_connections_valid': metrics.all_connections_valid,
                'has_orphaned_scenes': metrics.has_orphaned_scenes,
                'orphaned_scenes': list(metrics.orphaned_scenes) if metrics.orphaned_scenes else [],
                'invalid_connections': [],  # Legacy field, no longer tracked
                'completeness_percentage': metrics.completeness_percentage,
                'failures': failures,
                'threshold': self.pass_threshold
            }

            logger.info(
                f"Narrative map evaluation complete: score={score:.1f}, passed={passed}, "
                f"scenes={metrics.total_scenes}, orphans={len(metrics.orphaned_scenes) if metrics.orphaned_scenes else 0}"
            )

            return self._create_score(score, passed, feedback, details)

        except ValueError as e:
            logger.error(f"Failed to evaluate narrative map content: {e}")
            return self._create_score(
                score=0.0,
                passed=False,
                feedback=f"Failed to parse narrative map content: {str(e)}",
                details={'error': str(e)}
            )
        except Exception as e:
            logger.exception(f"Unexpected error evaluating narrative map: {e}")
            return self._create_score(
                score=0.0,
                passed=False,
                feedback=f"Unexpected error during evaluation: {str(e)}",
                details={'error': str(e)}
            )

    def generate_detailed_feedback(self, content: str) -> str:
        """
        Generate detailed, actionable feedback for improvement.

        Args:
            content: YAML string containing narrative map

        Returns:
            Multi-line feedback with specific suggestions
        """
        result = self.evaluate(content)

        lines = [
            f"Narrative Map Quality Score: {result.score:.1f}/10.0",
            f"Status: {'PASS ✓' if result.passed else 'FAIL ✗'}",
            "",
        ]

        if result.passed:
            lines.append("The narrative map meets all quality requirements!")
        else:
            lines.append("The narrative map needs improvement:")

        lines.append("")

        # Add specific findings
        details = result.details
        failures = details.get('failures', [])

        if failures:
            lines.append("Issues to address:")
            for failure in failures:
                lines.append(f"  • {failure}")
            lines.append("")

        # Add scene statistics
        lines.append(f"Scene count: {details.get('total_scenes', 0)} (min: 5)")
        lines.append(f"Completeness: {details.get('completeness_percentage', 0):.1f}%")

        # List orphaned scenes if any
        orphaned = details.get('orphaned_scenes', [])
        if orphaned:
            lines.append("")
            lines.append(f"Orphaned scenes ({len(orphaned)}):")
            for scene_id in orphaned:
                lines.append(f"  • {scene_id}")

        # List invalid connections if any
        invalid = details.get('invalid_connections', [])
        if invalid:
            lines.append("")
            lines.append(f"Invalid connections ({len(invalid)}):")
            for conn in invalid:
                lines.append(f"  • {conn}")

        # Add positive feedback
        lines.append("")
        if details.get('scenes_with_descriptions', 0) == details.get('total_scenes', 0):
            lines.append("✓ All scenes have descriptions")
        if details.get('all_connections_valid'):
            lines.append("✓ All connections are valid")
        if not details.get('has_orphaned_scenes'):
            lines.append("✓ No orphaned scenes")

        return "\n".join(lines)
