# Quick Start Guide for Agents

**Last Updated:** November 9, 2025

---

## Overview

You're working on the Space Hulk game generator project. This guide helps you quickly understand what to do.

---

## 📋 Your Essential Documents

1. **[master_implementation_plan.md](master_implementation_plan.md)** - The complete plan with all work chunks
2. **[AGENT_WORK_TEMPLATE.md](AGENT_WORK_TEMPLATE.md)** - How to receive and execute assignments
3. **[progress.md](progress.md)** - Where to report your results

---

## 🎯 Standard Assignment Format

You'll receive assignments like this:

```
Execute Chunk [X.Y]: [Name]
Prerequisites: [List or "None"]
```

### What To Do

1. **Open:** [master_implementation_plan.md](master_implementation_plan.md)
2. **Find:** Your chunk (search for "Chunk X.Y")
3. **Read:** The full specification (Objective, Tasks, Success Criteria)
4. **Check:** Prerequisites are met (look at the colored indicator)
5. **Execute:** Each task in order
6. **Validate:** Against success criteria
7. **Report:** Results in [progress.md](progress.md)

---

## 🚦 Understanding the Indicators

Every chunk has a colored indicator showing when it can run:

- **🔴 SERIAL - BLOCKING** → Must finish before ANYTHING else can start
- **🔴 SERIAL - CRITICAL PATH** → Required for MVP, must finish in order
- **🔴 SERIAL** → Must finish before next task in sequence
- **🟡 SERIAL - OPTIONAL** → Not required for MVP
- **🟠 CAN PARALLEL** → Can overlap with some other work
- **🟢 PARALLEL - INDEPENDENT** → Can run anytime after prerequisites

**Rule of Thumb:**

- See 🔴? Must wait for prerequisites to finish
- See 🟢? Can start immediately after prerequisites
- See 🟠? Ask about parallelization strategy

---

## 📝 Reporting Template

When you finish a chunk, update [progress.md](progress.md) with:

```markdown
### [Date]

**Chunk X.Y - COMPLETED** ✅

**Execution:**
- Duration: [time]
- Issues: [any problems or "None"]

**Success Criteria:**
- ✅ [Criterion 1]
- ✅ [Criterion 2]

**Deliverables:**
- [File 1]
- [File 2]

**Next:** Ready for Chunk [X.Y+1]
```

---

## 🎯 Current Status (Week of Nov 9, 2025)

**Current Phase:** Phase 0 - Validation
**Current Priority:** Prove sequential mode works

**Available Chunks:**

- **Chunk 0.1** 🔴 BLOCKING - Sequential validation (5 tasks) - Ready to start
- **Chunk 0.2** 🔴 BLOCKING - Sequential validation (11 tasks) - Waiting for 0.1
- **Chunk 0.3** 🔴 BLOCKING - Reliability testing - Waiting for 0.2

**Next After Phase 0:**

- **Track A:** Chunk 4.1 (Game Engine) - CRITICAL PATH
- **Track B:** Chunk 3.4 (Planning Templates) - Can run in parallel
- **Track C:** Chunk 6.1 (Memory Schema) - Can run in parallel

---

## ⚠️ Common Mistakes to Avoid

**DON'T:**

- ❌ Skip reading the full chunk specification
- ❌ Start before prerequisites are met
- ❌ Assume what's meant - ask for clarification
- ❌ Continue if you're blocked - report and stop
- ❌ Forget to update progress.md

**DO:**

- ✅ Read the entire chunk spec before starting
- ✅ Check prerequisites first
- ✅ Follow instructions exactly
- ✅ Validate your work
- ✅ Document everything

---

## 🔍 Finding Your Chunk

### Method 1: Search by Number

1. Open [master_implementation_plan.md](master_implementation_plan.md)
2. Search for `Chunk X.Y` (e.g., "Chunk 0.1")
3. Read from the chunk header to the end of the code block

### Method 2: Browse by Phase

1. Open [master_implementation_plan.md](master_implementation_plan.md)
2. Find your phase heading (e.g., "Phase 0")
3. Scroll to "Work Chunks for Agents" section
4. Find your chunk

---

## 📞 Questions?

**If blocked or unclear:**

1. Check [master_implementation_plan.md](master_implementation_plan.md) for details
2. Check [status_assessment.md](status_assessment.md) for context
3. Check [AGENT_WORK_TEMPLATE.md](AGENT_WORK_TEMPLATE.md) for examples
4. Ask for clarification (don't guess!)

**If you find an issue with the plan:**

1. Document it
2. Report it
3. Wait for guidance

---

## 🎓 Example Assignment

**Assignment:**

```
Execute Chunk 0.1: Sequential Mode Validation (5 Core Tasks)
Prerequisites: None
```

**Your Actions:**

1. ✅ Open master_implementation_plan.md
2. ✅ Search for "Chunk 0.1"
3. ✅ Read objective: "Validate sequential mode completes with 5 core tasks"
4. ✅ Check prerequisites: "None" → You can start
5. ✅ Execute 5 tasks listed
6. ✅ Validate against success criteria
7. ✅ Update progress.md with results

**Expected Deliverables:**

- Test results documented
- Generated game-config/*.yaml files (5 files)
- Validation script: tests/test_sequential_5_tasks.py
- Execution time noted
- Issues documented (if any)

**Success Looks Like:**

- ✅ All 5 core tasks complete
- ✅ All 5 YAML files exist and are valid
- ✅ Generation < 10 minutes
- ✅ No hanging/timeout

---

## 🚀 Ready to Start?

1. Wait for your assignment
2. Open [master_implementation_plan.md](master_implementation_plan.md)
3. Find your chunk
4. Execute it
5. Report results

Good luck! 🎯

---

**Quick Links:**

- [Master Plan](master_implementation_plan.md) - The complete roadmap
- [Agent Work Templates](AGENT_WORK_TEMPLATE.md) - How to work on chunks
- [Progress Tracker](progress.md) - Where to report
- [Status Assessment](status_assessment.md) - Current state
- [Project Overview](../../CLAUDE.md) - High-level context

---

**Last Updated:** November 9, 2025
