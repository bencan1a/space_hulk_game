# YAML Pipeline Refactor - Pre-Write Sanitization

## Executive Summary

**Problem**: The MD-to-YAML pipeline has 3 sophisticated validation layers that are NEVER invoked. CrewAI writes raw LLM output directly to disk, causing YAML syntax errors (mixed quotes, invalid list markers, unescaped apostrophes) to persist in files.

**Solution**: Implement pre-write sanitization by intercepting CrewAI's file write and applying existing validation/correction code BEFORE disk write.

**Status**: Planning complete, ready for implementation

---

## Architecture Overview

### Current (Broken) Flow
```
LLM Output → CrewAI Task._save_file() → Write to disk (corrupted)
                                       ↓
                             Post-cleanup (incomplete)
```

### New (Fixed) Flow
```
LLM Output → OutputSanitizer Pipeline → CrewAI Task._save_file() → Write to disk (clean)
              ├─ Strip markdown fences
              ├─ Fix syntax errors
              ├─ Validate schema
              └─ Auto-correct structure
```

---

## Phase 1: Core Sanitization (CRITICAL)

### Chunk 1: Create OutputSanitizer Class
**File**: `src/space_hulk_game/utils/output_sanitizer.py` (NEW)
**Dependencies**: None
**Parallel**: ✅ Can run in parallel with Chunks 2-3

**Tasks**:
1. Create OutputSanitizer class with sanitize() method
2. Orchestrate yaml_processor + corrector in correct order
3. Handle all 5 output types (plot, narrative, puzzle, scene, mechanics)
4. Implement graceful error handling and logging
5. Return sanitized YAML string

**Acceptance Criteria**:
- [ ] OutputSanitizer class exists
- [ ] sanitize(raw_output, output_type) method implemented
- [ ] Calls yaml_processor.strip_markdown_yaml_blocks()
- [ ] Calls corrector.correct_{type}() methods
- [ ] Returns string (sanitized YAML)
- [ ] Logs warnings if sanitization incomplete
- [ ] Has docstrings and type hints

---

### Chunk 2: Add Missing Error Handlers to Corrector
**File**: `src/space_hulk_game/validation/corrector.py` (EDIT)
**Dependencies**: None
**Parallel**: ✅ Can run in parallel with Chunks 1 and 3

**Tasks**:
1. Add `_fix_mixed_quotes(content: str) -> str` method
   - Handles "text' and 'text" patterns
   - Normalizes to consistent quote style
2. Add `_fix_invalid_list_markers(content: str) -> str` method
   - Replaces `----------------` with proper `- ` list markers
3. Add `_fix_unescaped_apostrophes(content: str) -> str` method
   - Converts 'Ship's' to "Ship's" (use double quotes to avoid escaping)
4. Update `_parse_yaml_safe()` to call all 3 new methods
5. Add unit tests for each new method

**Acceptance Criteria**:
- [ ] _fix_mixed_quotes() method added
- [ ] _fix_invalid_list_markers() method added
- [ ] _fix_unescaped_apostrophes() method added
- [ ] All 3 methods called in _parse_yaml_safe()
- [ ] Each method has docstring with examples
- [ ] Unit tests added to tests/test_corrector.py
- [ ] Tests pass with examples from CI failures

---

### Chunk 3: Monkey-Patch Task._save_file
**File**: `src/space_hulk_game/crew.py` (EDIT)
**Dependencies**: Chunk 1 (needs OutputSanitizer to exist)
**Parallel**: ⚠️ Must wait for Chunk 1 to complete

**Tasks**:
1. Import OutputSanitizer at top of crew.py
2. In SpaceHulkGame.__init__(), save original Task._save_file
3. Create sanitized_save_file() wrapper function
4. Detect output type from filename (plot_outline → 'plot', etc.)
5. Call sanitizer.sanitize() if output is string and type detected
6. Apply monkey-patch: Task._save_file = sanitized_save_file
7. Add logging for when sanitization runs
8. Handle edge cases (non-string outputs, no output_file, etc.)

**Acceptance Criteria**:
- [ ] OutputSanitizer imported in crew.py
- [ ] Monkey-patch applied in __init__()
- [ ] Output type detection logic works for all 5 file types
- [ ] Sanitization only runs for string outputs with output_file
- [ ] Original _save_file preserved and called after sanitization
- [ ] Logging shows "Sanitizing {filename} as {type}"
- [ ] Integration test verifies patch works

---

### Chunk 4: Comprehensive E2E Testing
**File**: `tests/test_output_sanitization.py` (NEW)
**Dependencies**: Chunks 1, 2, 3 (needs full pipeline)
**Parallel**: ⚠️ Must wait for Chunks 1-3 to complete

**Tasks**:
1. Create TestOutputSanitization test class
2. Test sanitizing mixed quotes
   - Input: `title: "Space Hulk: Lost Vessel'`
   - Expected: Valid YAML with consistent quotes
3. Test sanitizing invalid list markers
   - Input: `themes:\n  ---------------- horror`
   - Expected: Valid YAML with `- horror`
4. Test sanitizing unescaped apostrophes
   - Input: `description: 'The captain's log'`
   - Expected: Valid YAML (converted to double quotes)
