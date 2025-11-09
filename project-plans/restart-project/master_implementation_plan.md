# Space Hulk Game - Master Implementation Plan

**Version:** 2.0
**Created:** November 9, 2025
**Status:** Active
**Supersedes:** PROJECT_RESTART_PLAN.md, REVISED_RESTART_PLAN.md

---

## Executive Summary

This master plan unifies all restart planning documents into a single, actionable implementation roadmap for completing the Space Hulk text-based adventure game generator. The plan is organized into discrete, agent-executable work chunks with clear validation criteria.

**Core Philosophy:** Prove basic functionality first, then enhance incrementally.

**Timeline:** 8-10 weeks (part-time effort)
**Current Status:** Phase 0 foundation complete, ready for Phase 0 validation
**Next Milestone:** Prove sequential generation works end-to-end

---

## Project Status Assessment

### ✅ Completed Work

**Phase 0 Foundation (Weeks 1-2 of original plan)**
- [x] Sequential mode set as default in [crew.py](../src/space_hulk_game/crew.py)
- [x] Hierarchical mode available via `create_hierarchical_crew()` method
- [x] Memory and planning features disabled by default
- [x] Comprehensive error handling with `@before_kickoff` and `@after_kickoff` hooks
- [x] All 6 agents defined in [agents.yaml](../src/space_hulk_game/config/agents.yaml)
- [x] All 11 tasks defined in [tasks.yaml](../src/space_hulk_game/config/tasks.yaml)
- [x] Task dependencies configured (linear, no circular dependencies)
- [x] Basic test suite exists (19 tests, some passing)

**Phase 1 (Syntax & Bug Fixes) - COMPLETED MARCH 2025** ✅
- [x] YAML configuration files syntax validated
- [x] Input validation with default fallbacks
- [x] Error recovery mechanisms in place
- [x] Logging configured
- **Reference:** [phase1_implementation_plan.md](phase1_implementation_plan.md)
- **Evidence:** Code exists in [crew.py](../../src/space_hulk_game/crew.py) lines 119-189

**Phase 2 (Hierarchical Structure) - COMPLETED MARCH 2025** ✅
- [x] NarrativeDirectorAgent defined
- [x] Evaluation tasks created for narrative integration
- [x] Task dependency structure established
- [x] Hierarchical crew method implemented
- **Reference:** [phase2_implementation_plan.md](phase2_implementation_plan.md)
- **Evidence:** Code exists in [crew.py](../../src/space_hulk_game/crew.py), [agents.yaml](../../src/space_hulk_game/config/agents.yaml), [tasks.yaml](../../src/space_hulk_game/config/tasks.yaml)
- **Verification:** See [CODE_VERIFICATION.md](CODE_VERIFICATION.md) for detailed analysis

### ⚠️ In Progress

**Phase 0 Validation (Current Focus)**
- [ ] Sequential mode end-to-end test (5 core tasks)
- [ ] Sequential mode end-to-end test (all 11 tasks)
- [ ] Hierarchical mode validation
- [ ] Performance validation (< 10 minute generation)
- [ ] Reliability validation (3 consecutive successful runs)

### ❌ Not Started

**Phase 3: Quality & Iteration System** (Weeks 3-5)
**Phase 4: Game Engine** (Weeks 6-7) - CRITICAL PATH
**Phase 5: Output Validation** (Weeks 8-9)
**Phase 6: Enhanced Memory** (Week 10)
**Phase 7: Production Polish** (Weeks 11-12)

---

## Execution Strategy: Serial vs. Parallel

### Serial Dependencies (Must Complete in Order)

**Critical Path:**
```
Phase 0 Validation (BLOCKING)
   ↓
Phase 4 Game Engine (CRITICAL PATH)
   ↓
MVP Complete
```

**Phase Execution Order:**

1. **Phase 0 (SERIAL)** - Must complete first
   - All chunks (0.1-0.4) must run sequentially
   - BLOCKS all other work until proven functional

2. **After Phase 0, Two Parallel Tracks:**

   **Track A (Critical Path - Priority 1):**
   - Phase 4: Game Engine (serial within phase)
   - Required for MVP

   **Track B (Enhancements - Priority 2):**
   - Phase 3: Quality System (can run in parallel with Phase 4)
   - Phase 6: Memory System (can run anytime after Phase 0)

3. **After Phase 4 Complete:**
   - Phase 5: Output Validation (needs Phase 4 concepts)
   - Phase 7: Production Polish (needs Phase 4 game engine)

### Parallelization Opportunities

**Can Run in Parallel (After Phase 0):**

| Track | Phase | Reason |
|-------|-------|--------|
| A | Phase 4 (Game Engine) | Critical path - PRIORITY |
| B | Phase 3 (Quality System) | Independent of game engine |
| B | Phase 6 (Memory System) | Independent of game engine |

**Within Phase 3 (Quality System):**
- Chunk 3.1 (Metrics) → SERIAL (first)
- Chunks 3.2-3.4 → CAN PARALLELIZE after 3.1
  - 3.2 (Evaluators) - Depends on 3.1
  - 3.3 (Retry Logic) - Depends on 3.2
  - 3.4 (Planning Templates) - INDEPENDENT, can run anytime

**Within Phase 4 (Game Engine):**
- Chunks 4.1-4.6 → MOSTLY SERIAL
  - 4.1 (Game State) → First (SERIAL)
  - 4.2 (Command Parser) → After 4.1 (SERIAL)
  - 4.3 (Game Engine) → After 4.1, 4.2 (SERIAL)
  - 4.4 (Content Loader) → After 4.3 (SERIAL)
  - 4.5 (Validator) → After 4.4 (SERIAL)
  - 4.6 (Demo & Integration) → After 4.5 (SERIAL)

