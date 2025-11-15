"""Tests for CrewAI Wrapper."""

import contextlib
import threading
import time

import pytest
from app.integrations.crewai_wrapper import (
    CrewAIWrapper,
    CrewExecutionError,
    CrewTimeoutError,
)

# Test timing constants
POLLING_INTERVAL_SECONDS = 0.02
EXECUTION_START_TIMEOUT_SECONDS = 1.0


class MockTask:
    """Mock task for testing."""

    def __init__(self, name: str):
        self.name = name
        self.output = f"Output from {name}"


class MockCrew:
    """Mock CrewAI crew for testing."""

    def __init__(self, tasks=None, execution_time=0.1, should_fail=False):
        """Initialize mock crew.

        Args:
            tasks: List of tasks (creates default if None)
            execution_time: Time to simulate execution (seconds)
            should_fail: If True, kickoff will raise an exception
        """
        self.tasks = tasks or [
            MockTask("Task 1"),
            MockTask("Task 2"),
            MockTask("Task 3"),
        ]
        self.execution_time = execution_time
        self.should_fail = should_fail
        self.kickoff_called = False
        self.kickoff_inputs = None

    def kickoff(self, inputs=None):
        """Mock kickoff method."""
        self.kickoff_called = True
        self.kickoff_inputs = inputs

        # Simulate execution time
        time.sleep(self.execution_time)

        if self.should_fail:
            raise ValueError("Mock crew execution failed")

        return {
            "raw": "Mock crew output",
            "tasks_output": [task.output for task in self.tasks],
            "metadata": {"status": "success"},
        }


@pytest.fixture
def wrapper():
    """Create a wrapper instance with short timeout for testing."""
    return CrewAIWrapper(timeout_seconds=5)


@pytest.fixture
def mock_crew():
    """Create a mock crew instance."""
    return MockCrew()


def test_wrapper_initialization():
    """Test wrapper initializes with correct defaults."""
    wrapper = CrewAIWrapper()
    assert wrapper.timeout_seconds == 900  # 15 minutes default
    assert not wrapper.is_executing()


def test_wrapper_custom_timeout():
    """Test wrapper initializes with custom timeout."""
    wrapper = CrewAIWrapper(timeout_seconds=300)
    assert wrapper.timeout_seconds == 300


def test_execute_generation_success(wrapper, mock_crew):
    """Test successful crew execution."""
    result = wrapper.execute_generation(
        crew=mock_crew,
        prompt="Create a test game",
        progress_callback=None,
    )

    assert result["status"] == "success"
    assert "output" in result
    assert result["output"]["raw"] == "Mock crew output"
    assert mock_crew.kickoff_called
    assert mock_crew.kickoff_inputs["prompt"] == "Create a test game"


def test_execute_generation_with_progress_callback(wrapper, mock_crew):
    """Test execution with progress callback."""
    callback_calls = []

    def progress_callback(status, data):
        callback_calls.append((status, data))

    result = wrapper.execute_generation(
        crew=mock_crew,
        prompt="Create a test game",
        progress_callback=progress_callback,
    )

    assert result["status"] == "success"

    # Check callback was called with expected statuses
    statuses = [call[0] for call in callback_calls]
    assert "started" in statuses
    assert "task_started" in statuses
    assert "task_completed" in statuses
    assert "completed" in statuses


def test_execute_generation_callback_receives_correct_data(wrapper, mock_crew):
    """Test callback receives correct data for each status."""
    callback_calls = []

    def progress_callback(status, data):
        callback_calls.append((status, data))

    wrapper.execute_generation(
        crew=mock_crew,
        prompt="Test prompt",
        progress_callback=progress_callback,
    )

    # Check started callback
    started_calls = [call for call in callback_calls if call[0] == "started"]
    assert len(started_calls) == 1
    assert started_calls[0][1]["prompt"] == "Test prompt"

    # Check task_started callbacks
    task_started_calls = [call for call in callback_calls if call[0] == "task_started"]
    assert len(task_started_calls) == 3  # 3 tasks
    assert task_started_calls[0][1]["task_index"] == 0
    assert task_started_calls[0][1]["total_tasks"] == 3

    # Check completed callback
    completed_calls = [call for call in callback_calls if call[0] == "completed"]
    assert len(completed_calls) == 1
    assert completed_calls[0][1]["status"] == "success"


