"""Validation module for Space Hulk Game YAML outputs.

This module provides validators and auto-correctors for parsing, validating,
and fixing YAML outputs from AI agents against Pydantic schemas.

Exports:
    OutputValidator: Main validator class for all YAML outputs
    ValidationResult: Result dataclass containing validation status and errors
    OutputCorrector: Auto-corrector for fixing common YAML validation errors
    CorrectionResult: Result dataclass containing correction status and changes
"""

from space_hulk_game.validation.corrector import CorrectionResult, OutputCorrector
from space_hulk_game.validation.validator import OutputValidator, ValidationResult

__all__ = [
    "CorrectionResult",
    "OutputCorrector",
    "OutputValidator",
    "ValidationResult",
]
