---
status: active
owner: AI Agent / Development Team
created: 2025-11-10
updated: 2025-11-10
priority: high
estimated_duration: 3-4 working days (22 hours)
---

# Python Template Best Practices Adoption Plan

## Objective

Adopt best practices from the [python-template](https://github.com/bencan1a/python-template) repository to improve:

- Code organization and structure
- Automated quality assurance
- CI/CD pipelines
- AI agent collaboration workflows
- Developer experience

## Executive Summary

The python-template repository demonstrates mature patterns for Python development optimized for AI agent collaboration. This plan adapts those patterns for the Space Hulk CrewAI game project while preserving existing strengths.

**Key Improvements:**

- Structured file organization (agent-tmp/, agent-projects/, tools/)
- Automated quality checks (pre-commit hooks, Makefile)
- Comprehensive CI/CD (multi-platform testing, security scanning)
- Documentation automation (build_context.py for AI agents)
- Enhanced developer workflows

## Status

**Current Phase:** Planning Complete
**Next Phase:** Phase 1 - Foundation & Organization

## Implementation Phases

### Phase 1: Foundation & Organization (Week 1) - CRITICAL

**Status:** Not Started
**Effort:** ~6 hours
**Risk:** Low
**Tasks:** 1.1, 1.2, 1.3

### Phase 2: Quality Automation (Week 2) - HIGH PRIORITY

**Status:** Not Started
**Effort:** ~8 hours
**Risk:** Low
**Tasks:** 2.1, 2.2, 2.3

### Phase 3: CI/CD Enhancement (Week 3) - MEDIUM PRIORITY

**Status:** Not Started
**Effort:** ~6 hours
**Risk:** Medium
**Tasks:** 3.1, 3.2, 3.3

### Phase 4: Documentation Automation (Week 4) - MEDIUM PRIORITY

**Status:** Not Started
**Effort:** ~6 hours
**Risk:** Low
**Tasks:** 4.1, 4.2, 4.3

### Phase 5: Polish (Week 5) - LOW PRIORITY

**Status:** Not Started
**Effort:** ~3 hours
**Risk:** Low
**Tasks:** 5.1, 5.2, 5.3, 5.4

### Phase 6: Future Enhancements - DEFERRED

**Status:** Deferred
**Effort:** ~20+ hours
**Risk:** High
**Tasks:** Testing framework migration (unittest → pytest)

## Success Metrics

### Immediate (Post-Phase 1-2)

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
- [ ] Systematic technical debt tracking

## Dependencies

- **Phase 2** depends on **Phase 1** (need directory structure before automation)
- **Phase 3** partially depends on **Phase 2** (CI uses same tools as pre-commit)
- **Phase 4** partially depends on **Phase 1** (needs tools/ directory)
- **Phase 5** is independent (can run anytime)

## Risk Assessment

**High Risk:**

- Pre-commit hooks may conflict with game-config/ YAML files
- Multi-platform CI may reveal CrewAI compatibility issues

**Mitigation:**

- Exclude game-config/ from formatting hooks
- Start with Ubuntu-only CI, expand gradually

## Files

- [evaluation-report.md](./evaluation-report.md) - Detailed analysis of python-template
- [task-breakdown.md](./task-breakdown.md) - Detailed task list with dependencies
- [parallel-execution-plan.md](./parallel-execution-plan.md) - Parallelization opportunities

## Related Documentation

- Template: <https://github.com/bencan1a/python-template>
- Current CLAUDE.md: /home/devcontainers/space_hulk_game/CLAUDE.md
- Current pyproject.toml: /home/devcontainers/space_hulk_game/pyproject.toml
