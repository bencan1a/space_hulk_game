# Quick Start Guide for GitHub Copilot Agents

This is a quick reference guide for using the GitHub Copilot agents in the Space Hulk Game project.

## 🚀 Quick Setup

1. **Ensure GitHub Copilot is enabled** in your IDE (VS Code, JetBrains, etc.)
2. **Open any file** in the project
3. **Start coding** - agents automatically provide context-aware suggestions

## 📋 Agent Quick Reference

| Agent | File | Use When |
|-------|------|----------|
| **Project Assistant** | `space-hulk-game-assistant.md` | General project questions, navigation |
| **Python Specialist** | `python-developer.md` | Writing Python code, imports, error handling |
| **CrewAI Expert** | `crewai-specialist.md` | Working with agents, tasks, workflows |
| **Game Mechanics** | `game-mechanics-specialist.md` | Designing game features, narratives, puzzles |
| **YAML Expert** | `yaml-expert.md` | Editing YAML configs, validation |
| **Testing Specialist** | `testing-specialist.md` | Writing tests, mocking, coverage |

## 💡 Common Use Cases

### Adding a New CrewAI Agent

```python
# Ask Copilot: "How do I add a new agent?"
# 1. Edit src/space_hulk_game/config/agents.yaml
# 2. Add agent definition using CrewAI Expert patterns
# 3. Update crew.py with @agent decorator
```

### Writing a Test

```python
# Ask Copilot: "How do I test this function?"
# 1. Create test method in tests/test_*.py
# 2. Follow Testing Specialist patterns
# 3. Use mocking for external dependencies
```

### Creating a YAML Config

```yaml
# Ask Copilot: "What's the structure for task configs?"
# YAML Expert provides proper formatting and structure
```

### Designing Game Mechanics

```python
# Ask Copilot: "How do I create a puzzle?"
# Game Mechanics Specialist provides design patterns
```

## 🎯 Best Practices

### ✅ DO

- **Ask specific questions** in comments
- **Use descriptive function/variable names** to help agents understand context
- **Review suggestions** before accepting
- **Leverage multiple agents** for complex tasks
- **Consult agent files** (`.github/agents/*.md`) for capabilities

### ❌ DON'T

- Don't blindly accept all suggestions
- Don't ignore project patterns in favor of generic solutions
- Don't expect agents to understand unstated requirements
- Don't forget to validate YAML after editing

## 🔍 Example Workflows

### 1. Adding a New Feature

```python
# Comment your intent
# "Add a new inventory system for tracking items"

# Copilot uses:
# - Python Specialist for code structure
# - Game Mechanics for inventory design
# - Testing Specialist for test suggestions
```

### 2. Fixing a Bug

```python
# Describe the issue
# "Fix error handling when YAML file is missing"

# Copilot uses:
# - Python Specialist for error handling patterns
# - YAML Expert for file loading best practices
```

### 3. Refactoring Code

```python
# State your goal
# "Refactor this function to follow project patterns"

# Copilot uses:
# - Python Specialist for code quality
# - CrewAI Expert if it involves agents/tasks
```

## 📚 Key Files to Know

| File | Purpose |
|------|---------|
| `src/space_hulk_game/config/agents.yaml` | Agent definitions |
| `src/space_hulk_game/config/tasks.yaml` | Task definitions |
| `src/space_hulk_game/crew.py` | Crew implementation |
| `tests/test_space_hulk_game.py` | Test suite |
| `memory-bank/crewai-api-reference.md` | CrewAI reference |

## 🛠️ Common Commands

```bash
# Run the crew
crewai run

# Run tests
python -m unittest discover -s tests

# Install dependencies
crewai install

# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('file.yaml'))"
```

## 🔧 Troubleshooting

### Suggestions aren't helpful?
1. Be more specific in your comments
2. Check you're in the right file type
3. Consult the relevant agent markdown file in `.github/agents/`
4. Review CONTRIBUTING.md for patterns

### Agent knowledge seems outdated?
1. Update the agent markdown files in `.github/agents/`
2. Add new patterns and examples
3. Validate markdown and YAML frontmatter syntax
4. Restart your IDE

### Need more help?
1. Check AGENTS.md for detailed agent documentation
2. Review CONTRIBUTING.md for development guidelines
3. Consult memory-bank/ for project context
4. Ask in comments for specific guidance

## 📖 Documentation

- **AGENTS.md** - Detailed agent documentation
- **CONTRIBUTING.md** - Development guidelines
- **README.md** - Project overview
- **memory-bank/** - Comprehensive project docs

## ⚡ Pro Tips

1. **Use inline comments** to guide Copilot: `# Create agent that handles combat`
2. **Ask questions** in comments: `# Q: What's the best way to structure this?`
3. **Request examples**: `# Show me an example of a CrewAI task`
4. **Be explicit about patterns**: `# Follow the project's error handling pattern`
5. **Combine agents**: Work in files that trigger multiple relevant agents

## 🎓 Learning Path

### Beginner
1. Read AGENTS.md to understand available agents
2. Review CONTRIBUTING.md for project conventions
3. Explore existing code with Copilot suggestions enabled
4. Ask basic questions in comments

### Intermediate
1. Use agents to write new features
2. Let agents guide test writing
3. Refactor code with agent suggestions
4. Contribute to agent configurations

### Advanced
1. Customize agent configurations for your workflow
2. Add new patterns to agent knowledge
3. Create project-specific shortcuts
4. Help improve agent effectiveness

---

**Remember**: GitHub Copilot agents are tools to enhance your productivity, not replace your judgment. Always review and understand suggestions before accepting them.

For detailed information, see **AGENTS.md**.
