# YAML to JSON Migration Plan

**Date**: 2025-11-11
**Status**: APPROVED - Ready for Implementation
**Estimated Duration**: 2-3 hours with parallel workers

---

## Executive Summary

Complete migration from YAML to JSON for all game content outputs while maintaining YAML for configuration files (agents.yaml, tasks.yaml).

**Rationale**:

- LLM JSON mode provides guaranteed valid syntax
- Eliminates 500+ lines of YAML syntax correction code
- Simplifies validation pipeline by ~70%
- No existing users = breaking changes acceptable

**Impact**:

- ContentLoader (game engine)
- 16 test files
- 5+ documentation files
- Quality metrics tools
- Game config templates

---

## Architecture Decision

**What Changes**: Output format for generated game content
**From**: `game-config/*.yaml`
**To**: `game-config/*.json`

**What Stays YAML**: Configuration files

- `src/space_hulk_game/config/agents.yaml`
- `src/space_hulk_game/config/tasks.yaml`
- `planning_templates/*.yaml`

---

## Parallelization Strategy

### Wave 1: Foundation (Sequential) ⏱️ 30 min

**MUST complete before Wave 2** - Everything depends on this

- Update ContentLoader to support JSON
- Fix ContentLoader tests
- **Blocker removal**: Once done, Wave 2 can proceed in parallel

### Wave 2: Independent Streams (Parallel) ⏱️ 45-60 min

**Can ALL run simultaneously** - No dependencies between workers

- **Worker 1**: Test Fixtures
- **Worker 2**: Engine Components
- **Worker 3**: Quality Metrics
- **Worker 4**: Documentation
- **Worker 5**: Game Config Templates

### Wave 3: Integration (Sequential) ⏱️ 30-45 min

**Run after Wave 2 complete** - Requires all components

- Demo game updates
- Full integration testing
- Cleanup and verification

---

## Detailed Work Breakdown

## 🔵 WAVE 1: FOUNDATION (Sequential)

### Phase 1.1: ContentLoader Core

**Worker**: Lead Developer
**Time**: 20 min
**Files**:

- `src/space_hulk_game/engine/loader.py`

**Tasks**:

1. Add `load_json()` method

   ````python
   def load_json(self, filepath: str) -> dict[str, Any]:
       """Load JSON file with markdown fence stripping."""
       with open(filepath, 'r', encoding='utf-8') as f:
           content = f.read()
       # Strip markdown fences if present
       content = re.sub(r'^\s*```json\s*\n?', '', content, flags=re.IGNORECASE)
       content = re.sub(r'\n?\s*```\s*$', '', content)
       return json.loads(content)
   ````

2. Update `load_game()` method

   ```python
   def load_game(self, output_dir: str) -> GameData:
       base_path = Path(output_dir)
       plot = self.load_json(str(base_path / "plot_outline.json"))
       narrative = self.load_json(str(base_path / "narrative_map.json"))
       puzzles = self.load_json(str(base_path / "puzzle_design.json"))
       scenes = self.load_json(str(base_path / "scene_texts.json"))
       mechanics = self.load_json(str(base_path / "prd_document.json"))
       # ... rest of method unchanged
   ```

3. Keep `load_yaml()` method (used by config loaders)

**Verification**:

```bash
python -m py_compile src/space_hulk_game/engine/loader.py
```

---

### Phase 1.2: ContentLoader Tests

**Worker**: Lead Developer
**Time**: 10 min
**Files**:

- `tests/test_content_loader.py`
- `tests/demo_content_loader.py`

**Tasks**:

1. Create minimal JSON test fixtures (inline in test file)
2. Update test cases to use JSON format
3. Test both `load_json()` and `load_game()` methods

**Verification**:

```bash
python -m pytest tests/test_content_loader.py -v
python -m pytest tests/demo_content_loader.py -v
```

**Success Criteria**: All ContentLoader tests pass

---

## 🟢 WAVE 2: PARALLEL STREAMS (Can run simultaneously)

### Worker 1: Test Fixtures Migration

**Time**: 30 min
**Dependencies**: None (Wave 1 complete)

**Phase 2.1: Convert YAML Fixtures to JSON**

**Files to convert**:

- `tests/fixtures/plot_outline_*.yaml` → `*.json`
- `tests/fixtures/narrative_map_*.yaml` → `*.json`
- `tests/fixtures/puzzle_design_*.yaml` → `*.json`
- `tests/fixtures/scene_texts_*.yaml` → `*.json`
- `tests/fixtures/prd_document_*.yaml` → `*.json`
- Any integration test fixtures

**Conversion Script**:

```python
import yaml
import json
from pathlib import Path

fixtures_dir = Path("tests/fixtures")
for yaml_file in fixtures_dir.glob("*.yaml"):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    json_file = yaml_file.with_suffix(".json")
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Converted {yaml_file} → {json_file}")
```

