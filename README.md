# SpaceHulkGame Crew

Welcome to the SpaceHulkGame Crew project, powered by [crewAI](https://crewai.com). This is a text-based adventure game set in the Warhammer 40K universe, built using a multi-agent AI system that leverages the powerful and flexible framework provided by crewAI. Our specialized AI agents collaborate to create engaging narratives, design puzzles, and build immersive game mechanics.

## Project Overview

This project uses five specialized AI agents working together to create a complete text-based adventure game:

- **Plot Master**: Creates overarching narratives with branching paths and multiple endings
- **Narrative Architect**: Maps story structure into connected scenes
- **Puzzle Smith**: Designs puzzles, artifacts, NPCs, and challenges
- **Creative Scribe**: Writes vivid scene descriptions and dialogue
- **Mechanics Guru**: Defines game mechanics and creates technical documentation

## Installation

### Quick Start

**Automated Setup (Recommended)**

We provide automated setup scripts that handle all dependencies including Ollama and Python packages.

**Linux/macOS:**
```bash
git clone https://github.com/bencan1a/space_hulk_game.git
cd space_hulk_game
./setup.sh
```

**Windows:**
```powershell
git clone https://github.com/bencan1a/space_hulk_game.git
cd space_hulk_game
.\setup.ps1
```

**What gets installed:**
- ✓ UV package manager (fast Python package installer)
- ✓ Ollama (local LLM runtime)
- ✓ Qwen2.5 model for Ollama
- ✓ All Python dependencies (crewAI, mem0, PyYAML, litellm, etc.)
- ✓ Environment configuration (.env file)

For detailed setup instructions, troubleshooting, and manual installation, see **[SETUP.md](SETUP.md)**.

### Manual Installation

If you prefer manual installation:

1. **Install Python 3.10-3.12** from [python.org](https://www.python.org/downloads/)

2. **Install UV package manager:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
   # OR
   pip install uv
   ```

3. **Install dependencies:**
   ```bash
   uv pip install -e .
   ```

4. **Install Ollama (optional):**
   - Download from [ollama.com](https://ollama.com/download)
   - Pull model: `ollama pull qwen2.5`

5. **Configure environment:**
   - Copy `.env.example` to `.env` (or run setup script to create)
   - Edit `.env` to add API keys if using OpenAI

### Customizing

**Configuration Files:**

- `src/space_hulk_game/config/agents.yaml` - Define your AI agents
- `src/space_hulk_game/config/tasks.yaml` - Define agent tasks
- `src/space_hulk_game/crew.py` - Add custom logic and tools
- `src/space_hulk_game/main.py` - Modify entry point and inputs
- `.env` - Configure API keys and model selection

**Environment Variables:**

The `.env` file controls LLM and memory configuration:

```bash
# Use Ollama (local, free)
OPENAI_MODEL_NAME=ollama/qwen2.5
OLLAMA_BASE_URL=http://localhost:11434

# OR use OpenAI (requires API key)
# OPENAI_API_KEY=sk-your-key-here
# OPENAI_MODEL_NAME=gpt-4

# OR use Anthropic Claude (requires API key)
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# OPENAI_MODEL_NAME=claude-3-5-sonnet-20241022

# OR use OpenRouter (access to multiple providers)
# OPENROUTER_API_KEY=sk-or-v1-your-key-here
# OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet

# Optional: Mem0 for cloud-based memory
# MEM0_API_KEY=your-mem0-key-here
```

**For CI/CD and Test Environments:**

Set API keys as environment secrets in your CI platform (GitHub Actions, Docker, etc.) instead of using `.env` files. The application will use environment variables directly if set:

```yaml
# GitHub Actions example
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  OPENAI_MODEL_NAME: claude-3-5-sonnet-20241022
```

## Running the Project

### Prerequisites

**If using Ollama (local LLM):**
```bash
# Start Ollama service (if not already running)
ollama serve
```

**If using cloud LLM providers:**
- **OpenAI**: Set `OPENAI_API_KEY` in `.env`
- **Anthropic Claude**: Set `ANTHROPIC_API_KEY` in `.env`
- **OpenRouter**: Set `OPENROUTER_API_KEY` in `.env` (provides access to multiple models)
- **Azure OpenAI**: Set `AZURE_API_KEY`, `AZURE_API_BASE`, and `AZURE_API_VERSION` in `.env`

All providers are supported via [litellm](https://docs.litellm.ai/docs/providers).

### Run the Game

To start the crew of AI agents and begin game generation:

```bash
crewai run
```

Or use the Python entry point:

```bash
python -m space_hulk_game.main
```

This command initializes the Space Hulk Game crew, assembling the five specialized agents (Plot Master, Narrative Architect, Puzzle Smith, Creative Scribe, and Mechanics Guru) and executing their tasks sequentially to generate a complete text-based adventure game.

## Understanding Your Crew

The space_hulk_game Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Current Status: Phase 0 Complete ✅

✅ **CrewAI Best Practices Implemented** - The crew has been optimized following CrewAI framework best practices and the Phase 0 debugging strategy from `REVISED_RESTART_PLAN.md`.

**Recent Improvements:**
- ✅ Sequential process mode set as default (more reliable than hierarchical)
- ✅ Enhanced error handling with graceful fallbacks
- ✅ Comprehensive logging for debugging
- ✅ Complete documentation and quick start guide
- ✅ 19 validation tests (100% passing)

**Ready for Testing:**
The crew is now configured for reliable operation. See `QUICKSTART.md` for usage instructions.

**Key Documentation:**
- `QUICKSTART.md` - Quick reference guide
- `CREWAI_IMPROVEMENTS.md` - Complete improvement details
- `IMPLEMENTATION_SUMMARY.md` - What was delivered
- `REVISED_RESTART_PLAN.md` - Phase 0 strategy

**Next Steps:**
1. Run `python test_crew_init.py` to verify configuration
2. Test sequential mode: `crewai run --inputs "prompt: Your scenario"`
3. Validate outputs and performance
4. Proceed to Phase 1 enhancements

See `IMPLEMENTATION_SUMMARY.md` for complete details on improvements.

## GitHub Copilot Agents

This project includes specialized GitHub Copilot agent configurations to enhance development productivity. These agents provide context-aware assistance for different aspects of the project:

- **Main Project Assistant** (`.github/agents/space-hulk-game-assistant.md`): General project guidance and navigation
- **Python Development Specialist** (`.github/agents/python-developer.md`): Python best practices and code quality
- **CrewAI Framework Expert** (`.github/agents/crewai-specialist.md`): CrewAI patterns and agent/task configuration
- **Game Mechanics Specialist** (`.github/agents/game-mechanics-specialist.md`): Game design and narrative systems
- **YAML Configuration Expert** (`.github/agents/yaml-expert.md`): YAML file structure and validation
- **Testing Specialist** (`.github/agents/testing-specialist.md`): Testing patterns and coverage

When using GitHub Copilot, these agents automatically provide context-aware suggestions based on the file you're editing and the task you're performing.

## Testing

Run the test suite to verify the project is working correctly:

```bash
python -m unittest discover -s tests
```

For verbose output:

```bash
python -m unittest discover -s tests -v
```

## Project Documentation

The `memory-bank/` directory contains comprehensive project documentation:

- **productContext.md**: Project architecture and overview
- **activeContext.md**: Current development focus
- **progress.md**: Development history and milestones
- **decisionLog.md**: Design decisions and rationale
- **crewai-api-reference.md**: CrewAI framework reference guide

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Setting up the development environment
- Coding standards and best practices
- Testing requirements
- Using GitHub Copilot agents
- Pull request process

## Support

For support, questions, or feedback:
- Check the [CONTRIBUTING.md](CONTRIBUTING.md) guide
- Review the Memory Bank documentation in `memory-bank/`
- Visit crewAI [documentation](https://docs.crewai.com)
- Reach out through the [crewAI GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join crewAI Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with crewAI docs](https://chatg.pt/DWjSBZn)

## License

This project is open source. See the LICENSE file for details.

---

Let's create wonders together with the power and simplicity of crewAI!
