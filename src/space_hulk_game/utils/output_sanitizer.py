"""Output Sanitization Pipeline

This module provides pre-write sanitization for YAML outputs from CrewAI agents.
It orchestrates existing validation and correction layers to ensure clean YAML is
written to disk, preventing common syntax errors like mixed quotes, invalid list
markers, and unescaped apostrophes.

The OutputSanitizer intercepts raw LLM output BEFORE it's written to disk, applying:
1. Markdown fence stripping (removes ```yaml blocks)
2. YAML syntax correction (fixes common errors)
3. Schema validation and auto-correction (adds missing fields, fixes IDs)

This solves the critical issue where CrewAI writes raw LLM output directly to disk,
causing YAML syntax errors that break downstream processing.

Example:
    >>> sanitizer = OutputSanitizer()
    >>> raw_output = "```yaml\\ntitle: My Plot\\n```"
    >>> clean_yaml = sanitizer.sanitize(raw_output, 'plot')
    >>> print(clean_yaml)
    title: My Plot
    setting: ...
    # (with all required fields added and validated)
"""

import logging
from typing import TYPE_CHECKING

from space_hulk_game.utils.yaml_processor import strip_markdown_yaml_blocks

if TYPE_CHECKING:
    from space_hulk_game.validation.corrector import OutputCorrector

logger = logging.getLogger(__name__)


class OutputSanitizer:
    """Pre-write sanitization pipeline for YAML outputs.

    This class orchestrates the existing YAML processing and correction layers
    into a single sanitization pipeline that runs BEFORE CrewAI writes outputs
    to disk. It ensures that YAML files are syntactically valid and schema-compliant.

    The pipeline executes in two phases:
    1. Strip markdown fences using yaml_processor
    2. Apply type-specific correction using corrector

    Features:
        - Handles all 5 output types (plot, narrative, puzzle, scene, mechanics)
        - Graceful error handling - returns best-effort sanitized output
        - Comprehensive logging of all sanitization steps
        - Reuses existing validation/correction infrastructure

    Attributes:
        corrector: OutputCorrector instance for schema validation/correction

    Example:
        >>> sanitizer = OutputSanitizer()
        >>> # Raw output from LLM with markdown fences and missing fields
        >>> raw_output = '''```yaml
        ... title: "Space Hulk Adventure"
        ... setting: "Abandoned ship"
        ... ```'''
        >>> # Sanitize before writing to disk
        >>> clean_yaml = sanitizer.sanitize(raw_output, 'plot')
        >>> # clean_yaml now has markdown stripped and all required fields added
        >>> with open('plot_outline.yaml', 'w') as f:
        ...     f.write(clean_yaml)
    """

    def __init__(self) -> None:
        """Initialize the output sanitizer with a corrector instance.

        The corrector provides type-specific validation and auto-correction
        for all five output types.
        """
        # Lazy import to avoid circular dependency
        from space_hulk_game.validation.corrector import OutputCorrector

        self.corrector = OutputCorrector()
        logger.info("OutputSanitizer initialized with OutputCorrector")

    def sanitize(self, raw_output: str, output_type: str) -> str:
        """Sanitize raw LLM output before writing to disk.

        This method applies a two-phase sanitization pipeline:
        1. Strip markdown code fences (```yaml blocks)
        2. Apply type-specific correction (schema validation, error fixing)

        The method uses graceful error handling - if correction fails at any
        stage, it returns the best-effort sanitized output rather than raising
        exceptions. This ensures that SOME output is written, even if not
        perfectly validated.

        Args:
            raw_output: Raw YAML string from LLM, potentially with markdown fences,
                       syntax errors, and missing required fields.
            output_type: Type of output for type-specific correction. Valid values:
                        - 'plot': Plot outline with plot_points, characters, conflicts
                        - 'narrative': Narrative map with scenes and connections
                        - 'puzzle': Puzzle design with puzzles, artifacts, monsters, npcs
                        - 'scene': Scene texts with detailed descriptions and dialogue
                        - 'mechanics': Game mechanics with systems and state

        Returns:
            Sanitized YAML string, ready to be written to disk. If correction
            succeeds, the output is fully validated and schema-compliant. If
            correction fails, returns the markdown-stripped version with warnings
            logged.

        Raises:
            No exceptions are raised - all errors are logged and handled gracefully.

        Example:
            >>> sanitizer = OutputSanitizer()
            >>> # LLM output with markdown fences and mixed quotes
            >>> raw = '''```yaml
            ... title: "Space Hulk: Lost Vessel'
            ... setting: 'A dark ship
            ... ```'''
            >>> clean = sanitizer.sanitize(raw, 'plot')
            >>> # clean now has fences stripped, quotes fixed, missing fields added
        """
        logger.info(f"Sanitizing output as type: {output_type}")

        # Phase 1: Strip markdown fences
        # This removes ```yaml and ``` markers that LLMs often add
        try:
            markdown_stripped = strip_markdown_yaml_blocks(raw_output)
            logger.debug(
                f"Markdown fences stripped (length: {len(raw_output)} -> {len(markdown_stripped)})"
            )
        except Exception as e:
            logger.warning(
                f"Error stripping markdown fences, using raw output: {e}",
                exc_info=True,
            )
            markdown_stripped = raw_output

        # Phase 2: Apply type-specific correction
        # This validates schema and fixes common errors
        try:
            if output_type == "plot":
                result = self.corrector.correct_plot(markdown_stripped)
            elif output_type == "narrative":
                result = self.corrector.correct_narrative_map(markdown_stripped)
            elif output_type == "puzzle":
                result = self.corrector.correct_puzzle_design(markdown_stripped)
            elif output_type == "scene":
                result = self.corrector.correct_scene_texts(markdown_stripped)
            elif output_type == "mechanics":
                result = self.corrector.correct_game_mechanics(markdown_stripped)
            else:
                logger.warning(
                    f"Unknown output type '{output_type}', skipping type-specific correction"
                )
                # Return markdown-stripped version for unknown types
                return markdown_stripped

            # Log correction results
            if result.corrections:
                logger.info(
                    f"Applied {len(result.corrections)} corrections for {output_type}: "
                    f"{result.corrections}"
                )

            if result.success:
                logger.info(f"Sanitization successful for {output_type}")
                return result.corrected_yaml
            else:
                # Validation incomplete, but return corrected version anyway (best effort)
                logger.warning(
                    f"Sanitization incomplete for {output_type}, validation errors: "
                    f"{result.validation_result.errors}"
                )
                logger.warning("Returning corrected YAML despite validation errors (best effort)")
                return result.corrected_yaml

        except Exception as e:
            # Fallback: if correction fails completely, return markdown-stripped version
            logger.error(
                f"Error during type-specific correction for {output_type}: {e}",
                exc_info=True,
            )
            logger.warning("Returning markdown-stripped output without type-specific correction")
            return markdown_stripped
