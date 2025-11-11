"""Output validation for Space Hulk Game YAML outputs.

This module provides validation functionality for parsing and validating
YAML outputs from AI agents against Pydantic schemas.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

import yaml
from pydantic import ValidationError

from space_hulk_game.schemas.game_mechanics import GameMechanics
from space_hulk_game.schemas.narrative_map import NarrativeMap
from space_hulk_game.schemas.plot_outline import PlotOutline
from space_hulk_game.schemas.puzzle_design import PuzzleDesign
from space_hulk_game.schemas.scene_text import SceneTexts

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validating YAML output against a schema.

    Attributes:
        valid: Whether the validation succeeded.
        data: Parsed Pydantic model if validation succeeded, None otherwise.
        errors: List of error messages if validation failed, empty list otherwise.

    Example:
        >>> result = ValidationResult(valid=True, data=plot_outline, errors=[])
        >>> if result.valid:
        ...     print(f"Validation succeeded: {result.data.title}")
        ... else:
        ...     print(f"Errors: {result.errors}")
    """

    valid: bool
    data: Any | None
    errors: list[str]


class OutputValidator:
    """Validator for YAML outputs against Pydantic schemas.

    This class provides methods to parse and validate YAML strings
    against specific Pydantic schemas for different game design outputs.

    Features:
        - Handles markdown-wrapped YAML (common in AI outputs)
        - Provides detailed, helpful error messages
        - Validates against all schema constraints

    Example:
        >>> validator = OutputValidator()
        >>> result = validator.validate_plot(yaml_string)
        >>> if result.valid:
        ...     print(f"Valid plot: {result.data.title}")
        ... else:
        ...     for error in result.errors:
        ...         print(f"Error: {error}")
    """

    def __init__(self):
        """Initialize the output validator."""
        logger.info("OutputValidator initialized")

    def _strip_markdown_fences(self, raw_output: str) -> str:
        """Strip markdown code fences from YAML output.

        AI outputs often wrap YAML in markdown fences like:
        ```yaml
        content: here
        ```

        This method removes those fences to get clean YAML.

        Args:
            raw_output: Raw output string, potentially with markdown fences.

        Returns:
            Cleaned YAML string without markdown fences.

        Example:
            >>> validator = OutputValidator()
            >>> yaml_with_fences = "```yaml\\nkey: value\\n```"
            >>> clean = validator._strip_markdown_fences(yaml_with_fences)
            >>> clean
            'key: value'
        """
        # Remove opening fence (```yaml or ```)
        output = re.sub(r"\A```(?:yaml)?\s*\n", "", raw_output.strip())
        # Remove closing fence (```)
        output = re.sub(r"\n```\s*$", "", output, flags=re.MULTILINE)
        return output.strip()

    def _parse_yaml(self, raw_output: str) -> tuple[dict | None, list[str]]:
        """Parse YAML string into a dictionary.

        Args:
            raw_output: Raw YAML string to parse.

        Returns:
            Tuple of (parsed_data, errors). If parsing succeeds, parsed_data
            is a dict and errors is empty. If parsing fails, parsed_data is None
            and errors contains the error message.
        """
        try:
            # Strip markdown fences first
            clean_yaml = self._strip_markdown_fences(raw_output)

            # Parse YAML
            data = yaml.safe_load(clean_yaml)

            if data is None:
                return None, ["YAML is empty or contains only whitespace"]

            if not isinstance(data, dict):
                return None, [f"YAML must be a dictionary, got {type(data).__name__}"]

            return data, []

        except yaml.YAMLError as e:
            error_msg = f"YAML parsing error: {e!s}"
            logger.error(error_msg)
            return None, [error_msg]
        except Exception as e:
            error_msg = f"Unexpected error during YAML parsing: {e!s}"
            logger.error(error_msg)
            return None, [error_msg]

    def _format_pydantic_errors(self, validation_error: ValidationError) -> list[str]:
        """Format Pydantic validation errors into helpful messages.

        Pydantic errors can be complex. This method extracts the key information
        and formats it in a user-friendly way.

        Args:
            validation_error: Pydantic ValidationError to format.

        Returns:
            List of formatted error messages.
        """
        errors = []
        for error in validation_error.errors():
            loc = " -> ".join(str(x) for x in error["loc"])
            msg = error["msg"]
            error_type = error["type"]

            # Create a detailed error message
            ctx_dict = error.get("ctx")
            if ctx_dict:
                ctx = ", ".join(f"{k}={v}" for k, v in ctx_dict.items())
                error_msg = f"Field '{loc}': {msg} (type={error_type}, {ctx})"
            else:
                error_msg = f"Field '{loc}': {msg} (type={error_type})"

            errors.append(error_msg)

        return errors

    def validate_plot(self, raw_output: str) -> ValidationResult:
        """Parse and validate plot outline YAML against PlotOutline schema.

        Args:
            raw_output: Raw YAML string containing plot outline data.

        Returns:
            ValidationResult with validation status, parsed data if valid,
            and error messages if invalid.

        Example:
            >>> validator = OutputValidator()
            >>> yaml_str = '''
            ... title: "Test Plot"
            ... setting: "A dark and atmospheric setting with lots of detail..."
            ... themes: ["survival", "horror"]
            ... tone: "Dark and gritty atmosphere"
            ... plot_points: [...]
            ... characters: [...]
            ... conflicts: [...]
            ... '''
            >>> result = validator.validate_plot(yaml_str)
            >>> if result.valid:
            ...     print(f"Valid plot: {result.data.title}")
        """
        logger.info("Validating plot outline")

        # Parse YAML
        data, parse_errors = self._parse_yaml(raw_output)
        if parse_errors:
            return ValidationResult(valid=False, data=None, errors=parse_errors)

        # Type guard: data is guaranteed to be dict here since parse_errors is empty
        assert data is not None, "data should not be None when parse_errors is empty"

        # Validate against schema
        try:
            plot = PlotOutline(**data)
            logger.info(f"Plot outline validation successful: {plot.title}")
            return ValidationResult(valid=True, data=plot, errors=[])

        except ValidationError as e:
            errors = self._format_pydantic_errors(e)
            logger.error(f"Plot outline validation failed: {len(errors)} errors")
            return ValidationResult(valid=False, data=None, errors=errors)

        except Exception as e:
            error_msg = f"Unexpected error during plot outline validation: {e!s}"
            logger.error(error_msg)
            return ValidationResult(valid=False, data=None, errors=[error_msg])

    def validate_narrative_map(self, raw_output: str) -> ValidationResult:
        """Parse and validate narrative map YAML against NarrativeMap schema.

        Args:
            raw_output: Raw YAML string containing narrative map data.

        Returns:
            ValidationResult with validation status, parsed data if valid,
            and error messages if invalid.

        Example:
            >>> validator = OutputValidator()
            >>> yaml_str = '''
            ... start_scene: "scene_1"
            ... scenes:
            ...   scene_1:
            ...     name: "Opening Scene"
            ...     description: "A detailed description of the opening scene..."
            ...     connections: []
            ... '''
            >>> result = validator.validate_narrative_map(yaml_str)
            >>> if result.valid:
            ...     print(f"Valid map: {len(result.data.scenes)} scenes")
        """
        logger.info("Validating narrative map")

        # Parse YAML
        data, parse_errors = self._parse_yaml(raw_output)
        if parse_errors:
            return ValidationResult(valid=False, data=None, errors=parse_errors)

        # Type guard: data is guaranteed to be dict here since parse_errors is empty
        assert data is not None, "data should not be None when parse_errors is empty"

        # Validate against schema
        try:
            narrative_map = NarrativeMap(**data)
            logger.info(f"Narrative map validation successful: {len(narrative_map.scenes)} scenes")
            return ValidationResult(valid=True, data=narrative_map, errors=[])

        except ValidationError as e:
            errors = self._format_pydantic_errors(e)
            logger.error(f"Narrative map validation failed: {len(errors)} errors")
            return ValidationResult(valid=False, data=None, errors=errors)

        except Exception as e:
            error_msg = f"Unexpected error during narrative map validation: {e!s}"
            logger.error(error_msg)
            return ValidationResult(valid=False, data=None, errors=[error_msg])

    def validate_puzzle_design(self, raw_output: str) -> ValidationResult:
        """Parse and validate puzzle design YAML against PuzzleDesign schema.

        Args:
            raw_output: Raw YAML string containing puzzle design data.

        Returns:
            ValidationResult with validation status, parsed data if valid,
            and error messages if invalid.

        Example:
            >>> validator = OutputValidator()
            >>> yaml_str = '''
            ... puzzles: [...]
            ... artifacts: [...]
            ... monsters: [...]
            ... npcs: [...]
            ... '''
            >>> result = validator.validate_puzzle_design(yaml_str)
            >>> if result.valid:
            ...     print(f"Valid design: {len(result.data.puzzles)} puzzles")
        """
        logger.info("Validating puzzle design")

        # Parse YAML
        data, parse_errors = self._parse_yaml(raw_output)
        if parse_errors:
            return ValidationResult(valid=False, data=None, errors=parse_errors)

        # Type guard: data is guaranteed to be dict here since parse_errors is empty
        assert data is not None, "data should not be None when parse_errors is empty"

        # Validate against schema
        try:
            puzzle_design = PuzzleDesign(**data)
            logger.info(
                f"Puzzle design validation successful: {len(puzzle_design.puzzles)} puzzles"
            )
            return ValidationResult(valid=True, data=puzzle_design, errors=[])

        except ValidationError as e:
            errors = self._format_pydantic_errors(e)
            logger.error(f"Puzzle design validation failed: {len(errors)} errors")
            return ValidationResult(valid=False, data=None, errors=errors)

        except Exception as e:
            error_msg = f"Unexpected error during puzzle design validation: {e!s}"
            logger.error(error_msg)
            return ValidationResult(valid=False, data=None, errors=[error_msg])

    def validate_scene_texts(self, raw_output: str) -> ValidationResult:
        """Parse and validate scene texts YAML against SceneTexts schema.

        Args:
            raw_output: Raw YAML string containing scene texts data.

        Returns:
            ValidationResult with validation status, parsed data if valid,
            and error messages if invalid.

        Example:
            >>> validator = OutputValidator()
            >>> yaml_str = '''
            ... scenes:
            ...   scene_1:
            ...     name: "Scene 1"
            ...     description: "A very detailed description of what happens in this scene..."
            ...     atmosphere: "Dark and foreboding atmosphere"
            ...     initial_text: "You enter the dark corridor..."
            ...     examination_texts: {}
            ...     dialogue: []
            ... '''
            >>> result = validator.validate_scene_texts(yaml_str)
            >>> if result.valid:
            ...     print(f"Valid texts: {len(result.data.scenes)} scenes")
        """
        logger.info("Validating scene texts")

        # Parse YAML
        data, parse_errors = self._parse_yaml(raw_output)
        if parse_errors:
            return ValidationResult(valid=False, data=None, errors=parse_errors)

        # Type guard: data is guaranteed to be dict here since parse_errors is empty
        assert data is not None, "data should not be None when parse_errors is empty"

        # Validate against schema
        try:
            scene_texts = SceneTexts(**data)
            logger.info(f"Scene texts validation successful: {len(scene_texts.scenes)} scenes")
            return ValidationResult(valid=True, data=scene_texts, errors=[])

        except ValidationError as e:
            errors = self._format_pydantic_errors(e)
            logger.error(f"Scene texts validation failed: {len(errors)} errors")
            return ValidationResult(valid=False, data=None, errors=errors)

        except Exception as e:
            error_msg = f"Unexpected error during scene texts validation: {e!s}"
            logger.error(error_msg)
            return ValidationResult(valid=False, data=None, errors=[error_msg])

    def validate_game_mechanics(self, raw_output: str) -> ValidationResult:
        """Parse and validate game mechanics YAML against GameMechanics schema.

        Args:
            raw_output: Raw YAML string containing game mechanics data.

        Returns:
            ValidationResult with validation status, parsed data if valid,
            and error messages if invalid.

        Example:
            >>> validator = OutputValidator()
            >>> yaml_str = '''
            ... game_title: "Test Game"
            ... game_systems:
            ...   movement: {...}
            ...   inventory: {...}
            ...   combat: {...}
            ...   interaction: {...}
            ... game_state: {...}
            ... technical_requirements: [...]
            ... '''
            >>> result = validator.validate_game_mechanics(yaml_str)
            >>> if result.valid:
            ...     print(f"Valid mechanics: {result.data.game_title}")
        """
        logger.info("Validating game mechanics")

        # Parse YAML
        data, parse_errors = self._parse_yaml(raw_output)
        if parse_errors:
            return ValidationResult(valid=False, data=None, errors=parse_errors)

        # Type guard: data is guaranteed to be dict here since parse_errors is empty
        assert data is not None, "data should not be None when parse_errors is empty"

        # Validate against schema
        try:
            game_mechanics = GameMechanics(**data)
            logger.info(f"Game mechanics validation successful: {game_mechanics.game_title}")
            return ValidationResult(valid=True, data=game_mechanics, errors=[])

        except ValidationError as e:
            errors = self._format_pydantic_errors(e)
            logger.error(f"Game mechanics validation failed: {len(errors)} errors")
            return ValidationResult(valid=False, data=None, errors=errors)

        except Exception as e:
            error_msg = f"Unexpected error during game mechanics validation: {e!s}"
            logger.error(error_msg)
            return ValidationResult(valid=False, data=None, errors=[error_msg])