**Within Phase 5 (Output Validation):**
- All chunks SERIAL (each builds on previous)

**Within Phase 6 (Memory System):**
- Chunks 6.1-6.2 → SERIAL
- Chunks 6.3-6.4 → Can PARALLELIZE after 6.2

**Within Phase 7 (Production Polish):**
- Chunks 7.1-7.4 → CAN PARALLELIZE (all independent)

### Recommended Execution Plan

**Week 1 (This Week):**
```
SERIAL: Phase 0 Chunks 0.1 → 0.2 → 0.3
```

**Weeks 2-3 (If Phase 0 passes):**
```
PARALLEL:
├─ Track A: Phase 4 Chunks 4.1 → 4.2 → 4.3 (Critical)
└─ Track B: Phase 3 Chunk 3.4 (Planning Templates - independent)
```

**Weeks 4-5:**
```
PARALLEL:
├─ Track A: Phase 4 Chunks 4.4 → 4.5 → 4.6 (Complete game engine)
└─ Track B: Phase 3 Chunks 3.1 → 3.2 → 3.3 (Quality system)
```

**Weeks 6-7:**
```
SERIAL (requires Phase 4 complete):
Phase 5 Chunks 5.1 → 5.2 → 5.3 → 5.4
```

**Weeks 8-9:**
```
PARALLEL:
├─ Phase 6 Chunks 6.1 → 6.2 → 6.3 → 6.4
└─ Phase 7 Chunk 7.2 (Example Games)
```

**Week 10:**
```
PARALLEL: Phase 7 Chunks 7.1, 7.3, 7.4 (all independent)
```

### Execution Mode Legend

Each chunk is marked with an indicator showing its execution requirements:

| Indicator | Meaning | Can Start When | Notes |
|-----------|---------|----------------|-------|
| 🔴 SERIAL - BLOCKING | Must complete before ANY other work | Immediately | Blocks all phases |
| 🔴 SERIAL - CRITICAL PATH | Must complete in order, on critical path | After prerequisites | Required for MVP |
| 🔴 SERIAL FIRST | Must be first in its phase | After prerequisites | Starts the phase |
| 🔴 SERIAL | Must complete before next in sequence | After prerequisites | Linear dependency |
| 🟡 SERIAL - OPTIONAL | Optional serial execution | After prerequisites | Not required for MVP |
| 🟠 CAN PARALLEL | Can run in parallel after initial setup | After prerequisites | Some parallelism possible |
| 🟢 PARALLEL - INDEPENDENT | Fully independent, maximum parallelism | After prerequisites | No dependencies within phase |

**Quick Reference:**
- 🔴 = Must complete in order (serial)
- 🟡 = Optional serial task
- 🟠 = Can parallelize with planning
- 🟢 = Fully parallelizable

### Maximum Parallelization Strategy

If you have multiple agents available simultaneously:

**Immediate (After Phase 0):**
- Agent 1: Phase 4.1 → 4.2 → 4.3 (Game Engine Core) - PRIORITY
- Agent 2: Phase 3.4 (Planning Templates) - Can start immediately
- Agent 3: Phase 6.1 → 6.2 (Memory Schema & Manager) - Can start immediately

**Week 2-3:**
- Agent 1: Phase 4.4 → 4.5 (Content Loader, Validator)
- Agent 2: Phase 3.1 → 3.2 (Quality Metrics, Evaluators)
- Agent 3: Phase 6.3 (Agent Integration)

**Week 4:**
- Agent 1: Phase 4.6 (Demo Game Integration)
- Agent 2: Phase 3.3 (Retry Logic)
- Agent 3: Phase 6.4 (Cross-Session Learning)

**Week 5 (After Phase 4 complete):**
- Agent 1: Phase 5.1 → 5.2 (Pydantic Models, Validators)
- Agent 2: Phase 3.5 (Integration Testing)
- Agent 3: Phase 7.2 (Example Games)

**Week 6:**
- Agent 1: Phase 5.3 → 5.4 (Auto-correction, Integration)
- Agent 2: Phase 7.1 (Logging & Monitoring)
- Agent 3: Phase 7.3 (Documentation)

**Week 7:**
- All Agents: Phase 7.4 (Performance Optimization) - Collaborative

---

## Implementation Roadmap

### Phase 0: Crew Validation & Debugging ⭐ CURRENT PRIORITY

**Duration:** 1-2 weeks
**Goal:** Prove the basic crew generates complete game outputs without hanging
**Status:** Foundation complete, validation pending

#### Success Criteria

Before proceeding to any other phase:

| Criterion | Target | Status |
|-----------|--------|--------|
| Sequential generation (5 tasks) completes | 100% success | ❓ Not tested |
| Sequential generation (11 tasks) completes | 100% success | ❓ Not tested |
| Average generation time | < 10 minutes | ❓ Not tested |
| Reliability (3 consecutive runs) | 100% success | ❓ Not tested |
| Output files generated | 5/5 files valid YAML | ❓ Not tested |
| Hierarchical mode (3 tasks) completes | 100% success | ❓ Not tested |

#### Work Chunks for Agents

