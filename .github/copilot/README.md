# Legacy Agent Configuration Files

> **Note**: These files have been migrated to the correct location.

## Migration Notice

The agent configuration files in this directory were originally created as standalone YAML files. However, GitHub Copilot custom agents should be defined as **markdown files with YAML frontmatter** in the **`.github/agents/`** directory.

### What Changed

The agent profiles have been migrated:

| Old Location | New Location |
|--------------|--------------|
| `.github/copilot/agent.yml` | `.github/agents/space-hulk-game-assistant.md` |
| `.github/copilot/python-agent.yml` | `.github/agents/python-developer.md` |
| `.github/copilot/crewai-agent.yml` | `.github/agents/crewai-specialist.md` |
| `.github/copilot/game-mechanics-agent.yml` | `.github/agents/game-mechanics-specialist.md` |
| `.github/copilot/yaml-agent.yml` | `.github/agents/yaml-expert.md` |
| `.github/copilot/testing-agent.yml` | `.github/agents/testing-specialist.md` |

### New Format

The new agent profiles use markdown format with YAML frontmatter:

```markdown
---
name: agent-name
description: Agent description
---

# Agent Name

Agent documentation and instructions in markdown...
```

This format is the correct structure for GitHub Copilot custom agents and allows them to be properly discovered and used in:
- GitHub Copilot in IDEs (VS Code, JetBrains, etc.)
- GitHub Copilot CLI
- GitHub web interface

### What to Do

1. **Use the new location**: All agent profiles are now in `.github/agents/`
2. **Update any references**: If you have scripts or documentation referencing these files, update them to point to `.github/agents/`
3. **See documentation**: Check `AGENTS.md` for details about the new agent structure

### Additional Resources

- **Agent Profiles**: `.github/agents/` - New location for custom agents
- **Custom Instructions**: `.github/copilot-instructions.md` - Additional Copilot customization
- **Quick Start**: `.github/COPILOT_QUICKSTART.md` - Quick reference guide
- **Full Documentation**: `AGENTS.md` - Comprehensive agent documentation

---

These files are kept for reference but are no longer actively used by GitHub Copilot.
