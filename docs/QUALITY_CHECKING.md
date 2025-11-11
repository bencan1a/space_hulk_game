# Quality Checking Integration Guide

This guide explains how to use the quality checking and retry logic system in the Space Hulk Game project.

## Overview

The quality checking system (implemented in Phase 3, Chunk 3.3) provides:
- Automatic evaluation of generated content against quality metrics
- Retry mechanism for tasks that fail quality checks
- Specific feedback to improve outputs on each retry attempt
- Configurable thresholds and retry limits per task type

## Quick Start

### Enable Quality Checking

Quality checking is **disabled by default**. To enable it:

**Option 1: Environment Variable (Recommended for testing)**
```bash
export QUALITY_CHECK_ENABLED=true
crewai run
```

**Option 2: Configuration File**
```bash
# Edit src/space_hulk_game/config/quality_config.yaml
# Set: global.enabled: true
crewai run
```

### Configure Thresholds

Edit `src/space_hulk_game/config/quality_config.yaml` to adjust quality thresholds:

```yaml
thresholds:
  plot:
    pass_threshold: 7.0  # Increase for stricter quality (0.0-10.0)
    max_retries: 5       # Allow more retry attempts
```

Or use environment variables:
```bash
export QUALITY_PLOT_THRESHOLD=7.0
export QUALITY_MAX_RETRIES=5
```

## Usage Examples

### Standalone Usage

```python
from src.space_hulk_game.quality import (
    execute_with_quality_check,
    TaskType
)

def generate_plot(**kwargs):
    # Your plot generation logic
    return "title: My Plot\nsetting: A space hulk..."

# Execute with quality checking
output, quality, attempts = execute_with_quality_check(
    task_function=generate_plot,
    task_type=TaskType.PLOT,
    task_name="Generate Plot",
    pass_threshold=7.0,
    max_retries=3
)

print(f"Quality Score: {quality.score:.1f}/10.0")
print(f"Passed: {quality.passed}")
print(f"Attempts: {attempts}")
print(f"Feedback: {quality.feedback}")
```

### With TaskWrapper Class

```python
from src.space_hulk_game.quality import TaskWithQualityCheck, TaskType

# Create wrapper
wrapper = TaskWithQualityCheck(
    task_type=TaskType.PLOT,
    pass_threshold=6.0,
    max_retries=3
)

# Execute task
output, quality, attempts = wrapper.execute(
    task_function=generate_plot,
    task_name="Plot Generation"
)
```

### Using TaskExecutor for Integration

```python
from src.space_hulk_game.quality.integration import (
    TaskExecutor,
    TaskType
)

# Create executor (uses config from quality_config.yaml)
executor = TaskExecutor()

# Execute task (quality checking applied if enabled in config)
output = executor.execute_task(
    task_function=generate_plot,
    task_type=TaskType.PLOT,
    task_name="Generate Plot"
)
```

## Configuration Reference

### Global Settings

```yaml
global:
  enabled: false           # Enable/disable system-wide
  log_level: INFO         # Logging level
  verbose_logging: true   # Detailed quality score logging
```

### Task-Specific Thresholds

Each task type has independent configuration:

```yaml
thresholds:
  plot:                   # Plot outline generation
    enabled: true
    pass_threshold: 6.0   # Minimum score to pass (0.0-10.0)
    max_retries: 3        # Maximum retry attempts

  narrative:              # Narrative map creation
    enabled: true
    pass_threshold: 6.0
    max_retries: 3

  puzzle:                 # Puzzle and artifact design
    enabled: true
    pass_threshold: 6.0
    max_retries: 3

  scene:                  # Scene text and dialogue
    enabled: true
    pass_threshold: 6.0
    max_retries: 3

  mechanics:              # Game mechanics and PRD
    enabled: true
    pass_threshold: 6.0
    max_retries: 3
```

### Retry Behavior

```yaml
retry:
  provide_feedback: true          # Pass feedback to retry attempts
  fail_on_evaluation_error: false # Continue if evaluation fails
```

## Environment Variable Overrides