**Chunk 0.1: Sequential Mode Validation (5 Core Tasks)** 🔴 SERIAL - BLOCKING
```yaml
Objective: Validate sequential mode completes with 5 core tasks
Agent: validation-agent or general-purpose agent
Scope: Focused test execution
Execution Mode: SERIAL (must complete before any other work)
Prerequisites: None

Tasks:
1. Comment out all 6 evaluation tasks in tasks.yaml
2. Run: crewai run --inputs "prompt: A Space Marine boarding team discovers an ancient derelict vessel"
3. Monitor execution with 15-minute timeout
4. Validate outputs:
   - game-config/plot_outline.yaml exists and is valid YAML
   - game-config/narrative_map.yaml exists and is valid YAML
   - game-config/puzzle_design.yaml exists and is valid YAML
   - game-config/scene_texts.yaml exists and is valid YAML
   - game-config/prd_document.yaml exists and is valid YAML
5. Document: execution time, any errors, output quality

Success Criteria:
✅ All 5 core tasks complete without errors
✅ All 5 output files exist and contain valid YAML
✅ Generation completes in < 10 minutes
✅ No hanging or timeout issues

Validation Script:
- tests/test_sequential_5_tasks.py
```

**Chunk 0.2: Sequential Mode Validation (All 11 Tasks)** 🔴 SERIAL - BLOCKING
```yaml
Objective: Validate sequential mode completes with all tasks including evaluations
Agent: validation-agent or general-purpose agent
Scope: Full workflow test
Execution Mode: SERIAL (must complete after 0.1)
Prerequisites: Chunk 0.1 complete

Tasks:
1. Restore all 11 tasks in tasks.yaml (un-comment evaluation tasks)
2. Run: crewai run --inputs "prompt: A Space Marine boarding team discovers an ancient derelict vessel"
3. Monitor execution with 20-minute timeout
4. Validate outputs (same 5 files as above)
5. Review evaluation task outputs in logs
6. Document: execution time, evaluation results, any issues

Success Criteria:
✅ All 11 tasks complete without errors
✅ All 5 output files exist and contain valid YAML
✅ Generation completes in < 15 minutes
✅ Evaluation tasks provide meaningful feedback in logs

Validation Script:
- tests/test_sequential_11_tasks.py
```

**Chunk 0.3: Reliability Testing** 🔴 SERIAL - BLOCKING
```yaml
Objective: Prove system is reliable across multiple runs
Agent: validation-agent or general-purpose agent
Scope: Stress testing
Execution Mode: SERIAL (must complete after 0.2)
Prerequisites: Chunks 0.1 and 0.2 complete

Tasks:
1. Run sequential mode (11 tasks) 3 times with different prompts:
   - Prompt 1: "A Space Marine boarding team discovers an ancient derelict vessel"
   - Prompt 2: "A lone Tech-Priest investigates strange signals from a hulk"
   - Prompt 3: "A desperate escape from a Genestealer-infested hulk"
2. Track success/failure for each run
3. Measure average generation time
4. Compare output quality across runs
5. Document any failures or inconsistencies

Success Criteria:
✅ 3/3 runs complete successfully
✅ Average time < 10 minutes
✅ All runs produce valid YAML outputs
✅ No memory leaks or degradation over time

Validation Script:
- tests/test_reliability.py
```

**Chunk 0.4: Hierarchical Mode Validation (OPTIONAL)** 🟡 SERIAL - OPTIONAL
```yaml
Objective: Test hierarchical mode with minimal tasks
Agent: validation-agent or general-purpose agent
Scope: Advanced configuration testing
Execution Mode: SERIAL (optional, after 0.1-0.3)
Prerequisites: Chunks 0.1-0.3 must pass

Tasks:
1. Modify crew.py to use hierarchical mode (3 tasks only):
   - GenerateOverarchingPlot
   - CreateNarrativeMap
   - DesignArtifactsAndPuzzles
2. Run with manager agent coordination
3. Monitor for hanging/blocking (10-minute timeout)
4. If successful, incrementally add remaining tasks one at a time
5. Document at which point (if any) hierarchical mode hangs

Success Criteria:
✅ 3-task hierarchical mode completes
✅ Manager delegation works correctly
✅ Identify specific hanging point if hierarchical fails

Validation Script:
- tests/test_hierarchical_minimal.py

Note: If hierarchical mode continues to hang, document root cause and
proceed with sequential mode for remaining phases.
```

---

### Phase 3: Quality & Iteration System

**Duration:** 2-3 weeks
**Goal:** Enable quality evaluation and iterative improvement of generated content
**Prerequisites:** Phase 0 validation complete

#### Overview

Implement a quality measurement and feedback system that allows the crew to:
- Evaluate generated content against defined metrics
- Provide specific feedback for improvement
- Retry failed tasks with guidance
- Learn from successful patterns

#### Work Chunks for Agents

**Chunk 3.1: Quality Metrics Definition** 🔴 SERIAL FIRST (within phase)
```yaml
Objective: Define measurable quality criteria for each output type
Agent: design-agent or general-purpose agent
Scope: Specification and schema design
Execution Mode: SERIAL (first in Phase 3, but can start after Phase 0)
Prerequisites: Phase 0 complete

Tasks:
1. Create quality metrics schema for PlotOutline:
   - Has clear setting (yes/no)
   - Defines 2+ branching paths (count)
   - Includes at least 2 endings (count)
   - Themes clearly stated (yes/no)
   - Word count > 500 (number)
   - File: src/space_hulk_game/quality/plot_metrics.py

2. Create quality metrics schema for NarrativeMap:
   - All scenes have descriptions (completeness %)
   - All connections valid (validation)
   - No orphaned scenes (validation)
   - Min 5 scenes (count)
   - File: src/space_hulk_game/quality/narrative_metrics.py

3. Create quality metrics schema for Puzzles:
   - Clear solution described (yes/no)
   - Ties to narrative (text analysis)
   - Appropriate difficulty stated (yes/no)
   - File: src/space_hulk_game/quality/puzzle_metrics.py

4. Create quality metrics schema for Scenes:
   - Vivid descriptions (text quality score)
   - Consistent tone (analysis)
   - Dialogue present where appropriate (yes/no)
   - File: src/space_hulk_game/quality/scene_metrics.py

5. Create quality metrics schema for Mechanics:
   - All systems described (completeness %)
   - Rules are clear (readability score)
   - Balanced difficulty (analysis)
   - File: src/space_hulk_game/quality/mechanics_metrics.py

Success Criteria:
✅ Quality metrics defined for all 5 output types
✅ Metrics are measurable and objective
✅ Each metric has clear pass/fail threshold
✅ Metrics documented with examples

Deliverables:
- src/space_hulk_game/quality/ directory with 5 metrics modules
- docs/QUALITY_METRICS.md documentation
```

