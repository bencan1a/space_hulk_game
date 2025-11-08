# GitHub Copilot Agents

This document provides detailed information about the GitHub Copilot agent configurations available in this project. These agents are designed to provide context-aware assistance tailored to different aspects of the Space Hulk Game development.

## Overview

GitHub Copilot agents are specialized AI assistants configured with project-specific knowledge and patterns. When you use GitHub Copilot in this project, these agents automatically provide relevant suggestions based on:

- The file you're editing
- The programming language and framework
- Project-specific patterns and conventions
- Best practices for the task at hand

## Available Agents

### 1. Main Project Assistant

**File**: `.github/agents/space-hulk-game-assistant.md`

**Purpose**: Provides general project guidance and helps navigate the codebase.

**Best used for**:
- Understanding project structure
- Finding relevant files and documentation
- Learning about the technology stack
- General development questions

**Key knowledge areas**:
- Project architecture and organization
- CrewAI framework basics
- Configuration file locations
- Common development tasks

**Example use cases**:
- "Where are the agent definitions stored?"
- "How do I run the project?"
- "What's the project structure?"

---

### 2. Python Development Specialist

**File**: `.github/agents/python-developer.md`

**Purpose**: Expert in Python development best practices for this project.

**Best used for**:
- Writing Python code following project conventions
- Implementing error handling
- Adding type hints
- Structuring imports

**Key knowledge areas**:
- Python 3.10+ features
- Type hints and annotations
- Error handling patterns
- Logging best practices
- Project-specific Python patterns

**Example use cases**:
- "How should I handle errors in this function?"
- "What's the correct import structure?"
- "How do I add logging to this module?"

---

### 3. CrewAI Framework Expert

**File**: `.github/agents/crewai-specialist.md`

**Purpose**: Specialist in CrewAI framework patterns and multi-agent AI systems.

**Best used for**:
- Creating and configuring agents
- Defining tasks and workflows
- Implementing lifecycle hooks
- Configuring LLMs and memory

**Key knowledge areas**:
- Agent and task configuration
- CrewAI decorators (@agent, @task, @crew)
- Sequential and hierarchical processes
- Memory integration (Mem0)
- LLM configuration (Ollama)
- YAML configuration structure

**Example use cases**:
- "How do I add a new agent?"
- "What parameters can I use in task definitions?"
- "How do I configure memory for the crew?"
- "How do I implement a before_kickoff hook?"

---

### 4. Game Mechanics Specialist

**File**: `.github/agents/game-mechanics-specialist.md`

**Purpose**: Expert in text-based adventure game design and narrative systems.

**Best used for**:
- Designing game mechanics
- Creating branching narratives
- Developing puzzles and challenges
- Balancing gameplay

**Key knowledge areas**:
- Text adventure game patterns
- Branching narrative design
- Puzzle and combat mechanics
- Space Hulk/Warhammer 40K themes
- Interactive fiction best practices

**Example use cases**:
- "How should I structure a new area?"
- "What makes a good text adventure puzzle?"
- "How do I create meaningful player choices?"
- "How do I design an enemy encounter?"

---

### 5. YAML Configuration Expert

**File**: `.github/agents/yaml-expert.md`

**Purpose**: Specialist in YAML syntax, structure, and validation.

**Best used for**:
- Creating or modifying YAML configuration files
- Validating YAML syntax
- Organizing configuration data
- Following YAML best practices

**Key knowledge areas**:
- YAML syntax and formatting
- Multi-line strings (| and >)
- Anchors and references
- Agent and task YAML structures
- Safe loading practices

**Example use cases**:
- "How do I format multiline text in YAML?"
- "What's the correct structure for agent definitions?"
- "How do I reference another section in YAML?"
- "How do I validate this YAML file?"

---

### 6. Testing Specialist

**File**: `.github/agents/testing-specialist.md`

**Purpose**: Expert in testing strategies, unittest framework, and test organization.

**Best used for**:
- Writing unit and integration tests
- Mocking dependencies
- Organizing test suites
- Improving test coverage

**Key knowledge areas**:
- Python unittest framework
- Mocking patterns (unittest.mock)
- Test organization and naming
- Test coverage strategies
- CrewAI component testing

**Example use cases**:
- "How do I test this function?"
- "How do I mock this CrewAI agent?"
- "What's the proper test structure?"
- "How do I test error handling?"

---

## How to Use These Agents

### 1. Automatic Context-Aware Assistance

When you're working in a file, GitHub Copilot automatically uses the relevant agents to provide suggestions. For example:

