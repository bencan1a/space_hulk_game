"""
Base quality evaluator class for content evaluation.

This module defines the abstract base class for all content evaluators,
providing common functionality for YAML parsing, error handling, and
standardized evaluation interface.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

import yaml

from space_hulk_game.utils.yaml_processor import strip_markdown_yaml_blocks

from .score import QualityScore

logger = logging.getLogger(__name__)


class QualityEvaluator(ABC):
    """
    Abstract base class for all quality evaluators.

    All content-specific evaluators (Plot, Narrative, Puzzle, Scene, Mechanics)
    should inherit from this class and implement the required methods.

    Example:
        >>> class PlotEvaluator(QualityEvaluator):
        ...     def evaluate(self, content: str) -> QualityScore:
        ...         # Implementation here
        ...         pass
    """

    def __init__(self, pass_threshold: float = 6.0):
        """
        Initialize the evaluator.

        Args:
            pass_threshold: Minimum score required to pass (0.0-10.0)
        """
        if not 0.0 <= pass_threshold <= 10.0:
            raise ValueError(f"Pass threshold must be between 0.0 and 10.0, got {pass_threshold}")

        self.pass_threshold = pass_threshold
        logger.debug(f"{self.__class__.__name__} initialized with threshold {pass_threshold}")

    @abstractmethod
    def evaluate(self, content: str) -> QualityScore:
        """
        Evaluate content and return quality score.

        Args:
            content: Content to evaluate (usually YAML string)

        Returns:
            QualityScore with evaluation results

        Raises:
            ValueError: If content cannot be parsed or evaluated
        """
        pass

    def score(self, content: str) -> float:
        """
        Get numeric score for content (convenience method).

        Args:
            content: Content to evaluate

        Returns:
            Numeric score from 0.0 to 10.0
        """
        result = self.evaluate(content)
        return result.score

    def generate_feedback(self, content: str) -> str:
        """
        Generate feedback message for content (convenience method).

        Args:
            content: Content to evaluate

        Returns:
            Human-readable feedback message
        """
        result = self.evaluate(content)
        return result.feedback

    @staticmethod
    def parse_yaml(content: str) -> dict[str, Any]:
        """
        Parse YAML content, handling markdown-wrapped YAML.

        NOTE: YAML sanitization happens in OutputSanitizer (Phase 1).
        This method assumes YAML is already clean. If parsing fails, it's a real error.

        Args:
            content: YAML string, optionally wrapped in markdown code fences

        Returns:
            Parsed YAML as dictionary

        Raises:
            ValueError: If YAML cannot be parsed
        """
        try:
            # Handle markdown-wrapped YAML
            content_stripped = strip_markdown_yaml_blocks(content.strip())
            logger.debug("Stripped markdown fences from YAML content")

            data = yaml.safe_load(content_stripped)
            if data is None:
                raise ValueError("YAML content is empty or invalid")
            return dict(data)

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {e}")
            raise ValueError(f"Invalid YAML content: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error parsing YAML: {e}")
            raise ValueError(f"Failed to parse content: {e}") from e

    def _create_score(
        self, score: float, passed: bool, feedback: str, details: dict[str, Any] | None = None
    ) -> QualityScore:
        """
        Create a QualityScore instance (helper method).

        Args:
            score: Numeric score (0.0-10.0)
            passed: Whether quality threshold was met
            feedback: Feedback message
            details: Optional detailed metrics

        Returns:
            QualityScore instance
        """
        return QualityScore(score=score, passed=passed, feedback=feedback, details=details or {})

    def _build_feedback(self, score: float, failures: list, successes: list | None = None) -> str:  # noqa: ARG002
        """
        Build feedback message from score and findings.

        Args:
            score: Numeric score
            failures: List of failure messages
            successes: Optional list of success messages

        Returns:
            Human-readable feedback message
        """
        if score >= 9.0:
            base = "Excellent quality"
        elif score >= 7.0:
            base = "Good quality"
        elif score >= 5.0:
            base = "Acceptable quality"
        elif score >= 3.0:
            base = "Poor quality"
        else:
            base = "Very poor quality"

        if not failures:
            return f"{base} - all checks passed"

        if len(failures) == 1:
            return f"{base} - {failures[0]}"

        return f"{base} - {len(failures)} issues found"

    def __repr__(self) -> str:
        """String representation of evaluator."""
        return f"{self.__class__.__name__}(threshold={self.pass_threshold})"
