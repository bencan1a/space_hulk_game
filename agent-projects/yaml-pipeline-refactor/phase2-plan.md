# YAML Pipeline Refactor - Phase 2: Consolidate Redundant Code

## Status

**Phase 1**: ✅ COMPLETE
**Phase 2**: Ready for implementation
**Priority**: HIGH (code cleanup, technical debt)

---

## Objective

Eliminate code duplication and consolidate the 3-layer architecture now that Phase 1 has proven the pipeline works.

**Key Issues from Analysis**:

- Markdown stripping implemented 4 separate times
- Colon fixing implemented 3 separate times
- Post-write cleanup may be redundant
- No unified error handling types

---

## Phase 2 Tasks

### Task 1: Consolidate Markdown Fence Stripping

**Current State**: 4 implementations

1. `yaml_processor.strip_markdown_yaml_blocks()` - Lines 17-42 (160 lines file)
2. `corrector._strip_markdown_fences()` - Lines 75-88 (duplicates #1)
3. `evaluator.parse_yaml()` - Lines 143-148 (duplicates #1)
4. `crew.clean_yaml_output_files()` - Lines 509-518 (regex version)

**Action**:

- Keep ONLY `yaml_processor.strip_markdown_yaml_blocks()` (most complete)
- Remove from corrector.py (lines 75-88)
- Update corrector to import and use yaml_processor version
- Remove from evaluator.py (lines 143-148)
- Update evaluator to import and use yaml_processor version
- Update crew.clean_yaml_output_files() to use yaml_processor version

**Files to modify**:

- `src/space_hulk_game/validation/corrector.py` - Remove method, add import
- `src/space_hulk_game/quality/evaluator.py` - Remove inline code, add import
- `src/space_hulk_game/crew.py` - Replace regex with yaml_processor call

**Acceptance Criteria**:

- [ ] Only 1 implementation remains (in yaml_processor.py)
- [ ] All other modules import from yaml_processor
- [ ] All tests still pass
- [ ] Code reduction: ~50 lines removed

---

### Task 2: Consolidate Colon-in-Values Fixing

**Current State**: 3 implementations

1. `corrector._parse_yaml_safe()` - Lines 183-201 (quotes values with colons)
2. `evaluator._fix_common_yaml_errors()` - Lines 104-125 (duplicates #1)
3. `crew.clean_yaml_output_files()` - Lines 527-550 (nested quotes regex)

**Action**:

- Keep corrector implementation (most sophisticated)
- Remove from evaluator.py (lines 104-125)
- Update evaluator to call corrector if colon fixing needed
- Remove nested quotes regex from crew.clean_yaml_output_files()

**Files to modify**:

- `src/space_hulk_game/quality/evaluator.py` - Remove method
- `src/space_hulk_game/crew.py` - Remove nested quotes handling

**Acceptance Criteria**:

- [ ] Only 1 implementation (in corrector.py)
- [ ] evaluator uses corrector for syntax fixes
- [ ] All tests still pass
- [ ] Code reduction: ~40 lines removed

---

### Task 3: Evaluate crew.clean_yaml_output_files()

**Current State**: Post-write cleanup (lines 476-624, 149 lines)

- Runs AFTER files written to disk
- Now redundant with pre-write sanitization

**Action**:
Option A (Conservative): Keep as backup verification

- Add comment explaining it's backup sanitization
- Consider making it log-only (no writes)

Option B (Aggressive): Remove entirely

- All sanitization now happens pre-write
- Post-write cleanup no longer needed
- Simplifies crew.py

**Recommendation**: Option A for Phase 2, Option B for future

**Files to modify**:

- `src/space_hulk_game/crew.py` - Add documentation or remove method

**Acceptance Criteria**:

- [ ] Decision documented
- [ ] If kept: clear comments explain purpose
- [ ] If removed: all tests still pass
- [ ] Code reduction: 0-149 lines

---

### Task 4: Create Unified ProcessingResult Type

**Current State**: Multiple result types

- `ValidationResult` (validator.py)
- `CorrectionResult` (corrector.py)
- `QualityScore` (evaluator.py)
- Different error handling patterns

**Action**:

- Create `src/space_hulk_game/validation/types.py`
- Define `ProcessingResult` dataclass
- Migrate existing types to use ProcessingResult
- Unified error/warning/info reporting

**New File**:

```python
@dataclass
class ProcessingResult:
    success: bool
    data: Optional[Any]
    errors: List[str]
    warnings: List[str]
    corrections: List[str]

    @property
    def is_valid(self) -> bool:
        return self.success and not self.errors
```

**Files to modify**:

- NEW: `src/space_hulk_game/validation/types.py`
- `src/space_hulk_game/validation/validator.py` - Use ProcessingResult
- `src/space_hulk_game/validation/corrector.py` - Use ProcessingResult
- `src/space_hulk_game/quality/evaluator.py` - Use ProcessingResult (add score field)

**Acceptance Criteria**:

- [x] ProcessingResult type created
- [x] All 3 modules use consistent types (via conversion methods for backward compatibility)
- [x] All tests updated (all existing tests pass)
- [x] Error handling unified (conversion methods added to all result types)

---

## Implementation Strategy

### Sequential Execution (No Parallel)

Phase 2 tasks have dependencies on each other.

**Order**:

1. Task 1 (Markdown consolidation) - Independent
2. Task 2 (Colon fixing consolidation) - Depends on Task 1 being tested
3. Task 3 (Evaluate cleanup) - Decision task, low risk
4. Task 4 (Unified types) - Touches all modules, do last

---

## Success Criteria

**Phase 2 Complete When**:

- [ ] All 4 tasks completed
- [ ] Code duplication eliminated
- [ ] All tests pass (no regressions)
- [ ] Code reduction: 100-240 lines
- [ ] Unified error handling
- [ ] Documentation updated

**Specific Metrics**:

- Markdown stripping: 4 → 1 implementation
- Colon fixing: 3 → 1 implementation
- Test pass rate: 100%
- Code quality: No new linter warnings

---

## Estimated Effort

- Task 1: 1-1.5 hours
- Task 2: 1-1.5 hours
- Task 3: 0.5 hours (decision + docs)
- Task 4: 2-3 hours (touches many files)

**Total: 5-7.5 hours** for Phase 2

---

## Risk Assessment

**Low Risk**:

- Phase 1 already working and tested
- Only consolidating existing code
- All changes have test coverage

**Mitigation**:

- Run full test suite after each task
- Keep Phase 1 commits as rollback point
- Document all changes

---

## Files Impacted

**Modified**:

- `src/space_hulk_game/validation/corrector.py`
- `src/space_hulk_game/quality/evaluator.py`
- `src/space_hulk_game/crew.py`
- `src/space_hulk_game/validation/validator.py`
- Test files (update imports, assertions)

**New**:

- `src/space_hulk_game/validation/types.py`

---

**Phase 2 Plan Created**: 2025-11-11
**Ready for Implementation**: YES
**Phase 1 Prerequisite**: ✅ COMPLETE
