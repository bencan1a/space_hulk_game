# CrewAI Progress Monitoring Specification

**Version**: 1.0
**Created**: 2025-11-12
**Status**: Implementation Ready
**Risk Level**: High (Task 3.2)
**Purpose**: Define non-invasive progress monitoring for CrewAI agent execution

---

## Problem Statement

The web interface needs real-time progress updates during 5-10 minute story generation, but:

- **Cannot modify `src/space_hulk_game/crew.py`** (design constraint)
- **No built-in progress API** in CrewAI framework
- **User experience requires** visible progress (not just spinner)
- **WebSocket updates needed** to show which agent is working

**Goal**: Monitor CrewAI execution and provide progress updates to users without modifying existing code.

---

## Approach Evaluation

### Option A: File System Watching ⭐ **REJECTED**

**Mechanism**: Monitor `game-config/` directory for JSON file creation.

**How it works**:

```python
import watchdog.observers as observers

def watch_game_config():
    # Watch for file creation events
    # plot_outline.json → 20% progress
    # narrative_map.json → 40% progress
    # puzzle_design.json → 60% progress
    # scene_texts.json → 80% progress
    # prd_document.json → 100% progress
```

**Pros**:

- ✅ Non-invasive (no code changes)
- ✅ Works with existing CrewAI output
- ✅ Real progress (actual file creation)

**Cons**:

- ❌ Doesn't capture intermediate agent work (only file outputs)
- ❌ Polling/watching overhead
- ❌ File creation order may vary
- ❌ No visibility into why agent is taking long

**Verdict**: Too coarse-grained, misses most of the generation process.

---

### Option B: Log Parsing ⭐ **REJECTED**

**Mechanism**: Capture stdout/stderr from CrewAI, parse for agent names and task completions.

**How it works**:

```python
import subprocess
import re

proc = subprocess.Popen(['crewai', 'run'], stdout=subprocess.PIPE)
for line in proc.stdout:
    if re.search(r'Agent: (\w+)', line):
        # Detected agent start
        broadcast_progress(agent_name, percent)
```

**Pros**:

- ✅ Non-invasive
- ✅ More granular than file watching
- ✅ Can detect agent transitions

**Cons**:

- ❌ Fragile (log format may change)
- ❌ Complex regex parsing
- ❌ CrewAI logging may not be verbose enough
- ❌ No progress within agent execution

**Verdict**: Too fragile, relies on undocumented log format.

---

### Option C: Time-Based Estimation ⭐ **REJECTED**

**Mechanism**: Use hardcoded time estimates per agent, update progress based on elapsed time.

**How it works**:

```python
AGENT_TIME_ESTIMATES = {
    'PlotMaster': (0, 20, 120),  # (start%, end%, seconds)
    'NarrativeArchitect': (20, 40, 90),
    'PuzzleSmith': (40, 60, 100),
    'CreativeScribe': (60, 85, 80),
    'MechanicsGuru': (85, 100, 60)
}

def estimate_progress(start_time, current_time):
    elapsed = current_time - start_time
    # Calculate which agent should be running
    # Return estimated progress
```

**Pros**:

- ✅ Simple implementation
- ✅ Smooth progress bar
- ✅ Non-invasive

**Cons**:

- ❌ Inaccurate (actual times vary widely)
- ❌ Users see "99%" for minutes if agent takes longer
- ❌ No real feedback (just estimates)
- ❌ Doesn't help debug slow generations

**Verdict**: Poor user experience, misleading progress.

---

### Option D: Hybrid Approach (Time + File Detection) ⭐⭐ **CONSIDERED**

**Mechanism**: Combine time-based estimates with file detection for validation.

**How it works**:

1. Start with time-based progress (smooth updates)
2. When file appears, adjust estimate and jump to actual progress
3. Learn from historical data to improve estimates

**Pros**:

- ✅ Smooth progress updates (time-based)
- ✅ Accurate milestones (file detection)
- ✅ Adaptive (learns from history)

**Cons**:

- ⚠️ More complex implementation
- ⚠️ Still coarse-grained between files
- ⚠️ Requires historical timing data

**Verdict**: Better than A/B/C but still has gaps.

---