- **Editing Python files**: Python Development Specialist provides suggestions
- **Working with YAML configs**: YAML Configuration Expert helps
- **Writing tests**: Testing Specialist guides you
- **Modifying crew.py**: CrewAI Framework Expert assists

### 2. Asking Questions

You can ask GitHub Copilot specific questions, and it will use the appropriate agents to answer:

```
# In a comment or chat:
# Q: How do I add a new agent to the crew?
# Q: What's the best way to structure this test?
# Q: How should I format this YAML file?
```

### 3. Code Generation

When requesting code generation, Copilot uses the agents to ensure generated code follows project patterns:

```python
# Generate a new agent definition
# Copilot will use CrewAI Framework Expert and Python Specialist
```

### 4. Code Completion

As you type, Copilot provides completions based on agent knowledge:

```python
# Start typing...
def load_config(
# Copilot suggests the complete function following project patterns
```

## Agent Selection Strategy

GitHub Copilot intelligently selects which agent(s) to use based on:

1. **File type**: `.py`, `.yaml`, `.md` files trigger different agents
2. **File location**: Files in `tests/` use Testing Specialist
3. **File content**: CrewAI imports trigger CrewAI Framework Expert
4. **Context**: Your current task and the code you're working on

## Benefits of Using These Agents

### Consistency
All suggestions follow established project patterns and conventions.

### Learning
Agents help you learn project-specific best practices as you work.

### Efficiency
Reduce time spent looking up documentation and patterns.

### Quality
Automatically follow coding standards and best practices.

### Context
Get suggestions relevant to your specific task and file.

## Customizing Agents

The agent configuration files are located in `.github/agents/` and can be customized to better fit your needs:

1. **Add new patterns**: Include project-specific patterns you use frequently
2. **Update knowledge**: Add new frameworks or tools as the project evolves
3. **Refine suggestions**: Adjust agent knowledge based on team feedback
4. **Add examples**: Include more code examples for common tasks

## Maintenance

### Updating Agent Knowledge

As the project evolves, update the agent files to reflect:

- New patterns and conventions
- Additional frameworks or tools
- Updated best practices
- New project structures or files

### Validating Agents

Agents are markdown files with YAML frontmatter. You can validate the YAML frontmatter:

```bash
# Extract and validate YAML frontmatter from an agent file
python3 -c "import yaml; import re; content = open('.github/agents/space-hulk-game-assistant.md').read(); yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL); yaml.safe_load(yaml_match.group(1)) if yaml_match else None"
```

### Testing Agent Effectiveness

Periodically review:

- Are suggestions relevant and helpful?
- Do agents understand new project patterns?
- Are there gaps in agent knowledge?
- Should we add new specialized agents?

## Best Practices

### 1. Use Descriptive Comments

Help agents understand your intent:

```python
# Create a new puzzle that requires combining two items
# It should fit the Space Hulk theme
```

### 2. Ask Specific Questions

Better questions get better answers:

```python
# Good: "How do I add error handling to this YAML loader?"
# Less specific: "How do I handle errors?"
```

### 3. Leverage Multiple Agents

Some tasks benefit from multiple agents:

```python
# Writing a test for CrewAI agent configuration
# Uses: Testing Specialist + CrewAI Expert + Python Specialist
```

### 4. Review Suggestions

Always review suggestions to ensure they fit your specific needs.

### 5. Provide Feedback

If suggestions aren't helpful, refine your prompts or update agent configurations.

## Troubleshooting

### Suggestions Don't Match Project Patterns

- Verify agent YAML files are valid
- Check that agent knowledge is up to date
- Ensure you're working in the correct file type
- Try being more specific in your prompts

### Agent Not Providing Relevant Help

- Check file location and type
- Verify GitHub Copilot is enabled
- Try rephrasing your question or comment
- Consult the relevant agent file to understand its scope

### YAML Configuration Errors

- Validate YAML syntax
- Check indentation (use spaces, not tabs)
- Ensure all required fields are present
- Review examples in the agent files

## Additional Resources

- **CONTRIBUTING.md**: Development guidelines and workflow
- **memory-bank/**: Project documentation and context
- **memory-bank/crewai-api-reference.md**: Detailed CrewAI framework reference
- **tests/README.md**: Testing guidelines and examples

## Feedback and Improvements

If you have suggestions for improving these agents:

1. Test your proposed changes locally
2. Update the relevant agent YAML file
3. Validate the YAML syntax
4. Submit a pull request with your improvements
5. Document the changes and rationale

---

These specialized agents are designed to make your development experience more productive and enjoyable. They embody the project's knowledge and best practices, helping you write better code faster while learning project patterns along the way.
