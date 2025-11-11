# Space Hulk Game

A text-based adventure game set in the Warhammer 40K universe, powered by CrewAI multi-agent system.

## 🎮 Play the Game

Experience the grimdark universe of Warhammer 40,000 in this interactive text adventure!

```bash
# After installation, launch the demo game:
demo_game

# Or use the alternative command:
play_game
```

See **[How to Play](docs/PLAYING_GAMES.md)** for detailed player guide and commands.

## 📚 Documentation

All documentation has been moved to the [`docs/`](docs/) folder:

### For Players
- **[How to Play](docs/PLAYING_GAMES.md)** - Complete player guide with commands and tips

### For Developers
- **[Getting Started](docs/README.md)** - Project overview and quick start guide
- **[Setup Guide](docs/SETUP.md)** - Detailed installation instructions
- **[Quick Start](docs/QUICKSTART.md)** - Quick setup and running guide
- **[Game Engine Architecture](docs/GAME_ENGINE.md)** - Technical architecture and design patterns
- **[Contributing](docs/CONTRIBUTING.md)** - Development guidelines and best practices
- **[Agents Documentation](docs/AGENTS.md)** - AI agent system documentation
- **[Debugging Guide](docs/DEBUGGING_GUIDE.md)** - Troubleshooting and debugging tips
- **[Workflows Guide](docs/WORKFLOWS.md)** - GitHub Actions workflows documentation
- **[Secrets Setup](docs/SECRETS_SETUP.md)** - Setting up API keys for workflows
- **[CrewAI API Reference](docs/crewai-api-reference.md)** - CrewAI framework reference

## Quick Start

### Playing the Demo Game

```bash
# Clone the repository
git clone https://github.com/bencan1a/space_hulk_game.git
cd space_hulk_game

# Run automated setup (Linux/macOS)
./setup.sh

# Or on Windows
.\setup.ps1

# Activate the virtual environment
source .venv/bin/activate      # Linux/macOS/WSL
# OR
.venv\Scripts\activate         # Windows

# Play the demo game!
demo_game
```

### Generating New Games with AI

```bash
# Generate a new game using CrewAI agents
crewai run

# Then play your generated game
demo_game --game-dir game-config/
```

For detailed instructions, see the [Setup Guide](docs/SETUP.md).

## 🏗️ Project Structure

```
space_hulk_game/
├── docs/                          # Product documentation
│   ├── PLAYING_GAMES.md          # Player guide
│   └── GAME_ENGINE.md            # Engine architecture
├── game-config/                   # Game design configuration and AI-generated content
├── project-plans/                 # Development plans and architectural docs
├── src/
│   └── space_hulk_game/
│       ├── engine/               # Game engine (Chunks 4.1-4.5)
│       │   ├── game_state.py     # Game state model
│       │   ├── scene.py          # Scene model
│       │   ├── entities.py       # Items, NPCs, Events
│       │   ├── parser.py         # Command parser
│       │   ├── actions.py        # Action system
│       │   ├── engine.py         # Main game loop
│       │   ├── loader.py         # Content loader
│       │   ├── validator.py      # Game validator
│       │   └── persistence.py    # Save/load system
│       ├── demo_game.py          # CLI interface (Chunk 4.6)
│       ├── crew.py               # CrewAI agent orchestration
│       └── config/               # Agent and task configurations
├── tests/                         # Comprehensive test suite (250+ tests)
├── tmp/                          # Temporary debug scripts (gitignored)
└── .github/                      # GitHub configuration and Copilot agents
```

## 🎯 Features

### Game Engine (v1.0)
- ✅ **Text-based adventure engine** - Complete game loop with command parsing
- ✅ **Rich game world** - Scenes, items, NPCs, events, and puzzles
- ✅ **Save/load system** - Persistent game state with multiple save slots
- ✅ **Content validation** - Automatic validation of AI-generated content
- ✅ **Colorized CLI** - Beautiful terminal interface with color coding

### AI Content Generation
- ✅ **Multi-agent system** - 6 specialized CrewAI agents collaborate to create games
- ✅ **Procedural generation** - Unique stories, puzzles, and challenges
- ✅ **Warhammer 40K themed** - Authentic grimdark atmosphere and lore

### Quality Assurance
- ✅ **250+ tests** - Comprehensive test coverage (unit, integration, E2E)
- ✅ **Type safety** - Full type hints and mypy checking
- ✅ **Code quality** - PEP 8 compliant, linted with ruff and black
- ✅ **Security** - Bandit security scanning

## 🚀 Technology Stack

- **Python 3.10+** - Modern Python with type hints
- **CrewAI** - Multi-agent AI collaboration framework
- **Cloud LLM Services** - Anthropic Claude, OpenRouter, OpenAI
- **Ollama** - Optional local LLM integration
- **Mem0** - Context retention across agent interactions
- **Colorama** - Cross-platform terminal colors
- **PyYAML** - Configuration and content management

## License

See [LICENSE](LICENSE) file for details.