**Phase 2.2: Update Fixture Loaders**

**Files**:

- Any test helper modules that load fixtures
- Update hardcoded `.yaml` paths to `.json`

**Verification**:

```bash
python -m pytest tests/ -v
```

---

### Worker 2: Engine Components

**Time**: 40 min
**Dependencies**: Phase 1.1 complete (ContentLoader)

**Phase 3.1: Update Engine Validator**

**Files**:

- `src/space_hulk_game/engine/validator.py`
- `tests/test_validator.py`

**Tasks**:

1. Update error messages mentioning "YAML" → "JSON"
2. Update any format-specific validation logic
3. Convert test data in test_validator.py

**Verification**:

```bash
python -m pytest tests/test_validator.py -v
```

**Phase 3.2: Update Engine Tests**

**Files**:

- `tests/test_game_engine.py`
- `tests/test_scene.py`
- `tests/test_entities.py`
- `tests/test_game_state.py`
- `tests/test_parser.py`
- `tests/test_persistence.py`

**Tasks**:

1. Convert inline test data to JSON
2. Update fixture references
3. Update assertions checking file formats

**Verification**:

```bash
python -m pytest tests/test_game_engine.py -v
python -m pytest tests/test_scene.py tests/test_entities.py -v
```

**Phase 3.3: Update Demo Game**

**Files**:

- `src/space_hulk_game/engine/demo_game.py`
- `tests/test_demo_game.py`
- `tests/test_demo_game_validation.py`

**Tasks**:

1. Update default paths (.yaml → .json)
2. Update CLI help text
3. Update error messages
4. Convert test scenarios

**Verification**:

```bash
python -m pytest tests/test_demo_game*.py -v
python -m space_hulk_game.demo_game --help
```

---

### Worker 3: Quality Metrics

**Time**: 35 min
**Dependencies**: None (Wave 1 complete)

**Phase 5.1: Update Quality Checking Code**

**Files** (8 files in `src/space_hulk_game/quality/`):

- `coherence.py`
- `integration.py`
- `metrics.py`
- `narrative_quality.py`
- `plot_quality.py`
- `scene_quality.py`
- `puzzle_quality.py`
- `mechanics_quality.py`

**Tasks**:

1. Replace `yaml.safe_load()` with `json.load()`
2. Update file path expectations (.yaml → .json)
3. Update error messages

**Find/Replace Pattern**:

```python
# OLD:
with open(file_path) as f:
    data = yaml.safe_load(f)

# NEW:
with open(file_path) as f:
    data = json.load(f)
```

**Phase 5.2: Update Quality Tests**

**Files**:

- `tests/test_quality_*.py`

**Tasks**:

1. Convert test data to JSON
2. Update fixture paths

**Verification**:

```bash
python -m pytest tests/ -k quality -v
```

---

### Worker 4: Documentation

**Time**: 35 min
**Dependencies**: None (independent)

**Phase 7.1: Update Core Documentation**

**Files**:

- `docs/GAME_ENGINE.md`
- `docs/PLAYING_GAMES.md`
- `CLAUDE.md`
- `README.md`
- `game-config/README.md`

**Tasks**:

1. **Global find/replace**:
   - "YAML" → "JSON"
   - ".yaml" → ".json"
   - "`yaml" → "`json"

2. **Update code examples**:
   - Convert YAML examples to JSON
   - Update loader examples
   - Update file format descriptions

3. **Specific line updates**:
   - `docs/GAME_ENGINE.md` lines 302, 469-470
   - `docs/PLAYING_GAMES.md` lines 464-469

**Phase 7.2: Update docstrings**

**Files**:

- `src/space_hulk_game/engine/loader.py`
- `src/space_hulk_game/utils/output_sanitizer.py`
- Other modules with YAML references

**Tasks**:

- Update module docstrings
- Update method docstrings
- Update example code in docstrings

**Verification**:

```bash
grep -r "\.yaml" docs/
grep -r "YAML" docs/ | grep -v "agents.yaml\|tasks.yaml"
```

(Should only find config file references)

---

### Worker 5: Game Config Templates

**Time**: 20 min
**Dependencies**: None (independent)

**Phase 6.1: Convert Template Files**

**Files to convert**:

- `game-config/plot_outline.yaml` → `plot_outline.json`
- `game-config/narrative_map.yaml` → `narrative_map.json`
- `game-config/puzzle_design.yaml` → `puzzle_design.json`
- `game-config/scene_texts.yaml` → `scene_texts.json`
- `game-config/prd_document.yaml` → `prd_document.json`

**Conversion Method**:

