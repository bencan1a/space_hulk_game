"""
Puzzle design quality evaluator.

This module implements the evaluator for puzzle design content,
using PuzzleMetrics to score puzzles, artifacts, and NPCs.
"""

from typing import Dict, Any
import logging

from .evaluator import QualityEvaluator
from .score import QualityScore
from .puzzle_metrics import PuzzleMetrics

logger = logging.getLogger(__name__)


class PuzzleEvaluator(QualityEvaluator):
    """
    Evaluator for puzzle design content.
    
    Uses PuzzleMetrics to evaluate puzzle designs against quality criteria
    including clear solutions, narrative ties, and difficulty ratings.
    
    Example:
        >>> evaluator = PuzzleEvaluator()
        >>> score = evaluator.evaluate(puzzle_yaml_content)
        >>> print(f"Score: {score.score}/10")
        >>> print(score.feedback)
    """
    
    def __init__(self, pass_threshold: float = 6.0):
        """
        Initialize the puzzle evaluator.
        
        Args:
            pass_threshold: Minimum score required to pass (default: 6.0)
        """
        super().__init__(pass_threshold)
        logger.info(f"PuzzleEvaluator initialized with threshold {pass_threshold}")
    
    def evaluate(self, content: str) -> QualityScore:
        """
        Evaluate puzzle design content.
        
        Args:
            content: YAML string containing puzzle design
            
        Returns:
            QualityScore with evaluation results
            
        Raises:
            ValueError: If content cannot be parsed
        """
        try:
            # Parse YAML content using metrics class
            metrics = PuzzleMetrics.from_yaml_content(content)
            
            # Get score and check if passes threshold
            score = metrics.get_score()
            passed = score >= self.pass_threshold
            
            # Get failures for detailed feedback
            failures = metrics.get_failures()
            
            # Build feedback message
            feedback = self._build_feedback(score, failures)
            
            # Build details dictionary
            details = {
                'total_puzzles': metrics.total_puzzles,
                'puzzles_with_solutions': metrics.puzzles_with_solutions,
                'puzzles_with_narrative_ties': metrics.puzzles_with_narrative_ties,
                'puzzles_with_difficulty': metrics.puzzles_with_difficulty,
                'has_artifacts': metrics.has_artifacts,
                'has_monsters': metrics.has_monsters,
                'has_npcs': metrics.has_npcs,
                'puzzles_without_solutions': [],  # Can be computed if needed
                'puzzles_without_narrative_tie': [],
                'puzzles_without_difficulty': [],
                'failures': failures,
                'threshold': self.pass_threshold
            }
            
            logger.info(
                f"Puzzle evaluation complete: score={score:.1f}, passed={passed}, "
                f"puzzles={metrics.total_puzzles}, with_solutions={metrics.puzzles_with_solutions}"
            )
            
            return self._create_score(score, passed, feedback, details)
            
        except ValueError as e:
            logger.error(f"Failed to evaluate puzzle content: {e}")
            return self._create_score(
                score=0.0,
                passed=False,
                feedback=f"Failed to parse puzzle content: {str(e)}",
                details={'error': str(e)}
            )
        except Exception as e:
            logger.exception(f"Unexpected error evaluating puzzle: {e}")
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
            content: YAML string containing puzzle design
            
        Returns:
            Multi-line feedback with specific suggestions
        """
        result = self.evaluate(content)
        
        lines = [
            f"Puzzle Design Quality Score: {result.score:.1f}/10.0",
            f"Status: {'PASS ✓' if result.passed else 'FAIL ✗'}",
            "",
        ]
        
        if result.passed:
            lines.append("The puzzle design meets all quality requirements!")
        else:
            lines.append("The puzzle design needs improvement:")
        
        lines.append("")
        
        # Add specific findings
        details = result.details
        failures = details.get('failures', [])
        
        if failures:
            lines.append("Issues to address:")
            for failure in failures:
                lines.append(f"  • {failure}")
            lines.append("")
        
        # Add content statistics
        lines.append(f"Puzzle count: {details.get('total_puzzles', 0)} (min: 2)")
        lines.append(f"Puzzles with solutions: {details.get('puzzles_with_solutions', 0)}")
        lines.append(f"Puzzles with narrative ties: {details.get('puzzles_with_narrative_ties', 0)}")
        lines.append(f"Puzzles with difficulty: {details.get('puzzles_with_difficulty', 0)}")
        
        # Add positive feedback
        lines.append("")
        if details.get('has_artifacts'):
            lines.append("✓ Artifacts defined")
        if details.get('has_monsters'):
            lines.append("✓ Monsters/enemies defined")
        if details.get('has_npcs'):
            lines.append("✓ NPCs defined")
        
        total = details.get('total_puzzles', 0)
        if total > 0:
            if details.get('puzzles_with_solutions', 0) == total:
                lines.append("✓ All puzzles have clear solutions")
            if details.get('puzzles_with_narrative_ties', 0) == total:
                lines.append("✓ All puzzles tied to narrative")
            if details.get('puzzles_with_difficulty', 0) == total:
                lines.append("✓ All puzzles have difficulty ratings")
        
        return "\n".join(lines)