**Chunk 3.2: Quality Evaluator Implementation** 🔴 SERIAL
```yaml
Objective: Implement evaluators that score outputs against metrics
Agent: implementation-agent or general-purpose agent
Scope: Core evaluation system
Execution Mode: SERIAL (after 3.1)
Prerequisites: Chunk 3.1 complete

Tasks:
1. Create QualityEvaluator base class:
   - File: src/space_hulk_game/quality/evaluator.py
   - Methods: evaluate(), score(), generate_feedback()

2. Implement PlotEvaluator:
   - Uses plot_metrics.py
   - Returns QualityScore with 0-10 rating
   - Generates specific feedback for improvement

3. Implement NarrativeMapEvaluator:
   - Uses narrative_metrics.py
   - Validates scene graph structure
   - Checks for orphaned or unreachable scenes

4. Implement PuzzleEvaluator:
   - Uses puzzle_metrics.py
   - Verifies puzzles are solvable
   - Checks narrative integration

5. Implement SceneEvaluator:
   - Uses scene_metrics.py
   - Analyzes text quality
   - Checks tone consistency

6. Implement MechanicsEvaluator:
   - Uses mechanics_metrics.py
   - Validates completeness
   - Checks clarity and balance

7. Create QualityScore data class:
   - File: src/space_hulk_game/quality/score.py
   - Fields: score (0-10), passed (bool), feedback (str), details (dict)

Success Criteria:
✅ All 5 evaluators implemented and tested
✅ Each evaluator returns standardized QualityScore
✅ Feedback is specific and actionable
✅ Unit tests cover all evaluator methods

Validation:
- tests/test_quality_evaluators.py with sample outputs
```

**Chunk 3.3: Retry Logic with Feedback** 🔴 SERIAL
```yaml
Objective: Add retry mechanism for tasks that fail quality checks
Agent: implementation-agent or general-purpose agent
Scope: Task execution enhancement
Execution Mode: SERIAL (after 3.2)
Prerequisites: Chunk 3.2 complete

Tasks:
1. Create TaskWithQualityCheck wrapper:
   - File: src/space_hulk_game/quality/retry.py
   - Wraps existing Task execution
   - Adds quality evaluation after execution
   - Implements retry loop with feedback

2. Implement retry logic:
   ```python
   def execute_with_quality_check(task, max_retries=3):
       for attempt in range(max_retries):
           output = task.execute()
           quality = evaluate_quality(task.name, output)

           if quality.passed:
               return output

           # Provide feedback and retry
           feedback = quality.generate_feedback()
           task.add_context_feedback(feedback)

       # Max retries reached - accept with warning
       logger.warning(f"Task {task.name} did not meet quality threshold after {max_retries} attempts")
       return output
   ```

3. Integrate with crew.py:
   - Add quality_check parameter to task decorator
   - Wire up evaluators to tasks
   - Configure retry thresholds

4. Add configuration:
   - quality_config.yaml with thresholds and retry counts
   - Environment variable overrides

Success Criteria:
✅ Retry logic works for all task types
✅ Feedback is provided to tasks on retry
✅ Maximum retry limit prevents infinite loops
✅ Quality scores logged for monitoring

Validation:
- tests/test_retry_logic.py with intentionally poor outputs
```

**Chunk 3.4: Planning Templates** 🟢 PARALLEL - INDEPENDENT
```yaml
Objective: Create reusable templates for different game types
Agent: content-agent or general-purpose agent
Scope: Template creation
Execution Mode: PARALLEL (fully independent, can start after Phase 0)
Prerequisites: Phase 0 complete only

Tasks:
1. Create space_horror planning template:
   - File: planning_templates/space_horror.yaml
   - Define narrative focus, required elements, tone
   - Include example scenes and puzzles

2. Create mystery_investigation planning template:
   - File: planning_templates/mystery_investigation.yaml
   - Focus on clues, deduction, revelation

3. Create survival_escape planning template:
   - File: planning_templates/survival_escape.yaml
   - Focus on resource management, time pressure

4. Create combat_focused planning template:
   - File: planning_templates/combat_focused.yaml
   - Focus on tactical decisions, squad management

5. Update prompt processing to load templates:
   - Modify prepare_inputs() to detect template hints
   - Load appropriate template as context

Success Criteria:
✅ 4 planning templates created
✅ Each template has clear structure and examples
✅ Templates can be loaded and used as context
✅ Documentation explains how to use templates

Deliverables:
- planning_templates/ directory with 4 YAML files
- docs/PLANNING_TEMPLATES.md usage guide
```

**Chunk 3.5: Integration Testing** 🔴 SERIAL
```yaml
Objective: Test quality system end-to-end with crew
Agent: validation-agent or general-purpose agent
Scope: Integration validation
Execution Mode: SERIAL (after all Phase 3 chunks)
Prerequisites: Chunks 3.1-3.4 complete

Tasks:
1. Enable quality checks in crew.py
2. Run full generation with quality evaluation
3. Test that retry logic activates on poor outputs
4. Verify quality scores improve with retries
5. Test with different planning templates
6. Measure impact on generation time

Success Criteria:
✅ Quality system integrates smoothly with crew
✅ Quality scores are logged and visible
✅ Retry logic activates when needed
✅ Overall generation time remains < 15 minutes
✅ Output quality measurably improves

Validation:
- tests/test_quality_integration.py
```