```python
import yaml
import json
from pathlib import Path

game_config = Path("game-config")
for yaml_file in game_config.glob("*.yaml"):
    with open(yaml_file, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    json_file = yaml_file.with_suffix(".json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ {json_file.name}")
```

**Phase 6.2: Update game-config/README.md**

**Tasks**:

- Replace format references
- Update example snippets
- Update loading instructions

**Verification**:

```bash
ls -la game-config/*.json
python -m json.tool game-config/plot_outline.json > /dev/null
```

---

## 🔴 WAVE 3: INTEGRATION (Sequential)

### Phase 9.1: Cleanup Dead Code

**Worker**: Lead Developer
**Time**: 15 min
**Dependencies**: All Wave 2 complete

**Files to Remove** (no longer needed):

- `src/space_hulk_game/utils/yaml_processor.py` ❌
  - Markdown stripping now in OutputSanitizer
- `src/space_hulk_game/validation/corrector.py` ❌
  - YAML syntax correction not needed for JSON

**Files to Update**:

- Remove imports of deleted modules
- Remove unused functions

**Verification**:

```bash
python -m pytest tests/ -v
# Ensure no import errors
```

---

### Phase 9.2: Integration Testing

**Worker**: Lead Developer
**Time**: 30 min
**Dependencies**: All phases complete

**Test 1: Agent Generation**

```bash
crewai run --inputs "prompt: A survival horror game on a derelict station"
```

**Verify**:

- ✅ JSON files created in game-config/
- ✅ Files are valid JSON (not YAML)
- ✅ Pretty-formatted with 2-space indentation
- ✅ No markdown fences in output
- ✅ OutputSanitizer logs show JSON processing

**Test 2: Game Loading**

```bash
python -m space_hulk_game.demo_game
```

**Verify**:

- ✅ Loads JSON files without errors
- ✅ Game is playable
- ✅ All commands work
- ✅ No format-related errors

**Test 3: Quality Metrics**

```bash
python -m space_hulk_game.quality.metrics game-config/
```

**Verify**:

- ✅ Analyzes JSON files correctly
- ✅ Metrics calculated successfully

**Test 4: Full Test Suite**

```bash
python -m pytest tests/ -v --tb=short
make test  # If makefile exists
```

**Verify**:

- ✅ All tests pass
- ✅ No warnings about missing files
- ✅ No YAML parsing errors

**Test 5: End-to-End Workflow**

1. Generate game with agents
2. Load game in engine
3. Play through a scene
4. Save game (uses JSON already)
5. Load saved game

**Verify**: Complete workflow functions

---

## Rollback & Risk Mitigation

### Git Strategy

```bash
# After Wave 1
git add -A
git commit -m "feat(engine): add JSON support to ContentLoader"

# After each Worker in Wave 2
git commit -m "feat(tests): migrate fixtures to JSON"
git commit -m "feat(engine): update engine components for JSON"
git commit -m "feat(quality): migrate quality metrics to JSON"
git commit -m "docs: update documentation for JSON format"
git commit -m "feat(config): convert game config templates to JSON"

# After Wave 3
git commit -m "chore: remove YAML processing code"
git commit -m "test: verify full JSON migration"
```

### Rollback Commands

```bash
# If issues in Wave 2
git reset --hard HEAD~1  # Undo last commit

# If issues in Wave 3
git reset --hard <Wave-2-completion-commit>
```

---

## Dependencies & Requirements

### Already Completed

- ✅ JSON mode enabled in LLM config (crew.py)
- ✅ Task prompts request JSON format (tasks.yaml)
- ✅ OutputSanitizer uses JSON (output_sanitizer.py)

### Python Packages

- `json` (stdlib) - already available
- `PyYAML` - **KEEP** (still needed for agents.yaml, tasks.yaml)

---

## Parallel Execution Guide

### How to Execute with Multiple Workers

**Option 1: Multiple Terminal Windows**

```bash
# Terminal 1 - Wave 1 (Lead)
# Complete Phase 1.1 and 1.2

# Terminal 2 - Worker 1 (Fixtures)
git checkout -b worker1-fixtures
# Work on Phase 2.1 and 2.2

# Terminal 3 - Worker 2 (Engine)
git checkout -b worker2-engine
# Work on Phase 3.1, 3.2, 3.3

# Terminal 4 - Worker 3 (Quality)
git checkout -b worker3-quality
# Work on Phase 5.1 and 5.2

# Terminal 5 - Worker 4 (Docs)
git checkout -b worker4-docs
# Work on Phase 7.1 and 7.2

# Terminal 6 - Worker 5 (Templates)
git checkout -b worker5-templates
# Work on Phase 6.1 and 6.2
```

**Option 2: Single Developer Sequential**

```bash
# Wave 1
# Complete Phase 1.1, 1.2

# Wave 2 (do in any order)
# Phase 2 → Phase 3 → Phase 5 → Phase 7 → Phase 6

# Wave 3
# Phase 9
```

