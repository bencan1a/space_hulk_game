"""Unified result types for validation and processing operations.

This module provides standardized result types used across the validation,
correction, and quality evaluation layers to ensure consistent error handling
and reporting.

Migration Guide:
    - ValidationResult (validator.py) → ProcessingResult
    - CorrectionResult (corrector.py) → ProcessingResult
    - QualityScore (evaluator.py) → ProcessingResult with metadata['score']

For backward compatibility, existing result types are kept but provide
to_processing_result() conversion methods.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ProcessingResult:
    """Unified result type for YAML processing operations.

    This replaces ValidationResult, CorrectionResult, and parts of QualityScore
    to provide consistent error/warning/info reporting across all processing layers.

    Attributes:
        success: Whether the operation succeeded
        data: The processed data (if successful)
        errors: List of error messages (failures)
        warnings: List of warning messages (non-critical issues)
        corrections: List of corrections applied
        metadata: Additional context (e.g., score for quality checks)

    Examples:
        >>> result = ProcessingResult(
        ...     success=True,
        ...     data={'title': 'Game'},
        ...     errors=[],
        ...     warnings=['Missing optional field'],
        ...     corrections=['Added default value'],
        ...     metadata={'score': 8.5}
        ... )
        >>> result.is_valid
        True
    """

    success: bool
    data: Optional[Any] = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    corrections: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if result is valid (successful and no errors)."""
        return self.success and not self.errors

    @property
    def has_issues(self) -> bool:
        """Check if result has any issues (errors or warnings)."""
        return bool(self.errors or self.warnings)

    def __str__(self) -> str:
        """String representation of result."""
        status = "SUCCESS" if self.success else "FAILED"
        parts = [f"ProcessingResult({status})"]

        if self.errors:
            parts.append(f"{len(self.errors)} errors")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warnings")
        if self.corrections:
            parts.append(f"{len(self.corrections)} corrections")

        return " - ".join(parts)
