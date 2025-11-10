"""
Quality metrics and evaluation module for Space Hulk Game.

This module provides quality evaluation metrics and evaluators for generated
game content, including plot outlines, narrative maps, puzzles, scenes, and mechanics.
"""

import logging

from .evaluator import QualityEvaluator

# Integration helpers for CrewAI
from .integration import (
    CREW_TASK_MAPPING,
    QualityCheckConfig,
    TaskExecutor,
    execute_with_optional_quality_check,
    get_default_executor,
    get_task_type_for_crew_task,
)
from .mechanics_evaluator import MechanicsEvaluator
from .mechanics_metrics import MechanicsMetrics
from .narrative_evaluator import NarrativeMapEvaluator
from .narrative_metrics import NarrativeMetrics

# Evaluator implementations
from .plot_evaluator import PlotEvaluator

# Metrics classes
from .plot_metrics import PlotMetrics
from .puzzle_evaluator import PuzzleEvaluator
from .puzzle_metrics import PuzzleMetrics

# Retry logic with quality feedback
from .retry import TaskType, TaskWithQualityCheck, create_quality_config, execute_with_quality_check
from .scene_evaluator import SceneEvaluator
from .scene_metrics import SceneMetrics

# Quality score and evaluator base
from .score import QualityScore

# Configure logging for the quality metrics module
logger = logging.getLogger(__name__)

__all__ = [
    # Metrics
    'PlotMetrics',
    'NarrativeMetrics',
    'PuzzleMetrics',
    'SceneMetrics',
    'MechanicsMetrics',
    # Score and base evaluator
    'QualityScore',
    'QualityEvaluator',
    # Evaluators
    'PlotEvaluator',
    'NarrativeMapEvaluator',
    'PuzzleEvaluator',
    'SceneEvaluator',
    'MechanicsEvaluator',
    # Retry logic
    'TaskWithQualityCheck',
    'TaskType',
    'execute_with_quality_check',
    'create_quality_config',
    # Integration
    'QualityCheckConfig',
    'TaskExecutor',
    'get_default_executor',
    'execute_with_optional_quality_check',
    'get_task_type_for_crew_task',
    'CREW_TASK_MAPPING',
]