---

### Phase 4: Simple Game Engine ⭐ CRITICAL PATH

**Duration:** 2 weeks
**Goal:** Build minimal text adventure engine to validate generated content is playable
**Prerequisites:** Phase 0 validation complete (Phase 3 can run in parallel)

#### Overview

**Why This is Critical:** Without a game engine, we cannot verify that:
- Generated scenes are actually connected correctly
- Puzzles are solvable by players
- Game flow makes logical sense
- Player commands work as expected

The game engine is the ultimate validation tool for generated content.

#### Work Chunks for Agents

**Chunk 4.1: Game State Model** 🔴 SERIAL - CRITICAL PATH
```yaml
Objective: Define data structures for game state
Agent: implementation-agent or general-purpose agent
Scope: Core data model
Execution Mode: SERIAL (first in Phase 4, starts after Phase 0)
Prerequisites: Phase 0 complete

Tasks:
1. Create GameState class:
   - File: src/space_hulk_game/engine/game_state.py
   ```python
   from dataclasses import dataclass
   from typing import List, Dict, Set

   @dataclass
   class GameState:
       current_scene: str
       inventory: List[str]
       visited_scenes: Set[str]
       game_flags: Dict[str, bool]
       health: int
       max_health: int
   ```

2. Create Scene class:
   - File: src/space_hulk_game/engine/scene.py
   ```python
   @dataclass
   class Scene:
       id: str
       description: str
       exits: Dict[str, str]  # direction -> scene_id
       items: List['Item']
       npcs: List['NPC']
       events: List['Event']
   ```

3. Create supporting classes (Item, NPC, Event):
   - File: src/space_hulk_game/engine/entities.py

Success Criteria:
✅ All data classes defined with type hints
✅ Classes are immutable where appropriate
✅ Proper documentation with examples
✅ Unit tests for data model

Deliverables:
- src/space_hulk_game/engine/ directory with data models
```

**Chunk 4.2: Command Parser** 🔴 SERIAL - CRITICAL PATH
```yaml
Objective: Parse player text commands into actions
Agent: implementation-agent or general-purpose agent
Scope: Natural language command processing
Execution Mode: SERIAL (after 4.1)
Prerequisites: Chunk 4.1 complete

Tasks:
1. Create CommandParser class:
   - File: src/space_hulk_game/engine/parser.py
   ```python
   class CommandParser:
       COMMANDS = {
           'go': ['go', 'move', 'walk', 'run', 'north', 'south', 'east', 'west'],
           'take': ['take', 'get', 'grab', 'pick'],
           'use': ['use', 'activate', 'operate'],
           'look': ['look', 'examine', 'inspect'],
           'inventory': ['inventory', 'inv', 'i'],
           'talk': ['talk', 'speak', 'ask'],
           'help': ['help', 'commands', '?']
       }

       def parse(self, command: str) -> Action:
           """Convert text to Action object"""
           pass
   ```

2. Create Action class:
   - File: src/space_hulk_game/engine/actions.py
   - Support: MoveAction, TakeAction, UseAction, LookAction, etc.

3. Implement fuzzy matching for typos:
   - Use difflib or similar for close matches
   - Suggest corrections for unrecognized commands

4. Add context-aware parsing:
   - Consider items in current scene
   - Consider NPCs present
   - Disambiguate when needed

Success Criteria:
✅ Parser handles all basic commands
✅ Fuzzy matching works for common typos
✅ Context-aware suggestions work
✅ Unit tests cover command variations

Validation:
- tests/test_command_parser.py with diverse inputs
```

**Chunk 4.3: Game Engine Core** 🔴 SERIAL - CRITICAL PATH
```yaml
Objective: Implement main game loop and action execution
Agent: implementation-agent or general-purpose agent
Scope: Core game engine
Execution Mode: SERIAL (after 4.1 and 4.2)
Prerequisites: Chunks 4.1 and 4.2 complete

Tasks:
1. Create TextAdventureEngine class:
   - File: src/space_hulk_game/engine/engine.py
   ```python
   class TextAdventureEngine:
       def __init__(self, game_data: dict):
           self.state = GameState()
           self.scenes = self.load_scenes(game_data)
           self.parser = CommandParser()

       def run(self):
           """Main game loop"""
           while not self.state.game_over:
               self.display_scene()
               command = self.get_player_input()
               action = self.parser.parse(command)
               self.execute_action(action)

       def display_scene(self):
           """Show current scene to player"""
           pass

       def execute_action(self, action: Action):
           """Execute player action and update state"""
           pass
   ```

2. Implement action handlers:
   - handle_move(direction): Change scenes
   - handle_take(item): Add to inventory
   - handle_use(item, target): Use item interaction
   - handle_look(target): Show description
   - handle_talk(npc): Trigger dialogue

3. Implement game state transitions:
   - Scene changes
   - Flag updates
   - Event triggers
   - Victory/defeat conditions

4. Add save/load functionality:
   - Save game state to JSON
   - Load game state from JSON
   - File: src/space_hulk_game/engine/persistence.py

Success Criteria:
✅ Game loop runs without errors
✅ All basic actions work correctly
✅ State transitions are correct
✅ Save/load works reliably

Validation:
- tests/test_game_engine.py with scripted playthrough
```

