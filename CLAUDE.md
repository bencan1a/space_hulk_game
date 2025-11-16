# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a text-based adventure game set in the Warhammer 40K Space Hulk universe, built using CrewAI's multi-agent AI framework. Five specialized AI agents collaborate to generate complete game narratives, puzzles, mechanics, and documentation.

**Technology Stack:**

- Python 3.10-3.12
- CrewAI (multi-agent orchestration)
- Ollama (local LLM, qwen2.5 model) + cloud LLM support
- Mem0 (context retention)
- PyYAML (configuration)
- litellm (multi-provider LLM support)
- unittest (testing)
- uv (package manager)

## Essential Commands

**Important:** The setup script creates a `.venv` virtual environment. You must activate it before running any commands:

```bash
# Activate virtual environment
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# You should see (.venv) prefix in your terminal prompt
```

**Note:** VS Code will automatically detect and use the `.venv` virtual environment after you reload the window.

### Running the Game

```bash
# Ensure virtual environment is activated first!
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# Standard execution
crewai run

# Alternative entry point
python -m space_hulk_game.main

# With specific inputs
crewai run --inputs "prompt: Your scenario"
```

### Testing

```bash
# Ensure virtual environment is activated first!
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# Run all tests (mock mode, no API required)
python -m unittest discover -s tests -v

# Run specific test file
python -m unittest tests.test_api_validation -v

# Run with real API (requires API key)
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
export RUN_REAL_API_TESTS=1
python -m unittest tests.test_integration_sequential -v

# Validate API connectivity
python tools/validate_api.py
```

### Pre-commit Hooks

Automatic quality checks before commit:

```bash
# Install hooks (one-time setup)
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Skip hooks for a commit (use sparingly)
git commit --no-verify -m "message"
```

### Setup & Dependencies

```bash
# Automated setup (dependencies, .env, virtual environment)
./setup.sh              # Linux/macOS
.\setup.ps1             # Windows

# For development with type checking and linting tools
./setup.sh --dev        # Linux/macOS
.\setup.ps1 -Dev        # Windows

# Optional: Install Ollama for local LLM (not required for cloud services)
./setup.sh --with-ollama --with-model   # Linux/macOS
.\setup.ps1 -WithOllama -WithModel      # Windows

# After setup, activate the virtual environment
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# Manual dependency installation (with venv activated)
crewai install
# OR
uv pip install -e .

# Install with dev dependencies (includes mypy, pytest, black, ruff, type stubs)
uv pip install -e ".[dev]"

# Install type stubs only (if getting mypy errors about missing stubs)
pip install types-pyyaml

# Start Ollama (if using local LLM - optional)
ollama serve
ollama pull qwen2.5
```

### CrewAI Development Commands

```bash
# Ensure virtual environment is activated first!
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# Train the crew
python -m space_hulk_game.main train <iterations> <filename>

# Replay specific task
python -m space_hulk_game.main replay <task_id>

# Test crew
python -m space_hulk_game.main test <iterations> <model_name>
```

### Makefile Commands (New!)

Quick command shortcuts (run after activating venv):

```bash
make help           # Show all available commands
make test           # Run tests (mock mode)
make check-all      # Run all quality checks
make fix            # Auto-fix issues and format
make lint           # Check code quality
make format         # Auto-format code
make type-check     # Run type checking
make security       # Run security scan
make coverage       # Generate coverage report
make run-crew       # Run CrewAI crew
make validate-api   # Validate API connectivity
make clean          # Clean cache and old files
```

## New Tools and Automation

**Makefile** - 18 command shortcuts (see `make help`)

**Pre-commit Hooks** - 9 automatic quality checks before commit (see `.pre-commit-config.yaml`)

**CI/CD Workflows** - 5 GitHub Actions workflows in `.github/workflows/`:

- `ci.yml` - Multi-platform testing (Ubuntu, Windows, macOS) and PR validation
- `nightly-regression.yml` - Daily comprehensive testing
- `update-docs.yml` - Auto-generate documentation
- `run-crewai-agents.yml` - On-demand CrewAI agent execution
- `run-kloc-report.yml` - KLOC reporting

**Documentation Automation** - `tools/build_context.py` generates:

- API documentation (HTML, in `docs/_generated/api/`)
- `CONTEXT.md` (unified context for AI agents)
- `SUMMARY.md` (project quick stats)
- Runs daily at 3 AM UTC via workflow

For AI agent guidance, see **AGENTS.md** (START HERE when working with agent definitions).

## Architecture

### Multi-Agent System

