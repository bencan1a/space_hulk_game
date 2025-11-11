# Linter Fix Parallelization Plan

## Summary of Issues

**Total Issues:** ~100+ across all categories
- **Ruff errors:** ~80 issues
- **Bandit security warnings:** ~12 issues
- **Pylint errors:** ~8 issues

## Parallelization Strategy

Split work into 6 independent sub-agent tasks that can run in parallel with minimal file conflicts.

---

## Task 1: Path Operations Fixes (Priority: High)
**Agent:** path-operations-agent
**Files:** All files with PTH* errors
**Estimated fixes:** ~40 issues

### Files to modify:
- `src/space_hulk_game/crew.py` (10 instances)
- `src/space_hulk_game/engine/loader.py` (7 instances)
- `src/space_hulk_game/engine/persistence.py` (4 instances)
- `src/space_hulk_game/quality/*.py` (multiple files)
- `tests/*.py` (multiple files)
- `tools/*.py` (multiple files)

### Pattern to fix:
```python
# Before:
os.path.dirname(x)  -> PTH120
os.path.abspath(x)  -> PTH100
os.path.join(a, b)  -> PTH118
os.path.exists(x)   -> PTH110
open(filepath, 'r') -> PTH123

# After:
from pathlib import Path
Path(x).parent
Path(x).resolve()
Path(a) / b
Path(x).exists()
Path(filepath).open('r')
```

### Commands:
```bash
# Agent can use ruff to auto-fix many of these:
ruff check --select PTH --fix src/space_hulk_game/
ruff check --select PTH --fix tests/
ruff check --select PTH --fix tools/
```

---

## Task 2: Character Encoding & Code Cleanup (Priority: High)
**Agent:** encoding-cleanup-agent
**Files:** crew.py, parser.py, and others with RUF/ERA errors
**Estimated fixes:** ~15 issues

### Sub-tasks:
1. **Ambiguous characters (RUF001, RUF002):** Replace EN DASH (–) with HYPHEN-MINUS (-)
   - `src/space_hulk_game/crew.py:478` (docstring)
   - `src/space_hulk_game/crew.py:519,521` (strings)

2. **Commented code (ERA001):** Remove or uncomment
   - `src/space_hulk_game/crew.py:1162-1164`
   - `src/space_hulk_game/engine/parser.py:248`
   - Various test files

### Commands:
```bash
ruff check --select RUF001,RUF002,ERA001 --fix src/
ruff check --select RUF001,RUF002,ERA001 --fix tests/
```

---