### Option E: Wrapper with Thread Monitoring ⭐⭐⭐⭐⭐ **CHOSEN**

**Mechanism**: Execute CrewAI in separate thread, monitor both file creation AND crew execution stages.

**How it works**:

```python
import threading
import time
from pathlib import Path

class CrewAIMonitor:
    def __init__(self, game_config_dir, websocket_manager):
        self.game_config_dir = Path(game_config_dir)
        self.ws_manager = websocket_manager
        self.agents = ['PlotMaster', 'NarrativeArchitect', 'PuzzleSmith',
                      'CreativeScribe', 'MechanicsGuru']
        self.files_expected = ['plot_outline.json', 'narrative_map.json',
                              'puzzle_design.json', 'scene_texts.json',
                              'prd_document.json']

    def execute_with_monitoring(self, crew_instance, inputs):
        # Start crew execution in thread
        result = None
        error = None

        def run_crew():
            nonlocal result, error
            try:
                result = crew_instance.crew().kickoff(inputs=inputs)
            except Exception as e:
                error = e

        crew_thread = threading.Thread(target=run_crew)
        crew_thread.start()

        # Monitor progress in main thread
        self._monitor_progress(crew_thread)

        crew_thread.join(timeout=900)  # 15 minute timeout

        if crew_thread.is_alive():
            raise TimeoutError("Generation exceeded 15 minutes")

        if error:
            raise error

        return result

    def _monitor_progress(self, crew_thread):
        start_time = time.time()
        files_found = []
        current_agent_idx = 0

        while crew_thread.is_alive():
            elapsed = time.time() - start_time

            # Check for new files (real progress)
            new_files = [f for f in self.files_expected
                        if (self.game_config_dir / f).exists()
                        and f not in files_found]

            if new_files:
                files_found.extend(new_files)
                current_agent_idx = len(files_found)
                # File detected = agent completed
                self._broadcast_milestone(
                    agent=self.agents[current_agent_idx - 1],
                    progress=current_agent_idx * 20,
                    status='completed'
                )

            # Estimate within-agent progress
            if current_agent_idx < len(self.agents):
                agent_name = self.agents[current_agent_idx]
                base_progress = current_agent_idx * 20

                # Time-based estimate for current agent
                agent_elapsed = elapsed - (current_agent_idx * 100)  # avg 100s per agent
                agent_progress = min(18, int((agent_elapsed / 100) * 18))

                self._broadcast_progress(
                    agent=agent_name,
                    progress=base_progress + agent_progress,
                    status='in_progress',
                    message=f"Running {agent_name} agent..."
                )

            time.sleep(2)  # Update every 2 seconds

        # Final 100% on completion
        if not crew_thread.is_alive() and not error:
            self._broadcast_progress(
                agent='Complete',
                progress=100,
                status='completed',
                message="Story generation complete!"
            )
```

**Pros**:

- ✅ Non-invasive (wraps crew.kickoff(), no crew.py changes)
- ✅ Real progress (file detection validates completion)
- ✅ Smooth updates (time-based estimates between files)
- ✅ Timeout handling (15 minute maximum)
- ✅ Error detection (exceptions captured)
- ✅ Granular updates (every 2 seconds)

**Cons**:

- ⚠️ Still estimates within-agent progress (acceptable trade-off)
- ⚠️ Requires thread management (standard Python, not complex)

**Verdict**: ✅ **CHOSEN** - Best balance of accuracy, non-invasiveness, and user experience.

---

## Implementation Specification

### Progress Milestones

| Milestone | Trigger | Progress % | Agent | Status |
|-----------|---------|------------|-------|--------|
| **Generation Started** | Thread starts | 0% | PlotMaster | queued |
| **PlotMaster Running** | No file yet, elapsed < 2 min | 0-18% | PlotMaster | in_progress |
| **Plot Created** | plot_outline.json exists | 20% | PlotMaster | completed |
| **NarrativeArchitect Running** | No narrative file, elapsed < 4 min | 20-38% | NarrativeArchitect | in_progress |
| **Narrative Created** | narrative_map.json exists | 40% | NarrativeArchitect | completed |
| **PuzzleSmith Running** | No puzzle file, elapsed < 6 min | 40-58% | PuzzleSmith | in_progress |
| **Puzzles Created** | puzzle_design.json exists | 60% | PuzzleSmith | completed |
| **CreativeScribe Running** | No scene file, elapsed < 8 min | 60-83% | CreativeScribe | in_progress |
| **Scenes Created** | scene_texts.json exists | 85% | CreativeScribe | completed |
| **MechanicsGuru Running** | No PRD file, elapsed < 10 min | 85-98% | MechanicsGuru | in_progress |
| **Documentation Created** | prd_document.json exists | 100% | MechanicsGuru | completed |