The system orchestrates 6 specialized agents through CrewAI:

1. **NarrativeDirectorAgent**: Ensures narrative cohesion (manager in hierarchical mode)
2. **PlotMasterAgent**: Creates overarching plot and story structure
3. **NarrativeArchitectAgent**: Maps plot into detailed scene structure
4. **PuzzleSmithAgent**: Designs puzzles, artifacts, and game mechanics
5. **CreativeScribeAgent**: Writes vivid descriptions and dialogue
6. **MechanicsGuruAgent**: Defines game systems and creates technical documentation

### Process Modes

**Sequential Mode (Default):**

- All agents work as peers in defined order
- Simplest configuration, most reliable
- No manager delegation overhead
- Use this first to validate functionality

**Hierarchical Mode (Advanced):**

- NarrativeDirectorAgent acts as manager
- Manager delegates tasks to worker agents
- Enables feedback loops and iterative refinement
- More complex, requires careful dependency management
- Use `create_hierarchical_crew()` method

**Best Practice:** Start with sequential mode, only use hierarchical after validating basic functionality.

### Configuration Architecture

All agents and tasks are defined in YAML files under `src/space_hulk_game/config/`:

- **agents.yaml**: Agent definitions (role, goal, backstory, capabilities)
- **tasks.yaml**: Task definitions (description, expected output, dependencies)
- **gamedesign.yaml**: Game design templates and examples for AI agents

**CRITICAL:** Method names in `crew.py` must exactly match the keys in YAML config files (case-sensitive). For example:

```python
# In crew.py
@agent
def plot_master_agent(self) -> Agent:
    return Agent(config=self.agents_config["PlotMasterAgent"], ...)

# In agents.yaml
PlotMasterAgent:  # Must match the key used in crew.py
  role: "Master Storyteller"
  ...
```

### Output Structure

Agent outputs are written to `game-config/*.json` based on templates defined there. The game generation creates structured JSON files containing:

- Plot outlines with branching paths
- Scene maps and connections
- Puzzle definitions
- Character dialogues
- Game mechanics specifications

## LLM Configuration

The project supports multiple LLM providers via litellm. Configure in `.env`:

**Anthropic Claude (Recommended):**

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_MODEL_NAME=claude-3-5-sonnet-20241022
```

**OpenRouter (Access to multiple providers):**

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet
```

**OpenAI:**

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL_NAME=gpt-4
```

**Ollama (Local, Optional):**

```bash
OPENAI_MODEL_NAME=ollama/qwen2.5
OLLAMA_BASE_URL=http://localhost:11434
```

The system is configured for cloud LLM services by default. If using Ollama locally, you must install it using `./setup.sh --with-ollama --with-model` and ensure it's running (`ollama serve`) before starting the crew.

## Key Development Patterns

### CrewAI Agent Definition

```python
@agent
def agent_name(self) -> Agent:
    return Agent(
        config=self.agents_config["AgentName"],
        llm=self.llm,
        verbose=True
    )
```

### CrewAI Task Definition

```python
@task
def task_name(self) -> Task:
    return Task(
        config=self.tasks_config["TaskName"]
    )
```

### Lifecycle Hooks

```python
@before_kickoff
def prepare_inputs(self, inputs: dict) -> dict:
    """Validate and prepare inputs before crew starts"""
    # Add validation logic
    return inputs

@after_kickoff
def process_outputs(self, output) -> dict:
    """Process outputs after crew finishes"""
    # Add processing logic
    return output
```

### Python Coding Standards

- **PEP 8** compliance
- **Type hints** on all function parameters and return values
- **Docstrings** for classes and functions (Google or NumPy style)
- **Specific exception types** (never bare `except`)
- **Logging** for important operations
- **Import organization**: standard library → third-party → local

### Error Handling Pattern

```python
import logging
logger = logging.getLogger(__name__)

try:
    # Operation
    logger.info("Starting operation")
    result = some_function()
except SpecificException as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    # Graceful degradation or re-raise
    raise
