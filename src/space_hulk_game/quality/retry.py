"""
Retry logic with quality feedback for task execution.

This module provides retry mechanisms for tasks that fail quality checks,
enabling iterative improvement through specific feedback from evaluators.
"""

import logging
from typing import Optional, Callable, Any, Dict
from enum import Enum

from .score import QualityScore
from .evaluator import QualityEvaluator
from .plot_evaluator import PlotEvaluator
from .narrative_evaluator import NarrativeMapEvaluator
from .puzzle_evaluator import PuzzleEvaluator
from .scene_evaluator import SceneEvaluator
from .mechanics_evaluator import MechanicsEvaluator

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Enum for task types to map to appropriate evaluators."""
    PLOT = "plot"
    NARRATIVE = "narrative"
    PUZZLE = "puzzle"
    SCENE = "scene"
    MECHANICS = "mechanics"


class TaskWithQualityCheck:
    """
    Wrapper for task execution with quality checking and retry logic.
    
    This class wraps task execution to add quality evaluation after execution,
    implementing a retry loop that provides feedback for improvement.
    
    Example:
        >>> task_wrapper = TaskWithQualityCheck(
        ...     task_type=TaskType.PLOT,
        ...     pass_threshold=7.0,
        ...     max_retries=3
        ... )
        >>> result = task_wrapper.execute(task_function, task_name="Plot Generation")
    """
    
    def __init__(
        self,
        task_type: TaskType,
        pass_threshold: float = 6.0,
        max_retries: int = 3
    ):
        """
        Initialize the task wrapper with quality checking.
        
        Args:
            task_type: Type of task to execute (determines which evaluator to use)
            pass_threshold: Minimum quality score required to pass (0.0-10.0)
            max_retries: Maximum number of retry attempts (default: 3)
        
        Raises:
            ValueError: If parameters are invalid
        """
        if not 0.0 <= pass_threshold <= 10.0:
            raise ValueError(f"Pass threshold must be between 0.0 and 10.0, got {pass_threshold}")
        if max_retries < 1:
            raise ValueError(f"Max retries must be at least 1, got {max_retries}")
        
        self.task_type = task_type
        self.pass_threshold = pass_threshold
        self.max_retries = max_retries
        self.evaluator = self._create_evaluator()
        
        logger.debug(
            f"TaskWithQualityCheck initialized for {task_type.value} "
            f"(threshold={pass_threshold}, max_retries={max_retries})"
        )
    
    def _create_evaluator(self) -> QualityEvaluator:
        """
        Create the appropriate evaluator based on task type.
        
        Returns:
            QualityEvaluator instance for the task type
        """
        evaluator_map = {
            TaskType.PLOT: PlotEvaluator,
            TaskType.NARRATIVE: NarrativeMapEvaluator,
            TaskType.PUZZLE: PuzzleEvaluator,
            TaskType.SCENE: SceneEvaluator,
            TaskType.MECHANICS: MechanicsEvaluator,
        }
        
        evaluator_class = evaluator_map[self.task_type]
        return evaluator_class(pass_threshold=self.pass_threshold)
    
    def execute(
        self,
        task_function: Callable[..., str],
        task_name: str = "Task",
        **kwargs
    ) -> tuple[str, QualityScore, int]:
        """
        Execute task with quality checking and retry logic.
        
        Args:
            task_function: Function to execute (should return output string)
            task_name: Human-readable name for logging
            **kwargs: Additional arguments to pass to task_function
        
        Returns:
            Tuple of (output, final_quality_score, attempts_made)
        """
        logger.info(f"Executing {task_name} with quality checks")
        
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"{task_name}: Attempt {attempt}/{self.max_retries}")
            
            # Execute the task
            try:
                output = task_function(**kwargs)
            except Exception as e:
                logger.error(f"{task_name}: Execution failed on attempt {attempt}: {e}")
                if attempt == self.max_retries:
                    raise
                continue
            
            # Evaluate quality
            try:
                quality = self.evaluator.evaluate(output)
                logger.info(
                    f"{task_name}: Quality score {quality.score:.1f}/10.0 "
                    f"({'PASS' if quality.passed else 'FAIL'})"
                )
            except Exception as e:
                logger.error(f"{task_name}: Quality evaluation failed: {e}")
                # If evaluation fails, accept output with warning
                quality = QualityScore(
                    score=0.0,
                    passed=False,
                    feedback=f"Evaluation error: {str(e)}",
                    details={"evaluation_error": True}
                )
            
            # Check if quality threshold is met
            if quality.passed:
                logger.info(
                    f"{task_name}: Quality threshold met on attempt {attempt}. "
                    f"Score: {quality.score:.1f}/10.0"
                )
                return output, quality, attempt
            
            # Provide feedback for retry (if not last attempt)
            if attempt < self.max_retries:
                logger.warning(
                    f"{task_name}: Quality threshold not met "
                    f"(score: {quality.score:.1f}/{self.pass_threshold:.1f}). "
                    f"Feedback: {quality.feedback}"
                )
                
                # Add feedback to kwargs for next iteration
                if 'feedback_history' not in kwargs:
                    kwargs['feedback_history'] = []
                kwargs['feedback_history'].append({
                    'attempt': attempt,
                    'score': quality.score,
                    'feedback': quality.feedback,
                    'details': quality.details
                })
            else:
                # Max retries reached
                logger.warning(
                    f"{task_name}: Max retries ({self.max_retries}) reached. "
                    f"Accepting output with quality score {quality.score:.1f}/10.0. "
                    f"Feedback: {quality.feedback}"
                )
        
        # Return final attempt even if it didn't pass
        return output, quality, self.max_retries


def execute_with_quality_check(
    task_function: Callable[..., str],
    task_type: TaskType,
    task_name: str = "Task",
    pass_threshold: float = 6.0,
    max_retries: int = 3,
    **kwargs
) -> tuple[str, QualityScore, int]:
    """
    Execute a task with quality checking and retry logic (functional interface).
    
    This is a convenience function that wraps TaskWithQualityCheck for simpler usage.
    
    Args:
        task_function: Function to execute (should return output string)
        task_type: Type of task (determines which evaluator to use)
        task_name: Human-readable name for logging
        pass_threshold: Minimum quality score required to pass (0.0-10.0)
        max_retries: Maximum number of retry attempts (default: 3)
        **kwargs: Additional arguments to pass to task_function
    
    Returns:
        Tuple of (output, final_quality_score, attempts_made)
    
    Example:
        >>> def generate_plot(**kwargs):
        ...     # Your plot generation logic
        ...     return "title: My Plot\\nsetting: Space station"
        >>> 
        >>> output, quality, attempts = execute_with_quality_check(
        ...     task_function=generate_plot,
        ...     task_type=TaskType.PLOT,
        ...     task_name="Generate Plot",
        ...     pass_threshold=7.0,
        ...     max_retries=3
        ... )
        >>> print(f"Completed in {attempts} attempts with score {quality.score}")
    """
    wrapper = TaskWithQualityCheck(
        task_type=task_type,
        pass_threshold=pass_threshold,
        max_retries=max_retries
    )
    
    return wrapper.execute(task_function, task_name=task_name, **kwargs)


def create_quality_config(
    plot_threshold: float = 6.0,
    narrative_threshold: float = 6.0,
    puzzle_threshold: float = 6.0,
    scene_threshold: float = 6.0,
    mechanics_threshold: float = 6.0,
    max_retries: int = 3
) -> Dict[TaskType, Dict[str, Any]]:
    """
    Create a quality configuration dictionary for all task types.
    
    Args:
        plot_threshold: Pass threshold for plot tasks (0.0-10.0)
        narrative_threshold: Pass threshold for narrative tasks (0.0-10.0)
        puzzle_threshold: Pass threshold for puzzle tasks (0.0-10.0)
        scene_threshold: Pass threshold for scene tasks (0.0-10.0)
        mechanics_threshold: Pass threshold for mechanics tasks (0.0-10.0)
        max_retries: Maximum retry attempts for all tasks
    
    Returns:
        Dictionary mapping task types to their quality configurations
    
    Example:
        >>> config = create_quality_config(
        ...     plot_threshold=7.0,
        ...     narrative_threshold=8.0,
        ...     max_retries=3
        ... )
        >>> plot_config = config[TaskType.PLOT]
        >>> print(plot_config['pass_threshold'])  # 7.0
    """
    return {
        TaskType.PLOT: {
            'pass_threshold': plot_threshold,
            'max_retries': max_retries
        },
        TaskType.NARRATIVE: {
            'pass_threshold': narrative_threshold,
            'max_retries': max_retries
        },
        TaskType.PUZZLE: {
            'pass_threshold': puzzle_threshold,
            'max_retries': max_retries
        },
        TaskType.SCENE: {
            'pass_threshold': scene_threshold,
            'max_retries': max_retries
        },
        TaskType.MECHANICS: {
            'pass_threshold': mechanics_threshold,
            'max_retries': max_retries
        }
    }
