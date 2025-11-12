"""Output Sanitization Pipeline

This module provides pre-write sanitization for JSON outputs from CrewAI agents.
With JSON mode enabled in the LLM, most syntax errors are eliminated. The sanitizer
now focuses on:
1. Stripping markdown fences (if present: ```json blocks)
2. Validating JSON syntax
3. Pretty-formatting JSON for readability

This is significantly simpler than the previous YAML pipeline, as JSON mode provides
guaranteed valid syntax from the LLM.

Example:
    >>> sanitizer = OutputSanitizer()
    >>> raw_output = '{"narrative_foundation": {"title": "My Plot"}}'
    >>> clean_json = sanitizer.sanitize(raw_output, 'plot')
    >>> print(clean_json)
    {
      "narrative_foundation": {
        "title": "My Plot",
        ...
      }
    }
"""

from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger(__name__)


def strip_markdown_yaml_blocks(content: str) -> str:
    """Strip markdown code block markers from YAML content.

    DEPRECATED: This function is kept for backward compatibility with deprecated
    YAML validation modules (corrector.py, validator.py). New code should use
    JSON format and _strip_markdown_json_blocks instead.

    LLMs often wrap YAML in markdown code blocks like:
    ```yaml
    content: here
    ```

    This function removes those markers to produce clean YAML.

    Args:
        content: Raw content that may contain markdown markers

    Returns:
        Clean YAML content without markdown markers
    """
    # Remove leading ```yaml or ``` markers
    content = re.sub(r"^```ya?ml\s*\n", "", content, flags=re.MULTILINE)
    content = re.sub(r"^```\s*\n", "", content, flags=re.MULTILINE)

    # Remove trailing ``` markers
    content = re.sub(r"\n```\s*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"^```\s*$", "", content, flags=re.MULTILINE)

    return content.strip()


class OutputSanitizer:
    """Pre-write sanitization pipeline for JSON outputs.

    This class provides lightweight sanitization for JSON outputs from CrewAI agents.
    With JSON mode enabled in the LLM, most syntax errors are eliminated, so the
    sanitizer focuses on:
    1. Stripping markdown fences (```json blocks, if present)
    2. Validating JSON syntax
    3. Pretty-formatting JSON for readability

    Features:
        - Handles all 5 output types (plot, narrative, puzzle, scene, mechanics)
        - Graceful error handling - returns best-effort sanitized output
        - Comprehensive logging of all sanitization steps
        - Much simpler than YAML pipeline (JSON mode eliminates syntax errors)

    Example:
        >>> sanitizer = OutputSanitizer()
        >>> # Raw output from LLM (potentially with markdown fences)
        >>> raw_output = '''```json
        ... {"narrative_foundation": {"title": "Space Hulk Adventure"}}
        ... ```'''
        >>> # Sanitize before writing to disk
        >>> clean_json = sanitizer.sanitize(raw_output, 'plot')
        >>> # clean_json now has markdown stripped and is pretty-formatted
        >>> with open('plot_outline.json', 'w') as f:
        ...     f.write(clean_json)
    """

    def __init__(self) -> None:
        """Initialize the output sanitizer.

        With JSON mode, we don't need the complex corrector infrastructure.
        """
        logger.info("OutputSanitizer initialized for JSON outputs")

    def _strip_markdown_json_blocks(self, content: str) -> str:
        """Strip markdown JSON code blocks from content.

        Removes ```json and ``` markers that LLMs might add (though JSON mode should prevent this).

        Args:
            content: Raw string that might contain markdown fences

        Returns:
            Content with markdown fences removed
        """
        # Remove ```json at the start (with optional whitespace)
        content = re.sub(r"^\s*```json\s*\n?", "", content, flags=re.IGNORECASE)
        # Remove ``` at the end (with optional whitespace)
        content = re.sub(r"\n?\s*```\s*$", "", content)
        return content.strip()

    def sanitize(self, raw_output: str, output_type: str) -> str:
        """Sanitize raw LLM output before writing to disk.

        This method applies a simple sanitization pipeline:
        1. Strip markdown code fences (```json blocks, if present)
        2. Validate JSON syntax with json.loads()
        3. Pretty-format JSON with json.dumps()

        The method uses graceful error handling - if parsing fails, it returns
        the markdown-stripped version.

        Args:
            raw_output: Raw JSON string from LLM, potentially with markdown fences.
            output_type: Type of output (plot, narrative, puzzle, scene, mechanics).
                        Currently used only for logging.

        Returns:
            Sanitized JSON string, ready to be written to disk. Pretty-formatted
            with 2-space indentation for readability.

        Raises:
            No exceptions are raised - all errors are logged and handled gracefully.

        Example:
            >>> sanitizer = OutputSanitizer()
            >>> # LLM output with markdown fences
            >>> raw = '''```json
            ... {"narrative_foundation": {"title": "Space Hulk"}}
            ... ```'''
            >>> clean = sanitizer.sanitize(raw, 'plot')
            >>> # clean is now pretty-formatted JSON without fences
        """
        logger.info(f"Sanitizing JSON output as type: {output_type}")

        # Phase 1: Strip markdown fences (if present)
        try:
            markdown_stripped = self._strip_markdown_json_blocks(raw_output)
            logger.debug(
                f"Markdown fences stripped (length: {len(raw_output)} -> {len(markdown_stripped)})"
            )
        except Exception as e:
            logger.warning(
                f"Error stripping markdown fences, using raw output: {e}",
                exc_info=True,
            )
            markdown_stripped = raw_output

        # Phase 2: Validate JSON syntax and pretty-format
        try:
            # Parse JSON to validate syntax
            parsed_data = json.loads(markdown_stripped)
            logger.info(f"JSON syntax validated successfully for {output_type}")

            # Pretty-format with 2-space indentation
            pretty_json = json.dumps(parsed_data, indent=2, ensure_ascii=False)
            logger.info(f"Sanitization successful for {output_type}")
            return pretty_json

        except json.JSONDecodeError as e:
            # JSON parsing failed - log error and return markdown-stripped version
            logger.error(
                f"JSON parsing failed for {output_type}: {e}",
                exc_info=True,
            )
            logger.warning("Returning markdown-stripped output without validation (best effort)")
            return markdown_stripped

        except Exception as e:
            # Unexpected error during sanitization
            logger.error(
                f"Unexpected error during sanitization for {output_type}: {e}",
                exc_info=True,
            )
            logger.warning("Returning markdown-stripped output (fallback)")
            return markdown_stripped