**Chunk 4.4: Content Loader** 🔴 SERIAL - CRITICAL PATH
```yaml
Objective: Load generated YAML files into game engine format
Agent: implementation-agent or general-purpose agent
Scope: Content pipeline
Execution Mode: SERIAL (after 4.3)
Prerequisites: Chunk 4.3 complete

Tasks:
1. Create ContentLoader class:
   - File: src/space_hulk_game/engine/loader.py
   ```python
   class ContentLoader:
       def load_game(self, output_dir: str) -> GameData:
           """Load all generated files into playable game"""
           plot = self.load_yaml(f"{output_dir}/plot_outline.yaml")
           narrative = self.load_yaml(f"{output_dir}/narrative_map.yaml")
           puzzles = self.load_yaml(f"{output_dir}/puzzle_design.yaml")
           scenes = self.load_yaml(f"{output_dir}/scene_texts.yaml")
           mechanics = self.load_yaml(f"{output_dir}/prd_document.yaml")

           return self.merge_into_game_data(
               plot, narrative, puzzles, scenes, mechanics
           )
   ```

2. Implement format converters:
   - Convert YAML narrative map to Scene objects
   - Convert puzzle definitions to game mechanics
   - Merge scene texts with narrative structure
   - Apply mechanics rules to game state

3. Handle format variations:
   - Graceful handling of missing fields
   - Default values for optional content
   - Validation warnings for inconsistencies

4. Create GameData class to hold all content:
   - File: src/space_hulk_game/engine/game_data.py

Success Criteria:
✅ Loader handles all 5 YAML files
✅ Converts to engine-compatible format
✅ Handles missing or malformed data gracefully
✅ Integration test with real generated content

Validation:
- tests/test_content_loader.py with sample YAMLs
```

**Chunk 4.5: Game Validator** 🔴 SERIAL - CRITICAL PATH
```yaml
Objective: Validate that generated content can be played
Agent: implementation-agent or general-purpose agent
Scope: Content validation
Execution Mode: SERIAL (after 4.4)
Prerequisites: Chunk 4.4 complete

Tasks:
1. Create GameValidator class:
   - File: src/space_hulk_game/engine/validator.py
   ```python
   class GameValidator:
       def validate_game(self, game_data: GameData) -> ValidationResult:
           """Check for common playability issues"""
           issues = []

           # Check all scenes are reachable
           reachable = self.find_reachable_scenes(game_data)
           unreachable = set(game_data.scenes.keys()) - reachable
           if unreachable:
               issues.append(f"Unreachable scenes: {unreachable}")

           # Check puzzles are solvable
           for puzzle in game_data.puzzles:
               if not self.check_solvable(puzzle, game_data):
                   issues.append(f"Puzzle {puzzle.id} may not be solvable")

           # Check for dead ends
           dead_ends = self.find_dead_ends(game_data)
           if dead_ends:
               issues.append(f"Dead ends found: {dead_ends}")

           return ValidationResult(issues)
   ```

2. Implement validation checks:
   - Scene connectivity (graph traversal)
   - Puzzle solvability (prerequisite chain analysis)
   - Dead end detection
   - Missing required items
   - Broken NPC dialogues
   - Invalid scene exits

3. Add automated fix suggestions:
   - Suggest connections for orphaned scenes
   - Identify missing puzzle items
   - Recommend dialogue improvements

Success Criteria:
✅ Validator detects all major playability issues
✅ Validation report is clear and actionable
✅ No false positives in validation
✅ Integration with content loader

Validation:
- tests/test_game_validator.py with broken content
```

**Chunk 4.6: Demo Game & Integration** 🔴 SERIAL - CRITICAL PATH
```yaml
Objective: Create complete demo game and CLI interface
Agent: implementation-agent or general-purpose agent
Scope: End-to-end integration
Execution Mode: SERIAL (after 4.1-4.5)
Prerequisites: Chunks 4.1-4.5 complete

Tasks:
1. Create demo_game.py entry point:
   - File: src/space_hulk_game/demo_game.py
   - Load generated content from game-config/
   - Initialize engine
   - Run game loop
   - Handle player input/output

2. Add CLI formatting:
   - Colorized output for different text types
   - ASCII art title screen
   - Help system
   - Save/load menu

3. Create end-to-end test:
   - Generate game with crew
   - Load into engine
   - Run automated playthrough
   - Validate game completes successfully

4. Documentation:
   - docs/GAME_ENGINE.md architecture guide
   - docs/PLAYING_GAMES.md player guide
   - README.md updated with engine info

Success Criteria:
✅ Demo game runs from command line
✅ Can generate → load → play complete workflow
✅ Automated playthrough works
✅ Documentation complete

Deliverables:
- Playable demo game
- CLI interface
- Integration tests
- Documentation
```

---

### Phase 5: Output Validation with Pydantic

**Duration:** 2-3 weeks
**Goal:** Ensure all generated outputs follow defined schemas and are valid
**Prerequisites:** Phase 0 validation complete

#### Work Chunks for Agents

**Chunk 5.1: Pydantic Models Definition** 🔴 SERIAL
```yaml
Objective: Define Pydantic models for all output types
Agent: implementation-agent or general-purpose agent
Scope: Schema definition

Tasks:
1. Create PlotOutline model:
   - File: src/space_hulk_game/schemas/plot_outline.py
   ```python
   from pydantic import BaseModel, Field, validator

   class PlotBranch(BaseModel):
       path: str = Field(..., min_length=1)
       description: str = Field(..., min_length=50)

   class Ending(BaseModel):
       name: str = Field(..., min_length=1)
       description: str = Field(..., min_length=50)
       type: str = Field(..., regex="^(victory|defeat|neutral)$")

   class PlotOutline(BaseModel):
       title: str = Field(..., min_length=1, max_length=200)
       setting: str = Field(..., min_length=50)
       themes: List[str] = Field(..., min_items=1)
       tone: str
       main_branches: List[PlotBranch] = Field(..., min_items=2)
       endings: List[Ending] = Field(..., min_items=2)

       @validator('main_branches')
       def validate_branches(cls, v):
           if len(v) < 2:
               raise ValueError("Must have at least 2 branching paths")
           return v
   ```

2. Create NarrativeMap model:
   - File: src/space_hulk_game/schemas/narrative_map.py
   - Models: Scene, Connection, NarrativeMap

3. Create PuzzleDesign model:
   - File: src/space_hulk_game/schemas/puzzle_design.py
   - Models: Puzzle, Artifact, Monster, NPC

4. Create SceneText model:
   - File: src/space_hulk_game/schemas/scene_text.py

5. Create GameMechanics model:
   - File: src/space_hulk_game/schemas/game_mechanics.py

Success Criteria:
✅ All 5 output types have Pydantic models
✅ Models include field validation
✅ Custom validators for complex rules
✅ Models documented with examples

Deliverables:
- src/space_hulk_game/schemas/ with 5 model files
```

