# Parallel Execution Plan - Python Template Adoption

**Purpose:** Maximize implementation speed through parallel task execution while respecting dependencies.

**Strategy:** Identify independent tasks that can run simultaneously, organize into execution waves.

---

## Execution Waves Overview

```
Wave 1 (Parallel)     →  Wave 2 (Serial)     →  Wave 3 (Parallel)    →  Wave 4 (Parallel)
├─ Create directories    ├─ Move scripts         ├─ Makefile            ├─ CI workflows (3x)
├─ Update .gitignore     └─ Update refs          ├─ Pre-commit          └─ Docs workflow
├─ Create AGENTS.md                               ├─ Ruff rules
└─ Fix line length                                ├─ pytest config
                                                  ├─ Dev deps
                                                  └─ build_context.py

Total Sequential Time: ~22 hours
Total Parallel Time: ~14-16 hours
Efficiency Gain: ~35%
```

---

## Wave 1: Foundation Setup (PARALLEL)
**Duration:** 90 minutes
**Dependencies:** None
**Agents:** 4 agents working simultaneously

### Agent 1: File System Setup (15 minutes)
**Tasks:**
- 1.1.1: Create agent-tmp/ with README
- 1.1.2: Create agent-projects/ with README
- 1.1.3: Create tools/ with README

**Commands:**
```bash
mkdir -p agent-tmp agent-projects tools
# Create READMEs (see task-breakdown.md)
```

### Agent 2: Configuration Updates (10 minutes)
**Tasks:**
- 1.2.2: Update .gitignore
- 1.3.3: Add tools/ to type checking in pyproject.toml

**Files:**
- `.gitignore`
- `pyproject.toml` [tool.pyright] and [tool.mypy]

### Agent 3: Documentation (90 minutes)
**Tasks:**
- 1.3.1: Create AGENTS.md

**Effort:** Longest task in wave
**Deliverable:** Complete AGENTS.md file

### Agent 4: Configuration Fix (10 minutes)
**Tasks:**
- 1.3.2: Fix line length inconsistency in pyproject.toml

**Files:**
- `pyproject.toml` [tool.black] line-length = 100

**Wave 1 Completion Criteria:**
- [ ] All directories exist with READMEs
- [ ] .gitignore updated
- [ ] AGENTS.md complete
- [ ] Line length consistent (100 chars)
- [ ] tools/ in type checking config

---

## Wave 2: File Reorganization (SERIAL)
**Duration:** 30 minutes
**Dependencies:** Wave 1 complete (tools/ must exist)
**Agents:** 1 agent (sequential operations)

### Task Sequence:
1. Move scripts to tools/ (Task 1.2.1)
2. Update references in workflows
3. Update CLAUDE.md examples
4. Test scripts from new location

**Commands:**
```bash
git mv validate_api.py tools/
git mv test_connectivity.py tools/
git mv kloc_report.py tools/
git mv configure_mem0.py tools/

# Update references
sed -i 's|python validate_api.py|python tools/validate_api.py|g' .github/workflows/*.yml
sed -i 's|python kloc_report.py|python tools/kloc_report.py|g' .github/workflows/*.yml

# Test
python tools/validate_api.py --help
```

**Wave 2 Completion Criteria:**
- [ ] All scripts moved to tools/
- [ ] Workflow references updated
- [ ] CLAUDE.md updated
- [ ] Scripts execute from new location

---

## Wave 3: Quality Automation (MIXED)
**Duration:** 4 hours
**Dependencies:** Wave 2 complete
**Agents:** 5 agents (4 parallel + 1 serial chain)

### Parallel Group A (2-3 hours)

#### Agent 1: Makefile Creation (2 hours)
**Tasks:**
- 2.1.1: Create Makefile

**Deliverable:** Complete Makefile with all commands

#### Agent 2: Ruff Enhancement (30 minutes)
**Tasks:**
- 2.3.1: Add extended Ruff rules to pyproject.toml

**Then run:**
```bash
ruff check .
# Review and address new violations
```

