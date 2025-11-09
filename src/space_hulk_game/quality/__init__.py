"""
Quality metrics module for Space Hulk Game.

This module provides quality evaluation metrics for generated game content,
including plot outlines, narrative maps, puzzles, scenes, and mechanics.
"""

import logging

from .plot_metrics import PlotMetrics
from .narrative_metrics import NarrativeMetrics
from .puzzle_metrics import PuzzleMetrics
from .scene_metrics import SceneMetrics
from .mechanics_metrics import MechanicsMetrics

# Configure logging for the quality metrics module
logger = logging.getLogger(__name__)

__all__ = [
    'PlotMetrics',
    'NarrativeMetrics',
    'PuzzleMetrics',
    'SceneMetrics',
    'MechanicsMetrics',
]
