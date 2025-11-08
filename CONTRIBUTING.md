# Contributing to Space Hulk Game

Thank you for your interest in contributing to the Space Hulk Game project! This document provides guidelines and information to help you contribute effectively.

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [GitHub Copilot Agents](#github-copilot-agents)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Getting Started

### Prerequisites

- Python >= 3.10, < 3.13
- UV package manager
- Git
- OpenAI API key (for running the crew)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/bencan1a/space_hulk_game.git
cd space_hulk_game
```

2. Install UV package manager (if not already installed):
```bash
pip install uv
```

3. Install dependencies:
```bash
crewai install
```

4. Create a `.env` file and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_key_here
```

### Running the Project

```bash
crewai run
```

### Running Tests

```bash
python -m unittest discover -s tests
```

## Project Structure

```
space_hulk_game/
├── .github/
│   └── copilot/              # Copilot agent configurations
│       ├── agent.yml         # Main project assistant
│       ├── python-agent.yml  # Python development specialist
│       ├── crewai-agent.yml  # CrewAI framework expert
│       ├── game-mechanics-agent.yml  # Game design specialist
│       ├── yaml-agent.yml    # YAML configuration expert
│       └── testing-agent.yml # Testing specialist
├── src/
│   └── space_hulk_game/
│       ├── config/           # YAML configuration files
│       │   ├── agents.yaml   # Agent definitions
│       │   ├── tasks.yaml    # Task definitions
│       │   └── gamedesign.yaml
│       ├── tools/            # Custom tools for agents
│       ├── crew.py           # Main crew implementation
│       └── main.py           # Entry point
├── tests/                    # Test files
│   ├── test_space_hulk_game.py
│   └── README.md
├── memory-bank/              # Project documentation and context
│   ├── productContext.md     # Project overview
│   ├── activeContext.md      # Current development focus
│   ├── progress.md           # Development history
│   ├── decisionLog.md        # Design decisions
│   └── crewai-api-reference.md  # CrewAI framework reference
├── narrative_map.yaml        # Scene structure
├── scene_texts.yaml          # Scene descriptions
├── plot_outline.yaml         # Story outline
├── puzzle_design.yaml        # Puzzle specifications
├── prd_document.yaml         # Product requirements
└── pyproject.toml            # Project configuration

```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow the coding standards (see below)
- Write tests for new functionality
- Update documentation as needed
- Use GitHub Copilot agents for assistance (see below)

### 3. Test Your Changes

```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test file
python -m unittest tests.test_space_hulk_game
```

### 4. Commit and Push

```bash
git add .
git commit -m "Brief description of changes"
git push origin feature/your-feature-name
```

### 5. Create Pull Request

- Provide a clear description of changes
- Reference any related issues
- Ensure all tests pass
- Request review from maintainers

## GitHub Copilot Agents

This project includes specialized Copilot agents to assist with development. These agents provide context-aware suggestions based on project patterns and best practices.

### Available Agents

1. **Main Project Assistant** (`.github/copilot/agent.yml`)
   - General project guidance
   - Project structure navigation
   - Technology stack assistance

2. **Python Development Specialist** (`.github/copilot/python-agent.yml`)
   - Python best practices
   - Type hints and error handling
   - Code quality and style

3. **CrewAI Framework Expert** (`.github/copilot/crewai-agent.yml`)
   - Agent and task configuration
   - CrewAI patterns and workflows
   - Memory and LLM integration

4. **Game Mechanics Specialist** (`.github/copilot/game-mechanics-agent.yml`)
   - Game design patterns
   - Narrative branching
   - Puzzle and combat mechanics

5. **YAML Configuration Expert** (`.github/copilot/yaml-agent.yml`)
   - YAML syntax and structure
   - Configuration file management
   - Validation and best practices

6. **Testing Specialist** (`.github/copilot/testing-agent.yml`)
   - Test writing and organization
   - Mocking patterns
   - Coverage and validation

### Using Copilot Agents

When working with GitHub Copilot in this project:

1. **Context-Aware Suggestions**: Copilot will automatically use the agent configurations to provide relevant suggestions based on the file you're editing and the task you're performing.

2. **Ask Specific Questions**: You can ask Copilot questions related to specific agents' expertise areas. For example:
   - "How do I add a new CrewAI agent?"
   - "What's the YAML structure for tasks?"
   - "How should I test this function?"

3. **Code Generation**: Copilot will generate code following project patterns and conventions defined in the agent configurations.

4. **Documentation**: Copilot can help generate documentation consistent with project style.

## Coding Standards

### Python Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Code Organization

```python
# Standard library imports
import os
import sys

# Third-party imports
import yaml
from crewai import Agent, Task

# Local imports
from space_hulk_game.tools import CustomTool
```

### Documentation

- Use docstrings for all classes and functions
- Follow Google or NumPy docstring format
- Include usage examples for complex functions

### Error Handling

```python
try:
    # Code that might raise an exception
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Error in operation: {str(e)}")
    # Handle or re-raise
    raise
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Important operation completed")
logger.error(f"Error occurred: {error_message}")
```

## Testing Guidelines

### Test Structure

- One test file per module: `test_<module_name>.py`
- Use descriptive test names: `test_<functionality>_<condition>_<expected_result>`
- Group related tests in test classes

### Writing Tests

```python
import unittest
from unittest.mock import patch, MagicMock

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = {"key": "value"}
    
    def test_feature_with_valid_input(self):
        """Test that feature works with valid input"""
        result = my_feature(self.test_data)
        self.assertEqual(result, expected_value)
    
    def test_feature_handles_errors(self):
        """Test that feature handles errors gracefully"""
        with self.assertRaises(ValueError):
            my_feature(invalid_data)
```

### Test Coverage

- Aim for at least 70% code coverage
- Focus on critical paths and edge cases
- Test both success and failure scenarios
- Mock external dependencies

## Documentation

### Memory Bank

The `memory-bank/` directory contains project documentation:

- **productContext.md**: Project overview and architecture
- **activeContext.md**: Current development focus
- **progress.md**: Development history
- **decisionLog.md**: Design decisions and rationale
- **crewai-api-reference.md**: CrewAI framework reference

### Updating Documentation

- Update relevant Memory Bank files when making significant changes
- Keep README.md current
- Document design decisions in decisionLog.md
- Update API references when changing interfaces

## Pull Request Process

### Before Submitting

1. Ensure all tests pass
2. Update documentation
3. Follow coding standards
4. Add or update tests for new features
5. Run the full test suite locally

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or breaking changes documented)
```

### Review Process

1. Automated tests will run on your PR
2. Maintainers will review your code
3. Address any feedback
4. Once approved, your PR will be merged

## Questions or Issues?

- Check the Memory Bank documentation in `memory-bank/`
- Review the CrewAI API reference: `memory-bank/crewai-api-reference.md`
- Ask GitHub Copilot using the specialized agents
- Open an issue on GitHub
- Contact the maintainers

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Space Hulk Game! Your efforts help make this project better for everyone.
