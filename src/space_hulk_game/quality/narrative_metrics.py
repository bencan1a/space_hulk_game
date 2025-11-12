"""
Quality metrics for NarrativeMap evaluation.

This module defines measurable quality criteria for narrative maps generated
by the Space Hulk Game crew, including scene connectivity, completeness,
and structural validity.
"""

import json
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class NarrativeMetrics:
    """
    Quality metrics for evaluating narrative map content.

    Attributes:
        total_scenes: Total number of scenes in the narrative
        scenes_with_descriptions: Number of scenes that have descriptions
        completeness_percentage: Percentage of scenes with descriptions
        all_connections_valid: Whether all scene connections reference valid scenes
        has_orphaned_scenes: Whether there are unreachable scenes
        orphaned_scenes: List of orphaned scene IDs
        scene_count: Number of scenes (for threshold check)
        has_start_scene: Whether a start scene is defined
        min_scenes: Minimum required scenes (default: 5)
    """

    # Measured values
    total_scenes: int = 0
    scenes_with_descriptions: int = 0
    completeness_percentage: float = 0.0
    all_connections_valid: bool = True
    has_orphaned_scenes: bool = False
    orphaned_scenes: list[str] = field(default_factory=list)
    has_start_scene: bool = False

    # Thresholds
    min_scenes: int = 5
    min_completeness: float = 90.0  # 90% of scenes should have descriptions

    def __post_init__(self):
        """Initialize mutable default values."""
        if self.orphaned_scenes is None:
            self.orphaned_scenes = []

    @classmethod
    def from_json_content(cls, json_content: str) -> "NarrativeMetrics":
        """
        Create NarrativeMetrics from JSON content string.

        Args:
            json_content: JSON string containing narrative map data

        Returns:
            NarrativeMetrics instance with measured values
        """
        try:
            # Handle markdown-wrapped JSON
            content = json_content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])
                logger.debug("Stripped markdown fences from narrative JSON")

            data = json.loads(content)
            metrics = cls.from_dict(data)

            if metrics.has_orphaned_scenes:
                logger.warning(
                    f"NarrativeMetrics: Found {len(metrics.orphaned_scenes)} orphaned scenes: {metrics.orphaned_scenes}"
                )

            logger.info(
                f"NarrativeMetrics parsed: score={metrics.get_score():.1f}/10, passes={metrics.passes_threshold()}"
            )
            return metrics
        except Exception as e:
            logger.error(f"Failed to parse narrative JSON content: {e}")
            raise ValueError(f"Failed to parse JSON content: {e}") from e

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NarrativeMetrics":
        """
        Create NarrativeMetrics from a dictionary (parsed YAML).

        Args:
            data: Dictionary containing narrative map data

        Returns:
            NarrativeMetrics instance with measured values
        """
        metrics = cls()

        # Get narrative map structure
        narrative_map = data.get("narrative_map", data)

        # Check for start scene
        metrics.has_start_scene = bool(narrative_map.get("start_scene"))

        # Get scenes
        scenes = narrative_map.get("scenes", {})
        metrics.total_scenes = len(scenes)

        # Count scenes with descriptions
        for _scene_id, scene_data in scenes.items():
            if scene_data and scene_data.get("description"):
                metrics.scenes_with_descriptions += 1

        # Calculate completeness percentage
        if metrics.total_scenes > 0:
            metrics.completeness_percentage = (
                metrics.scenes_with_descriptions / metrics.total_scenes
            ) * 100.0

        # Validate connections
        metrics.all_connections_valid = cls._validate_connections(scenes)

        # Find orphaned scenes
        metrics.orphaned_scenes = cls._find_orphaned_scenes(
            scenes, narrative_map.get("start_scene")
        )
        metrics.has_orphaned_scenes = len(metrics.orphaned_scenes) > 0

        return metrics

    @staticmethod
    def _validate_connections(scenes: dict[str, Any]) -> bool:
        """
        Validate that all scene connections reference valid scenes.

        Args:
            scenes: Dictionary of scenes

        Returns:
            True if all connections are valid, False otherwise
        """
        scene_ids = set(scenes.keys())

        for _scene_id, scene_data in scenes.items():
            if not scene_data:
                continue

            connections = scene_data.get("connections", [])
            if not connections:
                continue

            for connection in connections:
                if isinstance(connection, dict):
                    target = connection.get("target")
                    if target and target not in scene_ids:
                        return False
                elif isinstance(connection, str):
                    if connection not in scene_ids:
                        return False

        return True

    @staticmethod
    def _find_orphaned_scenes(scenes: dict[str, Any], start_scene: str | None) -> list[str]:
        """
        Find scenes that are not reachable from the start scene.

        Args:
            scenes: Dictionary of scenes
            start_scene: ID of the starting scene

        Returns:
            List of orphaned scene IDs
        """
        if not start_scene or start_scene not in scenes:
            # If no valid start scene, all scenes are potentially orphaned
            return list(scenes.keys())

        # Perform graph traversal to find reachable scenes (BFS)
        reachable = set()
        to_visit = deque([start_scene])

        while to_visit:
            current = to_visit.popleft()
            if current in reachable:
                continue

            reachable.add(current)

            # Get connections from current scene
            scene_data = scenes.get(current)
            if not scene_data:
                continue

            connections = scene_data.get("connections", [])
            for connection in connections:
                if isinstance(connection, dict):
                    target = connection.get("target")
                    if target and target not in reachable:
                        to_visit.append(target)
                elif isinstance(connection, str):
                    if connection not in reachable:
                        to_visit.append(connection)

        # Find orphaned scenes (all scenes minus reachable)
        all_scenes = set(scenes.keys())
        orphaned = all_scenes - reachable

        return sorted(orphaned)

    def passes_threshold(self) -> bool:
        """
        Check if the narrative metrics pass all quality thresholds.

        Returns:
            True if all thresholds are met, False otherwise
        """
        return (
            self.has_start_scene
            and self.total_scenes >= self.min_scenes
            and self.completeness_percentage >= self.min_completeness
            and self.all_connections_valid
            and not self.has_orphaned_scenes
        )

    def get_failures(self) -> list[str]:
        """
        Get list of failed quality checks.

        Returns:
            List of failure messages for metrics that don't meet thresholds
        """
        failures = []

        if not self.has_start_scene:
            failures.append("No start scene defined")

        if self.total_scenes < self.min_scenes:
            failures.append(
                f"Insufficient scenes: {self.total_scenes} (minimum: {self.min_scenes})"
            )

        if self.completeness_percentage < self.min_completeness:
            failures.append(
                f"Scene descriptions incomplete: {self.completeness_percentage:.1f}% "
                f"(minimum: {self.min_completeness}%)"
            )

        if not self.all_connections_valid:
            failures.append("Some scene connections reference invalid scenes")

        if self.has_orphaned_scenes:
            failures.append(f"Orphaned scenes found: {', '.join(self.orphaned_scenes)}")

        return failures

    def get_score(self) -> float:
        """
        Calculate overall quality score (0.0 to 10.0).

        Returns:
            Quality score based on met criteria
        """
        score = 0.0

        # Start scene (2 points)
        if self.has_start_scene:
            score += 2.0

        # Minimum scenes (2 points)
        if self.total_scenes >= self.min_scenes:
            score += 2.0
        elif self.total_scenes > 0:
            # Partial credit
            score += 2.0 * (self.total_scenes / self.min_scenes)

        # Completeness (3 points)
        score += 3.0 * (self.completeness_percentage / 100.0)

        # Valid connections (2 points)
        if self.all_connections_valid:
            score += 2.0

        # No orphaned scenes (1 point)
        if not self.has_orphaned_scenes:
            score += 1.0

        return min(score, 10.0)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert metrics to dictionary for serialization.

        Returns:
            Dictionary representation of metrics
        """
        return {
            "total_scenes": self.total_scenes,
            "scenes_with_descriptions": self.scenes_with_descriptions,
            "completeness_percentage": round(self.completeness_percentage, 1),
            "all_connections_valid": self.all_connections_valid,
            "has_orphaned_scenes": self.has_orphaned_scenes,
            "orphaned_scenes": self.orphaned_scenes,
            "has_start_scene": self.has_start_scene,
            "passes_threshold": self.passes_threshold(),
            "score": self.get_score(),
            "failures": self.get_failures(),
        }