5. Test end-to-end pipeline with mocked Task
6. Test all 5 output types (plot, narrative, puzzle, scene, mechanics)
7. Test graceful degradation when sanitization fails
8. Verify existing test_sequential_5_tasks.py now passes

**Acceptance Criteria**:
- [ ] test_output_sanitization.py created
- [ ] Test for each error type (mixed quotes, lists, apostrophes)
- [ ] Test for all 5 output types
- [ ] Test with real broken YAML from CI failures
- [ ] Mocked integration test for Task monkey-patch
- [ ] All tests pass
- [ ] test_sequential_5_tasks.py::test_04_output_content_quality passes

---

## Implementation Strategy

### Parallel Execution Plan

**Wave 1** (Start immediately, run in parallel):
- Agent 1: Chunk 1 - Create OutputSanitizer class
- Agent 2: Chunk 2 - Add error handlers to corrector.py

**Wave 2** (After Wave 1 completes):
- Agent 3: Chunk 3 - Monkey-patch Task._save_file (needs Chunk 1)

**Wave 3** (After Wave 2 completes):
- Agent 4: Chunk 4 - Comprehensive testing (needs all previous chunks)

### Dependencies Graph
```
Chunk 1 (OutputSanitizer) ──┐
                            │
Chunk 2 (Error Handlers) ───┼──→ Chunk 3 (Monkey-patch) ──→ Chunk 4 (Testing)
                            │
        (both independent)  │
                            │
                     (Chunk 3 needs
                      OutputSanitizer
                      to import)
```

---

## Testing Strategy

### Unit Tests
- Each new error handler method (Chunk 2)
- OutputSanitizer.sanitize() with various inputs (Chunk 1)

### Integration Tests
- Monkey-patch with mocked Task (Chunk 3)
- Full pipeline with real broken YAML (Chunk 4)

### Regression Tests
- Existing test_sequential_5_tasks.py must pass (Chunk 4)
- All existing corrector tests must still pass (Chunk 2)

---

## Success Criteria

**Phase 1 Complete When**:
- [ ] All 4 chunks implemented
- [ ] All tests pass (unit + integration + E2E)
- [ ] test_sequential_5_tasks.py passes in CI
- [ ] No YAML syntax errors in generated files
- [ ] Logging shows sanitization happening
- [ ] Code reviewed and documented

**Specific Metrics**:
- Test coverage for new code: >90%
- CI test failure rate: 0%
- YAML validation errors: 0
- Markdown fence remnants: 0

---

## Rollback Plan

If implementation fails:
1. Remove monkey-patch from crew.py (revert __init__ changes)
2. Delete output_sanitizer.py
3. Revert corrector.py changes
4. System returns to previous (broken but known) state

---

## Future Work (Phase 2 & 3)

**Phase 2: Consolidate Redundant Code**
- Remove 3 duplicate markdown stripping implementations
- Remove duplicate colon-fixing from evaluator.py
- Refactor crew.clean_yaml_output_files() (may remove entirely)

**Phase 3: Optional Enhancements**
- Integrate quality checking (currently disabled)
- Add Task callback support
- Consider strictyaml for schema enforcement

---

## Files to be Modified

**New Files**:
- `src/space_hulk_game/utils/output_sanitizer.py` (Chunk 1)
- `tests/test_output_sanitization.py` (Chunk 4)

**Modified Files**:
- `src/space_hulk_game/validation/corrector.py` (Chunk 2)
- `src/space_hulk_game/crew.py` (Chunk 3)
- `tests/test_corrector.py` (Chunk 2 - add tests)

**No Changes Needed**:
- `src/space_hulk_game/utils/yaml_processor.py` (reused as-is)
- `src/space_hulk_game/validation/validator.py` (reused as-is)
- `src/space_hulk_game/quality/evaluator.py` (Phase 2)

---

## Estimated Effort

- Chunk 1: 1-1.5 hours
- Chunk 2: 1-1.5 hours
- Chunk 3: 0.5-1 hour
- Chunk 4: 1-1.5 hours

**Total: 4-5.5 hours** for Phase 1

---

## Agent Task Assignments

### Agent 1: OutputSanitizer Implementation
**Input**: This plan + existing yaml_processor.py + corrector.py
**Output**: New file src/space_hulk_game/utils/output_sanitizer.py
**Success**: File created, class works, basic tests pass

### Agent 2: Error Handler Implementation
**Input**: This plan + corrector.py + examples of broken YAML
**Output**: Modified corrector.py with 3 new methods + unit tests
**Success**: Methods added, tests pass, handles all 3 error types

### Agent 3: Monkey-Patch Integration
**Input**: This plan + crew.py + output_sanitizer.py (from Agent 1)
**Output**: Modified crew.py with monkey-patch
**Success**: Patch applied, sanitization runs, logging works

### Agent 4: Comprehensive Testing
**Input**: This plan + all modified files from Agents 1-3
**Output**: New test file + verification all tests pass
**Success**: All tests pass, including test_sequential_5_tasks.py

---

**Plan Created**: 2025-11-11
**Phase 1 Status**: ✅ COMPLETE (Committed: 0e0a133)
**Phase 2 Status**: Ready for implementation
**Priority**: HIGH (code cleanup, reduce duplication)
