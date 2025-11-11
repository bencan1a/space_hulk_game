# Agent Work Assignment - Prompt Template

Use this template when assigning work chunks to agents.

---

## Standard Work Assignment Prompt

```
Execute **Chunk [X.Y]** from the restart project implementation plan.

**Instructions:**
1. Open project-plans/restart-project/master_implementation_plan.md
2. Find Chunk [X.Y] in the plan and read its complete specification
3. The specification contains everything you need:
   - Objective and scope
   - Prerequisites to verify
   - Tasks to execute (numbered list)
   - Success criteria checklist
   - Deliverables and their locations
   - Validation requirements
4. Verify all prerequisites are met before starting
5. Execute each task in order, following the specification exactly
6. Validate your work against all success criteria
7. Update project-plans/restart-project/progress.md with your results

**Important:**
- Follow the chunk specification exactly as written
- Do not skip steps or take shortcuts
- If you encounter blockers, document them and stop
- All code must follow standards in CLAUDE.md
- All tests must pass before marking complete
```

---

## Quick Assignment (Minimal Version)

For experienced agents who know the project:

```
Execute Chunk [X.Y] per master_implementation_plan.md
Report results in progress.md when complete.
```

---

## Example: Assigning Chunk 0.1

```
Execute **Chunk 0.1** from the restart project implementation plan.

**Instructions:**
1. Open project-plans/restart-project/master_implementation_plan.md
2. Find Chunk 0.1 in the plan and read its complete specification
3. The specification contains everything you need:
   - Objective: Validate sequential mode completes with 5 core tasks
   - Prerequisites: None (first validation chunk)
   - Tasks: 5 specific steps including commenting out evaluation tasks, running the crew, and validating outputs
   - Success Criteria: All 5 core tasks complete without errors, valid YAML outputs, completion < 10 minutes
   - Validation Script: tests/test_sequential_5_tasks.py (to be created)
   - Deliverables: Test results, validation script, generated game-config/*.yaml files
4. Verify prerequisites (none for this chunk - ready to start)
5. Execute each task in order, following the specification exactly
6. Validate your work against all success criteria
7. Update project-plans/restart-project/progress.md with your results

**Important:**
- Follow the chunk specification exactly as written
- Monitor for hanging/timeout issues
- Document all outputs generated
- Validate YAML syntax for all output files
- If generation hangs, note the timeout duration
```

---

## Example: Assigning Chunk 4.1

```
Execute **Chunk 4.1** from the restart project implementation plan.

**Instructions:**
1. Open project-plans/restart-project/master_implementation_plan.md
2. Find Chunk 4.1 in Phase 4 and read its complete specification
3. The specification contains everything you need:
   - Objective: Implement game state data models
   - Prerequisites: Phase 0 validation complete, sequential mode proven
   - Tasks: Create engine directory, implement GameState, Scene, and supporting classes
   - Success Criteria: All classes implemented with type hints, tests pass
   - Deliverables: game_state.py, scene.py, entities.py, and test files
4. Verify prerequisites are met before starting
5. Execute each task in order, following the specification exactly
6. Validate your work against all success criteria
7. Update project-plans/restart-project/progress.md with your results

**Important:**
- Use Python dataclasses as shown in spec
- Include all type hints
- Follow PEP 8 standards
- Add docstrings with examples
- Make classes immutable where appropriate
```

---

## Parallel Execution Template

When assigning multiple chunks to run in parallel:

```
Execute these chunks in parallel: **[X.Y]**, **[A.B]**, **[C.D]**

**Instructions:**
1. Open project-plans/restart-project/master_implementation_plan.md
2. For EACH chunk listed above:
   - Find it in the plan and read its complete specification
   - Verify it has no dependencies on the other chunks in this list
   - Execute its tasks independently
   - Validate against its success criteria
   - Produce its deliverables
3. If you discover any dependencies between chunks, STOP and report
4. Update project-plans/restart-project/progress.md with results for ALL chunks

**Important:**
- These chunks should be truly independent
- Don't let one chunk's failure block others
- Report total time for parallel execution
```

---

## Troubleshooting Template

If an agent gets stuck or has questions:

```
I'm working on **Chunk [X.Y]** and need clarification.

**What I've Done:**
[List completed steps from the chunk specification]

**Where I'm Stuck:**
[Specific issue or question - reference which task number from the spec]

**What I've Tried:**
[Attempted solutions]

**What I Need:**
[Specific help needed]

**Context:**
- Currently executing task [number] from Chunk [X.Y] specification
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
[Copy the criteria from the chunk spec and mark each]
- ✅ [Criterion 1]
- ✅ [Criterion 2]
- ✅ [Criterion 3]

**Deliverables Created:**
[List from chunk specification]
- [File/artifact 1]
- [File/artifact 2]

**Validation Results:**
- Tests pass: [X/Y]
- Code quality: [Pass/Fail]
- Documentation: [Complete/Incomplete]

**Issues Encountered:**
[List any issues and how resolved, or "None"]

**Next Recommended Action:**
[Check master_implementation_plan.md for next chunk or dependencies]

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
