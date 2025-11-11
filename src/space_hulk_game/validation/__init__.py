"""Validation module for Space Hulk Game YAML outputs.

This module provides validators for parsing and validating YAML outputs
from AI agents against Pydantic schemas.

Exports:
    OutputValidator: Main validator class for all YAML outputs
    ValidationResult: Result dataclass containing validation status and errors
"""

from space_hulk_game.validation.validator import OutputValidator, ValidationResult

__all__ = ["OutputValidator", "ValidationResult"]
