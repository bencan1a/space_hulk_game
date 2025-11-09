"""
Quality metrics for Puzzle evaluation.

This module defines measurable quality criteria for puzzles generated
by the Space Hulk Game crew, including solution clarity, narrative integration,
and appropriate difficulty.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import yaml


@dataclass
class PuzzleMetrics:
    """
    Quality metrics for evaluating puzzle and artifact content.
    
    Attributes:
        total_puzzles: Total number of puzzles defined
        puzzles_with_solutions: Number of puzzles with clear solutions
        puzzles_with_narrative_ties: Number of puzzles tied to narrative
        puzzles_with_difficulty: Number of puzzles with difficulty ratings
        has_artifacts: Whether artifacts are defined
        has_monsters: Whether monsters/enemies are defined
        has_npcs: Whether NPCs are defined
        min_puzzles: Minimum required puzzles (default: 2)
    """
    
    # Measured values
    total_puzzles: int = 0
    puzzles_with_solutions: int = 0
    puzzles_with_narrative_ties: int = 0
    puzzles_with_difficulty: int = 0
    has_artifacts: bool = False
    has_monsters: bool = False
    has_npcs: bool = False
    
    # Thresholds
    min_puzzles: int = 2
    min_solution_percentage: float = 80.0  # 80% should have clear solutions
    
    @classmethod
    def from_yaml_content(cls, yaml_content: str) -> 'PuzzleMetrics':
        """
        Create PuzzleMetrics from YAML content string.
        
        Args:
            yaml_content: YAML string containing puzzle design data
            
        Returns:
            PuzzleMetrics instance with measured values
        """
        try:
            # Handle markdown-wrapped YAML
            content = yaml_content.strip()
            if content.startswith('```'):
                lines = content.split('\n')
                content = '\n'.join(lines[1:-1])
            
            data = yaml.safe_load(content)
            return cls.from_dict(data)
        except Exception as e:
            raise ValueError(f"Failed to parse YAML content: {e}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PuzzleMetrics':
        """
        Create PuzzleMetrics from a dictionary (parsed YAML).
        
        Args:
            data: Dictionary containing puzzle design data
            
        Returns:
            PuzzleMetrics instance with measured values
        """
        metrics = cls()
        
        # Check for artifacts
        artifacts = data.get('artifacts', [])
        metrics.has_artifacts = bool(artifacts) and len(artifacts) > 0
        
        # Check for monsters
        monsters = data.get('monsters', [])
        metrics.has_monsters = bool(monsters) and len(monsters) > 0
        
        # Check for NPCs
        npcs = data.get('npcs', [])
        metrics.has_npcs = bool(npcs) and len(npcs) > 0
        
        # Analyze puzzles
        puzzles = data.get('puzzles', [])
        if not puzzles:
            # Try alternate key
            puzzles = data.get('puzzle_design', {}).get('puzzles', [])
        
        metrics.total_puzzles = len(puzzles) if isinstance(puzzles, list) else 0
        
        if isinstance(puzzles, list):
            for puzzle in puzzles:
                if not isinstance(puzzle, dict):
                    continue
                
                # Check for solution
                if cls._has_clear_solution(puzzle):
                    metrics.puzzles_with_solutions += 1
                
                # Check for narrative tie
                if cls._has_narrative_tie(puzzle):
                    metrics.puzzles_with_narrative_ties += 1
                
                # Check for difficulty
                if cls._has_difficulty(puzzle):
                    metrics.puzzles_with_difficulty += 1
        
        return metrics
    
    @staticmethod
    def _has_clear_solution(puzzle: Dict[str, Any]) -> bool:
        """
        Check if puzzle has a clear solution described.
        
        Args:
            puzzle: Puzzle dictionary
            
        Returns:
            True if solution is clearly described
        """
        # Check for explicit solution field
        solution = puzzle.get('solution')
        if solution:
            if isinstance(solution, str):
                return len(solution.strip()) >= 20
            return True
        
        # Check for how_to_solve or similar fields
        how_to_solve = puzzle.get('how_to_solve')
        if how_to_solve:
            if isinstance(how_to_solve, str):
                return len(how_to_solve.strip()) >= 20
            return True
        
        # Check description for solution hints
        description = puzzle.get('description', '')
        if isinstance(description, str):
            # Look for solution-related keywords
            solution_keywords = ['solve', 'answer', 'key', 'unlock', 'activate']
            return any(keyword in description.lower() for keyword in solution_keywords)
        
        return False
    
    @staticmethod
    def _has_narrative_tie(puzzle: Dict[str, Any]) -> bool:
        """
        Check if puzzle is tied to the narrative.
        
        Args:
            puzzle: Puzzle dictionary
            
        Returns:
            True if puzzle has narrative integration
        """
        # Check for explicit narrative fields
        narrative_fields = ['narrative_tie', 'story_connection', 'lore', 'backstory']
        for field in narrative_fields:
            if puzzle.get(field):
                return True
        
        # Check description for narrative elements
        description = puzzle.get('description', '')
        if isinstance(description, str) and len(description) >= 30:
            # Descriptions with some detail likely include narrative context
            return True
        
        # Check for location or scene references
        if puzzle.get('location') or puzzle.get('scene'):
            return True
        
        return False
    
    @staticmethod
    def _has_difficulty(puzzle: Dict[str, Any]) -> bool:
        """
        Check if puzzle has difficulty rating.
        
        Args:
            puzzle: Puzzle dictionary
            
        Returns:
            True if difficulty is stated
        """
        difficulty_fields = ['difficulty', 'challenge_level', 'complexity']
        for field in difficulty_fields:
            if puzzle.get(field):
                return True
        
        return False
    
    def passes_threshold(self) -> bool:
        """
        Check if the puzzle metrics pass all quality thresholds.
        
        Returns:
            True if all thresholds are met, False otherwise
        """
        solution_percentage = 0.0
        if self.total_puzzles > 0:
            solution_percentage = (
                self.puzzles_with_solutions / self.total_puzzles
            ) * 100.0
        
        return (
            self.total_puzzles >= self.min_puzzles and
            solution_percentage >= self.min_solution_percentage
        )
    
    def get_failures(self) -> List[str]:
        """
        Get list of failed quality checks.
        
        Returns:
            List of failure messages for metrics that don't meet thresholds
        """
        failures = []
        
        if self.total_puzzles < self.min_puzzles:
            failures.append(
                f"Insufficient puzzles: {self.total_puzzles} "
                f"(minimum: {self.min_puzzles})"
            )
        
        solution_percentage = 0.0
        if self.total_puzzles > 0:
            solution_percentage = (
                self.puzzles_with_solutions / self.total_puzzles
            ) * 100.0
        
        if solution_percentage < self.min_solution_percentage:
            failures.append(
                f"Too few puzzles with clear solutions: {solution_percentage:.1f}% "
                f"(minimum: {self.min_solution_percentage}%)"
            )
        
        # Warnings (not failures)
        if self.total_puzzles > 0:
            narrative_percentage = (
                self.puzzles_with_narrative_ties / self.total_puzzles
            ) * 100.0
            if narrative_percentage < 50.0:
                failures.append(
                    f"Warning: Only {narrative_percentage:.1f}% of puzzles "
                    f"have narrative ties"
                )
        
        return failures
    
    def get_score(self) -> float:
        """
        Calculate overall quality score (0.0 to 10.0).
        
        Returns:
            Quality score based on met criteria
        """
        score = 0.0
        
        # Minimum puzzles (3 points)
        if self.total_puzzles >= self.min_puzzles:
            score += 3.0
        elif self.total_puzzles > 0:
            score += 3.0 * (self.total_puzzles / self.min_puzzles)
        
        # Solutions (3 points)
        if self.total_puzzles > 0:
            solution_percentage = (
                self.puzzles_with_solutions / self.total_puzzles
            ) * 100.0
            score += 3.0 * (solution_percentage / 100.0)
        
        # Narrative ties (2 points)
        if self.total_puzzles > 0:
            narrative_percentage = (
                self.puzzles_with_narrative_ties / self.total_puzzles
            ) * 100.0
            score += 2.0 * (narrative_percentage / 100.0)
        
        # Difficulty ratings (1 point)
        if self.total_puzzles > 0:
            difficulty_percentage = (
                self.puzzles_with_difficulty / self.total_puzzles
            ) * 100.0
            score += 1.0 * (difficulty_percentage / 100.0)
        
        # Bonus for having artifacts, monsters, NPCs (1 point)
        bonus_items = sum([
            self.has_artifacts,
            self.has_monsters,
            self.has_npcs
        ])
        score += 1.0 * (bonus_items / 3.0)
        
        return min(score, 10.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metrics to dictionary for serialization.
        
        Returns:
            Dictionary representation of metrics
        """
        return {
            'total_puzzles': self.total_puzzles,
            'puzzles_with_solutions': self.puzzles_with_solutions,
            'puzzles_with_narrative_ties': self.puzzles_with_narrative_ties,
            'puzzles_with_difficulty': self.puzzles_with_difficulty,
            'has_artifacts': self.has_artifacts,
            'has_monsters': self.has_monsters,
            'has_npcs': self.has_npcs,
            'passes_threshold': self.passes_threshold(),
            'score': self.get_score(),
            'failures': self.get_failures(),
        }
