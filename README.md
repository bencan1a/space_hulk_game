# Space Hulk Game

A text-based adventure game set in the Warhammer 40K universe, powered by CrewAI multi-agent system.

## Documentation

All documentation has been moved to the [`docs/`](docs/) folder:

- **[Getting Started](docs/README.md)** - Project overview and quick start guide
- **[Setup Guide](docs/SETUP.md)** - Detailed installation instructions
- **[Quick Start](docs/QUICKSTART.md)** - Quick setup and running guide
- **[Contributing](docs/CONTRIBUTING.md)** - Development guidelines and best practices
- **[Agents Documentation](docs/AGENTS.md)** - AI agent system documentation
- **[Debugging Guide](docs/DEBUGGING_GUIDE.md)** - Troubleshooting and debugging tips
- **[CrewAI API Reference](docs/crewai-api-reference.md)** - CrewAI framework reference

## Quick Start

```bash
# Clone the repository
git clone https://github.com/bencan1a/space_hulk_game.git
cd space_hulk_game

# Run automated setup (Linux/macOS)
./setup.sh

# Or on Windows
.\setup.ps1

# Run the game
crewai run
```

For detailed instructions, see the [Setup Guide](docs/SETUP.md).

## Project Structure

```
space_hulk_game/
├── docs/              # Product documentation
├── project-plans/     # Development plans and agent working files
├── src/               # Source code
├── tests/             # Test suite
├── tmp/               # Temporary debug scripts and reports (gitignored)
└── .github/           # GitHub configuration and Copilot agents
```

## License

See [LICENSE](LICENSE) file for details.
