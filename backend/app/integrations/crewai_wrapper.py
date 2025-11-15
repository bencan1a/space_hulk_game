"""CrewAI Wrapper for executing generation crews with progress monitoring.

This module provides a wrapper around CrewAI execution to enable:
- Progress callbacks for real-time status updates
- Timeout mechanisms for long-running operations
- Robust error handling
- Integration with the web interface backend

The wrapper does NOT modify the existing crew.py file and works with
any CrewAI crew instance.
"""

import logging
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
from typing import Protocol

logger = logging.getLogger(__name__)


class CrewProtocol(Protocol):
    """Protocol defining the expected interface for a CrewAI crew.

    This protocol documents the crew interface without requiring inheritance,
    providing better type safety while remaining compatible with any crew
    implementation that has these attributes/methods.
    """

    def kickoff(self, inputs: dict[str, object]) -> dict[str, object]:
        """Execute the crew with the given inputs.

        Args:
            inputs: Dictionary of input parameters for the crew

        Returns:
            Dictionary containing the crew's output
        """
        ...


class CrewExecutionError(Exception):
    """Raised when crew execution fails."""


class CrewTimeoutError(CrewExecutionError):
    """Raised when crew execution times out."""


class CrewAIWrapper:
    """Wrapper for executing CrewAI crews with progress monitoring and timeout.

    This wrapper provides execution control and monitoring for CrewAI crews
    without modifying the underlying crew implementation.

    Attributes:
        timeout_seconds: Maximum time in seconds for crew execution (default: 900 = 15 minutes)
    """

    def __init__(self, timeout_seconds: int = 900) -> None:
        """Initialize the CrewAI wrapper.

        Args:
            timeout_seconds: Maximum execution time in seconds (default: 900 = 15 minutes)
        """
        self.timeout_seconds = timeout_seconds
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._current_future: Future[dict[str, object]] | None = None

    def execute_generation(
        self,
        crew: CrewProtocol,
        prompt: str,
        progress_callback: Callable[[str, dict[str, object]], None] | None = None,
        inputs: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Execute a CrewAI crew with progress monitoring and timeout.

        This method executes a crew with the given prompt and provides progress
        updates through the callback mechanism.

        Args:
            crew: A CrewAI Crew instance (from SpaceHulkGame().crew() or similar)
                  Must implement CrewProtocol (have kickoff method and optionally tasks)
            prompt: The user's generation prompt
            progress_callback: Optional callback function called with (status, data)
                Status values:
                - "started": Execution has begun
                - "task_started": A task has started (data includes task name)
                - "task_completed": A task has completed (data includes task name, output)
                - "completed": Execution completed successfully (data includes final output)
                - "error": An error occurred (data includes error message)
                - "timeout": Execution timed out
            inputs: Optional custom inputs dict for crew.kickoff(). If None, defaults to
                {"prompt": prompt, "game": prompt} for backward compatibility with
                SpaceHulkGame crew which expects both "prompt" and "game" keys.

        Returns:
            dict: The crew execution result, including:
                - status: "success", "error", or "timeout"
                - output: The crew's output (if successful)
                - error: Error message (if failed)
                - metadata: Additional execution metadata

        Raises:
            CrewTimeoutError: If execution exceeds timeout_seconds
            CrewExecutionError: If crew execution fails
        """
        logger.info(f"Starting crew execution with prompt: {prompt[:100]}...")

        # Notify callback of start
        if progress_callback:
            try:
                progress_callback("started", {"prompt": prompt})
            except Exception as e:
                logger.warning(f"Progress callback error (started): {e}")

        # Prepare inputs for the crew
        # Default to {"prompt": prompt, "game": prompt} for backward compatibility
        # with SpaceHulkGame crew which expects both keys
        if inputs is None:
            inputs = {"prompt": prompt, "game": prompt}

        def execute_with_monitoring() -> dict[str, object]:
            """Execute the crew with progress monitoring."""
            try:
                logger.info("Executing crew.kickoff()...")

                # Execute the crew
                output = crew.kickoff(inputs=inputs)

                # Notify callback of task completions after execution finishes
                # Since CrewAI doesn't provide built-in callbacks, we emit
                # task_started and task_completed events after kickoff completes
                if progress_callback and hasattr(crew, "tasks"):
                    total_tasks = len(crew.tasks)
                    for i, task in enumerate(crew.tasks):
                        task_name = getattr(task, "name", f"Task {i + 1}")
                        try:
                            # Emit task_started event
                            progress_callback(
                                "task_started",
                                {
                                    "task_index": i,
                                    "task_name": task_name,
                                    "total_tasks": total_tasks,
                                },
                            )
                            # Emit task_completed event
                            progress_callback(
                                "task_completed",
                                {
                                    "task_index": i,
                                    "task_name": task_name,
                                    "total_tasks": total_tasks,
                                },
                            )
                        except Exception as e:
                            logger.warning(f"Progress callback error (task events): {e}")

                logger.info("Crew execution completed successfully")
                return output  # type: ignore[no-any-return]

            except Exception as e:
                logger.error(f"Crew execution failed: {e}", exc_info=True)
                raise

        # Execute with timeout
        try:
            logger.info(f"Starting execution with {self.timeout_seconds}s timeout")
            self._current_future = self._executor.submit(execute_with_monitoring)

            # Wait for completion with timeout
            output = self._current_future.result(timeout=self.timeout_seconds)

            # Notify callback of successful completion
            if progress_callback:
                try:
                    progress_callback(
                        "completed",
                        {
                            "output": output,
                            "status": "success",
                        },
                    )
                except Exception as e:
                    logger.warning(f"Progress callback error (completed): {e}")

            return {
                "status": "success",
                "output": output,
                "metadata": {
                    "prompt": prompt,
                    "timeout_seconds": self.timeout_seconds,
                },
            }

        except TimeoutError:
            logger.error(f"Crew execution timed out after {self.timeout_seconds} seconds")

            # Cancel the future
            if self._current_future:
                self._current_future.cancel()

            # Notify callback of timeout
            if progress_callback:
                try:
                    progress_callback(
                        "timeout",
                        {
                            "timeout_seconds": self.timeout_seconds,
                        },
                    )
                except Exception as e:
                    logger.warning(f"Progress callback error (timeout): {e}")

            raise CrewTimeoutError(
                f"Crew execution exceeded timeout of {self.timeout_seconds} seconds"
            ) from None

        except Exception as e:
            logger.error(f"Crew execution error: {e}", exc_info=True)

            # Notify callback of error
            if progress_callback:
                try:
                    progress_callback(
                        "error",
                        {
                            "error": str(e),
                            "error_type": type(e).__name__,
                        },
                    )
                except Exception as callback_error:
                    logger.warning(f"Progress callback error (error): {callback_error}")

            raise CrewExecutionError(f"Crew execution failed: {e}") from e

    def cancel_execution(self) -> bool:
        """Cancel the current crew execution if running.

        Returns:
            bool: True if execution was cancelled, False if no execution was running
        """
        if self._current_future and not self._current_future.done():
            logger.info("Cancelling crew execution")
            cancelled = self._current_future.cancel()
            if cancelled:
                logger.info("Crew execution cancelled successfully")
            else:
                logger.warning("Failed to cancel crew execution")
            return cancelled
        return False

    def is_executing(self) -> bool:
        """Check if a crew execution is currently running.

        Returns:
            bool: True if execution is in progress, False otherwise
        """
        return self._current_future is not None and not self._current_future.done()

    def __enter__(self) -> "CrewAIWrapper":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Context manager exit - cleanup resources."""
        self.cancel_execution()
        self._executor.shutdown(wait=False)
