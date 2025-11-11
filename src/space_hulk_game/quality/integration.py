"""
Integration helpers for quality checking in CrewAI tasks.

This module provides utilities to integrate quality checking and retry logic
into the CrewAI task execution workflow.
"""

import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from .retry import TaskType, execute_with_quality_check

logger = logging.getLogger(__name__)


class QualityCheckConfig:
    """
    Configuration for quality checking system.

    Loads configuration from quality_config.yaml and environment variables.
    """

    def __init__(self, config_path: str | None = None):
        """
        Initialize quality check configuration.

        Args:
            config_path: Path to quality_config.yaml (optional)
        """
        self.config = self._load_config(config_path)
        self.task_configs = self._create_task_configs()

    def _load_config(self, config_path: str | Path | None = None) -> dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config file (optional)

        Returns:
            Configuration dictionary
        """
        if config_path is None:
            # Default path relative to this module
            module_dir = Path(__file__).parent.parent
            config_path = module_dir / "config" / "quality_config.yaml"

        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded quality configuration from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Quality config file not found: {config_path}, using defaults")
            return self._default_config()
        except Exception as e:
            logger.error(f"Error loading quality config: {e}, using defaults")
            return self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """
        Get default configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            "global": {"enabled": False, "log_level": "INFO", "verbose_logging": True},
            "thresholds": {
                "plot": {"enabled": True, "pass_threshold": 6.0, "max_retries": 3},
                "narrative": {"enabled": True, "pass_threshold": 6.0, "max_retries": 3},
                "puzzle": {"enabled": True, "pass_threshold": 6.0, "max_retries": 3},
                "scene": {"enabled": True, "pass_threshold": 6.0, "max_retries": 3},
                "mechanics": {"enabled": True, "pass_threshold": 6.0, "max_retries": 3},
            },
            "retry": {"provide_feedback": True, "fail_on_evaluation_error": False},
        }

    def _create_task_configs(self) -> dict[TaskType, dict[str, Any]]:
        """
        Create task configuration dictionary from loaded config.

        Returns:
            Dictionary mapping task types to their configurations
        """
        thresholds = self.config.get("thresholds", {})

        # Map YAML keys to TaskType enum
        task_map = {
            "plot": TaskType.PLOT,
            "narrative": TaskType.NARRATIVE,
            "puzzle": TaskType.PUZZLE,
            "scene": TaskType.SCENE,
            "mechanics": TaskType.MECHANICS,
        }

        configs = {}
        for yaml_key, task_type in task_map.items():
            threshold_config = thresholds.get(yaml_key, {})
            configs[task_type] = {
                "enabled": threshold_config.get("enabled", True),
                "pass_threshold": self._get_env_override(
                    f"QUALITY_{yaml_key.upper()}_THRESHOLD",
                    threshold_config.get("pass_threshold", 6.0),
                ),
                "max_retries": self._get_env_override(
                    "QUALITY_MAX_RETRIES", threshold_config.get("max_retries", 3)
                ),
            }

        return configs

    def _get_env_override(self, env_var: str, default: Any) -> Any:
        """
        Get environment variable override for configuration value.

        Args:
            env_var: Environment variable name
            default: Default value if not set

        Returns:
            Value from environment or default
        """
        value = os.getenv(env_var)
        if value is None:
            return default

        # Try to convert to same type as default
        if isinstance(default, bool):
            return value.lower() in ("true", "1", "yes")
        elif isinstance(default, int):
            return int(value)
        elif isinstance(default, float):
            return float(value)
        else:
            return value

    def is_enabled(self) -> bool:
        """
        Check if quality checking is globally enabled.

        Returns:
            True if quality checking is enabled
        """
        # Check environment variable first
        env_enabled = os.getenv("QUALITY_CHECK_ENABLED")
        if env_enabled is not None:
            return env_enabled.lower() in ("true", "1", "yes")

        # Check config file
        return self.config.get("global", {}).get("enabled", False)

    def get_task_config(self, task_type: TaskType) -> dict[str, Any]:
        """
        Get configuration for specific task type.

        Args:
            task_type: Type of task

        Returns:
            Configuration dictionary for the task
        """
        return self.task_configs.get(
            task_type, {"enabled": True, "pass_threshold": 6.0, "max_retries": 3}
        )


class TaskExecutor:
    """
    Task executor with optional quality checking.

    This class wraps task execution to add quality checking when enabled.
    """

    def __init__(self, config: QualityCheckConfig | None = None):
        """
        Initialize task executor.

        Args:
            config: Quality check configuration (creates default if None)
        """
        self.config = config if config is not None else QualityCheckConfig()
        logger.debug(f"TaskExecutor initialized (quality checks: {self.config.is_enabled()})")

    def execute_task(
        self,
        task_function: Callable[..., str],
        task_type: TaskType,
        task_name: str = "Task",
        **kwargs,
    ) -> str:
        """
        Execute task with optional quality checking.

        Args:
            task_function: Function to execute
            task_type: Type of task (for evaluator selection)
            task_name: Human-readable task name
            **kwargs: Arguments to pass to task function

        Returns:
            Task output string
        """
        # Check if quality checking is enabled globally and for this task
        if not self.config.is_enabled():
            logger.debug(f"{task_name}: Quality checking disabled, executing directly")
            return task_function(**kwargs)

        task_config = self.config.get_task_config(task_type)
        if not task_config.get("enabled", True):
            logger.debug(f"{task_name}: Quality checking disabled for {task_type.value}")
            return task_function(**kwargs)

        # Execute with quality checking
        logger.info(f"{task_name}: Executing with quality checks")
        output, quality, attempts = execute_with_quality_check(
            task_function=task_function,
            task_type=task_type,
            task_name=task_name,
            pass_threshold=task_config["pass_threshold"],
            max_retries=task_config["max_retries"],
            **kwargs,
        )

        # Log results
        logger.info(
            f"{task_name}: Completed in {attempts} attempt(s) "
            f"with quality score {quality.score:.1f}/10.0 "
            f"({'PASS' if quality.passed else 'FAIL'})"
        )

        return output


# Singleton instance for easy access
_default_executor: TaskExecutor | None = None


def get_default_executor() -> TaskExecutor:
    """
    Get default task executor singleton.

    Returns:
        Default TaskExecutor instance
    """
    global _default_executor
    if _default_executor is None:
        _default_executor = TaskExecutor()
    return _default_executor


def execute_with_optional_quality_check(
    task_function: Callable[..., str], task_type: TaskType, task_name: str = "Task", **kwargs
) -> str:
    """
    Convenience function to execute task with optional quality checking.

    Uses the default executor singleton.

    Args:
        task_function: Function to execute
        task_type: Type of task
        task_name: Human-readable task name
        **kwargs: Arguments to pass to task function

    Returns:
        Task output string
    """
    executor = get_default_executor()
    return executor.execute_task(task_function, task_type, task_name, **kwargs)


# Task type mapping for crew.py integration
CREW_TASK_MAPPING = {
    "GenerateOverarchingPlot": TaskType.PLOT,
    "CreateNarrativeMap": TaskType.NARRATIVE,
    "DesignArtifactsAndPuzzles": TaskType.PUZZLE,
    "WriteSceneDescriptionsAndDialogue": TaskType.SCENE,
    "CreateGameMechanicsPRD": TaskType.MECHANICS,
}


def get_task_type_for_crew_task(task_name: str) -> TaskType | None:
    """
    Get TaskType for a CrewAI task name.

    Args:
        task_name: Name of CrewAI task

    Returns:
        TaskType if mapping exists, None otherwise
    """
    return CREW_TASK_MAPPING.get(task_name)