### WebSocket Message Format

**In Progress**:

```json
{
  "type": "progress",
  "generation_job_id": "uuid",
  "status": "in_progress",
  "progress_percent": 35,
  "current_agent": "NarrativeArchitect",
  "message": "Running NarrativeArchitect agent...",
  "elapsed_seconds": 210,
  "estimated_remaining_seconds": 90,
  "timestamp": "2025-11-12T10:03:30Z"
}
```

**Milestone Completed**:

```json
{
  "type": "milestone",
  "generation_job_id": "uuid",
  "agent": "PlotMaster",
  "progress_percent": 20,
  "message": "Plot outline created",
  "timestamp": "2025-11-12T10:02:00Z"
}
```

**Generation Complete**:

```json
{
  "type": "complete",
  "generation_job_id": "uuid",
  "story_id": "uuid",
  "progress_percent": 100,
  "total_time_seconds": 420,
  "timestamp": "2025-11-12T10:07:00Z"
}
```

**Error**:

```json
{
  "type": "error",
  "generation_job_id": "uuid",
  "error": {
    "code": "GENERATION_TIMEOUT",
    "message": "Generation exceeded 15 minute timeout",
    "user_message": "Story generation is taking longer than expected. Please try again.",
    "agent": "PuzzleSmith",
    "progress_percent": 58
  },
  "timestamp": "2025-11-12T10:15:00Z"
}
```

---

## Error Handling

### Timeout (15 minutes)

```python
if elapsed > 900:  # 15 minutes
    self._broadcast_error(
        code='GENERATION_TIMEOUT',
        message=f'Generation timed out after 15 minutes at {current_agent}',
        user_message='Story generation is taking longer than expected. Please try again.',
        agent=current_agent,
        progress=current_progress
    )
    # Terminate thread forcefully
    crew_thread._stop()  # Not recommended, but necessary
    raise TimeoutError("Generation timeout")
```

**Recovery**: User can retry generation. System logs timeout for analysis.

### Agent Failure (Exception)

```python
try:
    result = crew_instance.crew().kickoff(inputs=inputs)
except Exception as e:
    self._broadcast_error(
        code='GENERATION_AGENT_FAILED',
        message=f'Agent {current_agent} failed: {str(e)}',
        user_message='An AI agent encountered an error. Please try again.',
        agent=current_agent,
        progress=current_progress
    )
    raise
```

**Recovery**: System retries up to 1 time. If still fails, user notified with option to retry manually.

### Incomplete Generation (Missing Files)

```python
expected_files = len(self.files_expected)
actual_files = len(files_found)

if actual_files < expected_files and not crew_thread.is_alive():
    self._broadcast_error(
        code='GENERATION_INCOMPLETE',
        message=f'Only {actual_files}/{expected_files} agents completed',
        user_message='Story generation was incomplete. Some content may be missing.',
        progress=actual_files * 20
    )
```

**Recovery**: User can iterate to fill in missing content.

---

## Testing Strategy

### Unit Tests

```python
def test_monitor_detects_file_creation():
    monitor = CrewAIMonitor('/tmp/test', mock_ws)
    # Create plot_outline.json
    Path('/tmp/test/plot_outline.json').touch()
    # Monitor should broadcast 20% progress
    monitor._check_files()
    assert mock_ws.last_message['progress_percent'] == 20

def test_monitor_handles_timeout():
    monitor = CrewAIMonitor('/tmp/test', mock_ws)
    # Mock thread that never completes
    with pytest.raises(TimeoutError):
        monitor.execute_with_monitoring(mock_crew, inputs)

def test_monitor_reports_agent_failure():
    monitor = CrewAIMonitor('/tmp/test', mock_ws)
    # Mock crew that raises exception
    crew = Mock(side_effect=ValueError("Agent failed"))
    with pytest.raises(ValueError):
        monitor.execute_with_monitoring(crew, inputs)
    # Should have broadcast error
    assert mock_ws.last_message['type'] == 'error'
```

