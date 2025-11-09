"""
Plot outline quality evaluator.

This module implements the evaluator for plot outline content,
using PlotMetrics to score and provide feedback on plot quality.
"""

from typing import Dict, Any
import logging

from .evaluator import QualityEvaluator
from .score import QualityScore
from .plot_metrics import PlotMetrics

logger = logging.getLogger(__name__)


class PlotEvaluator(QualityEvaluator):
    """
    Evaluator for plot outline content.
    
    Uses PlotMetrics to evaluate plot outlines against quality criteria
    including setting clarity, branching paths, endings, themes, and word count.
    
    Example:
        >>> evaluator = PlotEvaluator()
        >>> score = evaluator.evaluate(plot_yaml_content)
        >>> print(f"Score: {score.score}/10")
        >>> print(score.feedback)
    """
    
    def __init__(self, pass_threshold: float = 6.0):
        """
        Initialize the plot evaluator.
        
        Args:
            pass_threshold: Minimum score required to pass (default: 6.0)
        """
        super().__init__(pass_threshold)
        logger.info(f"PlotEvaluator initialized with threshold {pass_threshold}")
    
    def evaluate(self, content: str) -> QualityScore:
        """
        Evaluate plot outline content.
        
        Args:
            content: YAML string containing plot outline
            
        Returns:
            QualityScore with evaluation results
            
        Raises:
            ValueError: If content cannot be parsed
        """
        try:
            # Parse YAML content using metrics class
            metrics = PlotMetrics.from_yaml_content(content)
            
            # Get score and check if passes threshold
            score = metrics.get_score()
            passed = score >= self.pass_threshold
            
            # Get failures for detailed feedback
            failures = metrics.get_failures()
            
            # Build feedback message
            feedback = self._build_feedback(score, failures)
            
            # Build details dictionary
            details = {
                'has_clear_setting': metrics.has_clear_setting,
                'branching_paths_count': metrics.branching_paths_count,
                'endings_count': metrics.endings_count,
                'themes_defined': metrics.themes_defined,
                'word_count': metrics.word_count,
                'has_title': metrics.has_title,
                'has_prologue': metrics.has_prologue,
                'has_acts': metrics.has_acts,
                'failures': failures,
                'threshold': self.pass_threshold
            }
            
            logger.info(
                f"Plot evaluation complete: score={score:.1f}, passed={passed}, "
                f"failures={len(failures)}"
            )
            
            return self._create_score(score, passed, feedback, details)
            
        except ValueError as e:
            logger.error(f"Failed to evaluate plot content: {e}")
            # Return failing score with error message
            return self._create_score(
                score=0.0,
                passed=False,
                feedback=f"Failed to parse plot content: {str(e)}",
                details={'error': str(e)}
            )
        except Exception as e:
            logger.exception(f"Unexpected error evaluating plot: {e}")
            return self._create_score(
                score=0.0,
                passed=False,
                feedback=f"Unexpected error during evaluation: {str(e)}",
                details={'error': str(e)}
            )
    
    def generate_detailed_feedback(self, content: str) -> str:
        """
        Generate detailed, actionable feedback for improvement.
        
        Args:
            content: YAML string containing plot outline
            
        Returns:
            Multi-line feedback with specific suggestions
        """
        result = self.evaluate(content)
        
        lines = [
            f"Plot Quality Score: {result.score:.1f}/10.0",
            f"Status: {'PASS ✓' if result.passed else 'FAIL ✗'}",
            "",
        ]
        
        if result.passed:
            lines.append("The plot outline meets all quality requirements!")
        else:
            lines.append("The plot outline needs improvement:")
        
        lines.append("")
        
        # Add specific findings
        details = result.details
        failures = details.get('failures', [])
        
        if failures:
            lines.append("Issues to address:")
            for failure in failures:
                lines.append(f"  • {failure}")
            lines.append("")
        
        # Add positive feedback
        if details.get('has_clear_setting'):
            lines.append("✓ Clear setting defined")
        if details.get('has_title'):
            lines.append("✓ Title present")
        if details.get('themes_defined'):
            lines.append("✓ Themes clearly stated")
        if details.get('has_prologue'):
            lines.append("✓ Prologue included")
        if details.get('has_acts'):
            lines.append("✓ Structured into acts")
        
        lines.append("")
        lines.append(f"Word count: {details.get('word_count', 0)} (min: 500)")
        lines.append(f"Branching paths: {details.get('branching_paths_count', 0)} (min: 2)")
        lines.append(f"Endings: {details.get('endings_count', 0)} (min: 2)")
        
        return "\n".join(lines)