#### Agent 3: pytest Configuration (20 minutes)
**Tasks:**
- 2.3.2: Add pytest and coverage config to pyproject.toml

**Note:** Prepares for future, doesn't require migration yet

#### Agent 4: Dev Dependencies (15 minutes)
**Tasks:**
- 2.3.3: Expand dev dependencies in pyproject.toml

**Then install:**
```bash
uv pip install -e ".[dev]"
```

### Serial Chain (after Agent 1 completes)

#### Agent 5: Pre-commit Setup (2 hours)
**Dependencies:** Makefile must exist
**Tasks:**
- 2.2.1: Create .pre-commit-config.yaml
- Install and test hooks

**Commands:**
```bash
# After creating config
pip install pre-commit
pre-commit install
pre-commit run --all-files

# May need to fix issues found
make fix  # Use new Makefile
```

**Wave 3 Completion Criteria:**
- [ ] Makefile complete and tested
- [ ] Extended Ruff rules active
- [ ] pytest config added
- [ ] Dev dependencies installed
- [ ] Pre-commit hooks installed and passing

---

## Wave 4: CI/CD & Documentation (PARALLEL)
**Duration:** 6 hours
**Dependencies:** Wave 3 complete
**Agents:** 4 agents working simultaneously

### Agent 1: Main CI Workflow (3 hours)
**Tasks:**
- 3.1.1: Create .github/workflows/ci.yml

**Deliverable:** Multi-platform CI workflow (includes PR validation)

### Agent 2: ~~PR Validation~~ (Merged into CI workflow)
**Note:** Originally planned as separate workflow, but merged into ci.yml to avoid redundancy

### Agent 3: Nightly Regression (1.5 hours)
**Tasks:**
- 3.3.1: Create .github/workflows/nightly-regression.yml

**Deliverable:** Comprehensive nightly testing

### Agent 4: Documentation Automation (6 hours)
**Tasks:**
- 4.3.1: Add pdoc3 to pyproject.toml (5 min)
- 4.1.1: Create tools/build_context.py (4 hours)
- 4.2.1: Create .github/workflows/update-docs.yml (1.5 hours)

**Deliverable:** Automated documentation generation system

**Wave 4 Completion Criteria:**
- [ ] CI workflow runs successfully
- [ ] PR validation workflow tested
- [ ] Nightly regression workflow configured
- [ ] build_context.py working
- [ ] Documentation auto-updates

---

## Wave 5: Polish (PARALLEL)
**Duration:** 2 hours
**Dependencies:** Waves 1-4 complete
**Agents:** 3 agents working simultaneously

### Agent 1: PR Template (1 hour)
**Tasks:**
- 5.1.1: Update .github/PULL_REQUEST_TEMPLATE.md

### Agent 2: DevContainer (1 hour)
**Tasks:**
- 5.2.1: Enhance .devcontainer/devcontainer.json

### Agent 3: Documentation Updates (30 minutes)
**Tasks:**
- 5.4.1: Update CLAUDE.md with new commands and structure

**Wave 5 Completion Criteria:**
- [ ] PR template enhanced
- [ ] DevContainer auto-setup working
- [ ] CLAUDE.md references updated

---

## Parallel Execution Gantt Chart

```
Time →  0h      2h      4h      6h      8h      10h     12h     14h     16h
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Wave 1:
Agent1  [═══]                                                   (directories)
Agent2  [═]                                                     (gitignore)
Agent3  [═══════════════════════]                              (AGENTS.md)
Agent4  [═]                                                     (line length)
        └─────────────────────┘ 1.5h

Wave 2:
Agent1           [═══]                                          (move scripts)
                 └──┘ 0.5h

Wave 3:
Agent1                [═══════════════════]                     (Makefile)
Agent2                [═══]                                     (Ruff rules)
Agent3                [══]                                      (pytest cfg)
Agent4                [═]                                       (dev deps)
Agent5                       [═══════════════════]              (pre-commit)
                      └────────────────────────┘ 4h

Wave 4:
Agent1                                      [═══════════════]   (CI workflow)
Agent2                                      [═════]             (PR workflow)
Agent3                                      [═══════]           (Nightly)
Agent4                                      [═══════════════════════] (docs)
                                            └──────────────────┘ 6h

Wave 5:
Agent1                                                      [═══] (PR template)
Agent2                                                      [═══] (DevContainer)
Agent3                                                      [═]   (CLAUDE.md)
                                                            └─┘ 1h

Total Parallel Time: ~14-16 hours (with some overlap/buffering)
```