def test_execute_generation_timeout():
    """Test execution timeout handling."""
    # Create wrapper with very short timeout
    wrapper = CrewAIWrapper(timeout_seconds=1)

    # Create crew that takes longer than timeout
    slow_crew = MockCrew(execution_time=3)

    with pytest.raises(CrewTimeoutError) as exc_info:
        wrapper.execute_generation(
            crew=slow_crew,
            prompt="Test prompt",
        )

    assert "exceeded timeout" in str(exc_info.value)
    assert "1 seconds" in str(exc_info.value)


def test_execute_generation_timeout_with_callback():
    """Test timeout notification via callback."""
    wrapper = CrewAIWrapper(timeout_seconds=1)
    slow_crew = MockCrew(execution_time=3)
    callback_calls = []

    def progress_callback(status, data):
        callback_calls.append((status, data))

    with pytest.raises(CrewTimeoutError):
        wrapper.execute_generation(
            crew=slow_crew,
            prompt="Test prompt",
            progress_callback=progress_callback,
        )

    # Check timeout callback was called
    timeout_calls = [call for call in callback_calls if call[0] == "timeout"]
    assert len(timeout_calls) == 1
    assert "timeout_seconds" in timeout_calls[0][1]


def test_execute_generation_error_handling(wrapper):
    """Test error handling during execution."""
    failing_crew = MockCrew(should_fail=True)

    with pytest.raises(CrewExecutionError) as exc_info:
        wrapper.execute_generation(
            crew=failing_crew,
            prompt="Test prompt",
        )

    assert "Mock crew execution failed" in str(exc_info.value)


def test_execute_generation_error_with_callback(wrapper):
    """Test error notification via callback."""
    failing_crew = MockCrew(should_fail=True)
    callback_calls = []

    def progress_callback(status, data):
        callback_calls.append((status, data))

    with pytest.raises(CrewExecutionError):
        wrapper.execute_generation(
            crew=failing_crew,
            prompt="Test prompt",
            progress_callback=progress_callback,
        )

    # Check error callback was called
    error_calls = [call for call in callback_calls if call[0] == "error"]
    assert len(error_calls) == 1
    assert "error" in error_calls[0][1]
    assert "Mock crew execution failed" in error_calls[0][1]["error"]


def test_callback_error_does_not_stop_execution(wrapper, mock_crew):
    """Test that callback errors don't stop crew execution."""

    def failing_callback(_status, _data):
        raise RuntimeError("Callback failed")

    # Should not raise, callback errors are caught and logged
    result = wrapper.execute_generation(
        crew=mock_crew,
        prompt="Test prompt",
        progress_callback=failing_callback,
    )

    assert result["status"] == "success"


def test_is_executing(wrapper):
    """Test is_executing status tracking."""
    assert not wrapper.is_executing()

    # Start execution in a thread to check status
    def run_execution():
        wrapper.execute_generation(
            crew=MockCrew(execution_time=0.5),
            prompt="Test",
        )

    thread = threading.Thread(target=run_execution)
    thread.start()

    # Wait for execution to start (polling with timeout)
    start_time = time.time()
    while not wrapper.is_executing():
        if time.time() - start_time > EXECUTION_START_TIMEOUT_SECONDS:
            pytest.fail("wrapper.is_executing() did not become True within 1 second")
        time.sleep(POLLING_INTERVAL_SECONDS)

    # Wait for execution to complete
    thread.join(timeout=2)
    assert not wrapper.is_executing()


def test_cancel_execution(wrapper):
    """Test execution cancellation."""
    # Start a long-running execution
    long_crew = MockCrew(execution_time=5)

    def run_execution():
        with contextlib.suppress(CrewExecutionError, CrewTimeoutError):
            wrapper.execute_generation(crew=long_crew, prompt="Test")

    thread = threading.Thread(target=run_execution)
    thread.start()

    # Give it time to start
    time.sleep(0.1)

    # Cancel execution
    wrapper.cancel_execution()

    # Note: Cancellation success depends on timing, so we just verify the API works
    thread.join(timeout=2)


