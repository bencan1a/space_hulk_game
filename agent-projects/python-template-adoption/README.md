# Python Template Adoption Project

**Status:** Active - Planning Complete
**Created:** 2025-11-10
**Priority:** High
**Estimated Duration:** 14-16 hours (with parallelization)

---

## Quick Links

- **[Main Plan](./plan.md)** - Project overview, phases, success metrics
- **[Task Breakdown](./task-breakdown.md)** - Detailed task list with 36 specific tasks
- **[Evaluation Report](./evaluation-report.md)** - Full analysis of python-template repository
- **[Parallel Execution Plan](./parallel-execution-plan.md)** - Strategy for concurrent execution

---

## Project Summary

Adopt best practices from [python-template](https://github.com/bencan1a/python-template) to improve:
- Code organization (agent-tmp/, agent-projects/, tools/)
- Quality automation (pre-commit, Makefile, CI/CD)
- AI agent collaboration (AGENTS.md, CONTEXT.md)
- Developer experience (enhanced workflows)

---

## Quick Start

### For Implementers

**Phase 1 (Week 1): Foundation**
```bash
# Execute Wave 1 (4 parallel agents)
mkdir -p agent-tmp agent-projects tools
# Create READMEs and AGENTS.md (see task-breakdown.md)
# Update .gitignore and pyproject.toml

# Execute Wave 2 (serial)
git mv validate_api.py tools/
git mv test_connectivity.py tools/
git mv kloc_report.py tools/
git mv configure_mem0.py tools/
# Update references
```

**Phase 2 (Week 2): Quality Automation**
```bash
# Execute Wave 3 (5 agents: 4 parallel + 1 serial)
# Create Makefile
# Create .pre-commit-config.yaml
# Update pyproject.toml (Ruff, pytest, dependencies)
pip install pre-commit
pre-commit install
make check-all
```

**Phase 3 (Week 3): CI/CD**
```bash
# Execute Wave 4 (4 parallel agents)
# Create .github/workflows/ci.yml
# Create .github/workflows/nightly-regression.yml
# Create tools/build_context.py
# Push to test branch to validate CI
# Note: pr-validation.yml was initially created but later removed as redundant with ci.yml
```

**Phase 4 (Week 4): Documentation**
```bash
# Execute Wave 5 (3 parallel agents)
# Update PR template
# Enhance DevContainer
# Update CLAUDE.md
# Final validation
```

### For Reviewers

**What to Check:**
1. **After Phase 1:** File organization makes sense, AGENTS.md comprehensive
2. **After Phase 2:** `make check-all` passes, pre-commit hooks work
3. **After Phase 3:** CI workflows run successfully on test branch
4. **After Phase 4:** Documentation auto-generates, devcontainer works

---

## Files in This Project

### Planning Documents

**plan.md** (Main plan)
- Project overview and objectives
- 5 implementation phases
- Success metrics
- Risk assessment
- Timeline: 3-4 weeks

**task-breakdown.md** (36 tasks)
- Detailed task specifications
- Dependencies clearly marked
- Effort estimates (⚡ quick, ⏱️ medium, 🕐 long)
- Validation criteria for each task
- Organized into 5 phases, 13 groups

**evaluation-report.md** (Analysis)
- Comprehensive analysis of python-template
- Gap analysis (current vs. template)
- Risk assessment
- Adaptation strategies
- Space Hulk-specific considerations

**parallel-execution-plan.md** (Optimization)
- 5 execution waves
- Agent assignments
- Synchronization points
- Gantt chart visualization
- Timeline: 14-16 hours with parallelization vs 22 hours sequential

### Quick Reference

**README.md** (This file)
- Project summary
- Quick start guide
- File descriptions
- Key decisions

---

## Key Decisions

### ✅ Adopted from Template

1. **File Organization**
   - agent-tmp/ for temporary outputs (gitignored, 7-day cleanup)
   - agent-projects/ for active work (committed, 21-day active window)
   - tools/ for utility scripts

2. **AGENTS.md**
   - Central AI guidance document
   - Consolidates guidance from CLAUDE.md and copilot-instructions.md
   - Prominent venv activation reminders

3. **Makefile**
   - Standard commands: test, lint, format, type-check, security
   - CrewAI commands: run-crew, validate-api
   - Developer convenience shortcuts

4. **Pre-commit Hooks**
   - Multi-layer checks: formatting, linting, type-checking, security
   - Exclude game-config/ from whitespace trimming
   - Runs before every commit

5. **CI/CD**
   - Multi-platform testing (Ubuntu, Windows, macOS)
   - Python version matrix (3.10, 3.11, 3.12)
   - Separate workflows: ci (includes PR validation), nightly-regression

6. **Documentation Automation**
   - build_context.py generates unified context for AI agents
   - Auto-generates API docs with pdoc3
   - GitHub Actions workflow for automatic updates

7. **Enhanced Configuration**
   - Line length: 100 chars (align Black and Ruff)
   - Extended Ruff rules (ARG, SIM, TCH, PTH, ERA, PL, RUF)
   - pytest configuration (prepare for future migration)
   - Expanded dev dependencies (hypothesis, ipdb, faker)

### ❌ Not Adopted / Deferred

1. **pytest Migration** (Deferred)
   - Current unittest framework works well
   - High effort, high disruption
   - Can revisit later if needed
   - pytest config added to pyproject.toml for future

2. **Test Framework Changes** (Deferred)
   - Keep mock-based testing approach
   - Maintain RUN_REAL_API_TESTS flag
   - unittest compatible with CI

### ⚠️ Adapted for Space Hulk

1. **YAML Handling**
   - Exclude game-config/*.yaml from pre-commit whitespace trimming
   - Preserve narrative text formatting
   - Maintain Warhammer 40K theme content

2. **CrewAI Integration**
   - Makefile includes CrewAI-specific commands
   - CI tests in mock mode by default
   - Real API tests optional in nightly workflow
   - Agent/task YAML configuration validation

3. **Nightly Regression**
   - Optional real API testing (if keys available)
   - Create GitHub issue on failure
   - Comprehensive coverage reporting

---

## Success Metrics

### Immediate (Post-Phase 1-2)
- [x] Planning complete
- [ ] All developers can run `make check-all` successfully
- [ ] Pre-commit hooks catch 80%+ of style issues before PR
- [ ] AGENTS.md reduces "forgot to activate venv" incidents to zero
- [ ] Makefile reduces command typing by ~70%

### Medium-term (Post-Phase 3-4)
- [ ] CI catches platform-specific bugs before merge
- [ ] Code coverage visibility improves
- [ ] AI agents successfully use CONTEXT.md
- [ ] Documentation auto-updates weekly

### Long-term (6 months)
- [ ] Test suite runs on all platforms
- [ ] Code quality issues decrease by 50%
- [ ] Faster contributor onboarding
- [ ] Systematic technical debt tracking via agent-projects/

---

## Risk Mitigation

### High Risks

**1. Pre-commit hooks conflict with game-config/ YAML**
- ✅ Mitigated: Explicit exclusions in .pre-commit-config.yaml
- ✅ Testing: Verify on existing YAML files before rollout

**2. Multi-platform CI reveals CrewAI issues**
- ✅ Mitigated: Start Ubuntu-only, expand gradually
- ✅ Testing: Local validation on Windows/macOS first

**3. Line length changes cause large diffs**
- ✅ Mitigated: Dedicated formatting commit, careful review
- ✅ Testing: Format in separate branch first

### Medium Risks

**4. build_context.py excessive context size**
- ✅ Mitigated: Configurable truncation (150k chars default)

**5. Pre-commit slows commits**
- ✅ Mitigated: Optional initially, optimize slow hooks

---

## Timeline

### Conservative Estimate (Sequential)
- Phase 1: Week 1 (6 hours)
- Phase 2: Week 2 (8 hours)
- Phase 3: Week 3 (6 hours)
- Phase 4: Week 4 (6 hours)
- Phase 5: Week 5 (3 hours)
- **Total: ~29 hours over 5 weeks**

### Aggressive Estimate (Parallel)
- Phase 1: Day 1 (2 hours)
- Phase 2: Day 2 (5 hours)
- Phase 3: Day 3 (6 hours)
- Phase 4: Day 4 (4 hours)
- **Total: ~17 hours over 4 days**

### Realistic Estimate (With Testing)
- Phase 1: Days 1-2 (4 hours)
- Phase 2: Days 3-4 (6 hours)
- Phase 3: Days 5-6 (6 hours)
- Phase 4: Day 7 (4 hours)
- **Total: ~20 hours over 7 days**

---

## Next Steps

### Immediate
1. Review this plan with team
2. Get approval to proceed
3. Assign agents to Phase 1 tasks
4. Schedule kickoff meeting

### Phase 1 Kickoff
1. Execute Wave 1 (parallel: 4 agents)
2. Execute Wave 2 (serial: 1 agent)
3. Review and validate changes
4. Commit with message: "feat: implement python-template file organization"

### Ongoing
- Tag each wave completion
- Test between waves
- Document any issues or adaptations
- Update this plan as needed

---

## Questions & Answers

**Q: Why not migrate to pytest immediately?**
A: unittest works well, pytest migration is high effort/disruption. We've added pytest config to prepare for future migration if needed.

**Q: Will pre-commit hooks slow down commits?**
A: First run on all files takes ~30-60s. Subsequent runs only check changed files (~2-5s). Can be skipped with `git commit --no-verify` if needed.

**Q: What if multi-platform CI finds issues?**
A: Start with Ubuntu-only, fix any issues, then gradually add Windows and macOS. This phased approach reduces risk.

**Q: How does this affect game content in game-config/?**
A: Explicitly excluded from formatting hooks. Narrative text formatting preserved. No impact on Warhammer 40K content.

**Q: Can we skip any phases?**
A: Phase 1-2 are critical. Phase 3-5 can be deferred if resources limited. Phase 6 (pytest) is already deferred.

**Q: How do we test this safely?**
A: Each phase includes validation criteria. Use test branch for CI workflows. Tag each wave for easy rollback.

---

## References

- Template Repository: https://github.com/bencan1a/python-template
- Current CLAUDE.md: [/home/devcontainers/space_hulk_game/CLAUDE.md](../../CLAUDE.md)
- Current pyproject.toml: [/home/devcontainers/space_hulk_game/pyproject.toml](../../pyproject.toml)
- Pre-commit Documentation: https://pre-commit.com
- GitHub Actions Documentation: https://docs.github.com/en/actions

---

## Contact & Support

For questions about this plan:
- Review the detailed documents in this directory
- Check the evaluation report for rationale
- Consult the task breakdown for specifics
- See the parallel execution plan for optimization

---

*Last Updated: 2025-11-10*
*Status: Ready for Implementation*