---

## Agent Assignment Strategy

### Recommended Agent Types

**Wave 1:**
- Agent 1: File System Agent (create directories, files)
- Agent 2: Configuration Agent (TOML, YAML editing)
- Agent 3: Documentation Agent (markdown writing)
- Agent 4: Configuration Agent (TOML editing)

**Wave 2:**
- Agent 1: File System Agent (git operations, path updates)

**Wave 3:**
- Agent 1: Build System Agent (Makefile creation)
- Agent 2: Configuration Agent (Ruff configuration)
- Agent 3: Configuration Agent (pytest configuration)
- Agent 4: Configuration Agent (dependencies)
- Agent 5: DevOps Agent (pre-commit setup)

**Wave 4:**
- Agent 1: CI/CD Agent (GitHub Actions workflows)
- Agent 2: CI/CD Agent (GitHub Actions workflows)
- Agent 3: CI/CD Agent (GitHub Actions workflows)
- Agent 4: Python Development Agent (complex scripting)

**Wave 5:**
- Agent 1: Documentation Agent (templates)
- Agent 2: Configuration Agent (devcontainer)
- Agent 3: Documentation Agent (update docs)

---

## Synchronization Points

### After Wave 1:
**Verify:**
- All directories exist
- Configuration files updated
- No merge conflicts

**Test:**
```bash
ls -la agent-tmp/ agent-projects/ tools/
grep "agent-tmp" .gitignore
mypy --version  # Should see tools/ in config
```

### After Wave 2:
**Verify:**
- Scripts moved successfully
- Workflows reference correct paths
- No broken imports

**Test:**
```bash
python tools/validate_api.py --help
python tools/kloc_report.py --help
git log --oneline -1  # Check commit message
```

### After Wave 3:
**Verify:**
- Makefile commands work
- Pre-commit hooks pass
- All quality checks pass

**Test:**
```bash
make help
make check-all
pre-commit run --all-files
```

### After Wave 4:
**Verify:**
- CI workflows valid
- Documentation generation works
- No syntax errors in YAML

**Test:**
```bash
# Validate GitHub Actions syntax
grep -r "on:" .github/workflows/

# Test build_context locally
python tools/build_context.py

# Push to test branch and verify CI runs
```

### After Wave 5:
**Verify:**
- All documentation consistent
- DevContainer rebuilds successfully
- PR template renders correctly

**Test:**
```bash
# Rebuild devcontainer
# Create test PR to preview template
```

---

## Dependency Graph (Visual)

```
┌─────────────┐
│   Wave 1    │ (Parallel: 4 agents)
│  Foundation │
└──────┬──────┘
       │
       v
┌─────────────┐
│   Wave 2    │ (Serial: 1 agent)
│ Reorganize  │
└──────┬──────┘
       │
       v
┌─────────────┐
│   Wave 3    │ (Mixed: 5 agents)
│  Automation │ (4 parallel + 1 serial chain)
└──────┬──────┘
       │
       v
┌─────────────┐
│   Wave 4    │ (Parallel: 4 agents)
│   CI/CD     │
└──────┬──────┘
       │
       v
┌─────────────┐
│   Wave 5    │ (Parallel: 3 agents)
│   Polish    │
└─────────────┘
```

---

## Task Execution Commands

### Wave 1 Parallel Kickoff

