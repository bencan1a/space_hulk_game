# Agent Work Assignment - Prompt Template

Use this template when assigning work chunks to agents.

---

## Standard Work Assignment Prompt

```
I need you to execute a specific work chunk from our implementation plan.

**Project Context:**
This is the Space Hulk text-based adventure game generator project. We're using CrewAI with multi-agent orchestration to generate complete games. Review the project overview at: project-plans/restart-project/master_implementation_plan.md

**Your Assignment:**
Execute **Chunk [X.Y]: [Chunk Name]** from Phase [X]

**Location in Plan:**
Open: project-plans/restart-project/master_implementation_plan.md
Find: Phase [X] section, then locate Chunk [X.Y]

**What You'll Find:**
The chunk specification includes:
- Objective: What you're trying to achieve
- Agent: Who should do this (you)
- Scope: Boundaries of the work
- Tasks: Step-by-step instructions (numbered list)
- Success Criteria: How to know you're done (checklist)
- Deliverables: What artifacts to produce
- Validation: How to verify your work

**Prerequisites:**
[Check the plan - list any chunks that must complete first, or write "None - ready to start"]

**Instructions:**
1. Read the full chunk specification in master_implementation_plan.md
2. Verify all prerequisites are met
3. Execute each task in order
4. Validate your work against the success criteria
5. Produce all required deliverables
6. Document your work in project-plans/restart-project/progress.md

**Important Guidelines:**
- Follow the chunk specification exactly as written
- Do not skip steps or take shortcuts
- If you encounter blockers, document them and stop (don't guess)
- All code must follow standards in CLAUDE.md
- All tests must pass before marking complete
- Update progress.md with your results

**Deliverables Location:**
[Specify where outputs should go - usually mentioned in chunk spec]

**Reporting:**
When complete, update project-plans/restart-project/progress.md with:
1. Chunk X.Y completion status
2. Execution time
3. Any issues encountered
4. Validation results
5. Next recommended chunk (if known)

**Questions?**
If anything is unclear:
1. Check master_implementation_plan.md for details
2. Check status_assessment.md for context
3. Ask for clarification before proceeding
```

---

## Quick Assignment (Minimal Version)

For experienced agents who know the project:

```
Execute **Chunk [X.Y]** from Phase [X] in master_implementation_plan.md

Prerequisites: [List or "None"]
Report results in progress.md when complete.
```

---

## Example: Assigning Chunk 0.1

```
I need you to execute a specific work chunk from our implementation plan.

**Project Context:**
This is the Space Hulk text-based adventure game generator project. We're using CrewAI with multi-agent orchestration to generate complete games. Review the project overview at: project-plans/restart-project/master_implementation_plan.md

**Your Assignment:**
Execute **Chunk 0.1: Sequential Mode Validation (5 Core Tasks)** from Phase 0

**Location in Plan:**
Open: project-plans/restart-project/master_implementation_plan.md
Find: Phase 0 section, then locate Chunk 0.1

**What You'll Find:**
The chunk specification includes:
- Objective: Validate sequential mode completes with 5 core tasks
- Tasks: 5 specific steps including commenting out evaluation tasks, running the crew, and validating outputs
- Success Criteria: All 5 core tasks complete without errors, valid YAML outputs, completion < 10 minutes
- Validation Script: tests/test_sequential_5_tasks.py (to be created)

**Prerequisites:**
None - this is the first validation chunk, ready to start

**Instructions:**
1. Read the full chunk specification in master_implementation_plan.md
2. Execute each task in order (comment out evaluations, run crew, validate)
3. Validate your work against the success criteria
4. Create the validation script if needed
5. Document execution time and any errors
6. Update progress.md with results

**Important Guidelines:**
- Follow the chunk specification exactly as written
- Monitor for hanging/timeout issues
- Document all outputs generated
- Validate YAML syntax for all output files
- If generation hangs, note the timeout duration

**Deliverables Location:**
- Test results: Document in progress.md
- Validation script: tests/test_sequential_5_tasks.py
- Generated outputs: game-config/*.yaml (5 files expected)

**Reporting:**
When complete, update project-plans/restart-project/progress.md with:
1. Chunk 0.1 completion status (✅ or ❌)
2. Execution time (actual duration)
3. Any issues encountered (errors, warnings, hangs)
4. Validation results (which success criteria met)
5. Next step: Proceed to Chunk 0.2 if successful

**Questions?**
If the crew hangs or errors occur:
1. Document the exact error/behavior
2. Note which task was executing when it failed
3. Check logs for details
4. Report findings before attempting fixes
```

---

## Example: Assigning Chunk 4.1