### Integration Tests

```python
def test_full_generation_with_monitoring(test_db):
    # Start real generation with monitoring
    job_id = generation_service.start_generation(prompt="Test")

    # Monitor WebSocket messages
    messages = []
    async def collect_messages():
        async for msg in websocket:
            messages.append(msg)
            if msg['type'] == 'complete':
                break

    # Should receive progress updates
    assert len(messages) > 10  # At least 10 updates
    # Should end at 100%
    assert messages[-1]['progress_percent'] == 100
```

### Manual Testing

1. **Normal Generation**: Verify progress updates every 2 seconds, files correlate with milestones
2. **Slow Generation**: Verify progress doesn't get stuck at 99%, continues updating
3. **Failed Generation**: Verify error message displayed, retry option available
4. **Timeout**: Set timeout to 1 minute, verify timeout error after 1 minute
5. **WebSocket Disconnect**: Disconnect client mid-generation, reconnect, verify progress resumed

---

## Performance Considerations

### Monitoring Overhead

- **File system checks**: 5 checks per poll (0.1ms each) = 0.5ms
- **Broadcast latency**: ~1ms per WebSocket message
- **Poll frequency**: Every 2 seconds
- **Total overhead**: < 2ms every 2 seconds = **negligible**

### Thread Safety

- CrewAI execution in separate thread (non-blocking)
- File system checks thread-safe (read-only)
- WebSocket broadcasts async (non-blocking)
- No shared mutable state between threads

---

## Code Location

**File**: `backend/app/integrations/crewai_monitor.py`

**Integration Point**:

```python
# backend/app/services/generation_service.py
from app.integrations.crewai_monitor import CrewAIMonitor

def execute_generation(job_id, prompt, feedback=None):
    monitor = CrewAIMonitor(
        game_config_dir=f'./game-config',
        websocket_manager=get_ws_manager(),
        job_id=job_id
    )

    crew_instance = SpaceHulkGame()
    inputs = {"prompt": prompt}
    if feedback:
        inputs["feedback"] = feedback

    try:
        result = monitor.execute_with_monitoring(crew_instance, inputs)
        return result
    except TimeoutError:
        # Handle timeout
        raise GenerationTimeoutError(f"Generation {job_id} timed out")
    except Exception as e:
        # Handle other errors
        raise GenerationError(f"Generation {job_id} failed: {str(e)}")
```

---

## Success Criteria

- [ ] Progress updates broadcast every 2 seconds via WebSocket
- [ ] File creation detected and triggers milestone updates
- [ ] Progress smoothly increases (no jumps backward)
- [ ] 15 minute timeout enforced and reported
- [ ] Agent failures detected and reported with helpful messages
- [ ] No modifications to `src/space_hulk_game/crew.py`
- [ ] Unit test coverage > 90%
- [ ] Manual testing confirms good user experience

---

## Future Enhancements

**Phase 2 (If needed)**:

1. **Historical Learning**: Track actual agent times, adjust estimates
2. **Parallel Agent Detection**: If CrewAI runs agents in parallel (future), detect concurrency
3. **Detailed Sub-Tasks**: If agents log sub-tasks, parse for finer progress
4. **Agent Health Checks**: Detect hung agents (no file changes for > 5 minutes)

**Phase 3 (If needed)**:

1. **Progress Prediction ML**: Train model to predict completion time based on prompt length
2. **Incremental Output**: If agents write partial JSON, parse for real-time progress

---

**This specification provides a non-invasive, user-friendly progress monitoring solution for CrewAI generation, addressing the high-risk Task 3.2 with a clear implementation path.**

**Status**: ✅ Ready for Implementation
**Estimated Effort**: 3 days (as planned in IMPLEMENTATION_PLAN.md Task 3.2)