**Option 3: AI Agents (Task tool)**

```python
# Launch parallel agents for Wave 2
Task(subagent_type="general-purpose", prompt="Worker 1: Migrate test fixtures...")
Task(subagent_type="general-purpose", prompt="Worker 2: Update engine components...")
Task(subagent_type="general-purpose", prompt="Worker 3: Update quality metrics...")
Task(subagent_type="general-purpose", prompt="Worker 4: Update documentation...")
Task(subagent_type="general-purpose", prompt="Worker 5: Convert templates...")
```

---

## Timeline Estimates

### With Parallel Execution (Multiple Workers)

| Wave      | Time   | Running Time |
| --------- | ------ | ------------ |
| Wave 1    | 30 min | 30 min       |
| Wave 2    | 40 min | 1h 10m       |
| Wave 3    | 45 min | 1h 55m       |
| **Total** |        | **~2 hours** |

### Sequential Execution (Single Developer)

| Phase            | Time   | Cumulative   |
| ---------------- | ------ | ------------ |
| 1. ContentLoader | 30 min | 30 min       |
| 2. Fixtures      | 30 min | 1h           |
| 3. Engine        | 40 min | 1h 40m       |
| 5. Quality       | 35 min | 2h 15m       |
| 6. Templates     | 20 min | 2h 35m       |
| 7. Docs          | 35 min | 3h 10m       |
| 9. Integration   | 45 min | 3h 55m       |
| **Total**        |        | **~4 hours** |

**Speedup with Parallelization**: 2x faster

---

## Success Criteria

### Technical

- [ ] All 16 test files pass
- [ ] ContentLoader loads JSON successfully
- [ ] Game engine runs with JSON files
- [ ] Demo game is playable
- [ ] Quality metrics analyze JSON
- [ ] No YAML syntax errors possible

### Code Quality

- [ ] No dead code (yaml_processor, corrector removed)
- [ ] ~500 lines of code removed
- [ ] Simpler OutputSanitizer (~163 lines vs 185)
- [ ] All docstrings updated

### Documentation

- [ ] All docs reference JSON
- [ ] Examples use JSON format
- [ ] README accurate
- [ ] GAME_ENGINE.md updated

### Integration

- [ ] Full workflow: generate → load → play
- [ ] Agent generation produces valid JSON
- [ ] Engine loads JSON without errors
- [ ] Save/load game works

---

## Post-Migration Benefits

### Immediate

- ✅ Eliminated YAML syntax errors (mixed quotes, list markers, apostrophes)
- ✅ Removed 500+ lines of correction code
- ✅ Simpler validation pipeline (70% reduction)
- ✅ JSON mode guarantees valid syntax from LLM

### Long-term

- ✅ Easier to maintain (one format)
- ✅ Better IDE support (JSON schema validation)
- ✅ Standard web format (easier tooling)
- ✅ Faster parsing (JSON parsers are optimized)

---

## Questions & Decisions

### Q: Can we remove PyYAML dependency?

**A**: NO - Still needed for:

- `src/space_hulk_game/config/agents.yaml`
- `src/space_hulk_game/config/tasks.yaml`
- `planning_templates/*.yaml`

These are configuration files (not outputs) and staying YAML.

### Q: What about existing game content?

**A**: No existing users, so no migration needed. Fresh start with JSON.

### Q: Should we support both formats in ContentLoader?

**A**: NO - Clean break to JSON only. Simpler codebase.

### Q: What if an LLM generates YAML despite JSON mode?

**A**: OutputSanitizer will detect invalid JSON and log error. Should be rare with JSON mode enabled.

---

## Approval & Sign-off

**Plan Author**: Claude (AI Assistant)
**Reviewed By**: **\*\*\*\***\_**\*\*\*\***
**Approved By**: **\*\*\*\***\_**\*\*\*\***
**Date**: 2025-11-11

**Status**: ✅ APPROVED - Ready for Implementation

---

## Execution Log

Track progress as work completes:

### Wave 1: Foundation

- [ ] Phase 1.1: ContentLoader Core (Lead)
- [ ] Phase 1.2: ContentLoader Tests (Lead)

### Wave 2: Parallel Streams

- [ ] Worker 1: Test Fixtures (Phase 2)
- [ ] Worker 2: Engine Components (Phase 3)
- [ ] Worker 3: Quality Metrics (Phase 5)
- [ ] Worker 4: Documentation (Phase 7)
- [ ] Worker 5: Game Config Templates (Phase 6)

### Wave 3: Integration

- [ ] Phase 9.1: Cleanup Dead Code
- [ ] Phase 9.2: Integration Testing

**Completion Date**: **\*\*\*\***\_**\*\*\*\***
