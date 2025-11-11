# Active Agent Projects

This directory contains active project folders for ongoing development initiatives managed by AI agents.

## Structure

Each project should be in its own subdirectory with:
```
agent-projects/
├── project-name/
│   ├── plan.md          # Required: Project plan with YAML frontmatter
│   ├── notes.md         # Optional: Implementation notes
│   ├── decisions.md     # Optional: Design decisions
│   └── ...             # Other project-specific files
```

## Plan.md Format

Each project's `plan.md` must include YAML frontmatter:

```yaml
---
status: active|completed|paused|abandoned
owner: AI Agent Name or Human Developer
created: YYYY-MM-DD
updated: YYYY-MM-DD
priority: high|medium|low
---

# Project Title

## Objective
[Clear statement of what this project aims to achieve]

## Status
[Current state and progress]

## Tasks
- [x] Completed task
- [ ] Pending task

## Notes
[Additional context, decisions, blockers]
```

## Lifecycle

1. **Active**: Projects less than 21 days old with status "active"
2. **Archived**: Move completed projects to `docs/archived-projects/`
3. **Context Generation**: Active plans are included in CONTEXT.md for AI agents

## Best Practices

- Update `plan.md` regularly with progress
- Keep plans focused and scoped appropriately
- Move to `docs/` when complete
- Use `agent-tmp/` for temporary exploration before creating a formal project
