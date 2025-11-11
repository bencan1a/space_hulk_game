"""Auto-correction for YAML validation outputs.

This module provides automatic correction functionality for common YAML validation
errors in AI agent outputs. It attempts to fix missing fields, syntax errors,
and format violations while preserving the intent of the original content.
"""

import logging
import re
from dataclasses import dataclass

import yaml

from space_hulk_game.utils.yaml_processor import strip_markdown_yaml_blocks
from space_hulk_game.validation.validator import OutputValidator, ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class CorrectionResult:
    """Result of attempting to auto-correct YAML output.

    Attributes:
        corrected_yaml: The corrected YAML string.
        corrections: List of corrections applied.
        validation_result: Result from validating the corrected output.
        success: Whether correction succeeded and output is now valid.

    Example:
        >>> result = CorrectionResult(
        ...     corrected_yaml="title: Fixed\\n...",
        ...     corrections=["Added missing 'plot_points' field"],
        ...     validation_result=ValidationResult(...),
        ...     success=True
        ... )
    """

    corrected_yaml: str
    corrections: list[str]
    validation_result: ValidationResult
    success: bool


class OutputCorrector:
    """Auto-corrector for YAML validation outputs.

    This class provides methods to automatically fix common validation errors
    in YAML outputs from AI agents. It attempts to add missing required fields,
    fix syntax errors, normalize field names, and correct ID format violations.

    Features:
        - Fixes missing required fields with sensible defaults
        - Repairs common YAML syntax errors
        - Normalizes field names (e.g., camelCase to snake_case)
        - Corrects ID format violations (lowercase, underscores, alphanumeric)
        - Logs all corrections transparently
        - Validates corrected output

    Example:
        >>> corrector = OutputCorrector()
        >>> result = corrector.correct_plot(invalid_yaml_string)
        >>> if result.success:
        ...     print(f"Corrections applied: {result.corrections}")
        ...     with open('output.yaml', 'w') as f:
        ...         f.write(result.corrected_yaml)
        ... else:
        ...     print(f"Correction failed: {result.validation_result.errors}")
    """

    def __init__(self):
        """Initialize the output corrector with a validator instance."""
        self.validator = OutputValidator()
        logger.info("OutputCorrector initialized")


    def _fix_id_format(self, id_value: str) -> str:
        """Fix ID format to match schema requirements.

        Ensures IDs are lowercase, use underscores, and contain only
        alphanumeric characters, underscores, and hyphens.

        Args:
            id_value: Original ID value.

        Returns:
            Corrected ID value.

        Example:
            >>> corrector = OutputCorrector()
            >>> corrector._fix_id_format("My-Scene ID!")
            'my_scene_id'
        """
        # Convert to lowercase
        fixed = id_value.lower()
        # Replace spaces with underscores
        fixed = fixed.replace(" ", "_")
        # Remove invalid characters (keep only alphanumeric, underscores, hyphens)
        fixed = re.sub(r"[^a-z0-9_-]", "", fixed)
        # Replace multiple underscores/hyphens with single underscore
        fixed = re.sub(r"[_-]+", "_", fixed)
        # Remove leading/trailing underscores/hyphens
        fixed = fixed.strip("_-")
        return fixed

    def _extend_short_description(self, description: str, min_length: int) -> str:
        """Extend a description that is too short to meet minimum length.

        Args:
            description: Original description.
            min_length: Minimum required length.

        Returns:
            Extended description if needed, otherwise original.
        """
        if len(description) >= min_length:
            return description

        # Add generic filler text to meet minimum length
        filler = (
            " Additional details and context will be developed further "
            "during the narrative design process."
        )
        extended = description + filler

        # If still not long enough, add more filler
        while len(extended) < min_length:
            extended += " Further elaboration and refinement will enhance this element."

        return extended

    def _fix_mixed_quotes(self, content: str) -> str:
        """Fix strings with mismatched quote delimiters.

        Handles strings like "entrance' or 'corridor_1" where the opening
        and closing quotes don't match. Normalizes to the opening quote type.

        Args:
            content: Raw YAML string with potential mixed quotes.

        Returns:
            Fixed YAML string with consistent quote usage.

        Example:
            >>> corrector = OutputCorrector()
            >>> corrector._fix_mixed_quotes('starting_scene: "entrance\\'')
            'starting_scene: "entrance"'
            >>> corrector._fix_mixed_quotes("south: 'corridor_1\\"")
            "south: 'corridor_1'"
        """
        # Strategy: Look for strings that start with one quote type and end with another
        # We need to be careful about apostrophes inside strings
        # Pattern 1: " ... ' at end of line (double quote start, single quote end)
        # Pattern 2: ' ... " at end of line (single quote start, double quote end)

        # Use line-by-line processing to avoid matching across multiple values
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Check for mismatched quotes on this line
            # Pattern: starts with " and ends with ' (at end of line)
            if re.search(r':\s*"[^"]*\'$', line):
                # Replace the final ' with "
                line = re.sub(r"\'$", '"', line)  # noqa: PLW2901
            # Pattern: starts with ' and ends with " (at end of line)
            elif re.search(r":\s*'[^']*\"$", line):
                # Replace the final " with '
                line = re.sub(r'"$', "'", line)  # noqa: PLW2901

            fixed_lines.append(line)

        content = "\n".join(fixed_lines)
        logger.debug("Fixed mixed quote delimiters")
        return content

    def _fix_invalid_list_markers(self, content: str) -> str:
        """Fix invalid YAML list markers with multiple dashes.

        Handles list items marked with multiple dashes (e.g., '---------------- item')
        and converts them to proper YAML list syntax ('- item').

        Args:
            content: Raw YAML string with potential invalid list markers.

        Returns:
            Fixed YAML string with proper list markers.

        Example:
            >>> corrector = OutputCorrector()
            >>> corrector._fix_invalid_list_markers('items:\\n  ---------------- flashlight')
            'items:\\n  - flashlight'
        """
        # Pattern: line starting with indentation, followed by 4+ dashes, then content
        # Captures: (indentation) (4+ dashes) (optional spaces) (rest of line)
        # Replace with: (indentation) - (rest of line)
        content = re.sub(
            r"^(\s*)-{4,}\s*(.+)$",
            r"\1- \2",
            content,
            flags=re.MULTILINE,
        )

        logger.debug("Fixed invalid list markers")
        return content

    def _fix_unescaped_apostrophes(self, content: str) -> str:
        """Fix unescaped apostrophes in single-quoted strings.

        Handles apostrophes inside single-quoted strings (e.g., 'Ship's Bridge')
        by converting them to double-quoted strings to avoid escaping.

        Args:
            content: Raw YAML string with potential unescaped apostrophes.

        Returns:
            Fixed YAML string with apostrophes properly handled.

        Example:
            >>> corrector = OutputCorrector()
            >>> corrector._fix_unescaped_apostrophes("name: 'Ship's Bridge'")
            'name: "Ship\\'s Bridge"'
            >>> corrector._fix_unescaped_apostrophes("description: 'The captain's quarters'")
            'description: "The captain\\'s quarters"'
        """
        # Pattern: find single-quoted strings that contain apostrophes
        # We need to match the entire string including any apostrophes inside
        # Strategy: Look for : 'some text with potential apostrophe' pattern
        # Use a greedy match to get everything between the outer quotes

        def replace_single_quoted_with_apostrophe(match):
            """Replace single-quoted string containing apostrophe with double-quoted version."""
            prefix = match.group(1)  # Everything before the opening quote (: and spaces)
            inner_content = match.group(2)  # Content inside the outer quotes

            # Check if content contains an apostrophe (but not just the closing quote)
            # We need to look for apostrophes that are NOT the final closing quote
            if "'" in inner_content:
                # Convert to double-quoted string
                # The content already has the apostrophes, just change the delimiters
                return f'{prefix}"{inner_content}"'
            else:
                # Keep as-is
                return match.group(0)

        # Pattern: (: + optional spaces) ' (everything until last ') '
        # This uses a possessive quantifier to match everything between outer quotes
        # The pattern matches: colon, spaces, opening single quote, content (greedy), closing single quote
        # We need to match the full quoted string, even if it contains apostrophes
        # The key insight: match from ' to the LAST ' on the line
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Look for pattern: key: 'value with potential apostrophes'
            # Use a more sophisticated approach: find : ' pairs and match to closing '
            if ": '" in line or ":\t'" in line:
                # Find the position of ": '"
                match = re.search(r"(\s*:\s*)'(.+)'$", line)
                if match:
                    prefix = match.group(1)
                    inner = match.group(2)
                    # Check if inner content has apostrophes
                    if "'" in inner:
                        # Replace the line with double-quoted version
                        fixed_line = line[: match.start()] + f'{prefix}"{inner}"'
                        fixed_lines.append(fixed_line)
                        continue
            # No match or no apostrophes, keep original
            fixed_lines.append(line)

        result = "\n".join(fixed_lines)
        logger.debug("Fixed unescaped apostrophes in single-quoted strings")
        return result

    def _parse_yaml_safe(self, raw_output: str) -> tuple[dict | None, list[str]]:
        """Safely parse YAML with error recovery.

        Attempts to parse YAML and apply basic syntax fixes if parsing fails.

        Args:
            raw_output: Raw YAML string.

        Returns:
            Tuple of (parsed_data, errors). If parsing succeeds, parsed_data
            is a dict and errors is empty. If parsing fails, parsed_data is None
            and errors contains the error messages.
        """
        try:
            # Strip markdown fences first
            clean_yaml = strip_markdown_yaml_blocks(raw_output)

            # Apply syntax fixes BEFORE parsing
            clean_yaml = self._fix_mixed_quotes(clean_yaml)
            clean_yaml = self._fix_invalid_list_markers(clean_yaml)
            clean_yaml = self._fix_unescaped_apostrophes(clean_yaml)

            # Try to parse
            data = yaml.safe_load(clean_yaml)

            if data is None:
                return None, ["YAML is empty or contains only whitespace"]

            if not isinstance(data, dict):
                return None, [f"YAML must be a dictionary, got {type(data).__name__}"]

            return data, []

        except yaml.YAMLError as e:
            # Attempt basic syntax fixes
            logger.warning(f"YAML parsing error, attempting fixes: {e}")

            try:
                # Common fix: remove duplicate colons, fix indentation issues
                clean_yaml = strip_markdown_yaml_blocks(raw_output)

                # NOTE: This is the ONLY implementation of colon-in-values fixing.
                # Other modules (evaluator, crew) have been refactored to rely on this.
                # Do not duplicate this logic elsewhere.
                #
                # Try to fix "mapping values are not allowed here" by escaping colons in values
                # This is a simple heuristic and may not catch all cases
                lines = clean_yaml.split("\n")
                fixed_lines = []
                for line in lines:
                    if ":" in line and not line.strip().startswith("#"):
                        # Check if there are multiple colons (potential issue)
                        parts = line.split(":", 1)
                        if len(parts) == 2 and ":" in parts[1]:
                            # Quote the value if it contains colons
                            indent = len(line) - len(line.lstrip())
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if not (value.startswith('"') or value.startswith("'")):
                                fixed_lines.append(f"{' ' * indent}{key}: '{value}'")
                            else:
                                fixed_lines.append(line)
                        else:
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)

                fixed_yaml = "\n".join(fixed_lines)
                data = yaml.safe_load(fixed_yaml)

                if data is None:
                    return None, ["YAML is empty after attempted fix"]

                if not isinstance(data, dict):
                    return None, [f"YAML must be a dictionary, got {type(data).__name__}"]

                logger.info("Successfully fixed YAML syntax error")
                return data, []

            except yaml.YAMLError as e2:
                error_msg = f"YAML parsing error (even after attempted fix): {e2!s}"
                logger.error(error_msg)
                return None, [error_msg]

        except Exception as e:
            error_msg = f"Unexpected error during YAML parsing: {e!s}"
            logger.error(error_msg)
            return None, [error_msg]

    def correct_plot(self, raw_output: str) -> CorrectionResult:
        """Attempt to correct common errors in plot outline YAML.

        Fixes:
            - Missing required fields (plot_points, characters, conflicts)
            - Invalid ID formats
            - Descriptions too short
            - YAML syntax errors

        Args:
            raw_output: Raw YAML string containing plot outline data.

        Returns:
            CorrectionResult with corrected YAML, list of corrections,
            validation result, and success status.

        Example:
            >>> corrector = OutputCorrector()
            >>> result = corrector.correct_plot(invalid_plot_yaml)
            >>> if result.success:
            ...     print(f"Plot corrected with {len(result.corrections)} changes")
        """
        logger.info("Attempting to correct plot outline YAML")
        corrections: list[str] = []

        # Parse YAML
        data, parse_errors = self._parse_yaml_safe(raw_output)
        if parse_errors:
            # Can't fix unparseable YAML beyond basic syntax fixes already attempted
            validation_result = ValidationResult(valid=False, data=None, errors=parse_errors)
            return CorrectionResult(
                corrected_yaml=raw_output,
                corrections=corrections,
                validation_result=validation_result,
                success=False,
            )

        # Type guard: data is guaranteed to be dict here
        assert data is not None, "data should not be None when parse_errors is empty"

        # Add missing required fields
        if "title" not in data:
            data["title"] = "Untitled Plot"
            corrections.append("Added missing 'title' field with default value")
            logger.info("Added missing 'title' field")

        if "setting" not in data:
            data["setting"] = self._extend_short_description(
                "A dark and atmospheric setting for the narrative.", 50
            )
            corrections.append("Added missing 'setting' field with default value")
            logger.info("Added missing 'setting' field")
        elif len(data["setting"]) < 50:
            original_setting = data["setting"]
            data["setting"] = self._extend_short_description(data["setting"], 50)
            corrections.append(
                f"Extended short 'setting' field (was {len(original_setting)} chars)"
            )
            logger.info("Extended 'setting' field")

        if "themes" not in data or not data["themes"]:
            data["themes"] = ["survival", "conflict"]
            corrections.append("Added missing 'themes' field with default values")
            logger.info("Added missing 'themes' field")

        if "tone" not in data:
            data["tone"] = "Dark and atmospheric"
            corrections.append("Added missing 'tone' field with default value")
            logger.info("Added missing 'tone' field")
        elif len(data["tone"]) < 10:
            original_tone = data["tone"]
            data["tone"] = self._extend_short_description(data["tone"], 10)
            corrections.append(f"Extended short 'tone' field (was {len(original_tone)} chars)")
            logger.info("Extended 'tone' field")

        if "plot_points" not in data or not data["plot_points"]:
            data["plot_points"] = [
                {
                    "id": "pp_01_opening",
                    "name": "Opening",
                    "description": self._extend_short_description(
                        "The story begins with the initial situation.", 50
                    ),
                },
                {
                    "id": "pp_02_development",
                    "name": "Development",
                    "description": self._extend_short_description(
                        "The plot develops as events unfold.", 50
                    ),
                },
                {
                    "id": "pp_03_conclusion",
                    "name": "Conclusion",
                    "description": self._extend_short_description(
                        "The story reaches its conclusion and resolution.", 50
                    ),
                },
            ]
            corrections.append("Added missing 'plot_points' field with minimal defaults")
            logger.info("Added missing 'plot_points' field")

        if "characters" not in data or not data["characters"]:
            data["characters"] = [
                {
                    "name": "Protagonist",
                    "role": "Main character",
                    "backstory": self._extend_short_description(
                        "The protagonist's background and history.", 50
                    ),
                }
            ]
            corrections.append("Added missing 'characters' field with minimal default")
            logger.info("Added missing 'characters' field")

        if "conflicts" not in data or not data["conflicts"]:
            data["conflicts"] = [
                {
                    "type": "Main Conflict",
                    "description": self._extend_short_description(
                        "The primary conflict driving the narrative.", 50
                    ),
                }
            ]
            corrections.append("Added missing 'conflicts' field with minimal default")
            logger.info("Added missing 'conflicts' field")

        # Fix plot point IDs and descriptions
        if "plot_points" in data and isinstance(data["plot_points"], list):
            for _i, pp in enumerate(data["plot_points"]):
                if isinstance(pp, dict):
                    # Fix ID format
                    if "id" in pp:
                        original_id = pp["id"]
                        fixed_id = self._fix_id_format(original_id)
                        if original_id != fixed_id:
                            pp["id"] = fixed_id
                            corrections.append(
                                f"Fixed plot point ID format: '{original_id}' -> '{fixed_id}'"
                            )
                            logger.info(f"Fixed plot point ID: {original_id} -> {fixed_id}")

                    # Extend short descriptions
                    if "description" in pp and len(pp["description"]) < 50:
                        original_desc = pp["description"]
                        pp["description"] = self._extend_short_description(pp["description"], 50)
                        corrections.append(
                            f"Extended short plot point description "
                            f"(was {len(original_desc)} chars)"
                        )
                        logger.info(
                            f"Extended plot point description from {len(original_desc)} "
                            f"to {len(pp['description'])} chars"
                        )

        # Fix character backstories
        if "characters" in data and isinstance(data["characters"], list):
            for char in data["characters"]:
                if isinstance(char, dict) and "backstory" in char and len(char["backstory"]) < 50:
                    original_backstory = char["backstory"]
                    char["backstory"] = self._extend_short_description(char["backstory"], 50)
                    corrections.append(
                        f"Extended short character backstory (was {len(original_backstory)} chars)"
                    )
                    logger.info(
                        f"Extended character backstory from {len(original_backstory)} "
                        f"to {len(char['backstory'])} chars"
                    )

        # Fix conflict descriptions
        if "conflicts" in data and isinstance(data["conflicts"], list):
            for conflict in data["conflicts"]:
                if (
                    isinstance(conflict, dict)
                    and "description" in conflict
                    and len(conflict["description"]) < 50
                ):
                    original_desc = conflict["description"]
                    conflict["description"] = self._extend_short_description(
                        conflict["description"], 50
                    )
                    corrections.append(
                        f"Extended short conflict description (was {len(original_desc)} chars)"
                    )
                    logger.info(
                        f"Extended conflict description from {len(original_desc)} "
                        f"to {len(conflict['description'])} chars"
                    )

        # Convert back to YAML
        try:
            corrected_yaml = yaml.dump(
                data, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
        except Exception as e:
            logger.error(f"Error converting corrected data to YAML: {e}")
            validation_result = ValidationResult(
                valid=False, data=None, errors=[f"Error converting to YAML: {e!s}"]
            )
            return CorrectionResult(
                corrected_yaml=raw_output,
                corrections=corrections,
                validation_result=validation_result,
                success=False,
            )

        # Validate corrected output
        validation_result = self.validator.validate_plot(corrected_yaml)

        logger.info(
            f"Plot correction complete: {len(corrections)} corrections, "
            f"valid={validation_result.valid}"
        )

        return CorrectionResult(
            corrected_yaml=corrected_yaml,
            corrections=corrections,
            validation_result=validation_result,
            success=validation_result.valid,
        )

    def correct_narrative_map(self, raw_output: str) -> CorrectionResult:
        """Attempt to correct common errors in narrative map YAML.

        Fixes:
            - Missing required fields (start_scene, scenes)
            - Invalid ID formats
            - Descriptions too short
            - YAML syntax errors

        Args:
            raw_output: Raw YAML string containing narrative map data.

        Returns:
            CorrectionResult with corrected YAML, list of corrections,
            validation result, and success status.

        Example:
            >>> corrector = OutputCorrector()
            >>> result = corrector.correct_narrative_map(invalid_map_yaml)
            >>> if result.success:
            ...     print(f"Map corrected with {len(result.corrections)} changes")
        """
        logger.info("Attempting to correct narrative map YAML")
        corrections: list[str] = []

        # Parse YAML
        data, parse_errors = self._parse_yaml_safe(raw_output)
        if parse_errors:
            validation_result = ValidationResult(valid=False, data=None, errors=parse_errors)
            return CorrectionResult(
                corrected_yaml=raw_output,
                corrections=corrections,
                validation_result=validation_result,
                success=False,
            )

        assert data is not None, "data should not be None when parse_errors is empty"

        # Add missing required fields
        if "scenes" not in data or not data["scenes"]:
            data["scenes"] = {
                "scene_default": {
                    "name": "Default Scene",
                    "description": self._extend_short_description(
                        "A default scene in the narrative.", 50
                    ),
                    "connections": [],
                }
            }
            corrections.append("Added missing 'scenes' field with minimal default")
            logger.info("Added missing 'scenes' field")

        if "start_scene" not in data:
            # Use the first scene as the start scene
            if isinstance(data.get("scenes"), dict) and data["scenes"]:
                first_scene_id = next(iter(data["scenes"].keys()))
                data["start_scene"] = first_scene_id
                corrections.append(f"Added missing 'start_scene' field (set to '{first_scene_id}')")
                logger.info(f"Added missing 'start_scene' field: {first_scene_id}")
            else:
                data["start_scene"] = "scene_default"
                corrections.append("Added missing 'start_scene' field with default value")
                logger.info("Added missing 'start_scene' field")

        # Fix scene IDs and descriptions
        if "scenes" in data and isinstance(data["scenes"], dict):
            fixed_scenes = {}
            for scene_id, scene in data["scenes"].items():
                # Fix scene ID format
                fixed_id = self._fix_id_format(scene_id)
                if scene_id != fixed_id:
                    corrections.append(f"Fixed scene ID format: '{scene_id}' -> '{fixed_id}'")
                    logger.info(f"Fixed scene ID: {scene_id} -> {fixed_id}")
                    # Update start_scene if it matches the old ID
                    if data.get("start_scene") == scene_id:
                        data["start_scene"] = fixed_id
                        corrections.append(f"Updated 'start_scene' to match fixed ID: '{fixed_id}'")

                if isinstance(scene, dict):
                    # Extend short descriptions
                    if "description" in scene and len(scene["description"]) < 50:
                        original_desc = scene["description"]
                        scene["description"] = self._extend_short_description(
                            scene["description"], 50
                        )
                        corrections.append(
                            f"Extended short scene description (was {len(original_desc)} chars)"
                        )
                        logger.info(
                            f"Extended scene description from {len(original_desc)} "
                            f"to {len(scene['description'])} chars"
                        )

                    # Ensure connections is a list
                    if "connections" not in scene:
                        scene["connections"] = []
                        corrections.append(
                            f"Added missing 'connections' field to scene '{fixed_id}'"
                        )

                    # Fix connection target IDs
                    if "connections" in scene and isinstance(scene["connections"], list):
                        for conn in scene["connections"]:
                            if isinstance(conn, dict) and "target" in conn:
                                original_target = conn["target"]
                                fixed_target = self._fix_id_format(original_target)
                                if original_target != fixed_target:
                                    conn["target"] = fixed_target
                                    corrections.append(
                                        f"Fixed connection target ID: "
                                        f"'{original_target}' -> '{fixed_target}'"
                                    )

                fixed_scenes[fixed_id] = scene

            data["scenes"] = fixed_scenes

        # Convert back to YAML
        try:
            corrected_yaml = yaml.dump(
                data, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
        except Exception as e:
            logger.error(f"Error converting corrected data to YAML: {e}")
            validation_result = ValidationResult(
                valid=False, data=None, errors=[f"Error converting to YAML: {e!s}"]
            )
            return CorrectionResult(
                corrected_yaml=raw_output,
                corrections=corrections,
                validation_result=validation_result,
                success=False,
            )

        # Validate corrected output
        validation_result = self.validator.validate_narrative_map(corrected_yaml)

        logger.info(
            f"Narrative map correction complete: {len(corrections)} corrections, "
            f"valid={validation_result.valid}"
        )

        return CorrectionResult(
            corrected_yaml=corrected_yaml,
            corrections=corrections,
            validation_result=validation_result,
            success=validation_result.valid,
        )

    def correct_puzzle_design(self, raw_output: str) -> CorrectionResult:
        """Attempt to correct common errors in puzzle design YAML.

        Fixes:
            - Missing required fields (puzzles, artifacts, monsters, npcs)
            - Invalid ID formats
            - Descriptions too short
            - YAML syntax errors

        Args:
            raw_output: Raw YAML string containing puzzle design data.

        Returns:
            CorrectionResult with corrected YAML, list of corrections,
            validation result, and success status.

        Example:
            >>> corrector = OutputCorrector()
            >>> result = corrector.correct_puzzle_design(invalid_puzzle_yaml)
            >>> if result.success:
            ...     print(f"Puzzle design corrected with {len(result.corrections)} changes")
        """
        logger.info("Attempting to correct puzzle design YAML")
        corrections: list[str] = []

        # Parse YAML
        data, parse_errors = self._parse_yaml_safe(raw_output)
        if parse_errors:
            validation_result = ValidationResult(valid=False, data=None, errors=parse_errors)
            return CorrectionResult(
                corrected_yaml=raw_output,
                corrections=corrections,
                validation_result=validation_result,
                success=False,
            )

        assert data is not None, "data should not be None when parse_errors is empty"

        # Add missing required fields
        if "puzzles" not in data or not data["puzzles"]:
            data["puzzles"] = [
                {
                    "id": "puzzle_default",
                    "name": "Default Puzzle",
                    "description": self._extend_short_description(
                        "A puzzle in the game that requires solving.", 50
                    ),
                    "location": "scene_default",
                    "narrative_purpose": "Provides a challenge for the player to overcome.",
                    "solution": {
                        "type": "multi-step",
                        "steps": [{"step": "Complete the required actions to solve this puzzle."}],
                    },
                    "difficulty": "medium",
                }
            ]
            corrections.append("Added missing 'puzzles' field with minimal default")
            logger.info("Added missing 'puzzles' field")

        if "artifacts" not in data or not data["artifacts"]:
            data["artifacts"] = [
                {
                    "id": "artifact_default",
                    "name": "Default Artifact",
                    "description": "An artifact found in the game world.",
                    "location": "scene_default",
                    "narrative_significance": "Holds narrative importance to the story.",
                    "properties": [{"property": "Has special properties or effects"}],
                }
            ]
            corrections.append("Added missing 'artifacts' field with minimal default")
            logger.info("Added missing 'artifacts' field")

        if "monsters" not in data or not data["monsters"]:
            data["monsters"] = [
                {
                    "id": "monster_default",
                    "name": "Default Monster",
                    "description": "A hostile entity encountered in the game.",
                    "locations": ["scene_default"],
                    "narrative_role": "Provides combat challenge and threat.",
                    "abilities": ["Attack"],
                }
            ]
            corrections.append("Added missing 'monsters' field with minimal default")
            logger.info("Added missing 'monsters' field")

        if "npcs" not in data or not data["npcs"]:
            data["npcs"] = [
                {
                    "id": "npc_default",
                    "name": "Default NPC",
                    "role": "Supporting character",
                    "description": "A non-player character in the game.",
                    "locations": ["scene_default"],
                    "dialogue_themes": ["General conversation"],
                }
            ]
            corrections.append("Added missing 'npcs' field with minimal default")
            logger.info("Added missing 'npcs' field")

        # Fix puzzle IDs and descriptions
        if "puzzles" in data and isinstance(data["puzzles"], list):
            for puzzle in data["puzzles"]:
                if isinstance(puzzle, dict):
                    # Fix ID format
                    if "id" in puzzle:
                        original_id = puzzle["id"]
                        fixed_id = self._fix_id_format(original_id)
                        if original_id != fixed_id:
                            puzzle["id"] = fixed_id
                            corrections.append(
                                f"Fixed puzzle ID format: '{original_id}' -> '{fixed_id}'"
                            )
                            logger.info(f"Fixed puzzle ID: {original_id} -> {fixed_id}")

                    # Extend short descriptions
                    if "description" in puzzle and len(puzzle["description"]) < 50:
                        original_desc = puzzle["description"]
                        puzzle["description"] = self._extend_short_description(
                            puzzle["description"], 50
                        )
                        corrections.append(
                            f"Extended short puzzle description (was {len(original_desc)} chars)"
                        )

        # Fix artifact IDs
        if "artifacts" in data and isinstance(data["artifacts"], list):
            for artifact in data["artifacts"]:
                if isinstance(artifact, dict) and "id" in artifact:
                    original_id = artifact["id"]
                    fixed_id = self._fix_id_format(original_id)
                    if original_id != fixed_id:
                        artifact["id"] = fixed_id
                        corrections.append(
                            f"Fixed artifact ID format: '{original_id}' -> '{fixed_id}'"
                        )
                        logger.info(f"Fixed artifact ID: {original_id} -> {fixed_id}")

        # Fix monster IDs
        if "monsters" in data and isinstance(data["monsters"], list):
            for monster in data["monsters"]:
                if isinstance(monster, dict) and "id" in monster:
                    original_id = monster["id"]
                    fixed_id = self._fix_id_format(original_id)
                    if original_id != fixed_id:
                        monster["id"] = fixed_id
                        corrections.append(
                            f"Fixed monster ID format: '{original_id}' -> '{fixed_id}'"
                        )
                        logger.info(f"Fixed monster ID: {original_id} -> {fixed_id}")

        # Fix NPC IDs
        if "npcs" in data and isinstance(data["npcs"], list):
            for npc in data["npcs"]:
                if isinstance(npc, dict) and "id" in npc:
                    original_id = npc["id"]
                    fixed_id = self._fix_id_format(original_id)
                    if original_id != fixed_id:
                        npc["id"] = fixed_id
                        corrections.append(f"Fixed NPC ID format: '{original_id}' -> '{fixed_id}'")
                        logger.info(f"Fixed NPC ID: {original_id} -> {fixed_id}")

        # Convert back to YAML
        try:
            corrected_yaml = yaml.dump(
                data, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
        except Exception as e:
            logger.error(f"Error converting corrected data to YAML: {e}")
            validation_result = ValidationResult(
                valid=False, data=None, errors=[f"Error converting to YAML: {e!s}"]
            )
            return CorrectionResult(
                corrected_yaml=raw_output,
                corrections=corrections,
                validation_result=validation_result,
                success=False,
            )

        # Validate corrected output
        validation_result = self.validator.validate_puzzle_design(corrected_yaml)

        logger.info(
            f"Puzzle design correction complete: {len(corrections)} corrections, "
            f"valid={validation_result.valid}"
        )

        return CorrectionResult(
            corrected_yaml=corrected_yaml,
            corrections=corrections,
            validation_result=validation_result,
            success=validation_result.valid,
        )

    def correct_scene_texts(self, raw_output: str) -> CorrectionResult:
        """Attempt to correct common errors in scene texts YAML.

        Fixes:
            - Missing required fields (scenes)
            - Invalid ID formats
            - Descriptions too short
            - YAML syntax errors

        Args:
            raw_output: Raw YAML string containing scene texts data.

        Returns:
            CorrectionResult with corrected YAML, list of corrections,
            validation result, and success status.

        Example:
            >>> corrector = OutputCorrector()
            >>> result = corrector.correct_scene_texts(invalid_scene_yaml)
            >>> if result.success:
            ...     print(f"Scene texts corrected with {len(result.corrections)} changes")
        """
        logger.info("Attempting to correct scene texts YAML")
        corrections: list[str] = []

        # Parse YAML
        data, parse_errors = self._parse_yaml_safe(raw_output)
        if parse_errors:
            validation_result = ValidationResult(valid=False, data=None, errors=parse_errors)
            return CorrectionResult(
                corrected_yaml=raw_output,
                corrections=corrections,
                validation_result=validation_result,
                success=False,
            )

        assert data is not None, "data should not be None when parse_errors is empty"

        # Add missing required fields
        if "scenes" not in data or not data["scenes"]:
            data["scenes"] = {
                "scene_default": {
                    "name": "Default Scene",
                    "description": self._extend_short_description(
                        "A detailed description of this scene in the narrative, "
                        "providing context and atmosphere for the player.",
                        100,
                    ),
                    "atmosphere": "Atmospheric and immersive",
                    "initial_text": "You find yourself in this scene.",
                    "examination_texts": {},
                    "dialogue": [],
                }
            }
            corrections.append("Added missing 'scenes' field with minimal default")
            logger.info("Added missing 'scenes' field")

        # Fix scene IDs and descriptions
        if "scenes" in data and isinstance(data["scenes"], dict):
            fixed_scenes = {}
            for scene_id, scene in data["scenes"].items():
                # Fix scene ID format
                fixed_id = self._fix_id_format(scene_id)
                if scene_id != fixed_id:
                    corrections.append(f"Fixed scene ID format: '{scene_id}' -> '{fixed_id}'")
                    logger.info(f"Fixed scene ID: {scene_id} -> {fixed_id}")

                if isinstance(scene, dict):
                    # Extend short descriptions (scene texts require 100 chars minimum)
                    if "description" in scene and len(scene["description"]) < 100:
                        original_desc = scene["description"]
                        scene["description"] = self._extend_short_description(
                            scene["description"], 100
                        )
                        corrections.append(
                            f"Extended short scene description (was {len(original_desc)} chars)"
                        )
                        logger.info(
                            f"Extended scene description from {len(original_desc)} "
                            f"to {len(scene['description'])} chars"
                        )

                    # Ensure required fields exist
                    if "atmosphere" not in scene:
                        scene["atmosphere"] = "Atmospheric and immersive"
                        corrections.append(
                            f"Added missing 'atmosphere' field to scene '{fixed_id}'"
                        )
                    elif len(scene["atmosphere"]) < 10:
                        original_atmo = scene["atmosphere"]
                        scene["atmosphere"] = self._extend_short_description(
                            scene["atmosphere"], 10
                        )
                        corrections.append(
                            f"Extended short 'atmosphere' field in scene '{fixed_id}' "
                            f"(was {len(original_atmo)} chars)"
                        )

                    if "initial_text" not in scene:
                        scene["initial_text"] = "You find yourself in this scene."
                        corrections.append(
                            f"Added missing 'initial_text' field to scene '{fixed_id}'"
                        )
                    elif len(scene["initial_text"]) < 20:
                        original_text = scene["initial_text"]
                        scene["initial_text"] = self._extend_short_description(
                            scene["initial_text"], 20
                        )
                        corrections.append(
                            f"Extended short 'initial_text' field in scene '{fixed_id}' "
                            f"(was {len(original_text)} chars)"
                        )

                    if "examination_texts" not in scene:
                        scene["examination_texts"] = {}
                        corrections.append(
                            f"Added missing 'examination_texts' field to scene '{fixed_id}'"
                        )

                    if "dialogue" not in scene:
                        scene["dialogue"] = []
                        corrections.append(f"Added missing 'dialogue' field to scene '{fixed_id}'")

                fixed_scenes[fixed_id] = scene

            data["scenes"] = fixed_scenes

        # Convert back to YAML
        try:
            corrected_yaml = yaml.dump(
                data, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
        except Exception as e:
            logger.error(f"Error converting corrected data to YAML: {e}")
            validation_result = ValidationResult(
                valid=False, data=None, errors=[f"Error converting to YAML: {e!s}"]
            )
            return CorrectionResult(
                corrected_yaml=raw_output,
                corrections=corrections,
                validation_result=validation_result,
                success=False,
            )

        # Validate corrected output
        validation_result = self.validator.validate_scene_texts(corrected_yaml)

        logger.info(
            f"Scene texts correction complete: {len(corrections)} corrections, "
            f"valid={validation_result.valid}"
        )

        return CorrectionResult(
            corrected_yaml=corrected_yaml,
            corrections=corrections,
            validation_result=validation_result,
            success=validation_result.valid,
        )

    def correct_game_mechanics(self, raw_output: str) -> CorrectionResult:
        """Attempt to correct common errors in game mechanics YAML.

        Fixes:
            - Missing required fields (game_systems, game_state, technical_requirements)
            - Descriptions too short
            - YAML syntax errors

        Args:
            raw_output: Raw YAML string containing game mechanics data.

        Returns:
            CorrectionResult with corrected YAML, list of corrections,
            validation result, and success status.

        Example:
            >>> corrector = OutputCorrector()
            >>> result = corrector.correct_game_mechanics(invalid_mechanics_yaml)
            >>> if result.success:
            ...     print(f"Game mechanics corrected with {len(result.corrections)} changes")
        """
        logger.info("Attempting to correct game mechanics YAML")
        corrections: list[str] = []

        # Parse YAML
        data, parse_errors = self._parse_yaml_safe(raw_output)
        if parse_errors:
            validation_result = ValidationResult(valid=False, data=None, errors=parse_errors)
            return CorrectionResult(
                corrected_yaml=raw_output,
                corrections=corrections,
                validation_result=validation_result,
                success=False,
            )

        assert data is not None, "data should not be None when parse_errors is empty"

        # Add missing required fields
        if "game_title" not in data:
            data["game_title"] = "Untitled Game"
            corrections.append("Added missing 'game_title' field with default value")
            logger.info("Added missing 'game_title' field")

        if "game_systems" not in data:
            data["game_systems"] = {}
            corrections.append("Added missing 'game_systems' field")
            logger.info("Added missing 'game_systems' field")

        # Ensure game_systems has all required subsystems
        game_systems = data["game_systems"]
        if not isinstance(game_systems, dict):
            game_systems = {}
            data["game_systems"] = game_systems
            corrections.append("Converted 'game_systems' to dictionary")

        if "movement" not in game_systems:
            game_systems["movement"] = {
                "description": self._extend_short_description(
                    "Movement system for navigating the game world.", 50
                ),
                "commands": ["move"],
                "narrative_purpose": self._extend_short_description(
                    "Allows players to explore and navigate the environment.", 50
                ),
            }
            corrections.append("Added missing 'movement' system")
            logger.info("Added missing 'movement' system")

        if "inventory" not in game_systems:
            game_systems["inventory"] = {
                "description": self._extend_short_description(
                    "Inventory system for managing items and equipment.", 50
                ),
                "capacity": 10,
                "commands": ["take", "drop", "use"],
                "narrative_purpose": self._extend_short_description(
                    "Allows players to collect and manage resources.", 50
                ),
            }
            corrections.append("Added missing 'inventory' system")
            logger.info("Added missing 'inventory' system")

        if "combat" not in game_systems:
            game_systems["combat"] = {
                "description": self._extend_short_description(
                    "Combat system for engaging with enemies and threats.", 50
                ),
                "mechanics": [
                    {
                        "name": "Attack",
                        "rules": "Basic attack mechanic for engaging enemies in combat.",
                    }
                ],
                "narrative_purpose": self._extend_short_description(
                    "Provides challenge and conflict resolution.", 50
                ),
            }
            corrections.append("Added missing 'combat' system")
            logger.info("Added missing 'combat' system")

        if "interaction" not in game_systems:
            game_systems["interaction"] = {
                "description": self._extend_short_description(
                    "Interaction system for engaging with the environment and NPCs.", 50
                ),
                "commands": ["examine", "talk"],
                "narrative_purpose": self._extend_short_description(
                    "Allows players to discover information and progress the story.", 50
                ),
            }
            corrections.append("Added missing 'interaction' system")
            logger.info("Added missing 'interaction' system")

        if "game_state" not in data:
            data["game_state"] = {
                "tracked_variables": [
                    {
                        "variable": "progress",
                        "purpose": "Tracks player progress through the game.",
                    }
                ],
                "win_conditions": [{"condition": "Successfully complete the primary objective."}],
                "lose_conditions": [
                    {"condition": "Player character is defeated or incapacitated."}
                ],
            }
            corrections.append("Added missing 'game_state' field with minimal defaults")
            logger.info("Added missing 'game_state' field")

        if "technical_requirements" not in data or not data["technical_requirements"]:
            data["technical_requirements"] = [
                {
                    "requirement": (
                        "Basic game engine functionality for managing game state and logic."
                    ),
                    "justification": "Required for the game to function properly.",
                }
            ]
            corrections.append("Added missing 'technical_requirements' field with minimal default")
            logger.info("Added missing 'technical_requirements' field")

        # Convert back to YAML
        try:
            corrected_yaml = yaml.dump(
                data, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
        except Exception as e:
            logger.error(f"Error converting corrected data to YAML: {e}")
            validation_result = ValidationResult(
                valid=False, data=None, errors=[f"Error converting to YAML: {e!s}"]
            )
            return CorrectionResult(
                corrected_yaml=raw_output,
                corrections=corrections,
                validation_result=validation_result,
                success=False,
            )

        # Validate corrected output
        validation_result = self.validator.validate_game_mechanics(corrected_yaml)

        logger.info(
            f"Game mechanics correction complete: {len(corrections)} corrections, "
            f"valid={validation_result.valid}"
        )

        return CorrectionResult(
            corrected_yaml=corrected_yaml,
            corrections=corrections,
            validation_result=validation_result,
            success=validation_result.valid,
        )
