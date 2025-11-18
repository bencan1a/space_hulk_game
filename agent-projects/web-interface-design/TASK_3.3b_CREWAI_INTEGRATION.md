# Task 3.3b: CrewAI Integration in Generation Task

**Priority**: P0
**Effort**: 1 day
**Dependencies**: Task 3.2 (CrewAI Wrapper - Complete), Task 3.3 (Generation Service - Complete)

---

## Context

The generation pipeline infrastructure is complete: `CrewAIWrapper` exists with timeout/progress support, `GenerationService` manages sessions, and the Celery task `run_generation_crew` handles async execution. However, the task currently uses a **simulation** instead of the actual CrewAI crew.

The existing `SpaceHulkGame` crew in `src/space_hulk_game/crew.py` generates game content via multiple AI agents. This task connects that crew to the web interface generation pipeline.

**Project Documentation**:

- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 3.2, Task 3.3
- CrewAI Wrapper: `backend/app/integrations/crewai_wrapper.py`
- Generation Task: `backend/app/tasks/generation_tasks.py` (lines 158-225 contain TODO and simulation)
- Existing Crew: `src/space_hulk_game/crew.py`

---

## Your Mission

Replace the simulation code in `run_generation_crew` Celery task with actual CrewAI execution using the `CrewAIWrapper`. The crew generates game content that must be parsed into the expected `game.json` format.

---

## Deliverables

```
backend/
└── app/
    └── tasks/
        └── generation_tasks.py  # Updated with real CrewAI integration
```

No new files required - this is an update to existing code.

---

## Implementation Steps

### 1. Import the Crew

Add import for the existing SpaceHulkGame crew:

```python
from src.space_hulk_game.crew import SpaceHulkGame
```

Note: You may need to adjust Python path or use relative imports depending on how the backend is structured.

### 2. Replace Simulation with Real Execution

In `run_generation_crew` task (around line 158-225), replace the simulation code with:

```python
# Create crew instance
crew_instance = SpaceHulkGame()
crew = crew_instance.crew()

# Create wrapper with timeout
wrapper = CrewAIWrapper(timeout_seconds=840)  # 14 minutes

# Execute with progress callback
result = wrapper.execute_generation(
    crew=crew,
    prompt=prompt,
    progress_callback=progress_callback,
)

# Extract output from crew result
game_data = result.get("output", {})
```

### 3. Parse Crew Output to game.json Format

The crew output may not match the expected `game.json` structure. You need to:

1. Examine what the crew actually outputs (check `game-config/` for templates)
2. Transform the crew output into the expected format:

```python
game_data = {
    "metadata": {
        "title": extracted_title,
        "description": extracted_description,
        "theme": "warhammer40k",
        "difficulty": "medium",
        "estimated_duration": "30-45 minutes",
    },
    "scenes": [...],
    "items": [...],
    "npcs": [...],
    "puzzles": [...],
}
```

### 4. Handle Edge Cases

- If crew output is a string (raw text), parse it
- If crew output is CrewOutput object, extract the relevant data
- Handle missing fields with sensible defaults
- Log warnings for unexpected output formats

---

## Acceptance Criteria

- [ ] Simulation code removed from `run_generation_crew`
- [ ] `SpaceHulkGame` crew is imported and instantiated
- [ ] `CrewAIWrapper.execute_generation()` is called with the crew and prompt
- [ ] Progress callback receives updates for each agent task
- [ ] Crew output is transformed into valid `game.json` format
- [ ] Story record is created with correct metadata from crew output
- [ ] Error handling for crew failures (timeout, execution errors)
- [ ] Integration test: Full generation creates playable game.json

---

## Testing Requirements

### Manual Testing

1. Start all services: `docker-compose up`
2. Navigate to Create page
3. Select a template and click "Generate Story"
4. Verify progress updates in UI
5. Check celery-worker logs for crew execution
6. Verify story appears in Library with correct metadata
7. Verify `data/stories/{session_id}/game.json` contains valid game data

### Unit Testing

```python
# tests/test_generation_tasks.py

def test_generation_task_uses_real_crew(mocker):
    """Test that generation task calls CrewAIWrapper with real crew."""
    mock_crew = mocker.patch('src.space_hulk_game.crew.SpaceHulkGame')
    mock_wrapper = mocker.patch('backend.app.integrations.crewai_wrapper.CrewAIWrapper')

    # Run task
    result = run_generation_crew(session_id, prompt, template_id)

    # Verify crew was instantiated and wrapper was used
    mock_crew.assert_called_once()
    mock_wrapper.return_value.execute_generation.assert_called_once()
```

---

## Important Notes

### Python Path Configuration

The backend runs from `/app` in Docker but needs to import from `src/space_hulk_game/`. Options:

1. Add `src/` to Python path in the Celery worker
2. Install the space_hulk_game package in the backend container
3. Use absolute imports with proper path setup

Update `docker-compose.yml` if needed:

```yaml
celery-worker:
  environment:
    - PYTHONPATH=/app:/workspaces/space_hulk_game
  volumes:
    - ../src:/workspaces/space_hulk_game/src  # Mount the crew source
```

### Crew Output Format

Check the existing crew output by:

1. Running `crewai run` in the main project
2. Examining files in `game-config/`
3. Reviewing the crew's task configurations in `src/space_hulk_game/config/tasks.yaml`

The crew may output separate files for different aspects (plot, scenes, puzzles). You'll need to consolidate these into a single `game.json`.

### LLM Configuration

Ensure the Celery worker has access to LLM API keys:

```yaml
# docker-compose.yml
celery-worker:
  environment:
    - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    # ... other LLM configs from .env
```

---

## Reference Files

- `backend/app/integrations/crewai_wrapper.py` - Wrapper implementation
- `backend/app/tasks/generation_tasks.py` - Task to modify (lines 158-225)
- `src/space_hulk_game/crew.py` - Existing crew to integrate
- `src/space_hulk_game/config/tasks.yaml` - Task definitions showing crew output
- `game-config/` - Templates showing expected output format

---

## Success Metrics

1. Generation task completes without simulation
2. Real AI-generated content appears in game.json
3. Progress updates reflect actual agent execution
4. Story metadata extracted from crew output
5. No regressions in generation flow

---

_End of Task 3.3b_