**Chunk 5.2: Schema Validators** 🔴 SERIAL
```yaml
Objective: Implement validators that parse and validate outputs
Agent: implementation-agent or general-purpose agent
Scope: Validation logic
Prerequisites: Chunk 5.1 complete

Tasks:
1. Create OutputValidator class:
   - File: src/space_hulk_game/validation/validator.py
   ```python
   class OutputValidator:
       def validate_plot(self, raw_output: str) -> ValidationResult:
           try:
               data = yaml.safe_load(raw_output)
               plot = PlotOutline(**data)
               return ValidationResult(valid=True, data=plot)
           except Exception as e:
               return ValidationResult(
                   valid=False,
                   errors=[str(e)],
                   data=None
               )
   ```

2. Implement validators for each output type
3. Create ValidationResult class
4. Add detailed error messages

Success Criteria:
✅ All validators work correctly
✅ Error messages are specific and helpful
✅ Valid outputs parse successfully
✅ Invalid outputs are caught with clear errors

Validation:
- tests/test_validators.py with valid/invalid samples
```

**Chunk 5.3: Auto-Correction** 🔴 SERIAL
```yaml
Objective: Attempt to auto-fix common validation errors
Agent: implementation-agent or general-purpose agent
Scope: Error recovery
Prerequisites: Chunk 5.2 complete

Tasks:
1. Create OutputCorrector class:
   - File: src/space_hulk_game/validation/corrector.py
   - Auto-fix common issues:
     - Add missing required fields with defaults
     - Fix formatting problems
     - Correct YAML syntax errors
     - Normalize field names

2. Implement correction strategies for each output type
3. Log all corrections for transparency
4. Validate corrected output

Success Criteria:
✅ Common errors are auto-fixed
✅ Corrections are logged
✅ Corrected output is valid
✅ Doesn't over-correct (preserves intent)

Validation:
- tests/test_corrector.py with common errors
```

**Chunk 5.4: Integration with Tasks** 🔴 SERIAL
```yaml
Objective: Wire up validation into task execution
Agent: implementation-agent or general-purpose agent
Scope: Task integration
Prerequisites: Chunks 5.2-5.3 complete

Tasks:
1. Add validation hooks to crew.py:
   - Validate after each task completes
   - Attempt auto-correction if validation fails
   - Log validation results
   - Optionally retry task if validation fails critically

2. Update tasks.yaml with validation config:
   - Specify schema for each task
   - Set validation strictness level

3. Add validation metrics to output metadata

Success Criteria:
✅ All task outputs are validated
✅ Validation results logged
✅ Auto-correction activates when needed
✅ 95%+ of generations produce valid output

Validation:
- tests/test_validation_integration.py
```

---

### Phase 6: Enhanced Memory System

**Duration:** 2 weeks
**Goal:** Fully utilize mem0 for cross-agent collaboration and learning
**Prerequisites:** Phase 0 validation complete

#### Work Chunks for Agents

**Chunk 6.1: Memory Schema Design** 🔴 SERIAL FIRST
```yaml
Objective: Define what to store in mem0
Agent: design-agent or general-purpose agent
Scope: Schema specification

Tasks:
1. Design memory schemas:
   - NARRATIVE_CONTEXT: themes, tone, setting, constraints
   - DESIGN_DECISIONS: decision, rationale, agent, timestamp
   - QUALITY_FEEDBACK: component, issue, suggestion, resolved
   - GENERATED_CONTENT: type, id, summary, tags
   - File: src/space_hulk_game/memory/schemas.py

2. Define memory types and relationships
3. Plan memory lifecycle (creation, update, retrieval)

Success Criteria:
✅ Clear schema for each memory type
✅ Relationships between memory types defined
✅ Lifecycle documented

Deliverables:
- Memory schema documentation
```

**Chunk 6.2: Memory Manager Implementation** 🔴 SERIAL
```yaml
Objective: Create manager for mem0 operations
Agent: implementation-agent or general-purpose agent
Scope: Memory operations
Prerequisites: Chunk 6.1 complete

Tasks:
1. Create MemoryManager class:
   - File: src/space_hulk_game/memory/manager.py
   - Methods for storing/retrieving each memory type
   - Integration with mem0 client

2. Implement memory operations:
   - store_narrative_context()
   - store_design_decision()
   - store_quality_feedback()
   - get_relevant_context()
   - get_feedback_history()

Success Criteria:
✅ All memory operations work
✅ Integration with mem0 successful
✅ Memory persists across sessions

Validation:
- tests/test_memory_manager.py
```

**Chunk 6.3: Agent Integration** 🟠 CAN PARALLEL
```yaml
Objective: Give agents access to memory
Agent: implementation-agent or general-purpose agent
Scope: Agent enhancement
Prerequisites: Chunk 6.2 complete

Tasks:
1. Add memory access to agent tools
2. Update agent prompts to use memory context
3. Test cross-agent context sharing

Success Criteria:
✅ Agents can access memory
✅ Context flows between agents
✅ Memory improves output quality

Validation:
- tests/test_agent_memory.py
```