All settings can be overridden via environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `QUALITY_CHECK_ENABLED` | Enable/disable globally | `true` / `false` |
| `QUALITY_PLOT_THRESHOLD` | Plot quality threshold | `7.0` |
| `QUALITY_NARRATIVE_THRESHOLD` | Narrative quality threshold | `8.0` |
| `QUALITY_PUZZLE_THRESHOLD` | Puzzle quality threshold | `6.5` |
| `QUALITY_SCENE_THRESHOLD` | Scene quality threshold | `7.5` |
| `QUALITY_MECHANICS_THRESHOLD` | Mechanics quality threshold | `6.0` |
| `QUALITY_MAX_RETRIES` | Max retries for all tasks | `5` |

## Quality Levels

The system defines standard quality levels:

| Level | Score Range | Description |
|-------|-------------|-------------|
| Excellent | 9.0-10.0 | Exceeds expectations |
| Good | 7.0-8.9 | Meets all requirements well |
| Acceptable | 6.0-6.9 | Meets minimum requirements |
| Poor | 4.0-5.9 | Significant issues present |
| Failing | 0.0-3.9 | Does not meet requirements |

## Understanding Quality Scores

Quality scores are calculated by evaluators specific to each content type:

### Plot Evaluator
- Clear setting description
- Multiple branching paths (≥2)
- Multiple endings (≥2)
- Clear themes
- Adequate word count (≥500)

### Narrative Map Evaluator
- All scenes have descriptions
- Scene connections are valid
- No orphaned/unreachable scenes
- Minimum scene count (≥5)

### Puzzle Evaluator
- Clear solutions described
- Ties to narrative
- Appropriate difficulty stated

### Scene Evaluator
- Vivid descriptions
- Consistent tone
- Dialogue present where appropriate
- Sensory details included

### Mechanics Evaluator
- All systems described
- Rules are clear
- Balanced difficulty
- Complete documentation

## Feedback on Retries

When a task fails quality checks, the system provides specific feedback:

```
Example feedback for plot with score 4.5/10.0:
"Poor quality - 3 issues found:
- Setting description too brief (need ≥50 words)
- Insufficient branching paths (found 1, need ≥2)
- Missing required themes"
```

This feedback is passed to subsequent retry attempts via `feedback_history` parameter.

## Integration with CrewAI

The quality system integrates seamlessly with CrewAI:

```python
from src.space_hulk_game.quality.integration import (
    get_task_type_for_crew_task,
    execute_with_optional_quality_check
)

# Get task type from crew task name
task_type = get_task_type_for_crew_task('GenerateOverarchingPlot')
# Returns: TaskType.PLOT

# Execute with optional quality checking (enabled via config)
output = execute_with_optional_quality_check(
    task_function=my_task_function,
    task_type=task_type,
    task_name="Generate Plot"
)
```

## Testing

Run quality checking tests:

```bash
# Test retry logic
python -m unittest tests.test_retry_logic -v

# Test quality evaluators
python -m unittest tests.test_quality_evaluators -v

# Test quality metrics
python -m unittest tests.test_quality_metrics -v
```

## Troubleshooting

### Quality checking doesn't activate
- Verify `QUALITY_CHECK_ENABLED=true` is set
- Or check `global.enabled` in quality_config.yaml
- Check logs for "Quality checking disabled" messages

### All outputs fail quality checks
- Lower the pass_threshold in config
- Review quality metrics for your content type
- Check evaluator feedback for specific issues

### Tasks retry too many times
- Reduce max_retries in config
- Increase pass_threshold (if outputs are good)
- Disable quality checking for specific task types

## Best Practices

1. **Start with quality checks disabled** - Ensure basic generation works first
2. **Enable for one task type at a time** - Easier to diagnose issues
3. **Review feedback carefully** - Quality metrics may need tuning
4. **Adjust thresholds based on results** - Default 6.0 may be too strict/lenient
5. **Monitor retry counts** - High retries indicate need for threshold adjustment
6. **Use verbose logging** - Helps understand quality evaluation process

## Related Documentation

- **Quality Metrics**: `docs/QUALITY_METRICS.md` - Detailed metrics documentation
- **Evaluators**: `src/space_hulk_game/quality/` - Evaluator implementations
- **Configuration**: `src/space_hulk_game/config/quality_config.yaml` - Full config
- **Tests**: `tests/test_retry_logic.py` - Usage examples in tests
