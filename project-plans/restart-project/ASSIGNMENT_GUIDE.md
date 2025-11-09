# Agent Assignment Guide

**Quick reference for assigning work to agents**

---

## Standard Assignment Prompt

```
I need you to execute a specific work chunk from our implementation plan.

**Project Context:**
This is the Space Hulk text-based adventure game generator project using CrewAI
multi-agent orchestration. Review: project-plans/restart-project/master_implementation_plan.md

**Your Assignment:**
Execute **Chunk [X.Y]: [Chunk Name]** from Phase [X]

**Location:**
project-plans/restart-project/master_implementation_plan.md → Phase [X] → Chunk [X.Y]

**Prerequisites:**
[List prerequisites or "None - ready to start"]

**Instructions:**
1. Read the full chunk specification
2. Execute each task in order
3. Validate against success criteria
4. Produce all deliverables
5. Update project-plans/restart-project/progress.md with results

**Important:**
- Follow CLAUDE.md coding standards
- All tests must pass
- Document any blockers immediately
```

---

## Current Assignments (Nov 9, 2025)

### Available Now

**Chunk 0.1** 🔴 BLOCKING
```
Execute Chunk 0.1: Sequential Mode Validation (5 Core Tasks) from Phase 0

Prerequisites: None - ready to start

This is our HIGHEST PRIORITY task. It validates the basic crew works.
```

### After 0.1 Completes

**Chunk 0.2** 🔴 BLOCKING
```
Execute Chunk 0.2: Sequential Mode Validation (All 11 Tasks) from Phase 0

Prerequisites: Chunk 0.1 complete

Validates full workflow including evaluation tasks.
```

### After 0.2 Completes

**Chunk 0.3** 🔴 BLOCKING
```
Execute Chunk 0.3: Reliability Testing from Phase 0

Prerequisites: Chunks 0.1 and 0.2 complete

Runs 3 consecutive tests to prove reliability.
```

---

## Parallel Assignments (After Phase 0)

Once Phase 0 completes, you can assign these in parallel:

### Critical Path (Priority 1)
```
Agent 1: Execute Chunk 4.1: Game State Model from Phase 4
Prerequisites: Phase 0 complete
```

### Enhancement Track (Priority 2)
```
Agent 2: Execute Chunk 3.4: Planning Templates from Phase 3
Prerequisites: Phase 0 complete

Agent 3: Execute Chunk 6.1: Memory Schema Design from Phase 6
Prerequisites: Phase 0 complete
```

---

## Assignment Examples

### Example 1: Chunk 0.1 (Current)

```
I need you to execute a specific work chunk from our implementation plan.

**Project Context:**
Space Hulk game generator using CrewAI. Phase 0 is proving the basic system works.
Review: project-plans/restart-project/master_implementation_plan.md

**Your Assignment:**
Execute **Chunk 0.1: Sequential Mode Validation (5 Core Tasks)** from Phase 0

**Location:**
project-plans/restart-project/master_implementation_plan.md → Phase 0 → Chunk 0.1

**Prerequisites:**
None - ready to start

**Instructions:**
1. Read the full chunk specification in master_implementation_plan.md
2. Comment out evaluation tasks as specified
3. Run crew with test prompt
4. Validate all 5 YAML outputs
5. Document execution time and any issues
6. Update progress.md with results

**Important:**
- This is BLOCKING - all other work waits for this
- Monitor for hanging (15min timeout)
- Document exact behavior if errors occur
- Generation should complete in < 10 minutes
```

### Example 2: Chunk 4.1 (After Phase 0)

```
I need you to execute a specific work chunk from our implementation plan.

**Project Context:**
Space Hulk game generator. Building game engine to validate generated content.
Review: project-plans/restart-project/master_implementation_plan.md

**Your Assignment:**
Execute **Chunk 4.1: Game State Model** from Phase 4

**Location:**
project-plans/restart-project/master_implementation_plan.md → Phase 4 → Chunk 4.1

**Prerequisites:**
Phase 0 complete (sequential mode validated)

**Instructions:**
1. Read the full chunk specification (includes code examples)
2. Create src/space_hulk_game/engine/ directory
3. Implement GameState, Scene, and entity classes as specified
4. Add type hints and docstrings
5. Write unit tests for all classes
6. Update progress.md with results

**Important:**
- This is CRITICAL PATH for MVP
- Follow code examples in chunk spec
- Use Python dataclasses
- All tests must pass before marking complete
```

### Example 3: Parallel Assignment

```
I need you to execute multiple work chunks in parallel.

**Project Context:**
Space Hulk game generator. Phase 0 complete, starting enhancement tracks.

**Your Assignments (Execute in Parallel):**
1. **Chunk 4.1**: Game State Model (Critical Path)
2. **Chunk 3.4**: Planning Templates (Independent)

**Why Parallel:**
These chunks are independent and can run simultaneously.

**Instructions:**
For EACH chunk:
1. Read its specification in master_implementation_plan.md
2. Execute its tasks independently
3. Validate against its success criteria
4. Produce its deliverables

**Reporting:**
Update progress.md with results for BOTH chunks, noting total parallel execution time.
```

---

## Quick Assignments (Experienced Agents)

For agents familiar with the project:

```
Execute Chunk [X.Y] from Phase [X]
Prerequisites: [List or "None"]
Report in progress.md when complete.
```

---

## Troubleshooting Assignments

If agent reports issues:

```
I'm investigating the issue you encountered with Chunk [X.Y].

**What I Need:**
1. Exact error message or behavior
2. Which step you were on when it failed
3. What you've tried
4. Relevant log excerpts

**Don't:**
- Continue past the failure
- Make assumptions about the cause
- Try fixes not in the spec

**Do:**
- Document exactly what happened
- Report and wait for guidance
- Preserve all error logs
```

---

## Assignment Checklist

Before assigning:
- [ ] Phase 0 complete? (if assigning Phase 3-7)
- [ ] Prerequisites met?
- [ ] Chunk indicator checked? (🔴 🟡 🟠 🟢)
- [ ] Clear about deliverables?
- [ ] Agent has access to master plan?

After assignment:
- [ ] Agent acknowledged?
- [ ] Execution started?
- [ ] Progress updates received?
- [ ] Results documented in progress.md?
- [ ] Next chunk identified?

---

## Links

- [Master Implementation Plan](master_implementation_plan.md) - Complete roadmap
- [Agent Work Templates](AGENT_WORK_TEMPLATE.md) - Detailed examples
- [Quick Start Guide](QUICK_START.md) - Agent quick reference
- [Progress Tracker](progress.md) - Where agents report

---

**Last Updated:** November 9, 2025
