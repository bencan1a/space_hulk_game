"""
Quality metrics for Scene evaluation.

This module defines measurable quality criteria for scene texts generated
by the Space Hulk Game crew, including vivid descriptions, consistent tone,
and appropriate dialogue.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import yaml
import re


@dataclass
class SceneMetrics:
    """
    Quality metrics for evaluating scene text content.
    
    Attributes:
        total_scenes: Total number of scenes
        scenes_with_vivid_descriptions: Number of scenes with quality descriptions
        scenes_with_dialogue: Number of scenes containing dialogue
        average_description_length: Average length of scene descriptions (words)
        tone_consistency_score: Score for tone consistency (0.0 to 10.0)
        has_sensory_details: Whether scenes include sensory details
        min_scenes: Minimum required scenes (default: 5)
        min_description_length: Minimum description length in words (default: 50)
    """
    
    # Measured values
    total_scenes: int = 0
    scenes_with_vivid_descriptions: int = 0
    scenes_with_dialogue: int = 0
    average_description_length: float = 0.0
    tone_consistency_score: float = 0.0
    has_sensory_details: bool = False
    
    # Thresholds
    min_scenes: int = 5
    min_description_length: int = 50
    min_vivid_percentage: float = 70.0  # 70% should be vivid
    
    @classmethod
    def from_yaml_content(cls, yaml_content: str) -> 'SceneMetrics':
        """
        Create SceneMetrics from YAML content string.
        
        Args:
            yaml_content: YAML string containing scene texts data
            
        Returns:
            SceneMetrics instance with measured values
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
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneMetrics':
        """
        Create SceneMetrics from a dictionary (parsed YAML).
        
        Args:
            data: Dictionary containing scene texts data
            
        Returns:
            SceneMetrics instance with measured values
        """
        metrics = cls()
        
        # Get scenes
        scenes = data.get('scenes', {})
        if not scenes:
            # Try alternate structure
            scenes = data.get('scene_texts', {})
        
        metrics.total_scenes = len(scenes)
        
        if metrics.total_scenes == 0:
            return metrics
        
        # Analyze each scene
        total_description_length = 0
        tones = []
        
        for scene_id, scene_data in scenes.items():
            if not isinstance(scene_data, dict):
                continue
            
            # Get description
            description = scene_data.get('description', '')
            if not description:
                description = scene_data.get('text', '')
            
            # Check for vivid description
            if cls._is_vivid_description(description):
                metrics.scenes_with_vivid_descriptions += 1
            
            # Check for dialogue
            if cls._has_dialogue(description, scene_data):
                metrics.scenes_with_dialogue += 1
            
            # Track description length
            desc_length = len(description.split()) if isinstance(description, str) else 0
            total_description_length += desc_length
            
            # Track tone
            tone = scene_data.get('tone', '')
            if tone:
                tones.append(tone)
            
            # Check for sensory details
            if cls._has_sensory_details(description):
                metrics.has_sensory_details = True
        
        # Calculate averages
        metrics.average_description_length = (
            total_description_length / metrics.total_scenes
        )
        
        # Calculate tone consistency
        metrics.tone_consistency_score = cls._calculate_tone_consistency(tones)
        
        return metrics
    
    @staticmethod
    def _is_vivid_description(description: str) -> bool:
        """
        Check if description is vivid and engaging.
        
        A vivid description should:
        - Be at least 50 words
        - Contain descriptive adjectives
        - Include specific details
        
        Args:
            description: Scene description text
            
        Returns:
            True if description is vivid
        """
        if not isinstance(description, str):
            return False
        
        # Check length
        words = description.split()
        if len(words) < 50:
            return False
        
        # Check for descriptive words (simple heuristic)
        descriptive_patterns = [
            r'\b(dark|ancient|massive|twisted|corrupted|flickering|ominous)\b',
            r'\b(gleaming|rusted|broken|shattered|blood|shadows|decay)\b',
            r'\b(echoing|silent|screaming|whispering|rumbling)\b',
        ]
        
        has_descriptive = False
        for pattern in descriptive_patterns:
            if re.search(pattern, description.lower()):
                has_descriptive = True
                break
        
        return has_descriptive
    
    @staticmethod
    def _has_dialogue(description: str, scene_data: Dict[str, Any]) -> bool:
        """
        Check if scene contains dialogue.
        
        Args:
            description: Scene description text
            scene_data: Full scene data dictionary
            
        Returns:
            True if dialogue is present
        """
        # Check for explicit dialogue field
        if scene_data.get('dialogue'):
            return True
        
        if not isinstance(description, str):
            return False
        
        # Check for dialogue markers
        dialogue_markers = ['"', "'", ':', 'says', 'said', 'asks', 'asked']
        
        # Look for quoted text
        if '"' in description or "'" in description:
            return True
        
        # Look for dialogue keywords
        for marker in dialogue_markers:
            if marker in description.lower():
                return True
        
        return False
    
    @staticmethod
    def _has_sensory_details(description: str) -> bool:
        """
        Check if description includes sensory details.
        
        Args:
            description: Scene description text
            
        Returns:
            True if sensory details are present
        """
        if not isinstance(description, str):
            return False
        
        # Sensory detail patterns
        sensory_patterns = [
            # Visual
            r'\b(see|sees|saw|look|looks|glimpse|observe|witness)\b',
            r'\b(dark|bright|dim|glowing|shadowy|lit)\b',
            # Auditory
            r'\b(hear|hears|heard|sound|noise|echo|silence)\b',
            r'\b(loud|quiet|whisper|scream|rumble)\b',
            # Tactile
            r'\b(feel|feels|felt|touch|cold|hot|warm)\b',
            # Olfactory
            r'\b(smell|smells|stench|odor|scent)\b',
            # Other
            r'\b(taste|atmosphere|sense)\b',
        ]
        
        desc_lower = description.lower()
        matches = sum(1 for pattern in sensory_patterns if re.search(pattern, desc_lower))
        
        # At least 2 different sensory references
        return matches >= 2
    
    @staticmethod
    def _calculate_tone_consistency(tones: List[str]) -> float:
        """
        Calculate tone consistency score.
        
        Args:
            tones: List of tone descriptors from scenes
            
        Returns:
            Score from 0.0 to 10.0
        """
        if not tones:
            return 5.0  # Neutral score if no tones defined
        
        # Count unique tones
        unique_tones = set(tone.lower() for tone in tones)
        
        # More consistency = fewer unique tones relative to total
        # Perfect consistency would be 1 unique tone
        consistency_ratio = 1.0 - ((len(unique_tones) - 1) / max(len(tones), 1))
        
        return consistency_ratio * 10.0
    
    def passes_threshold(self) -> bool:
        """
        Check if the scene metrics pass all quality thresholds.
        
        Returns:
            True if all thresholds are met, False otherwise
        """
        vivid_percentage = 0.0
        if self.total_scenes > 0:
            vivid_percentage = (
                self.scenes_with_vivid_descriptions / self.total_scenes
            ) * 100.0
        
        return (
            self.total_scenes >= self.min_scenes and
            self.average_description_length >= self.min_description_length and
            vivid_percentage >= self.min_vivid_percentage
        )
    
    def get_failures(self) -> List[str]:
        """
        Get list of failed quality checks.
        
        Returns:
            List of failure messages for metrics that don't meet thresholds
        """
        failures = []
        
        if self.total_scenes < self.min_scenes:
            failures.append(
                f"Insufficient scenes: {self.total_scenes} "
                f"(minimum: {self.min_scenes})"
            )
        
        if self.average_description_length < self.min_description_length:
            failures.append(
                f"Descriptions too short: avg {self.average_description_length:.0f} words "
                f"(minimum: {self.min_description_length})"
            )
        
        vivid_percentage = 0.0
        if self.total_scenes > 0:
            vivid_percentage = (
                self.scenes_with_vivid_descriptions / self.total_scenes
            ) * 100.0
        
        if vivid_percentage < self.min_vivid_percentage:
            failures.append(
                f"Too few vivid descriptions: {vivid_percentage:.1f}% "
                f"(minimum: {self.min_vivid_percentage}%)"
            )
        
        # Warnings
        if self.total_scenes > 0:
            dialogue_percentage = (
                self.scenes_with_dialogue / self.total_scenes
            ) * 100.0
            if dialogue_percentage < 30.0:
                failures.append(
                    f"Warning: Only {dialogue_percentage:.1f}% of scenes "
                    f"contain dialogue"
                )
        
        return failures
    
    def get_score(self) -> float:
        """
        Calculate overall quality score (0.0 to 10.0).
        
        Returns:
            Quality score based on met criteria
        """
        score = 0.0
        
        # Minimum scenes (2 points)
        if self.total_scenes >= self.min_scenes:
            score += 2.0
        elif self.total_scenes > 0:
            score += 2.0 * (self.total_scenes / self.min_scenes)
        
        # Description length (2 points)
        if self.average_description_length >= self.min_description_length:
            score += 2.0
        elif self.average_description_length > 0:
            score += 2.0 * (self.average_description_length / self.min_description_length)
        
        # Vivid descriptions (3 points)
        if self.total_scenes > 0:
            vivid_percentage = (
                self.scenes_with_vivid_descriptions / self.total_scenes
            ) * 100.0
            score += 3.0 * (vivid_percentage / 100.0)
        
        # Dialogue (1 point)
        if self.total_scenes > 0:
            dialogue_percentage = (
                self.scenes_with_dialogue / self.total_scenes
            ) * 100.0
            score += 1.0 * (dialogue_percentage / 100.0)
        
        # Tone consistency (1 point)
        score += self.tone_consistency_score / 10.0
        
        # Sensory details (1 point)
        if self.has_sensory_details:
            score += 1.0
        
        return min(score, 10.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metrics to dictionary for serialization.
        
        Returns:
            Dictionary representation of metrics
        """
        return {
            'total_scenes': self.total_scenes,
            'scenes_with_vivid_descriptions': self.scenes_with_vivid_descriptions,
            'scenes_with_dialogue': self.scenes_with_dialogue,
            'average_description_length': round(self.average_description_length, 1),
            'tone_consistency_score': round(self.tone_consistency_score, 2),
            'has_sensory_details': self.has_sensory_details,
            'passes_threshold': self.passes_threshold(),
            'score': self.get_score(),
            'failures': self.get_failures(),
        }
