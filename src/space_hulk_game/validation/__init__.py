"""Validation module for Space Hulk Game YAML outputs.

This module provides validators and auto-correctors for parsing, validating,
and fixing YAML outputs from AI agents against Pydantic schemas.

DEPRECATED: This module is deprecated as the system has migrated to JSON outputs.
JSON mode in LLMs guarantees valid syntax, eliminating the need for this validation layer.
For game playability validation, use space_hulk_game.engine.validator instead.

Exports:
    ProcessingResult: Unified result type for all processing operations (NEW)
    OutputValidator: Main validator class for all YAML outputs (DEPRECATED)
    ValidationResult: Result dataclass containing validation status and errors (DEPRECATED)
    OutputCorrector: Auto-corrector for fixing common YAML validation errors (DEPRECATED)
    CorrectionResult: Result dataclass containing correction status and changes (DEPRECATED)
"""

from space_hulk_game.validation.corrector import CorrectionResult, OutputCorrector
from space_hulk_game.validation.types import ProcessingResult
from space_hulk_game.validation.validator import OutputValidator, ValidationResult

__all__ = [
    "CorrectionResult",
    "OutputCorrector",
    "OutputValidator",
    "ProcessingResult",
    "ValidationResult",
]