```bash
# Terminal 1: Agent 1 (File System)
mkdir -p agent-tmp agent-projects tools
# Create READMEs (copy from task-breakdown.md)

# Terminal 2: Agent 2 (Configuration)
# Edit .gitignore
# Edit pyproject.toml [tool.pyright]

# Terminal 3: Agent 3 (Documentation)
# Create AGENTS.md (see task-breakdown.md for content)

# Terminal 4: Agent 4 (Configuration)
# Edit pyproject.toml [tool.black] line-length = 100
```

### Wave 2 Serial Execution

```bash
git mv validate_api.py tools/
git mv test_connectivity.py tools/
git mv kloc_report.py tools/
git mv configure_mem0.py tools/
# Update references in workflows and docs
```

### Wave 3 Mixed Execution

```bash
# Parallel start (Terminals 1-4)

# Terminal 1: Makefile
# Create Makefile (see task-breakdown.md)

# Terminal 2: Ruff rules
# Edit pyproject.toml [tool.ruff.lint]

# Terminal 3: pytest config
# Edit pyproject.toml [tool.pytest.ini_options]

# Terminal 4: Dev dependencies
# Edit pyproject.toml [project.optional-dependencies]
uv pip install -e ".[dev]"

# Wait for Terminal 1 to complete, then:

# Terminal 5: Pre-commit (serial chain)
# Create .pre-commit-config.yaml
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Wave 4 Parallel Kickoff

```bash
# Terminal 1: Main CI
# Create .github/workflows/ci.yml

# Terminal 2: PR Validation
# Note: pr-validation.yml was initially planned but merged into ci.yml to avoid redundancy

# Terminal 3: Nightly
# Create .github/workflows/nightly-regression.yml

# Terminal 4: Documentation
# Add pdoc3 to pyproject.toml
# Create tools/build_context.py
# Create .github/workflows/update-docs.yml
```

### Wave 5 Parallel Kickoff

```bash
# Terminal 1: PR Template
# Update .github/PULL_REQUEST_TEMPLATE.md

# Terminal 2: DevContainer
# Update .devcontainer/devcontainer.json

# Terminal 3: CLAUDE.md
# Update CLAUDE.md with new paths and commands
```

---

## Risk Mitigation in Parallel Execution

### Merge Conflict Prevention

**Strategy:** Each agent works on different files

**Wave 1 File Assignments:**
- Agent 1: agent-tmp/README.md, agent-projects/README.md, tools/README.md
- Agent 2: .gitignore
- Agent 3: AGENTS.md (new file)
- Agent 4: pyproject.toml [tool.black] section only

**Wave 3 File Assignments:**
- Agent 1: Makefile (new file)
- Agent 2: pyproject.toml [tool.ruff.lint] section
- Agent 3: pyproject.toml [tool.pytest.ini_options] section
- Agent 4: pyproject.toml [project.optional-dependencies] section
- Agent 5: .pre-commit-config.yaml (new file)

**If conflicts occur:**
1. Coordinate pyproject.toml edits carefully
2. Use git merge strategies
3. Review diffs before committing

### Testing Between Waves

**After each wave:**
```bash
# Run quality checks
make check-all  # (after Wave 3)

# Run tests
make test

# Verify no regressions
git diff HEAD~1  # Review all changes
```

### Rollback Strategy

**If wave fails:**
```bash
# Rollback to previous wave
git reset --hard wave-N-complete

# Or cherry-pick successful changes
git cherry-pick <successful-commit>
```

**Tag each wave:**
```bash
git tag wave-1-complete
git tag wave-2-complete
git tag wave-3-complete
git tag wave-4-complete
git tag wave-5-complete
```

---

## Performance Optimization

### Agent Resource Allocation

**CPU-Intensive Tasks:**
- Wave 3: Pre-commit hooks (first run on all files)
- Wave 4: Documentation generation (pdoc3)

**Allocate more resources to:**
- Wave 3 Agent 5 (pre-commit)
- Wave 4 Agent 4 (build_context.py)

### Execution Order Optimization

**Critical Path:** Wave 1 → Wave 2 → Wave 3 → Wave 4 → Wave 5

**Bottleneck:** Wave 3 (4 hours)
- Longest single wave
- Contains serial dependency (Makefile → pre-commit)

**Optimization:**
- Start Wave 3 parallel tasks immediately after Wave 2
- Don't wait for all Wave 3 to complete before starting Wave 4
- Wave 4 only depends on Makefile existing, not pre-commit
- Can overlap Wave 3 (agents 1-4) with Wave 4 start

**Revised timing with overlap:**
```
Wave 1: 0h - 1.5h
Wave 2: 1.5h - 2h
Wave 3 (parallel): 2h - 4h
Wave 3 (serial): 4h - 6h  ← Can overlap with Wave 4
Wave 4: 5h - 11h  ← Start 1 hour early
Wave 5: 11h - 12h