**Chunk 6.4: Cross-Session Learning** 🟠 CAN PARALLEL
```yaml
Objective: Enable improvement across generations
Agent: implementation-agent or general-purpose agent
Scope: Learning system
Prerequisites: Chunk 6.3 complete

Tasks:
1. Create LearningSystem class:
   - Record generation metrics
   - Identify successful patterns
   - Retrieve patterns for new generations

2. Integrate with crew workflow

Success Criteria:
✅ Successful patterns recorded
✅ Patterns used in future generations
✅ Quality improves over time

Validation:
- tests/test_learning.py with multiple generations
```

---

### Phase 7: Production Polish

**Duration:** 2 weeks
**Goal:** Make system production-ready
**Prerequisites:** Phases 0, 4 complete (3, 5, 6 optional)

#### Work Chunks for Agents

**Chunk 7.1: Logging & Monitoring** 🟢 PARALLEL - INDEPENDENT
```yaml
Objective: Add structured logging and metrics
Agent: implementation-agent
Scope: Observability

Tasks:
1. Implement structured logging with structlog
2. Add metrics collection
3. Create performance dashboard

Success Criteria:
✅ Comprehensive logging
✅ Metrics tracked
✅ Easy to debug issues

Deliverables:
- Logging configuration
- Metrics collectors
```

**Chunk 7.2: Example Games** 🟢 PARALLEL - INDEPENDENT
```yaml
Objective: Create 3+ example games
Agent: content-agent
Scope: Examples and templates

Tasks:
1. Generate space_horror example
2. Generate mystery_investigation example
3. Generate survival_escape example
4. Document each example

Success Criteria:
✅ 3 complete example games
✅ All examples playable
✅ Documentation for each

Deliverables:
- examples/ directory with 3 games
```

**Chunk 7.3: Documentation** 🟢 PARALLEL - INDEPENDENT
```yaml
Objective: Write comprehensive documentation
Agent: documentation-agent
Scope: User and developer docs

Tasks:
1. Update README.md
2. Write USER_GUIDE.md
3. Write DEVELOPER_GUIDE.md
4. Document all APIs
5. Create troubleshooting guide

Success Criteria:
✅ All documentation complete
✅ Clear and comprehensive
✅ Examples included

Deliverables:
- Complete documentation set
```

**Chunk 7.4: Performance Optimization** 🟢 PARALLEL - INDEPENDENT
```yaml
Objective: Optimize performance
Agent: optimization-agent
Scope: Speed improvements

Tasks:
1. Profile slow operations
2. Optimize LLM calls
3. Add caching where appropriate
4. Enable parallel execution

Success Criteria:
✅ Generation time < 5 minutes
✅ Reduced API calls
✅ Better resource usage

Validation:
- Performance benchmarks
```

---

## Success Criteria

### Overall Project Success

- [ ] Can generate playable games from simple prompts
- [ ] Games are narratively coherent
- [ ] Puzzles are solvable
- [ ] Quality consistently good (8+/10)
- [ ] Generation time < 5 minutes
- [ ] System is maintainable and documented

---

## Resource Requirements

**Development Time:** 8-10 weeks at 10-15 hours/week = 80-150 hours total

**Compute Resources:**
- Local: Ollama with 8GB+ VRAM (recommended)
- Cloud: Optional API access for complex tasks
- Storage: ~100MB for generated games

**Dependencies:**
- Current: CrewAI, Ollama, mem0, PyYAML, unittest
- New: Pydantic v2, structlog

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Quality varies widely | Quality metrics + retry logic |
| Game engine too complex | Start minimal, add features incrementally |
| Ollama model limitations | Multi-model support + cloud fallback |
| Scope creep | Strict phase boundaries, MVP focus |
| Timeline overruns | Buffer time, can ship after Phase 4 |

---

## Next Actions

### Immediate (This Week)
1. [ ] Review and approve this master plan
2. [ ] Execute Chunk 0.1: Sequential validation (5 tasks)
3. [ ] Execute Chunk 0.2: Sequential validation (11 tasks)
4. [ ] Execute Chunk 0.3: Reliability testing

### This Month
- [ ] Complete Phase 0 validation
- [ ] Begin Phase 4 (Game Engine) - CRITICAL PATH
- [ ] Optionally begin Phase 3 (Quality System)

### Next Month
- [ ] Complete Phase 4 (Game Engine)
- [ ] Complete Phase 3 (Quality System)
- [ ] Begin Phase 5 (Validation) and Phase 6 (Memory)

### Month 3
- [ ] Complete Phases 5 and 6
- [ ] Complete Phase 7 (Production Polish)
- [ ] Production-ready release

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-09 | 2.0 | Unified plan created from PROJECT_RESTART_PLAN + REVISED_RESTART_PLAN |
| 2025-11-08 | 1.1 | REVISED_RESTART_PLAN created with Phase 0 focus |
| 2025-11-08 | 1.0 | PROJECT_RESTART_PLAN created |

---

## Related Documents

- [progress.md](progress.md) - Project progress tracking
- [CREWAI_IMPROVEMENTS.md](CREWAI_IMPROVEMENTS.md) - Phase 0 implementation details
- [phase1_implementation_plan.md](phase1_implementation_plan.md) - Historical Phase 1 reference
- [phase2_implementation_plan.md](phase2_implementation_plan.md) - Historical Phase 2 reference
- [CLAUDE.md](../../CLAUDE.md) - Project overview and coding standards

---

**End of Master Implementation Plan**
