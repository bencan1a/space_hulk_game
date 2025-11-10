# Quick Start Guide - Improved CrewAI Setup

This guide helps you quickly understand and use the improved Space Hulk Game CrewAI system.

## TL;DR

**What Changed**: The crew now uses **sequential process** by default (instead of hierarchical) to ensure reliability and prevent hanging.

**Why**: Phase 0 of the restart plan requires proving basic generation works before adding complexity.

**How to Use**: Same as before - `crewai run` - but now it's more reliable!

## Quick Commands

**Important:** Always activate the virtual environment first!

```bash
# Activate virtual environment
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows
```

### Test the Setup

```bash
# Verify everything is configured correctly (doesn't run LLM)
python test_crew_init.py
```

### Run the Crew

```bash
# Default: sequential mode with all 11 tasks
crewai run

# With custom prompt
crewai run --inputs "prompt: A Space Marine team investigates a derelict vessel..."
```

### Run Tests

```bash
# All tests (should see 19 passing)
python -m unittest discover -s tests -v

# Just the improvement tests
python -m unittest tests.test_crew_improvements -v
```

## What's Different?

### Before (Problematic)

```python
# Hierarchical process - could hang
process=Process.hierarchical
manager_agent=NarrativeDirectorAgent
memory=True
planning=True
```

### After (Reliable)

```python
# Sequential process - predictable and stable
process=Process.sequential
# Memory and planning disabled until basic flow proven
```

## Process Modes Explained

### Sequential Mode (Default) ✅

- **What**: Agents work in order, one after another
- **When**: Use this first to validate the system works
- **Pros**: Simple, reliable, easy to debug
- **Cons**: No manager coordination or feedback loops

**Flow**:

```
PlotMaster → NarrativeArchitect → PuzzleSmith → CreativeScribe → MechanicsGuru
   (with evaluation tasks in between)
```

### Hierarchical Mode (Advanced) ⚠️

- **What**: Manager agent (NarrativeDirector) coordinates workers
- **When**: Use after sequential mode is proven stable
- **Pros**: Enables delegation, feedback, quality control
- **Cons**: More complex, potential for hanging

**Flow**:

```
        NarrativeDirector (Manager)
               ↓
    ┌──────────┼──────────┐
    ↓          ↓          ↓
PlotMaster  PuzzleSmith  CreativeScribe
    ↓          ↓          ↓
        (returns to manager for evaluation)
```

## Task Execution Order

### Core Tasks (Always Run)

1. **GenerateOverarchingPlot** - PlotMasterAgent creates plot
2. **CreateNarrativeMap** - NarrativeArchitectAgent maps scenes
3. **DesignArtifactsAndPuzzles** - PuzzleSmithAgent creates gameplay elements
4. **WriteSceneDescriptionsAndDialogue** - CreativeScribeAgent writes text
5. **CreateGameMechanicsPRD** - MechanicsGuruAgent defines systems

### Evaluation Tasks (Quality Gates)

6. **EvaluateNarrativeFoundation** - Director checks plot quality
7. **EvaluateNarrativeStructure** - Director checks scene structure
8. **NarrativeIntegrationCheckPuzzles** - Director checks puzzle integration
9. **NarrativeIntegrationCheckScenes** - Director checks scene quality
10. **NarrativeIntegrationCheckMechanics** - Director checks mechanics fit
11. **FinalNarrativeIntegration** - Director does final review

## Output Files

After successful run, you'll find:

- `plot_outline.yaml` - Overall narrative structure
- `narrative_map.yaml` - Scene-by-scene breakdown
- `puzzle_design.yaml` - Puzzles, artifacts, NPCs, monsters
- `scene_texts.yaml` - Descriptions and dialogue
- `prd_document.yaml` - Game mechanics and systems

## Troubleshooting

### Problem: Crew hangs or becomes unresponsive

**Solution**: You're probably using hierarchical mode. Switch to sequential:

```python
# In crew.py, the @crew method should use:
process=Process.sequential
```

### Problem: Import errors

**Solution**: Make sure the virtual environment is activated and you're in the project root:

```bash
# Activate virtual environment first
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# Verify you're in the project root
cd /path/to/space_hulk_game
python test_crew_init.py
```

**Common Cause:** The virtual environment is not activated. Always activate `.venv` before running commands.

### Problem: Tasks produce errors

**Solution**: Check the logs for details. The improved error handling will:

1. Log the specific error
2. Attempt recovery with defaults
3. Continue execution if possible
4. Mark output with error flag

### Problem: Want to test hierarchical mode

