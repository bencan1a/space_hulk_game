# GitHub Copilot Custom Instructions

This file provides custom instructions and context for GitHub Copilot when working in this repository.

## Project Overview

This is the **Space Hulk Game** project - a text-based adventure game set in the Warhammer 40K universe. The project uses the **CrewAI framework** to orchestrate multiple specialized AI agents that collaborate to create engaging narratives, design puzzles, and build immersive game mechanics.

## Key Technologies

- **Language**: Python 3.10+
- **Framework**: CrewAI (multi-agent AI collaboration)
- **LLM**: Ollama (local, qwen2.5 model)
- **Memory**: Mem0 for context retention
- **Testing**: Python unittest
- **Package Manager**: uv

## Project Structure

```
space_hulk_game/
├── src/space_hulk_game/
│   ├── config/
│   │   ├── agents.yaml      # Agent definitions
│   │   ├── tasks.yaml       # Task definitions
│   │   └── gamedesign.yaml  # Game design examples
│   ├── crew.py              # Main CrewAI crew implementation
│   ├── main.py              # Entry point
│   └── tools/               # Custom tools
├── tests/                   # Test suite
├── docs/                    # Product documentation
├── game-config/             # Game design configuration for AI agents
├── project-plans/           # Development plans and architectural docs
├── tmp/                     # Temporary debug scripts (gitignored)
└── .github/agents/          # GitHub Copilot custom agents
```

### Folder Organization

- **docs/**: All user-facing documentation (README, SETUP, guides)
- **game-config/**: Game configuration files that define structure and examples for AI agents
- **project-plans/**: Development plans and architectural documentation
- **tmp/**: Temporary files, debug scripts, and reports (not committed to git)
- **src/**: Source code for the game
- **tests/**: Unit tests and test infrastructure
- **.github/agents/**: Custom GitHub Copilot agents

## Coding Standards

### Python Style
- Follow **PEP 8** guidelines
- Use **type hints** for function parameters and return values
- Add **docstrings** for classes and functions (Google or NumPy style)
- Use **descriptive variable names**
- Add **logging** for important operations

### Import Organization
1. Standard library imports
2. Third-party imports (CrewAI, yaml, etc.)
3. Local imports

### Error Handling
- Use **specific exception types** (not bare `except`)
- Provide **meaningful error messages**
- **Log errors** with context
- Implement **graceful degradation** where possible

## CrewAI Patterns

### Agent Definition
```python
@agent
def agent_name(self) -> Agent:
    return Agent(
        config=self.agents_config["AgentName"],
        llm=self.llm,
        verbose=True
    )
```

### Task Definition
```python
@task
def task_name(self) -> Task:
    return Task(
        config=self.tasks_config["TaskName"]
    )
```

### Lifecycle Hooks
- `@before_kickoff`: Validate inputs before crew starts
- `@after_kickoff`: Process outputs after crew finishes

## Configuration Files

### agents.yaml Structure
```yaml
AgentName:
  role: "Agent's role"
  goal: "What the agent aims to achieve"
  description: "Brief description"
  backstory: >
    Multi-line backstory using folded style.
  allow_delegation: true
  verbose: true
```

### tasks.yaml Structure
```yaml
TaskName:
  name: "Human-readable task name"
  description: >
    Clear description of what the task should do.
  expected_output: >
    Description of the expected output.
  agent: "AgentName"
  context:
    - "PreviousTask"
  dependencies:
    - "TaskThatMustCompleteFirst"
  output_file: "output.yaml"
```

## Testing Guidelines

- Use **unittest** framework
- **Mock external dependencies** (LLM, file I/O)
- Test **edge cases** and **error handling**
- Keep tests **isolated** and **independent**
- Run tests: `python -m unittest discover -s tests`

## Common Commands

```bash
# Run the crew
crewai run

# Run tests
python -m unittest discover -s tests -v

# Install dependencies
crewai install
```

## Important Notes

1. **All agents and tasks** are defined in YAML files under `src/space_hulk_game/config/`
2. **Product documentation** is in the `docs/` folder
3. **Game configuration** (YAML templates and examples) is in `game-config/`
4. **Development plans** are in `project-plans/`
5. **Temporary files** should go in `tmp/` (not committed to git)
6. The project uses **Ollama** for local LLM integration at `http://localhost:11434`
7. **Mem0** is used for memory management across agents
8. Method names in `crew.py` **must match** the keys in YAML config files (case-sensitive)
9. **Agent output files** write to `game-config/*.yaml` based on templates there

## When Suggesting Code

- **Prefer configuration over code**: Use YAML configs when possible
- **Follow existing patterns**: Match the style of existing code
- **Add logging**: Include logger statements for important operations
- **Handle errors**: Add try-except blocks with specific exceptions
- **Use type hints**: Annotate function parameters and return types
- **Write tests**: Suggest test cases for new functionality
- **Document**: Add docstrings explaining purpose and usage

## Custom Agents Available

Six specialized GitHub Copilot agents are available in `.github/agents/`:
1. **space-hulk-game-assistant**: General project guidance
2. **python-developer**: Python best practices
3. **crewai-specialist**: CrewAI framework expertise
4. **game-mechanics-specialist**: Game design patterns
5. **yaml-expert**: YAML configuration help
6. **testing-specialist**: Testing strategies

Use these agents for specialized assistance by invoking them in supported IDEs or the GitHub Copilot CLI.

## Warhammer 40K / Space Hulk Themes

When working on game content:
- **Gothic horror**: Dark, oppressive atmosphere
- **Grimdark**: No good choices, only survival
- **Body horror**: Mutations, corruption
- **Military fiction**: Squad tactics, duty, sacrifice
- **Isolation**: Cut off from help, on your own
- **Ancient technology**: Failing systems, machine spirits

## Helpful Resources

- **docs/CONTRIBUTING.md**: Detailed development guidelines
- **docs/AGENTS.md**: Comprehensive agent documentation
- **docs/crewai-api-reference.md**: CrewAI framework reference
- **project-plans/**: Development plans and architectural context