```
I need you to execute a specific work chunk from our implementation plan.

**Project Context:**
This is the Space Hulk text-based adventure game generator project. We're building a game engine to validate generated content is playable.

**Your Assignment:**
Execute **Chunk 4.1: Game State Model** from Phase 4

**Location in Plan:**
Open: project-plans/restart-project/master_implementation_plan.md
Find: Phase 4 section, then locate Chunk 4.1

**What You'll Find:**
Complete data model specifications for GameState, Scene, and supporting classes with code examples and type hints.

**Prerequisites:**
- Phase 0 validation must be complete
- Sequential mode proven to work

**Instructions:**
1. Read the full chunk specification in master_implementation_plan.md
2. Create src/space_hulk_game/engine/ directory
3. Implement GameState class with all specified fields
4. Implement Scene class with all specified fields
5. Create supporting classes (Item, NPC, Event)
6. Add comprehensive docstrings and type hints
7. Write unit tests for all data models
8. Validate tests pass

**Important Guidelines:**
- Use Python dataclasses as shown in spec
- Include all type hints
- Follow PEP 8 standards
- Add docstrings with examples
- Make classes immutable where appropriate

**Deliverables Location:**
- src/space_hulk_game/engine/game_state.py
- src/space_hulk_game/engine/scene.py
- src/space_hulk_game/engine/entities.py
- tests/test_game_state.py
- tests/test_scene.py
- tests/test_entities.py

**Reporting:**
When complete, update project-plans/restart-project/progress.md with:
1. Chunk 4.1 completion status
2. All deliverables created
3. Test pass rate
4. Any design decisions made
5. Ready for Chunk 4.2 (Command Parser)

**Questions?**
Check the detailed code examples in the chunk specification before asking.
```

---

## Parallel Execution Template

When assigning multiple chunks to run in parallel:

```
I need you to execute multiple work chunks in parallel.

**Project Context:**
[Same as above]

**Your Assignments (Execute in Parallel):**
1. **Chunk [X.Y]**: [Name]
2. **Chunk [A.B]**: [Name]
3. **Chunk [C.D]**: [Name]

**Why Parallel:**
These chunks have no dependencies on each other and can be executed simultaneously to save time.

**Instructions:**
For EACH chunk:
1. Read its specification in master_implementation_plan.md
2. Execute its tasks independently
3. Validate against its success criteria
4. Produce its deliverables

**Reporting:**
Update progress.md with results for ALL chunks when complete:
- Which chunks completed successfully
- Which chunks encountered issues
- Total time for parallel execution
- Any discovered dependencies (if chunks interfered)

**Important:**
- Ensure chunks truly are independent
- If you discover a dependency, STOP and report
- Don't let one chunk's failure block others
```

---

## Troubleshooting Template

If an agent gets stuck or has questions:

```
I'm working on **Chunk [X.Y]** and need clarification.

**What I've Done:**
[List completed steps]

**Where I'm Stuck:**
[Specific issue or question]

**What I've Tried:**
[Attempted solutions]

**What I Need:**
[Specific help needed]

**Context:**
- Chunk: [X.Y]
- Phase: [X]
- Step: [number] in task list
- Error/Issue: [exact error or description]
```

---

## Completion Template

When agent finishes a chunk:

```
**Chunk [X.Y] - COMPLETED** ✅

**Execution Summary:**
- Start time: [timestamp]
- End time: [timestamp]
- Duration: [X hours/minutes]

**Success Criteria Met:**
- ✅ [Criterion 1]
- ✅ [Criterion 2]
- ✅ [Criterion 3]
[List all criteria with checkmarks]

**Deliverables Created:**
- [File/artifact 1]
- [File/artifact 2]
- [File/artifact 3]

**Validation Results:**
- Tests pass: [X/Y]
- Code quality: [Pass/Fail]
- Documentation: [Complete/Incomplete]

**Issues Encountered:**
[List any issues and how resolved, or "None"]

**Next Recommended Action:**
Proceed to Chunk [X.Y+1] OR [specify next step]

**Notes:**
[Any relevant observations or decisions made]
```

---

## Tips for Effective Agent Work

**Do:**
- ✅ Read the entire chunk specification before starting
- ✅ Follow instructions exactly as written
- ✅ Validate work against success criteria
- ✅ Document results thoroughly
- ✅ Ask for clarification when unclear
- ✅ Update progress.md regularly

**Don't:**
- ❌ Skip prerequisite checks
- ❌ Modify the plan without discussion
- ❌ Assume what's meant - ask
- ❌ Continue if blocked - report and stop
- ❌ Forget to validate before marking complete
- ❌ Leave undocumented decisions

---

**Last Updated:** November 9, 2025
**Template Version:** 1.0