Optimized Total: ~12 hours (vs 14-16 hours)
```

---

## Success Criteria Checklist

### Wave 1 Complete ✓
- [ ] agent-tmp/ exists with README
- [ ] agent-projects/ exists with README
- [ ] tools/ exists with README
- [ ] .gitignore updated
- [ ] AGENTS.md created and comprehensive
- [ ] Line length consistent (100 chars) in pyproject.toml
- [ ] tools/ in type checking config

### Wave 2 Complete ✓
- [ ] All 4 scripts moved to tools/
- [ ] Workflow references updated
- [ ] CLAUDE.md updated
- [ ] Scripts execute from new location
- [ ] No broken imports

### Wave 3 Complete ✓
- [ ] Makefile with all commands
- [ ] `make help` works
- [ ] `make test` runs tests
- [ ] Extended Ruff rules active
- [ ] pytest configuration added
- [ ] Dev dependencies installed
- [ ] Pre-commit hooks installed
- [ ] `pre-commit run --all-files` passes

### Wave 4 Complete ✓
- [ ] CI workflow file created
- [ ] PR validation workflow created
- [ ] Nightly regression workflow created
- [ ] pdoc3 installed
- [ ] build_context.py working
- [ ] Documentation workflow created
- [ ] All workflows syntactically valid

### Wave 5 Complete ✓
- [ ] PR template enhanced
- [ ] DevContainer auto-setup working
- [ ] CLAUDE.md updated
- [ ] All documentation consistent

### Final Validation ✓
- [ ] `make check-all` passes
- [ ] All tests pass
- [ ] CI workflow runs successfully (push to test branch)
- [ ] Documentation generates correctly
- [ ] Pre-commit hooks catch issues
- [ ] No regression in existing functionality

---

## Timeline Estimates

### Conservative (Sequential)
- Wave 1: 1.5 hours
- Wave 2: 0.5 hours
- Wave 3: 4 hours
- Wave 4: 6 hours
- Wave 5: 1 hour
- **Total: ~13 hours**

### Aggressive (Maximum Parallelization)
- Wave 1: 1.5 hours (limited by longest task: AGENTS.md)
- Wave 2: 0.5 hours (serial bottleneck)
- Wave 3: 2.5 hours (parallel tasks + 30min buffer for serial)
- Wave 4: 4 hours (limited by longest task: build_context.py)
- Wave 5: 1 hour (parallel)
- **Total: ~9.5 hours**

### Realistic (With Coordination Overhead)
- Wave 1: 2 hours (coordination + testing)
- Wave 2: 1 hour (testing + validation)
- Wave 3: 5 hours (coordination + fixing issues)
- Wave 4: 6 hours (testing workflows)
- Wave 5: 1.5 hours (final validation)
- **Total: ~15.5 hours**

---

## Conclusion

Parallel execution can reduce implementation time by ~35% compared to sequential execution:
- **Sequential:** 22 hours
- **Parallel:** 14-16 hours
- **Savings:** 6-8 hours

**Key Success Factors:**
1. Clear agent assignments (no file conflicts)
2. Well-defined synchronization points
3. Testing between waves
4. Rollback strategy
5. Critical path optimization

**Recommended Approach:** Use realistic timeline (15.5 hours) for planning, aim for aggressive (9.5 hours) with experienced agents, expect conservative (13 hours) as baseline.
