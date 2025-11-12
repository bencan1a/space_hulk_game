"""
Quality metrics for PlotOutline evaluation.

This module defines measurable quality criteria for plot outlines generated
by the Space Hulk Game crew, including structure, branching paths, endings,
and narrative completeness.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PlotMetrics:
    """
    Quality metrics for evaluating plot outline content.

    Attributes:
        has_clear_setting: Whether the plot has a clearly defined setting (yes/no)
        branching_paths_count: Number of branching paths in the plot (count)
        endings_count: Number of defined endings (count)
        themes_defined: Whether themes are clearly stated (yes/no)
        word_count: Total word count of the plot outline (number)
        has_title: Whether the plot has a title (yes/no)
        has_prologue: Whether the plot includes a prologue (yes/no)
        has_acts: Whether the plot is structured into acts (yes/no)
        min_branching_paths: Minimum required branching paths (default: 2)
        min_endings: Minimum required endings (default: 2)
        min_word_count: Minimum required word count (default: 500)
    """

    # Measured values
    has_clear_setting: bool = False
    branching_paths_count: int = 0
    endings_count: int = 0
    themes_defined: bool = False
    word_count: int = 0
    has_title: bool = False
    has_prologue: bool = False
    has_acts: bool = False

    # Thresholds
    min_branching_paths: int = 2
    min_endings: int = 2
    min_word_count: int = 500

    @classmethod
    def from_json_content(cls, json_content: str) -> "PlotMetrics":
        """
        Create PlotMetrics from JSON content string.

        Args:
            json_content: JSON string containing plot outline data

        Returns:
            PlotMetrics instance with measured values

        Example:
            >>> metrics = PlotMetrics.from_json_content(json_string)
            >>> print(metrics.passes_threshold())
        """
        try:
            # Handle markdown-wrapped JSON
            content = json_content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                # Remove first and last lines (markdown fences)
                content = "\n".join(lines[1:-1])
                logger.debug("Stripped markdown fences from JSON content")

            # Try to parse as-is first
            try:
                data = json.loads(content)
            except json.JSONDecodeError as parse_error:
                # Attempt to fix common JSON syntax errors
                logger.debug(f"Initial JSON parse failed, attempting to fix: {parse_error}")
                content = cls._fix_json_syntax(content)
                data = json.loads(content)
                logger.info("Successfully parsed JSON after fixing syntax errors")

            metrics = cls.from_dict(data)
            logger.info(
                f"PlotMetrics parsed: score={metrics.get_score():.1f}/10, passes={metrics.passes_threshold()}"
            )
            return metrics
        except Exception as e:
            logger.error(f"Failed to parse plot JSON content: {e}")
            raise ValueError(f"Failed to parse JSON content: {e}") from e

    @staticmethod
    def _fix_json_syntax(content: str) -> str:
        """
        Fix common JSON syntax errors like unquoted strings and trailing commas.

        Args:
            content: JSON string with potential syntax errors

        Returns:
            Fixed JSON string
        """
        # This is a basic fix - more complex errors may still occur
        # Remove trailing commas before closing braces/brackets
        content = content.replace(",}", "}")
        content = content.replace(",]", "]")
        logger.debug("Fixed common JSON syntax errors (trailing commas)")
        return content

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlotMetrics":
        """
        Create PlotMetrics from a dictionary (parsed YAML).

        Args:
            data: Dictionary containing plot outline data

        Returns:
            PlotMetrics instance with measured values
        """
        metrics = cls()

        # Check for title
        metrics.has_title = bool(data.get("title"))

        # Check for clear setting
        setting = data.get("setting")
        if setting:
            if isinstance(setting, dict):
                # Setting is a structured dict with location, time, environment
                metrics.has_clear_setting = bool(
                    setting.get("location") or setting.get("time") or setting.get("environment")
                )
            elif isinstance(setting, str):
                # Setting is a simple string - any non-empty string is valid
                metrics.has_clear_setting = len(setting.strip()) > 0

        # Check for themes
        themes = data.get("themes", [])
        metrics.themes_defined = bool(themes) and len(themes) > 0

        # Count branching paths
        metrics.branching_paths_count = cls._count_branching_paths(data)

        # Count endings
        metrics.endings_count = cls._count_endings(data)

        # Check for prologue
        plot = data.get("plot", {})
        metrics.has_prologue = "prologue" in plot

        # Check for acts (act1, act2, act3, etc.)
        metrics.has_acts = any(key.startswith("act") for key in plot)

        # Calculate word count
        metrics.word_count = cls._calculate_word_count(data)

        return metrics

    @staticmethod
    def _count_branching_paths(data: dict[str, Any]) -> int:
        """
        Count the number of branching paths in the plot.

        Searches for "Branching Path" mentions in the plot structure
        and validates them by checking for associated choice options.
        """
        count = 0
        plot = data.get("plot", {})

        # Convert entire plot to string for searching
        plot_str = str(plot)

        # Count explicit "Branching Path" mentions (primary method)
        # This is more reliable than counting option patterns
        branching_path_count = plot_str.count("Branching Path")
        count += branching_path_count

        # If no explicit "Branching Path" mentions, look for structured choice patterns
        # Only as a fallback, and with more careful validation
        if branching_path_count == 0:
            lines = plot_str.split("\n")
            in_choice_block = False

            for i, line in enumerate(lines):
                line_stripped = line.strip()

                # Look for "A)" at start of line, preceded by some context
                # and followed by "B)" to confirm it's a real choice
                if line_stripped.startswith("A)") and not in_choice_block:
                    # Check if next few lines contain "B)" to validate this is a choice
                    is_valid_choice = False
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if lines[j].strip().startswith("B)"):
                            is_valid_choice = True
                            break

                    if is_valid_choice:
                        count += 1
                        in_choice_block = True
                elif not line_stripped.startswith(("A)", "B)", "C)", "D)")):
                    in_choice_block = False

        return count

    @staticmethod
    def _count_endings(data: dict[str, Any]) -> int:
        """
        Count the number of defined endings.

        Looks for 'endings' key or ending-related content in the plot.
        """
        # Check for explicit endings section
        endings = data.get("endings")
        if endings and isinstance(endings, dict | list):
            return len(endings)

        # Check within plot structure
        plot = data.get("plot", {})
        if "endings" in plot:
            endings = plot["endings"]
            if isinstance(endings, dict | list):
                return len(endings)

        # Count ending-related mentions
        plot_str = str(data).lower()
        ending_keywords = ["good ending", "bad ending", "ending:"]
        count = sum(plot_str.count(keyword) for keyword in ending_keywords)

        return max(count, 0)

    @staticmethod
    def _calculate_word_count(data: dict[str, Any]) -> int:
        """
        Calculate total word count of the plot outline.

        Counts all words in string values throughout the structure.
        """

        def count_words_recursive(obj: Any) -> int:
            """Recursively count words in nested structures."""
            if isinstance(obj, str):
                return len(obj.split())
            elif isinstance(obj, dict):
                return sum(count_words_recursive(v) for v in obj.values())
            elif isinstance(obj, list):
                return sum(count_words_recursive(item) for item in obj)
            else:
                return 0

        return count_words_recursive(data)

    def passes_threshold(self) -> bool:
        """
        Check if the plot metrics pass all quality thresholds.

        Returns:
            True if all thresholds are met, False otherwise
        """
        return (
            self.has_clear_setting
            and self.branching_paths_count >= self.min_branching_paths
            and self.endings_count >= self.min_endings
            and self.themes_defined
            and self.word_count >= self.min_word_count
        )

    def get_failures(self) -> list[str]:
        """
        Get list of failed quality checks.

        Returns:
            List of failure messages for metrics that don't meet thresholds
        """
        failures = []

        if not self.has_clear_setting:
            failures.append("Plot lacks a clear setting description")

        if self.branching_paths_count < self.min_branching_paths:
            failures.append(
                f"Insufficient branching paths: {self.branching_paths_count} "
                f"(minimum: {self.min_branching_paths})"
            )

        if self.endings_count < self.min_endings:
            failures.append(
                f"Insufficient endings: {self.endings_count} (minimum: {self.min_endings})"
            )

        if not self.themes_defined:
            failures.append("Themes are not clearly defined")

        if self.word_count < self.min_word_count:
            failures.append(
                f"Word count too low: {self.word_count} (minimum: {self.min_word_count})"
            )

        return failures

    def get_score(self) -> float:
        """
        Calculate overall quality score (0.0 to 10.0).

        Returns:
            Quality score based on met criteria
        """
        total_checks = 5  # Number of main quality checks
        passed_checks = 0

        if self.has_clear_setting:
            passed_checks += 1
        if self.branching_paths_count >= self.min_branching_paths:
            passed_checks += 1
        if self.endings_count >= self.min_endings:
            passed_checks += 1
        if self.themes_defined:
            passed_checks += 1
        if self.word_count >= self.min_word_count:
            passed_checks += 1

        return (passed_checks / total_checks) * 10.0

    def to_dict(self) -> dict[str, Any]:
        """
        Convert metrics to dictionary for serialization.

        Returns:
            Dictionary representation of metrics
        """
        return {
            "has_clear_setting": self.has_clear_setting,
            "branching_paths_count": self.branching_paths_count,
            "endings_count": self.endings_count,
            "themes_defined": self.themes_defined,
            "word_count": self.word_count,
            "has_title": self.has_title,
            "has_prologue": self.has_prologue,
            "has_acts": self.has_acts,
            "passes_threshold": self.passes_threshold(),
            "score": self.get_score(),
            "failures": self.get_failures(),
        }