**Solution**: After sequential works 3+ times successfully:

```python
# Modify crew.py temporarily
@crew
def crew(self) -> Crew:
    return self.create_hierarchical_crew()  # Use hierarchical
```

**Important**: Start with just 3-5 tasks, add evaluation tasks incrementally!

## Testing Strategy

### Phase 0: Validate Sequential Mode

**Prerequisites:** Activate the virtual environment for all commands below.

```bash
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows
```

1. **Smoke Test** (5 core tasks only)

   ```bash
   # Comment out evaluation tasks in crew.py
   # Run with simple prompt
   crewai run --inputs "prompt: Simple test scenario"
   ```

   **Expected**: ~5-8 minutes, 5 output files

2. **Full Test** (All 11 tasks)

   ```bash
   # All tasks enabled
   crewai run --inputs "prompt: Complex scenario with choices"
   ```

   **Expected**: ~10-15 minutes, 5 output files + evaluations

3. **Reliability Test** (Multiple runs)

   ```bash
   # Run 3 times with different prompts
   # Verify consistent success
   ```

   **Expected**: All 3 complete successfully

### Phase 1: Test Hierarchical (Future)

Only after Phase 0 succeeds:

1. Test with 3 tasks only
2. Add tasks one at a time
3. Monitor for hanging
4. Document any issues
5. Fix before proceeding

## Success Criteria

### Minimum (Must Achieve)

- ✅ Sequential mode runs without hanging
- ✅ All 5 output files generated
- ✅ YAML files are valid
- ✅ Content is coherent and related to prompt

### Ideal (Phase 0 Goal)

- ✅ Completes in < 10 minutes
- ✅ Can run 3 times successfully
- ✅ Error messages are clear
- ✅ No manual intervention needed

## Advanced Usage

### Custom Prompt Examples

**Prerequisites:** Activate the virtual environment first.

```bash
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows
```

**Simple Exploration**:

```bash
crewai run --inputs "prompt: A squad explores an abandoned mining station"
```

**Complex Narrative**:

```bash
crewai run --inputs "prompt: A desperate escape from a xenos-infested vessel, \
with moral choices about saving civilians vs completing the mission"
```

**Specific Theme**:

```bash
crewai run --inputs "prompt: Gothic horror in tight corridors, \
emphasizing claustrophobia and body horror"
```

### Programmatic Usage

```python
from space_hulk_game.crew import SpaceHulkGame

# Create instance
game = SpaceHulkGame()

# Prepare input
inputs = {
    "prompt": "Your scenario description here",
}

# Run crew (sequential mode)
result = game.crew().kickoff(inputs)

# Access output
print(result.raw)
print(result.metadata)

# Check for errors
if hasattr(result, 'errors') and result.errors:
    print("Errors occurred:", result.errors)
```

### Testing Hierarchical Mode

```python
from space_hulk_game.crew import SpaceHulkGame

game = SpaceHulkGame()

# Use hierarchical crew
h_crew = game.create_hierarchical_crew()

# Run with simple scenario first
result = h_crew.kickoff({"prompt": "Simple test"})
```

## Getting Help

### Documentation

- **CREWAI_IMPROVEMENTS.md** - Complete improvement details
- **REVISED_RESTART_PLAN.md** - Phase 0 strategy and goals
- **CONTRIBUTING.md** - Development guidelines
- **AGENTS.md** - Agent architecture details

### Diagnostics

```bash
# Activate virtual environment first
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# Check configuration
python test_crew_init.py

# Run tests
python -m unittest tests.test_crew_improvements -v

# Check logs (after a run)
grep -i error *.log
grep -i warning *.log
```

### Common Issues

1. **Hanging**: Switch to sequential mode
2. **Import errors**: Activate virtual environment, check you're in project root
3. **LLM errors**: Verify Ollama is running on localhost:11434
4. **YAML errors**: Check output file syntax
5. **Module not found**: Ensure `.venv` is activated before running commands

## Next Steps

1. **Validate**: Run `python test_crew_init.py` to verify setup
2. **Test**: Run sequential mode 3 times successfully
3. **Measure**: Track completion time and success rate
4. **Document**: Note any issues or unexpected behavior
5. **Iterate**: Only add complexity after basic flow proven

## Summary

The improved setup prioritizes **reliability over features**:

- ✅ Sequential mode by default
- ✅ Memory/planning disabled initially
- ✅ Comprehensive error handling
- ✅ Clear documentation
- ✅ Validated with tests

**Goal**: Prove the crew works reliably before adding advanced features.

**Next**: Run actual game generation and measure success!