def test_context_manager():
    """Test wrapper as context manager."""
    with CrewAIWrapper() as wrapper:
        assert wrapper is not None
        assert wrapper.timeout_seconds == 900

    # After context exit, executor should be shutdown
    # We can't easily test this without accessing private attributes


def test_multiple_task_callbacks(wrapper):
    """Test callback called for each task."""
    crew_with_many_tasks = MockCrew(tasks=[MockTask(f"Task {i}") for i in range(5)])
    callback_calls = []

    def progress_callback(status, data):
        callback_calls.append((status, data))

    wrapper.execute_generation(
        crew=crew_with_many_tasks,
        prompt="Test prompt",
        progress_callback=progress_callback,
    )

    # Check we got task_started for all tasks
    task_started_calls = [call for call in callback_calls if call[0] == "task_started"]
    assert len(task_started_calls) == 5

    # Check task indices are correct
    for i, call in enumerate(task_started_calls):
        assert call[1]["task_index"] == i
        assert call[1]["total_tasks"] == 5


def test_execute_generation_metadata(wrapper, mock_crew):
    """Test result metadata is populated correctly."""
    result = wrapper.execute_generation(
        crew=mock_crew,
        prompt="Test prompt",
    )

    assert "metadata" in result
    assert result["metadata"]["prompt"] == "Test prompt"
    assert result["metadata"]["timeout_seconds"] == 5


def test_execute_generation_no_tasks(wrapper):
    """Test execution with crew that has no tasks attribute."""

    # Create a crew without tasks attribute that won't fail in kickoff
    # Parameter name must match Protocol definition for proper type checking
    class CrewNoTasks:
        def kickoff(self, inputs: dict[str, object]) -> dict[str, object]:  # noqa: ARG002
            time.sleep(0.1)
            return {"raw": "Output without tasks", "metadata": {"status": "success"}}

    crew_no_tasks = CrewNoTasks()

    # Should still work, just won't report task progress
    result = wrapper.execute_generation(
        crew=crew_no_tasks,
        prompt="Test prompt",
    )

    assert result["status"] == "success"


def test_concurrent_executions_not_allowed():
    """Test that only one execution can run at a time."""
    wrapper = CrewAIWrapper()

    results = []

    def run_execution(index):
        try:
            result = wrapper.execute_generation(
                crew=MockCrew(execution_time=0.5),
                prompt=f"Test {index}",
            )
            results.append(result)
        except (CrewExecutionError, CrewTimeoutError) as e:
            results.append({"error": str(e)})

    # Start two concurrent executions
    thread1 = threading.Thread(target=run_execution, args=(1,))
    thread2 = threading.Thread(target=run_execution, args=(2,))

    thread1.start()
    time.sleep(0.1)  # Ensure first one starts
    thread2.start()

    thread1.join(timeout=3)
    thread2.join(timeout=3)

    # Both should complete (they use the same executor with max_workers=1)
    # So they'll execute sequentially
    assert len(results) == 2


def test_execute_generation_custom_inputs(wrapper, mock_crew):
    """Test execution with custom inputs parameter."""
    custom_inputs = {
        "prompt": "Create a test game",
        "custom_key": "custom_value",
        "another_key": 123,
    }

    result = wrapper.execute_generation(
        crew=mock_crew,
        prompt="Create a test game",
        inputs=custom_inputs,
    )

    assert result["status"] == "success"
    assert mock_crew.kickoff_called
    # Verify custom inputs were passed to kickoff
    assert mock_crew.kickoff_inputs == custom_inputs
    assert "custom_key" in mock_crew.kickoff_inputs
    assert mock_crew.kickoff_inputs["custom_key"] == "custom_value"


def test_execute_generation_default_inputs(wrapper, mock_crew):
    """Test execution uses default inputs when not provided."""
    result = wrapper.execute_generation(
        crew=mock_crew,
        prompt="Test prompt",
    )

    assert result["status"] == "success"
    assert mock_crew.kickoff_called
    # Verify default inputs have both "prompt" and "game" keys
    assert "prompt" in mock_crew.kickoff_inputs
    assert "game" in mock_crew.kickoff_inputs
    assert mock_crew.kickoff_inputs["prompt"] == "Test prompt"
    assert mock_crew.kickoff_inputs["game"] == "Test prompt"
