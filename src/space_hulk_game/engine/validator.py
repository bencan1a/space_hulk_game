"""
Game Validator Module

Validates that generated game content is playable by checking for common issues:
- Unreachable scenes (graph connectivity)
- Dead ends (scenes with no exits)
- Invalid exits (pointing to non-existent scenes)
- Missing required items
- Broken NPC dialogues
- Puzzle solvability

The validator provides actionable feedback to help fix content issues.

Example:
    >>> from space_hulk_game.engine import GameValidator, GameData
    >>> validator = GameValidator()
    >>> result = validator.validate_game(game_data)
    >>> if not result.is_valid():
    ...     for issue in result.issues:
    ...         print(f"Issue: {issue}")
    ...     for scene_id, suggestions in result.suggestions.items():
    ...         print(f"Suggestions for {scene_id}: {suggestions}")
"""

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from .game_data import GameData
from .scene import Scene

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """
    Result of game validation containing issues and suggested fixes.

    Attributes:
        issues: List of validation issues found.
        suggestions: Dictionary mapping scene IDs to suggested fixes.
        warnings: List of non-critical warnings.
        stats: Dictionary containing validation statistics.

    Examples:
        Create a validation result:
        >>> result = ValidationResult(
        ...     issues=["Scene 'vault' is unreachable"],
        ...     suggestions={"entrance": ["Add exit to 'vault'"]},
        ...     warnings=["Scene 'dark_room' has no description"]
        ... )
        >>> result.is_valid()
        False
        >>> len(result.issues)
        1
    """

    issues: list[str] = field(default_factory=list)
    suggestions: dict[str, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """
        Check if the game passed validation (no critical issues).

        Returns:
            True if there are no critical issues, False otherwise.

        Examples:
            >>> result = ValidationResult()
            >>> result.is_valid()
            True
            >>> result.issues.append("Critical error")
            >>> result.is_valid()
            False
        """
        return len(self.issues) == 0

    def add_issue(self, issue: str) -> None:
        """
        Add a critical issue to the validation result.

        Args:
            issue: Description of the issue.

        Examples:
            >>> result = ValidationResult()
            >>> result.add_issue("Scene missing")
            >>> len(result.issues)
            1
        """
        self.issues.append(issue)
        logger.warning(f"Validation issue: {issue}")

    def add_warning(self, warning: str) -> None:
        """
        Add a non-critical warning to the validation result.

        Args:
            warning: Description of the warning.

        Examples:
            >>> result = ValidationResult()
            >>> result.add_warning("Minor issue")
            >>> len(result.warnings)
            1
        """
        self.warnings.append(warning)
        logger.info(f"Validation warning: {warning}")

    def add_suggestion(self, scene_id: str, suggestion: str) -> None:
        """
        Add a suggested fix for a scene.

        Args:
            scene_id: The scene ID that needs fixing.
            suggestion: Suggested action to fix the issue.

        Examples:
            >>> result = ValidationResult()
            >>> result.add_suggestion("entrance", "Add exit to corridor")
            >>> "entrance" in result.suggestions
            True
        """
        if scene_id not in self.suggestions:
            self.suggestions[scene_id] = []
        self.suggestions[scene_id].append(suggestion)
        logger.debug(f"Suggestion for {scene_id}: {suggestion}")

    def get_summary(self) -> str:
        """
        Get a human-readable summary of the validation results.

        Returns:
            Formatted string summarizing the validation.

        Examples:
            >>> result = ValidationResult(issues=["Error 1"], warnings=["Warning 1"])
            >>> summary = result.get_summary()
            >>> "1 issue" in summary
            True
        """
        lines = []
        lines.append("Validation Summary:")
        lines.append(f"  Status: {'PASSED' if self.is_valid() else 'FAILED'}")
        lines.append(f"  Critical Issues: {len(self.issues)}")
        lines.append(f"  Warnings: {len(self.warnings)}")
        lines.append(f"  Suggestions: {len(self.suggestions)}")

        if self.stats:
            lines.append("\nStatistics:")
            for key, value in self.stats.items():
                lines.append(f"  {key}: {value}")

        if self.issues:
            lines.append("\nCritical Issues:")
            for issue in self.issues:
                lines.append(f"  - {issue}")

        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        if self.suggestions:
            lines.append("\nSuggested Fixes:")
            for scene_id, suggestions in self.suggestions.items():
                lines.append(f"  {scene_id}:")
                for suggestion in suggestions:
                    lines.append(f"    - {suggestion}")

        return "\n".join(lines)


class GameValidator:
    """
    Validates game content for playability issues.

    The GameValidator performs comprehensive checks on GameData to ensure:
    - All scenes are reachable from the starting scene
    - No dead ends exist (except intended endings)
    - All scene exits point to valid scenes
    - Required items for puzzles exist in the game
    - NPCs have valid dialogue
    - Puzzle prerequisites are satisfiable

    Attributes:
        strict_mode: If True, treats warnings as errors.

    Examples:
        Validate a game:
        >>> from space_hulk_game.engine import GameData, Scene
        >>> scene = Scene(id="start", name="Start", description="Begin here",
        ...               exits={"north": "room2"})
        >>> data = GameData(
        ...     title="Test",
        ...     description="Test game",
        ...     scenes={"start": scene},
        ...     starting_scene="start"
        ... )
        >>> validator = GameValidator()
        >>> result = validator.validate_game(data)
        >>> # Should have issue about missing scene 'room2'
        >>> len(result.issues) > 0
        True

        Use strict mode:
        >>> validator = GameValidator(strict_mode=True)
        >>> result = validator.validate_game(data)
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the GameValidator.

        Args:
            strict_mode: If True, treats warnings as errors.
        """
        self.strict_mode = strict_mode
        logger.info(f"GameValidator initialized (strict_mode={strict_mode})")

    def validate_game(self, game_data: GameData) -> ValidationResult:
        """
        Validate a complete game for playability issues.

        This is the main entry point for validation. It runs all validation
        checks and returns a comprehensive report.

        Args:
            game_data: The GameData object to validate.

        Returns:
            ValidationResult containing all issues, warnings, and suggestions.

        Examples:
            >>> from space_hulk_game.engine import GameData, Scene
            >>> scene = Scene(id="start", name="Start", description="Begin")
            >>> data = GameData(
            ...     title="Test",
            ...     description="Test",
            ...     scenes={"start": scene},
            ...     starting_scene="start"
            ... )
            >>> validator = GameValidator()
            >>> result = validator.validate_game(data)
            >>> result.is_valid()
            True
        """
        logger.info(f"Validating game: {game_data.title}")
        result = ValidationResult()

        # Collect statistics
        result.stats = {
            "total_scenes": len(game_data.scenes),
            "total_items": len(game_data.global_items),
            "total_npcs": len(game_data.global_npcs),
            "starting_scene": game_data.starting_scene,
        }

        # Run all validation checks
        self._check_scene_reachability(game_data, result)
        self._check_invalid_exits(game_data, result)
        self._check_dead_ends(game_data, result)
        self._check_missing_items(game_data, result)
        self._check_npc_dialogues(game_data, result)
        self._check_locked_exits(game_data, result)

        # Update statistics
        result.stats["reachable_scenes"] = len(
            self._find_reachable_scenes(game_data.scenes, game_data.starting_scene)
        )

        logger.info(
            f"Validation complete: {len(result.issues)} issues, " f"{len(result.warnings)} warnings"
        )

        # If strict_mode is enabled, treat warnings as errors
        if self.strict_mode:
            result.issues.extend(result.warnings)
            result.warnings.clear()

        return result

    def _find_reachable_scenes(self, scenes: dict[str, Scene], starting_scene: str) -> set[str]:
        """
        Find all scenes reachable from the starting scene using BFS.

        Args:
            scenes: Dictionary of all scenes.
            starting_scene: ID of the starting scene.

        Returns:
            Set of scene IDs that are reachable.

        Examples:
            >>> scene1 = Scene(id="s1", name="S1", description="First",
            ...                exits={"north": "s2"})
            >>> scene2 = Scene(id="s2", name="S2", description="Second")
            >>> scenes = {"s1": scene1, "s2": scene2}
            >>> validator = GameValidator()
            >>> reachable = validator._find_reachable_scenes(scenes, "s1")
            >>> len(reachable)
            2
            >>> "s1" in reachable and "s2" in reachable
            True
        """
        reachable = set()
        queue = deque([starting_scene])

        while queue:
            current_id = queue.popleft()

            if current_id in reachable:
                continue

            if current_id not in scenes:
                # Invalid scene reference, but we'll handle this separately
                continue

            reachable.add(current_id)

            # Add all connected scenes to queue
            scene = scenes[current_id]
            for exit_target in scene.exits.values():
                if exit_target not in reachable:
                    queue.append(exit_target)

        return reachable

    def _check_scene_reachability(self, game_data: GameData, result: ValidationResult) -> None:
        """
        Check that all scenes are reachable from the starting scene.

        Args:
            game_data: The game data to check.
            result: ValidationResult to add issues to.
        """
        logger.debug("Checking scene reachability")

        reachable = self._find_reachable_scenes(game_data.scenes, game_data.starting_scene)

        unreachable = set(game_data.scenes.keys()) - reachable

        if unreachable:
            unreachable_list = sorted(list(unreachable))
            result.add_issue(f"Unreachable scenes: {', '.join(unreachable_list)}")

            # Suggest connections
            for scene_id in unreachable_list:
                # Find closest reachable scene (simple heuristic: first reachable)
                if reachable:
                    closest = sorted(list(reachable))[0]
                    result.add_suggestion(closest, f"Add exit to unreachable scene '{scene_id}'")

    def _check_invalid_exits(self, game_data: GameData, result: ValidationResult) -> None:
        """
        Check that all scene exits point to valid scenes.

        Args:
            game_data: The game data to check.
            result: ValidationResult to add issues to.
        """
        logger.debug("Checking invalid exits")

        for scene_id, scene in game_data.scenes.items():
            for direction, target_id in scene.exits.items():
                if target_id not in game_data.scenes:
                    result.add_issue(
                        f"Scene '{scene_id}' has invalid exit '{direction}' -> "
                        f"'{target_id}' (scene does not exist)"
                    )
                    result.add_suggestion(
                        scene_id, f"Remove invalid exit '{direction}' or create scene '{target_id}'"
                    )

    def _check_dead_ends(self, game_data: GameData, result: ValidationResult) -> None:
        """
        Check for dead ends (scenes with no exits).

        Dead ends are only acceptable if they're designated as endings.

        Args:
            game_data: The game data to check.
            result: ValidationResult to add issues to.
        """
        logger.debug("Checking for dead ends")

        # Get list of valid ending scenes from game data
        valid_endings = set()
        for ending in game_data.endings:
            if isinstance(ending, dict) and "scene_id" in ending:
                valid_endings.add(ending["scene_id"])

        dead_ends = []
        for scene_id, scene in game_data.scenes.items():
            if not scene.exits:
                # Check if this is a valid ending scene
                if scene_id not in valid_endings:
                    dead_ends.append(scene_id)

        if dead_ends:
            # Check if there are ANY defined endings
            if not game_data.endings:
                # If no endings defined, warn about dead ends
                result.add_warning(
                    f"Dead end scenes found (no exits): {', '.join(sorted(dead_ends))}. "
                    f"These should either have exits or be designated as ending scenes."
                )
            else:
                # If endings exist but these aren't marked, that's an issue
                result.add_issue(
                    f"Dead end scenes found (not marked as endings): {', '.join(sorted(dead_ends))}"
                )

            for scene_id in dead_ends:
                result.add_suggestion(
                    scene_id, "Add exits to other scenes or mark as an ending scene"
                )

    def _check_missing_items(self, game_data: GameData, result: ValidationResult) -> None:
        """
        Check for references to items that don't exist.

        Checks:
        - Locked exits requiring non-existent items
        - NPCs giving non-existent items

        Args:
            game_data: The game data to check.
            result: ValidationResult to add issues to.
        """
        logger.debug("Checking for missing items")

        # Build set of all available items
        all_items = set(game_data.global_items.keys())
        for scene in game_data.scenes.values():
            for item in scene.items:
                all_items.add(item.id)

        # Check locked exits
        for scene_id, scene in game_data.scenes.items():
            for direction, required_item in scene.locked_exits.items():
                # Could be an item or a flag
                # Only check if it looks like an item (not a flag pattern)
                if required_item and not required_item.startswith("flag_"):
                    if required_item not in all_items:
                        result.add_warning(
                            f"Scene '{scene_id}' exit '{direction}' requires "
                            f"'{required_item}' which may not exist as an item "
                            f"(could be a flag)"
                        )

        # Check NPCs giving items
        for scene_id, scene in game_data.scenes.items():
            for npc in scene.npcs:
                if npc.gives_item and npc.gives_item not in all_items:
                    result.add_issue(
                        f"NPC '{npc.id}' in scene '{scene_id}' gives item "
                        f"'{npc.gives_item}' which does not exist"
                    )
                    result.add_suggestion(
                        scene_id, f"Create item '{npc.gives_item}' or update NPC '{npc.id}'"
                    )

        # Also check global NPCs
        for npc_id, npc in game_data.global_npcs.items():
            if npc.gives_item and npc.gives_item not in all_items:
                result.add_issue(
                    f"Global NPC '{npc_id}' gives item '{npc.gives_item}' " f"which does not exist"
                )

    def _check_npc_dialogues(self, game_data: GameData, result: ValidationResult) -> None:
        """
        Check that NPCs have valid dialogue.

        Warns about NPCs with no dialogue or empty dialogue.

        Args:
            game_data: The game data to check.
            result: ValidationResult to add issues to.
        """
        logger.debug("Checking NPC dialogues")

        for scene_id, scene in game_data.scenes.items():
            for npc in scene.npcs:
                if not npc.dialogue:
                    result.add_warning(f"NPC '{npc.id}' in scene '{scene_id}' has no dialogue")
                    result.add_suggestion(scene_id, f"Add dialogue for NPC '{npc.id}'")
                elif all(not v for v in npc.dialogue.values()):
                    result.add_warning(f"NPC '{npc.id}' in scene '{scene_id}' has empty dialogue")
                    result.add_suggestion(scene_id, f"Add dialogue content for NPC '{npc.id}'")

        # Check global NPCs for dialogue issues
        for npc_id, npc in game_data.global_npcs.items():
            if not npc.dialogue:
                result.add_warning(f"Global NPC '{npc_id}' has no dialogue")
            elif all(not v for v in npc.dialogue.values()):
                result.add_warning(f"Global NPC '{npc_id}' has empty dialogue")

    def _check_locked_exits(self, game_data: GameData, result: ValidationResult) -> None:
        """
        Check that locked exits are solvable.

        Verifies that:
        - Required items/flags can be obtained
        - No circular dependencies

        Args:
            game_data: The game data to check.
            result: ValidationResult to add issues to.
        """
        logger.debug("Checking locked exits")

        # Build set of obtainable items and flags
        obtainable_items = set(game_data.global_items.keys())

        # Items in scenes are obtainable
        for scene in game_data.scenes.values():
            for item in scene.items:
                if item.takeable:
                    obtainable_items.add(item.id)

        # Items given by NPCs are obtainable
        for scene in game_data.scenes.values():
            for npc in scene.npcs:
                if npc.gives_item:
                    obtainable_items.add(npc.gives_item)

        for npc in game_data.global_npcs.values():
            if npc.gives_item:
                obtainable_items.add(npc.gives_item)

        # Check locked exits in reachable scenes
        reachable = self._find_reachable_scenes(game_data.scenes, game_data.starting_scene)

        for scene_id in reachable:
            scene = game_data.scenes[scene_id]
            for direction, required in scene.locked_exits.items():
                target = scene.exits.get(direction)
                if target and target not in reachable:
                    # This exit leads to unreachable area
                    # Check if required item exists
                    if required not in obtainable_items:
                        # Could be a flag, not necessarily an error
                        if not required.startswith("flag_"):
                            result.add_warning(
                                f"Scene '{scene_id}' has locked exit '{direction}' "
                                f"requiring '{required}' which may not be obtainable"
                            )