```

## Testing Philosophy

The project uses **unittest** with comprehensive mocking to allow tests to run without API access:

**Mock Mode (Default):**

- No API credentials required
- Fast execution, no API costs
- Suitable for CI/CD
- Tests validate structure and logic

**Real API Mode:**

- Requires API keys
- Validates actual LLM behavior
- Use sparingly (costs, slower)
- Set `RUN_REAL_API_TESTS=1`

**Test Coverage:**

- Unit tests with mocked dependencies
- Integration tests for full crew execution
- API validation tests
- Configuration validation tests

When writing new features, add unit tests with mocks first, then optionally validate with real API.

## Critical Implementation Notes

### YAML Configuration Rules

1. **Method names in crew.py must match YAML keys exactly** (case-sensitive)
2. Use folded style (`>`) for multi-line strings in YAML
3. Task dependencies use `dependencies:` (execution order), not `context:`
4. `context:` provides data flow between tasks without blocking

### CrewAI Best Practices (from REVISED_RESTART_PLAN.md)

1. Start with sequential process (simplest)
2. Validate all agents complete without hanging
3. Test hierarchical with minimal tasks (3-5) first
4. Incrementally add complexity
5. Monitor for hanging/blocking behavior
6. Debug specific issues before adding features

### Known Issues & Mitigations

- **Hierarchical mode can hang with complex dependencies**: Use sequential first
- **Memory/planning features can cause blocks**: Disabled until proven stable
- **Evaluation tasks may create deadlocks**: Add incrementally
- **LLM timeouts in Ollama**: Consider timeout detection in crew execution

### Output Files

- Agent outputs write to `game-config/*.json`
- Templates in `game-config/` define expected structure
- Temporary debug scripts go in `tmp/` (gitignored)
- Development plans go in `project-plans/`
- Product documentation goes in `docs/`

## Project Structure Context

```
space_hulk_game/
├── .github/
│   ├── agents/              # Custom agent profiles
│   └── workflows/           # CI/CD automation (5 workflows)
├── agent-tmp/               # Temporary outputs (gitignored, 7-day cleanup)
├── agent-projects/          # Active projects (committed, requires plan.md)
├── docs/
│   └── _generated/api/      # Auto-generated API docs
├── src/space_hulk_game/
│   ├── crew.py              # Main CrewAI crew implementation
│   ├── main.py              # Entry point with run/train/replay/test
│   ├── config/
│   │   ├── agents.yaml      # Agent definitions
│   │   ├── tasks.yaml       # Task definitions
│   │   └── gamedesign.yaml  # Game design examples
│   └── tools/               # Custom tools (if needed)
├── tests/                   # Test suite (unittest)
├── tools/                   # Utility scripts (validate_api.py, build_context.py, etc.)
├── game-config/             # Game design templates for AI agents
├── AGENTS.md                # AI agent guidance (START HERE!)
├── CONTEXT.md               # Auto-generated project context for AI
├── SUMMARY.md               # Auto-generated project summary
├── Makefile                 # Command shortcuts
├── .pre-commit-config.yaml  # Quality check hooks
└── project-plans/           # Development plans and architectural docs
```

## Environment Setup

1. **Run setup script**: `./setup.sh` (Linux/macOS) or `.\setup.ps1` (Windows)
2. **Activate virtual environment**:
   - Linux/macOS/WSL: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`
3. **Configure LLM provider**: Edit `.env` with your API key and model
4. **Optional - Install Ollama** (if using local LLM):
   - Run setup again with: `./setup.sh --with-ollama --with-model` or `.\setup.ps1 -WithOllama -WithModel`
   - Start Ollama: `ollama serve`
5. **Validate setup**: `python validate_api.py`

**Important:** The setup script creates a `.venv` virtual environment containing all dependencies. Always activate it before running commands. The setup script does NOT install Ollama by default - it's designed for cloud LLM services.

For CI/CD environments, set API keys as environment variables instead of using `.env` files.

## Warhammer 40K / Space Hulk Theme

When working on game content, maintain these themes:

- **Gothic horror**: Dark, oppressive atmosphere
- **Grimdark**: No good choices, only survival
- **Body horror**: Mutations, corruption
- **Military fiction**: Squad tactics, duty, sacrifice
- **Isolation**: Cut off from help, on your own
- **Ancient technology**: Failing systems, machine spirits

## Additional Resources

- **AGENTS.md**: AI agent guidance (start here when working with agent definitions)
- **CONTEXT.md**: Auto-generated unified context for AI agents
- **SUMMARY.md**: Auto-generated project summary and quick stats
- **docs/SETUP.md**: Detailed installation instructions
- **docs/QUICKSTART.md**: Quick reference guide
- **docs/CONTRIBUTING.md**: Development guidelines
- **docs/crewai-api-reference.md**: CrewAI framework reference
- **project-plans/REVISED_RESTART_PLAN.md**: Phase 0 debugging strategy
- **.github/copilot-instructions.md**: Complete coding standards reference
- **Makefile**: Run `make help` for all available commands
- **.pre-commit-config.yaml**: Automatic quality checks configuration