## Task 3: Code Quality Issues (Priority: Medium)
**Agent:** code-quality-agent
**Files:** demo_game.py, engine/*.py, various test files
**Estimated fixes:** ~20 issues

### Issues to fix:
1. **Unused arguments (ARG001):**
   - `src/space_hulk_game/demo_game.py:42` - remove or use `kwargs`

2. **Nested if statements (SIM102):**
   - `src/space_hulk_game/demo_game.py:339,459` - flatten conditions

3. **Unused variables (F841):**
   - `src/space_hulk_game/engine/engine.py:396` - remove `unlock_target`
   - Various test files

4. **Loop variable binding (B023):**
   - `src/space_hulk_game/crew.py:535,593` - fix closure issue in callbacks

### Pattern for B023 fix:
```python
# Before (BROKEN):
for filepath in files:
    callbacks.append(lambda x: process(filepath, x))  # BUG: captures last filepath

# After (FIXED):
for filepath in files:
    callbacks.append(lambda x, fp=filepath: process(fp, x))  # captures current value
```

---

## Task 4: Type Hints & Annotations (Priority: Medium)
**Agent:** type-hints-agent
**Files:** parser.py, persistence.py, various engine files
**Estimated fixes:** ~10 issues

### Issues to fix:
1. **ClassVar annotations (RUF012):**
   - `src/space_hulk_game/engine/parser.py:75` - add `typing.ClassVar`

2. **Implicit Optional (RUF013):**
   - `src/space_hulk_game/engine/persistence.py:36,362,363`
   - Various other files

### Pattern:
```python
# Before:
class Foo:
    shared_dict = {}  # RUF012

def bar(x: str = None):  # RUF013
    pass

# After:
from typing import ClassVar, Optional

class Foo:
    shared_dict: ClassVar[dict] = {}

def bar(x: Optional[str] = None):
    pass
```

---

## Task 5: Function Complexity Refactoring (Priority: Low)
**Agent:** refactoring-agent
**Files:** crew.py, engine.py, parser.py
**Estimated fixes:** ~5 issues

### Issues to fix:
1. **Too many statements (PLR0915, R0915):**
   - `src/space_hulk_game/crew.py:472` (66 statements)
   - `src/space_hulk_game/engine/engine.py:342` (56 statements)

2. **Too many return statements (PLR0911):**
   - `src/space_hulk_game/engine/parser.py:99` (12 returns)

### Strategy:
- Extract helper methods
- Use early returns
- Simplify conditional logic
- Consider state pattern or strategy pattern

---

## Task 6: Security Issues (Priority: Medium)
**Agent:** security-agent
**Files:** test files and tools/
**Estimated fixes:** ~12 issues

### Issues to fix:
1. **Test file hardcoded passwords (B105, B101):**
   - Add `# noqa: S105` or `# nosec` annotations
   - These are test fixtures, not real secrets

2. **Assert statements in tests (B101, S101):**
   - Add `# noqa: S101` to test files (standard unittest pattern)

3. **Tools subprocess usage (B404, B603, B607):**
   - `tools/build_context.py` - add security checks or noqa
   - Validate input paths

4. **Try-except-pass (B110):**
   - `tools/configure_mem0.py:200,587` - add logging

5. **Requests without timeout (B113):**
   - `tools/kloc-report.py:157,246,252` - add timeout parameter

### Pattern for tests:
```python
# Add at top of test files:
# ruff: noqa: S101, S105, B101

# Or per-line:
assert foo == bar  # noqa: S101
password = "test123"  # noqa: S105
```

### Pattern for requests:
```python
# Before:
resp = requests.get(url, headers=headers)

# After:
resp = requests.get(url, headers=headers, timeout=30)
```

---

## Execution Order

### Phase 1: Independent fixes (can run in parallel)
- Task 1: Path Operations (Agent 1)
- Task 2: Character Encoding & Cleanup (Agent 2)
- Task 6: Security Issues (Agent 3)

### Phase 2: Code quality fixes (can run in parallel after Phase 1)
- Task 3: Code Quality Issues (Agent 4)
- Task 4: Type Hints (Agent 5)

### Phase 3: Complex refactoring (after all above complete)
- Task 5: Function Complexity (Agent 6)

---

## Sub-Agent Invocation Commands

```bash
# Phase 1 (parallel)
Task(subagent_type="general-purpose", description="Fix path operations", prompt="...")
Task(subagent_type="general-purpose", description="Fix character encoding", prompt="...")
Task(subagent_type="general-purpose", description="Fix security annotations", prompt="...")

# Phase 2 (parallel)
Task(subagent_type="general-purpose", description="Fix code quality issues", prompt="...")
Task(subagent_type="general-purpose", description="Fix type hints", prompt="...")

# Phase 3 (sequential)
Task(subagent_type="general-purpose", description="Refactor complex functions", prompt="...")
```

---

## Verification

After each phase, run:
```bash
pre-commit run --all-files
```

Track progress:
- Phase 1 completion: ~65 issues fixed
- Phase 2 completion: ~95 issues fixed
- Phase 3 completion: ~100 issues fixed (ALL CLEAR)

---

## Notes

- **File conflicts:** Minimal expected due to file/task separation
- **Testing:** Run `make test` after all fixes to ensure no breakage
- **Git strategy:** Consider one commit per phase or per task
- **Time estimate:**
  - Phase 1: 15-20 minutes per agent
  - Phase 2: 10-15 minutes per agent
  - Phase 3: 20-30 minutes
  - Total: ~2 hours with parallel execution
