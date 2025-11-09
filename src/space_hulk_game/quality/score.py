"""
Quality score data class for evaluation results.

This module defines the QualityScore data structure used by all evaluators
to standardize evaluation results across different content types.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
import json


@dataclass
class QualityScore:
    """
    Standardized quality score returned by all evaluators.
    
    Attributes:
        score: Quality score from 0.0 to 10.0
        passed: Boolean indicating if quality threshold was met
        feedback: Human-readable feedback message
        details: Dictionary with detailed metrics and findings
    
    Example:
        >>> score = QualityScore(
        ...     score=8.5,
        ...     passed=True,
        ...     feedback="Good quality with minor issues",
        ...     details={"word_count": 650, "branching_paths": 3}
        ... )
        >>> print(score)
        QualityScore(8.5/10, PASS)
    """
    
    score: float
    passed: bool
    feedback: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate score is in valid range."""
        if not 0.0 <= self.score <= 10.0:
            raise ValueError(f"Score must be between 0.0 and 10.0, got {self.score}")
    
    def __str__(self) -> str:
        """String representation of the quality score."""
        status = "PASS" if self.passed else "FAIL"
        return f"QualityScore({self.score:.1f}/10, {status})"
    
    def __repr__(self) -> str:
        """Detailed representation of the quality score."""
        feedback_display = (
            self.feedback[:50] + "..." if len(self.feedback) > 50 else self.feedback
        )
        return (
            f"QualityScore(score={self.score:.1f}, passed={self.passed}, "
            f"feedback='{feedback_display}')"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert quality score to dictionary for serialization.
        
        Returns:
            Dictionary representation of the score
        """
        return {
            'score': self.score,
            'passed': self.passed,
            'feedback': self.feedback,
            'details': self.details
        }
    
    def to_json(self) -> str:
        """
        Convert quality score to JSON string.
        
        Returns:
            JSON string representation of the score
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualityScore':
        """
        Create QualityScore from dictionary.
        
        Args:
            data: Dictionary containing score data
            
        Returns:
            QualityScore instance
        """
        return cls(
            score=data['score'],
            passed=data['passed'],
            feedback=data['feedback'],
            details=data.get('details', {})
        )
    
    def get_failures(self) -> List[str]:
        """
        Extract failure messages from details.
        
        Returns:
            List of failure messages if present in details
        """
        return self.details.get('failures', [])
    
    def get_summary(self) -> str:
        """
        Get a multi-line summary of the quality score.
        
        Returns:
            Formatted summary string
        """
        lines = [
            f"Quality Score: {self.score:.1f}/10.0",
            f"Status: {'PASS' if self.passed else 'FAIL'}",
            f"Feedback: {self.feedback}",
        ]
        
        if self.details:
            lines.append("\nDetails:")
            for key, value in self.details.items():
                if key != 'failures':  # Failures shown separately
                    lines.append(f"  {key}: {value}")
        
        failures = self.get_failures()
        if failures:
            lines.append("\nIssues Found:")
            for failure in failures:
                lines.append(f"  - {failure}")
        
        return "\n".join(lines)
