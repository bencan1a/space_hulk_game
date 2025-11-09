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

### Running the Game
```bash
# Standard execution
crewai run

# Alternative entry point
python -m space_hulk_game.main

# With specific inputs
crewai run --inputs "prompt: Your scenario"
```

### Testing
```bash
# Run all tests (mock mode, no API required)
python -m unittest discover -s tests -v

# Run specific test file
python -m unittest tests.test_api_validation -v

# Run with real API (requires API key)
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
export RUN_REAL_API_TESTS=1
python -m unittest tests.test_integration_sequential -v

# Validate API connectivity
python validate_api.py
```

### Setup & Dependencies
```bash
# Automated setup (includes Ollama, dependencies, .env)
./setup.sh              # Linux/macOS
.\setup.ps1             # Windows

# Manual dependency installation
crewai install
# OR
uv pip install -e .

# Start Ollama (if using local LLM)
ollama serve
ollama pull qwen2.5
```

### CrewAI Development Commands
```bash
# Train the crew
python -m space_hulk_game.main train <iterations> <filename>

# Replay specific task
python -m space_hulk_game.main replay <task_id>

# Test crew
python -m space_hulk_game.main test <iterations> <model_name>
```

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

Agent outputs are written to `game-config/*.yaml` based on templates defined there. The game generation creates structured YAML files containing:
- Plot outlines with branching paths
- Scene maps and connections
- Puzzle definitions
- Character dialogues
- Game mechanics specifications

## LLM Configuration

The project supports multiple LLM providers via litellm. Configure in `.env`:

**Ollama (Local, Free):**
```bash
OPENAI_MODEL_NAME=ollama/qwen2.5
OLLAMA_BASE_URL=http://localhost:11434
```

**Anthropic Claude (Recommended for production):**
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

The system uses Ollama by default for local development. Ollama must be running (`ollama serve`) before starting the crew.

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
- Agent outputs write to `game-config/*.yaml`
- Templates in `game-config/` define expected structure
- Temporary debug scripts go in `tmp/` (gitignored)
- Development plans go in `project-plans/`
- Product documentation goes in `docs/`

## Project Structure Context

```
space_hulk_game/
├── src/space_hulk_game/
│   ├── crew.py              # Main CrewAI crew implementation
│   ├── main.py              # Entry point with run/train/replay/test
│   ├── config/
│   │   ├── agents.yaml      # Agent definitions
│   │   ├── tasks.yaml       # Task definitions
│   │   └── gamedesign.yaml  # Game design examples
│   └── tools/               # Custom tools (if needed)
├── tests/                   # Test suite (unittest)
├── docs/                    # Product documentation
├── game-config/             # Game design templates for AI agents
├── project-plans/           # Development plans and architectural docs
└── tmp/                     # Temporary debug scripts (gitignored)
```

## Environment Setup

1. **Copy .env.example to .env**: `cp .env.example .env`
2. **Configure LLM provider**: Edit `.env` with your API key and model
3. **Install dependencies**: `./setup.sh` or `crewai install`
4. **Start Ollama** (if using local): `ollama serve`
5. **Validate setup**: `python validate_api.py`

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

- **docs/SETUP.md**: Detailed installation instructions
- **docs/QUICKSTART.md**: Quick reference guide
- **docs/CONTRIBUTING.md**: Development guidelines
- **docs/AGENTS.md**: Comprehensive agent documentation
- **docs/crewai-api-reference.md**: CrewAI framework reference
- **project-plans/REVISED_RESTART_PLAN.md**: Phase 0 debugging strategy
- **.github/copilot-instructions.md**: Complete coding standards reference
