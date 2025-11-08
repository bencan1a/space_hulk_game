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

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/space_hulk_game/config/agents.yaml` to define your agents
- Modify `src/space_hulk_game/config/tasks.yaml` to define your tasks
- Modify `src/space_hulk_game/crew.py` to add your own logic, tools and specific args
- Modify `src/space_hulk_game/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the space_hulk_game Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The space_hulk_game Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Current Status: Debugging Phase

⚠️ **Important:** This project is currently in a debugging phase to validate that the multi-agent crew works reliably before adding additional features.

**Known Issue:** The hierarchical process mode has been experiencing hangs where agents become unresponsive. We are currently testing and validating the crew configuration.

**Testing Approach:**
1. Test sequential mode first (simpler, more reliable)
2. Debug hierarchical mode to identify coordination issues  
3. Once working reliably, proceed with planned enhancements

See `REVISED_RESTART_PLAN.md` for details on the debugging approach and `test_crew_generation.py` for validation testing.

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
