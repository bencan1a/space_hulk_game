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
- Git
- (Optional) Ollama for local LLM support
- (Optional) OpenAI API key for using OpenAI models

### Installation

**Option 1: Automated Setup (Recommended)**

Use the automated setup script that installs all dependencies and creates a virtual environment:

```bash
# Clone the repository
git clone https://github.com/bencan1a/space_hulk_game.git
cd space_hulk_game

# Run setup script
./setup.sh              # Linux/macOS
.\setup.ps1             # Windows

# For development environment
./setup.sh --dev        # Linux/macOS
.\setup.ps1 -Dev        # Windows

# Activate the virtual environment
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows
```

**Option 2: Manual Installation**

See the detailed [docs/SETUP.md](docs/SETUP.md) guide for manual installation steps.

**Quick manual setup:**

1. Create virtual environment:

   ```bash
   python -m venv .venv
   ```

2. Activate virtual environment:

   ```bash
   source .venv/bin/activate      # Linux/macOS/WSL
   .venv\Scripts\activate         # Windows
   ```

3. Install UV package manager:

   ```bash
   pip install uv
   ```

4. Install dependencies:

   ```bash
   uv pip install -e ".[dev]"
   ```

5. Configure environment:
   - Create `.env` file (see docs/SETUP.md or run setup script)
   - Add API keys if using OpenAI or Mem0

### Running the Project

**Important:** Always activate the virtual environment first!

```bash
# Activate virtual environment
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# If using Ollama, start it first
ollama serve  # In a separate terminal

# Run the game
crewai run
```

### Running Tests

```bash
# Activate virtual environment first
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# Run tests
python -m unittest discover -s tests -v
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
├── docs/                     # Product documentation
│   ├── README.md             # Main project documentation
│   ├── SETUP.md              # Setup instructions
│   ├── CONTRIBUTING.md       # This file
│   ├── AGENTS.md             # Agent documentation
│   └── crewai-api-reference.md  # CrewAI framework reference
├── project-plans/            # Development plans and agent outputs
│   ├── productContext.md     # Project architecture overview
│   ├── activeContext.md      # Current development focus
│   ├── progress.md           # Development history
│   ├── decisionLog.md        # Design decisions
│   ├── *.yaml                # Agent-generated outputs (gitignored)
│   └── README.md             # Folder documentation
├── tmp/                      # Temporary files (gitignored)
│   └── README.md             # Usage guidelines
└── pyproject.toml            # Project configuration

```

## Development Workflow

**Important:** Always ensure the virtual environment is activated before development work!

```bash
# Activate virtual environment
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# You should see (.venv) prefix in your terminal prompt
```

**Note:** VS Code will automatically use the `.venv` virtual environment after you reload the window. You don't need to manually activate it in VS Code's integrated terminal.

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow the coding standards (see below)
- Write tests for new functionality
- Update documentation as needed
- Use GitHub Copilot agents for assistance (see below)
- Ensure virtual environment is activated when running Python code

### 3. Test Your Changes

```bash
# Ensure virtual environment is activated
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

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

### Project Documentation Structure

The project uses a clear documentation structure:

**docs/** - User-facing product documentation:

- **README.md**: Main project documentation
- **SETUP.md**: Installation and setup instructions
- **CONTRIBUTING.md**: Development guidelines (this file)
- **AGENTS.md**: AI agent system documentation
- **crewai-api-reference.md**: CrewAI framework reference

**project-plans/** - Development plans and architectural context:

- **productContext.md**: Project architecture overview
- **activeContext.md**: Current development focus
- **progress.md**: Development history and timeline
- **decisionLog.md**: Design decisions and rationale
- **\*.yaml**: Agent-generated outputs (gitignored, regenerated each run)

**tmp/** - Temporary files (gitignored):

- Debug scripts, analysis reports, and working files
- Not committed to version control

### Updating Documentation

- Update relevant Memory Bank files when making significant changes
- Keep README.md current
- Document design decisions in decisionLog.md
- Update API references when changing interfaces

## Pull Request Process

### Before Submitting

1. Ensure virtual environment is activated
2. Ensure all tests pass
3. Update documentation
4. Follow coding standards
5. Add or update tests for new features
6. Run the full test suite locally

```bash
# Activate virtual environment
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# Run all tests
python -m unittest discover -s tests -v
```

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

- Check project documentation in `docs/`
- Review development plans in `project-plans/`
- Review the CrewAI API reference: `docs/crewai-api-reference.md`
- Ask GitHub Copilot using the specialized agents
- Open an issue on GitHub
- Contact the maintainers

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Space Hulk Game! Your efforts help make this project better for everyone.
