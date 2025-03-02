# Space Hulk Game Project Context

## Project Overview

The Space Hulk Game is a text-based adventure game built using the crewAI framework. The game is set in the Warhammer 40,000 universe aboard a derelict Space Hulk (a massive conglomeration of ancient starships) adrift in space. Players navigate through the Space Hulk, encountering dangers, solving puzzles, and making moral choices that affect the game's outcome.

## Memory Bank Structure

This Memory Bank contains the following core files:

- **productContext.md** (this file): Provides an overview of the project, its architecture, components, and project patterns.
- **activeContext.md**: Records the current development focus, ongoing tasks, and immediate priorities.
- **progress.md**: Tracks project milestones, completed tasks, and development history.
- **decisionLog.md**: Documents key architectural and design decisions, including alternatives considered and rationale.
- **crewai-api-reference.md**: Token-efficient reference of CrewAI framework components (agents, tasks, tools, flows, knowledge, processes, LLMs, memory, planning) optimized for AI assistant use.

## CrewAI API Reference

The `crewai-api-reference.md` file contains a structured, token-efficient reference for the CrewAI framework components. This reference is designed specifically for AI assistant use to enhance decision-making and provide accurate answers about CrewAI implementation.

### How to Use the Reference

To access information about specific CrewAI components, refer to the corresponding sections in the reference document:

1. For information on **agents**, see the "Agents" section, which includes parameters, syntax, relationships, and examples.
2. For information on **tasks**, see the "Tasks" section for details on task configuration and assignment.
3. For information on **tools**, **flows**, **knowledge**, **processes**, **LLMs**, **memory**, and **planning**, see their respective sections.

Each component section is structured consistently with:
- Definition
- Parameters
- Syntax
- Relationships with other components
- Integration patterns
- Examples

This reference should be consulted when:
- Implementing CrewAI components
- Understanding component relationships
- Identifying optimal patterns for specific use cases
- Troubleshooting integration issues

## Project Architecture

### crewAI Framework

This project leverages the crewAI framework to create a multi-agent AI system where different AI agents collaborate to build and enhance the game. The core components include:

#### Agents

Five specialized AI agents with distinct roles focused on text adventure development:

1. **Plot Master Agent**: Creates the overarching plot with multiple endings and branching paths
2. **Narrative Architect Agent**: Maps the narrative structure into connected scenes
3. **Puzzle Smith Agent**: Designs puzzles, artifacts, NPCs, and monsters that align with the story
4. **Creative Scribe Agent**: Produces vivid text descriptions and dialogue for all scenes
5. **Mechanics Guru Agent**: Defines game mechanics, systems, and creates the final PRD

#### Tasks

Each agent is assigned specific tasks in a sequential workflow:

1. **Generate Overarching Plot**: Plot creation with key branches and possible endings
2. **Create Narrative Map**: Transform plot outline into a structured map of connected scenes
3. **Design Artifacts And Puzzles**: Create interactive elements like puzzles, artifacts, and NPCs
4. **Write Scene Descriptions And Dialogue**: Provide immersive descriptions and dialogue
5. **Create Game Mechanics PRD**: Draft product requirements defining mechanics and systems

#### Process Flow

The system follows a sequential process where:
1. The overarching plot is created first
2. The narrative map is developed based on the plot
3. Puzzles and artifacts are designed to fit into the narrative
4. Scene descriptions and dialogues are written
5. Game mechanics are defined and documented in a PRD

#### Implementation Extensions

The implementation includes:
- **Pre-processing hook**: Prepares inputs before the crew starts
- **Post-processing hook**: Refines the output after the crew finishes
- **YAML configuration**: All agents and tasks defined in external YAML files for easy editing

### Game Structure

The game itself follows a text adventure format with:

- **Text-based interface**: Players use commands like "GO EAST," "OPEN HATCH," etc.
- **Exploration mechanics**: Navigate through the Space Hulk environment
- **Item interaction**: Find and use items to solve puzzles
- **Combat system**: Turn-based encounters with enemies
- **Branching narrative**: Player choices affect the story outcome
- **Health & trauma system**: Track player status
- **Multiple endings**: Based on moral choices made during gameplay

## Technology Stack

- **Python**: Primary programming language
- **crewAI**: Framework for AI agent collaboration
- **YAML**: Configuration for agents and tasks
- **Text-based UI**: For game interaction

## Development Patterns

- **Configuration-driven design**: Agents and tasks are defined in YAML files
- **Decorator pattern**: Used for agent and task definitions
- **Sequential processing**: Tasks execute in a defined order
- **Collaborative AI**: Multiple specialized agents contribute to the final product
- **Lifecycle hooks**: Pre-processing inputs and post-processing outputs
- **Separation of concerns**: Each agent has a specialized role in the development workflow

## Project Status

The project is currently in development with the basic framework in place. The codebase has been updated to use improved agent and task implementations with a more specialized focus on text adventure game development. The Memory Bank will track ongoing progress and architectural decisions as the project evolves.