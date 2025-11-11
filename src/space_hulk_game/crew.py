# crew.py
"""
Space Hulk Game - CrewAI Implementation

This module implements a multi-agent AI system using CrewAI to generate
text-based adventure games set in the Warhammer 40K Space Hulk universe.

## Architecture Overview

The system uses 6 specialized agents coordinated through CrewAI:
- NarrativeDirectorAgent: Ensures narrative cohesion (manager in hierarchical mode)
- PlotMasterAgent: Creates overarching plot and story structure
- NarrativeArchitectAgent: Maps plot into detailed scene structure
- PuzzleSmithAgent: Designs puzzles, artifacts, and game mechanics
- CreativeScribeAgent: Writes vivid descriptions and dialogue
- MechanicsGuruAgent: Defines game systems and creates PRD

## Process Modes

### Sequential Mode (Default)
- All agents work as peers in defined order
- Simplest configuration, most reliable
- Use this mode first to validate basic functionality
- No manager delegation or coordination overhead

### Hierarchical Mode (Advanced)
- NarrativeDirectorAgent acts as manager
- Manager delegates tasks to specialized worker agents
- Enables feedback loops and iterative refinement
- More complex, requires careful task dependency management
- Use create_hierarchical_crew() method for testing

## Implementation Notes (per REVISED_RESTART_PLAN.md)

Phase 0 Debugging Strategy:
1. Start with sequential process (simplest configuration)
2. Validate all agents complete their tasks without hanging
3. Test hierarchical with minimal tasks (3-5 tasks)
4. Incrementally add evaluation tasks
5. Monitor for hanging/blocking behavior
6. Debug specific issues before adding complexity

Best Practices Applied:
- Clear separation of sequential vs hierarchical modes
- Comprehensive logging for debugging
- Graceful error handling with recovery mechanisms
- Metadata tracking for monitoring and analysis
- Explicit timeout handling (to be added in kickoff)
- Task dependencies separated from context usage

## Quality Checking Integration (Phase 3)

Quality checking with retry logic is available but DISABLED by default.
To enable quality checking:
1. Set environment variable: export QUALITY_CHECK_ENABLED=true
2. Or modify src/space_hulk_game/config/quality_config.yaml (global.enabled: true)

Quality checking features:
- Evaluates task outputs against quality metrics
- Automatically retries tasks that fail quality checks (up to 3 attempts)
- Provides specific feedback for improvement on each retry
- Logs quality scores for monitoring
- Configurable thresholds per task type

For integration examples, see src/space_hulk_game/quality/integration.py

Known Issues & Mitigations:
- Hierarchical mode can hang with complex dependencies: Use sequential first
- Memory/planning features can cause blocks: Disabled until proven stable
- Evaluation tasks may create deadlocks: Add incrementally
- LLM timeouts in Ollama: Add timeout detection in crew execution
"""

import datetime
import logging
import os
from pathlib import Path
from typing import Any, cast

import yaml
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, after_kickoff, agent, before_kickoff, crew, task

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@CrewBase
class SpaceHulkGame:
    """
    A specialized crew that designs text-based adventure games, from overarching
    plot creation to puzzle design, world-building, and final PRD documentation.
    """

    # Paths to the YAML configuration files
    agents_config_path = "config/agents.yaml"
    tasks_config_path = "config/tasks.yaml"

    # These attributes are populated dynamically by CrewAI decorators
    # Using Any to avoid type variance issues with crewai's internal types
    agents: Any
    tasks: Any

    def __init__(self):
        """
        Initialize the SpaceHulkGame crew by loading YAML configuration files
        and setting up shared memory.
        """
        logger.info("Initializing SpaceHulkGame crew")

        # Initialize Mem0 memory client for context retention across agents
        logger.info("Initializing Mem0 memory client")

        # Setup memory configuration for the crew
        # Note: Memory client creation commented out until memory features are enabled
        self.memory_config = {
            "provider": "mem0",
            "config": {
                "user_id": "space_hulk_user"  # User identifier for mem0
            },
        }
        # Will be used in the crew configuration
        self.shared_memory = None

        # Define the LLM configuration
        # Check for OpenRouter API key first, then fall back to Ollama
        logger.info("Initializing LLM configuration")

        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        openai_model = os.environ.get("OPENAI_MODEL_NAME", "ollama/qwen2.5")

        if openrouter_key and "openrouter" in openai_model:
            # Use OpenRouter
            logger.info(f"Using OpenRouter with model: {openai_model}")
            self.llm = LLM(model=openai_model, api_key=openrouter_key)
        else:
            # Use Ollama (default)
            logger.info("Using Ollama with model: ollama/qwen2.5")
            self.llm = LLM(model="ollama/qwen2.5", base_url="http://localhost:11434")

        # Determine the base directory for relative paths
        base_dir = Path(__file__).resolve().parent

        # Load agents configuration
        agents_path = base_dir / self.agents_config_path
        logger.info(f"Loading agents config from: {agents_path}")
        try:
            with Path(agents_path).open() as file:
                self.agents_config = yaml.safe_load(file)
            logger.info(f"Loaded agents: {list(self.agents_config.keys())}")
        except Exception as e:
            logger.error(f"Error loading agents config: {e!s}")
            raise

        # Load tasks configuration
        tasks_path = base_dir / self.tasks_config_path
        logger.info(f"Loading tasks config from: {tasks_path}")
        try:
            with Path(tasks_path).open() as file:
                self.tasks_config = yaml.safe_load(file)
            logger.info(f"Loaded tasks: {list(self.tasks_config.keys())}")
        except Exception as e:
            logger.error(f"Error loading tasks config: {e!s}")
            raise

    @before_kickoff
    def prepare_inputs(self, inputs):
        """
        Hook method that validates inputs before the crew starts.
        Ensures required fields are present and adds additional data.

        Best Practices Applied:
        - Explicit validation with clear error messages
        - Graceful fallback to defaults when appropriate
        - Logging for debugging and monitoring
        - Template loading based on prompt hints (Chunk 3.4)
        """
        try:
            logger.info(f"Preparing inputs: {inputs}")

            # Handle the case where input is provided as 'game' instead of 'prompt'
            if "game" in inputs and "prompt" not in inputs:
                logger.info("Converting 'game' input to 'prompt'")
                inputs["prompt"] = inputs["game"]

            # Validate required inputs
            if "prompt" not in inputs:
                logger.warning("No 'prompt' or 'game' key found in inputs")
                # Use default instead of raising error to allow testing
                inputs[
                    "prompt"
                ] = "A mysterious derelict space hulk drifts in the void, its corridors dark and silent."
                logger.info(f"Using default prompt: {inputs['prompt']}")

            # Load planning template if template hint detected in prompt (Chunk 3.4)
            template_context = self._load_planning_template(inputs.get("prompt", ""))
            if template_context:
                inputs["planning_template"] = template_context
                logger.info(
                    f"Loaded planning template: {template_context.get('template_name', 'unknown')}"
                )

            # Add context for all agents
            inputs["additional_data"] = "Space Hulk game context for all agents."

            # Add metadata for tracking
            inputs["_timestamp"] = str(datetime.datetime.now())
            inputs["_process_mode"] = "sequential"  # Track which mode is being used

            logger.info(f"Prepared inputs successfully: {list(inputs.keys())}")
            return inputs

        except Exception as e:
            # Log error with full context
            logger.error(f"Error in prepare_inputs: {e!s}", exc_info=True)

            # Provide recovery with defaults
            default_inputs = {
                "prompt": "A mysterious derelict space hulk drifts in the void.",
                "additional_data": "Space Hulk game context for all agents.",
                "_timestamp": str(datetime.datetime.now()),
                "_error_recovery": True,
                "_original_error": str(e),
            }
            logger.warning(f"Recovering with default inputs: {default_inputs}")
            return default_inputs

    def _load_planning_template(self, prompt: str) -> dict:
        """
        Load a planning template based on keywords detected in the prompt.

        This method implements Chunk 3.4 functionality by:
        1. Detecting template hints in the user's prompt
        2. Loading the corresponding YAML template file
        3. Returning template content as context for agents

        Template Detection Keywords:
        - "horror", "scary", "terrifying", etc. → space_horror.yaml
        - "mystery", "investigation", "investigate", "detective", "clue", etc. → mystery_investigation.yaml
        - "survival", "escape", "desperate", "resource", etc. → survival_escape.yaml
        - "combat", "battle", "tactical", "squad", etc. → combat_focused.yaml

        Template Priority:
        If multiple keywords match, templates are selected in priority order:
        space_horror > mystery_investigation > survival_escape > combat_focused

        Args:
            prompt: User's input prompt text

        Returns:
            Dictionary containing template content, or empty dict if no template found
        """
        try:
            # Convert prompt to lowercase for case-insensitive matching
            prompt_lower = prompt.lower()

            # Define template detection keywords
            template_keywords = {
                "space_horror": [
                    "horror",
                    "scary",
                    "terrifying",
                    "dread",
                    "fear",
                    "nightmare",
                    "corruption",
                ],
                "mystery_investigation": [
                    "mystery",
                    "investigation",
                    "investigate",
                    "detective",
                    "clue",
                    "solve",
                    "evidence",
                    "discover",
                ],
                "survival_escape": [
                    "survival",
                    "escape",
                    "desperate",
                    "resource",
                    "trapped",
                    "flee",
                    "running",
                ],
                "combat_focused": [
                    "combat",
                    "battle",
                    "tactical",
                    "squad",
                    "fight",
                    "warrior",
                    "assault",
                ],
            }

            # Check for template keywords in prompt
            detected_template = None
            for template_name, keywords in template_keywords.items():
                if any(keyword in prompt_lower for keyword in keywords):
                    detected_template = template_name
                    logger.info(f"Detected template hint: {template_name} (matched keywords)")
                    break

            # If no template detected, return empty dict
            if not detected_template:
                logger.debug("No planning template hint detected in prompt")
                return {}

            # Construct template file path
            # Templates are in planning_templates/ at project root
            # Use pathlib for cleaner, more maintainable path manipulation
            project_root = Path(__file__).parent.parent.parent
            template_path = project_root / "planning_templates" / f"{detected_template}.yaml"

            # Check if template file exists
            if not template_path.exists():
                logger.warning(f"Template file not found: {template_path}")
                return {}

            # Load template YAML file
            with Path(template_path).open(encoding="utf-8") as f:
                template_content = yaml.safe_load(f)

            # Validate that loaded content is a dictionary
            if not isinstance(template_content, dict):
                logger.warning(f"Template file has invalid structure: {template_path}")
                return {}

            # Validate required fields in template
            required_fields = ["template_name", "template_version", "description"]
            if not all(field in template_content for field in required_fields):
                logger.warning(f"Template missing required fields: {template_path}")
                return {}

            logger.info(f"Successfully loaded planning template: {detected_template}")
            logger.debug(f"Template path: {template_path}")

            return template_content

        except Exception as e:
            # Don't fail the entire process if template loading fails
            logger.warning(f"Error loading planning template: {e!s}", exc_info=True)
            return {}

    def handle_task_failure(self, task, exception):
        """
        Handle task execution failures with appropriate recovery mechanisms.
        Provides task-specific fallback content to allow the process to continue.
        """
        error_message = f"Error executing task '{task.name}': {exception!s}"
        print(error_message)

        # Task-specific recovery mechanisms
        if task.name == "Generate Overarching Plot":
            # Return a basic default plot outline
            return {
                "plot_outline": {
                    "title": "Default Space Hulk Adventure",
                    "setting": "Derelict space vessel",
                    "main_branches": [
                        {"path": "Exploration", "description": "Explore the vessel cautiously"},
                        {"path": "Combat", "description": "Fight through hostile entities"},
                    ],
                    "endings": [
                        {"name": "Escape", "description": "Successfully escape the vessel"},
                        {"name": "Trapped", "description": "Become trapped in the vessel"},
                    ],
                }
            }
        elif task.name == "Create Narrative Map":
            # Return a basic narrative map
            return {
                "narrative_tree": {
                    "start_scene": "entrance",
                    "scenes": {
                        "entrance": {
                            "description": "The entrance to the derelict vessel",
                            "connections": ["corridor", "control_room"],
                            "items": [],
                        },
                        "corridor": {
                            "description": "A long, dark corridor",
                            "connections": ["entrance", "engine_room"],
                            "items": ["flashlight"],
                        },
                        "control_room": {
                            "description": "The ship's control room",
                            "connections": ["entrance"],
                            "items": ["keycard"],
                        },
                        "engine_room": {
                            "description": "The ship's engine room",
                            "connections": ["corridor"],
                            "items": ["tool_kit"],
                            "requires": "keycard",
                        },
                    },
                }
            }
        elif task.name == "Design Artifacts, Puzzles, Monsters, and NPCs":
            # Return basic puzzle design
            return {
                "puzzle_design": {
                    "puzzles": [
                        {
                            "name": "Engine Repair",
                            "description": "Repair the engine to power up the ship",
                            "requires": ["tool_kit"],
                            "solution": "Use the tool kit on the engine",
                        }
                    ],
                    "artifacts": [
                        {
                            "name": "flashlight",
                            "description": "A basic flashlight to illuminate dark areas",
                        },
                        {"name": "keycard", "description": "Grants access to restricted areas"},
                        {"name": "tool_kit", "description": "Tools for repairing ship systems"},
                    ],
                    "monsters": [
                        {
                            "name": "Shadow Lurker",
                            "description": "A creature that lurks in the darkness",
                            "location": "corridor",
                        }
                    ],
                }
            }
        elif task.name == "Write Scene Descriptions and Dialogue":
            # Return basic scene descriptions
            return {
                "scene_texts": {
                    "entrance": {
                        "description": "The massive entrance hatch creaks open, revealing a cavernous docking bay. The air is stale and cold, carrying the metallic scent of ancient machinery. Emergency lights flicker weakly, casting long shadows across abandoned cargo containers.",
                        "examination": "The docking bay shows signs of a hasty evacuation. Cargo containers lie scattered, their contents spilled across the floor. Most of the escape pods are missing from their berths.",
                    },
                    "corridor": {
                        "description": "A long, narrow corridor stretches before you, its metal walls scarred and dented. The overhead lights flicker erratically, plunging sections into momentary darkness. Something has clearly been dragged along the floor, leaving dark streaks.",
                        "examination": "The damage to the walls appears to be from both weapons fire and something with tremendous strength. There are claw marks gouged into the metal in several places.",
                    },
                }
            }
        elif task.name == "Create Game Mechanics PRD":
            # Return basic PRD document
            return {
                "prd_document": {
                    "game_title": "Space Hulk: Derelict Vessel",
                    "game_systems": {
                        "exploration": {
                            "movement": "Players navigate using cardinal directions (north, south, east, west) or specific exits.",
                            "perception": "A 'look' or 'examine' command reveals additional details about the environment.",
                        },
                        "inventory": {
                            "collection": "Items can be picked up with 'take [item]'",
                            "management": "Players can check inventory with 'inventory' command",
                            "capacity": "Limited to 10 items",
                        },
                        "combat": {
                            "initiative": "Player acts first, then enemies",
                            "actions": ["attack", "defend", "use item", "flee"],
                            "damage_types": ["physical", "energy"],
                        },
                    },
                }
            }

        # Default fallback
        return {"error": error_message, "recovered": False}

    def clean_yaml_output_files(self):  # noqa: PLR0915
        """
        Post-process YAML output files to remove markdown code fences and fix common YAML issues.

        The LLM sometimes:
        1. Wraps YAML content in markdown code blocks (```yml ... ```)
        2. Uses em dashes (-) instead of hyphens (--)
        3. Creates improper line continuations in multiline strings
        4. Generates numbered lists that break YAML syntax

        This method cleans all these issues.
        """
        output_files = [
            "game-config/plot_outline.yaml",
            "game-config/narrative_map.yaml",
            "game-config/puzzle_design.yaml",
            "game-config/scene_texts.yaml",
            "game-config/prd_document.yaml",
        ]

        import re

        cleaned_count = 0
        for filepath in output_files:
            try:
                if not Path(filepath).exists():
                    logger.warning(f"Output file not found: {filepath}")
                    continue

                with Path(filepath).open(encoding="utf-8") as f:
                    content = f.read()

                original_content = content
                needs_cleaning = False

                # 1. Remove markdown code fence markers
                if content.startswith("```") or "```yml" in content or "```yaml" in content:
                    logger.info(f"Removing code fences from {filepath}")
                    content = (
                        content.replace("```yml\n", "")
                        .replace("```yaml\n", "")
                        .replace("```\n", "")
                    )
                    content = content.replace("\n```", "").replace("```", "")
                    needs_cleaning = True

                # 2. Replace em dashes with double hyphens (for YAML compatibility)
                if "-" in content or "-" in content:
                    logger.info(f"Replacing em dashes in {filepath}")
                    content = content.replace("-", "--").replace("-", "--")
                    needs_cleaning = True

                # 2b. Fix nested quotes in double-quoted strings
                # Pattern: description: "text with "nested" quotes"
                # Replace inner double quotes with single quotes
                def fix_nested_quotes(match, fp=filepath):
                    """Replace nested double quotes with single quotes inside YAML strings."""
                    full_match = match.group(0)
                    key = match.group(1)  # e.g., "description"
                    value = match.group(2)  # The quoted string content

                    # Check if there are nested double quotes
                    if '"' in value:
                        logger.info(f"Fixing nested quotes in {fp}")
                        # Replace internal double quotes with single quotes
                        fixed_value = value.replace('"', "'")
                        return f'{key}: "{fixed_value}"'

                    return full_match

                # Match YAML key-value pairs with quoted strings
                content = re.sub(
                    r'(\w+):\s+"([^"]*(?:"[^"]*)*)"',
                    fix_nested_quotes,
                    content,
                    flags=re.MULTILINE,
                )

                # 3. Fix improper line continuations in YAML strings
                # Pattern: lines within a quoted string that have wrong indentation
                # Find lines that continue a string but have incorrect indentation
                # (e.g., line starting with more spaces than the parent)
                lines = content.split("\n")
                fixed_lines = []
                i = 0
                while i < len(lines):
                    line = lines[i]
                    # Check if this is a description line that's broken
                    if (
                        i + 1 < len(lines)
                        and 'description: "' in line
                        and not line.rstrip().endswith('"')
                    ):
                        # This line starts a description but doesn't end it
                        # Check if next line is a continuation with wrong indentation
                        next_line = lines[i + 1]
                        current_indent = len(line) - len(line.lstrip())
                        next_indent = len(next_line) - len(next_line.lstrip())

                        # If next line has more indentation and isn't a YAML key
                        if next_indent > current_indent and ":" not in next_line.lstrip()[:20]:
                            logger.info(f"Fixing line continuation in {filepath} at line {i + 1}")
                            # Merge the lines
                            fixed_line = line.rstrip() + " " + next_line.lstrip()
                            fixed_lines.append(fixed_line)
                            i += 2  # Skip the next line since we merged it
                            needs_cleaning = True
                            continue

                    fixed_lines.append(line)
                    i += 1

                content = "\n".join(fixed_lines)

                # 4. Fix numbered lists inside quoted strings
                # Pattern: description: "text:\n        1. item\n        2. item"
                # Should be: description: "text: (1) item (2) item"
                def fix_numbered_list(match, fp=filepath):
                    text = match.group(0)
                    # If there are numbered items on separate lines, inline them
                    if re.search(r"\n\s+\d+\.", text):
                        logger.info(f"Fixing numbered list in {fp}")
                        # Convert multiline numbered list to inline
                        fixed = re.sub(r"\n\s+(\d+)\.\s+", r" (\1) ", text)
                        return fixed
                    return text

                content = re.sub(
                    r'description: "[^"]*"',
                    fix_numbered_list,
                    content,
                    flags=re.MULTILINE | re.DOTALL,
                )

                # Write cleaned content back if any changes were made
                if needs_cleaning or content != original_content:
                    with Path(filepath).open("w", encoding="utf-8") as f:
                        f.write(content)

                    cleaned_count += 1
                    logger.info(f"✅ Cleaned {filepath}")
                else:
                    logger.debug(f"No issues found in {filepath}")

            except Exception as e:
                logger.error(f"Error cleaning {filepath}: {e!s}")

        if cleaned_count > 0:
            logger.info(f"Cleaned {cleaned_count} YAML file(s)")

        return cleaned_count

    @after_kickoff
    def process_output(self, output):
        """
        Hook method that modifies the final output after the crew finishes all tasks.
        Adds metadata and formats the output for better usability.

        Best Practices Applied:
        - Comprehensive metadata for debugging and tracking
        - Graceful error handling to preserve output
        - Clear status indicators for quality assessment
        - Post-processing to clean YAML output files
        """
        try:
            logger.info("Processing crew output...")

            # Clean YAML output files first
            try:
                cleaned_files = self.clean_yaml_output_files()
                logger.info(f"Post-processed {cleaned_files} YAML files")
            except Exception as e:
                logger.error(f"Error cleaning YAML files: {e!s}")
                # Continue processing even if cleaning fails

            # Get crew configuration safely
            try:
                crew_obj = self.crew()
                total_tasks = len(crew_obj.tasks)
                total_agents = len(crew_obj.agents)
            except Exception:
                # Fallback if crew() isn't available
                total_tasks = 0
                total_agents = 0

            # Add comprehensive metadata
            output.metadata = {
                "processed_at": str(datetime.datetime.now()),
                "validation_applied": True,
                "error_handling_applied": True,
                "crew_mode": "sequential",  # Track execution mode
                "total_tasks": total_tasks,
                "total_agents": total_agents,
            }

            # Add completion summary
            completion_summary = "\n\n=== Crew Execution Complete ===\n"
            completion_summary += f"Timestamp: {output.metadata['processed_at']}\n"
            completion_summary += f"Mode: {output.metadata['crew_mode']}\n"
            if total_tasks > 0:
                completion_summary += f"Tasks Completed: {output.metadata['total_tasks']}\n"
                completion_summary += f"Agents Used: {output.metadata['total_agents']}\n"

            # Check for errors during processing
            if hasattr(output, "errors") and output.errors:
                completion_summary += "\n⚠️  WARNING: Some errors occurred during processing.\n"
                completion_summary += (
                    "Recovery mechanisms were applied. Please review the content.\n"
                )
                output.metadata["had_errors"] = True
            else:
                completion_summary += "\n✅ All tasks completed successfully.\n"
                output.metadata["had_errors"] = False

            output.raw += completion_summary

            logger.info("Output processing complete")
            return output

        except Exception as e:
            # Handle any errors in post-processing without losing output
            logger.error(f"Error in post-processing: {e!s}", exc_info=True)

            # Try to add minimal metadata
            try:
                if not hasattr(output, "metadata"):
                    output.metadata = {}
                output.metadata["post_processing_error"] = str(e)
                output.metadata["processed_at"] = str(datetime.datetime.now())
            except Exception:  # nosec B110
                # Last resort: catch any exception to preserve crew output integrity
                pass

            # Return original output to preserve crew results
            logger.warning("Returning output with minimal post-processing due to error")
            return output

    # ---------------------------------
    # Agents
    # ---------------------------------

    @agent
    def NarrativeDirectorAgent(self) -> Agent:
        """
        Returns the NarrativeDirectorAgent definition from agents.yaml.

        This agent ensures narrative cohesion across all game elements and
        coordinates the narrative-driven development process.

        Note: The method name must match the agent name in the YAML file for CrewAI to properly
        map between tasks and agents.
        """
        logger.info(
            f"Creating NarrativeDirectorAgent with config: {self.agents_config.get('NarrativeDirectorAgent')}"
        )
        return Agent(  # type: ignore[call-arg]
            config=self.agents_config["NarrativeDirectorAgent"],
            llm=self.llm,  # Use the Ollama LLM configuration
            verbose=True,
        )

    @agent
    def PlotMasterAgent(self) -> Agent:
        """
        Returns the PlotMasterAgent definition from agents.yaml.

        Note: The method name must match the agent name in the YAML file for CrewAI to properly
        map between tasks and agents.
        """
        logger.info(
            f"Creating PlotMasterAgent with config: {self.agents_config.get('PlotMasterAgent')}"
        )
        return Agent(  # type: ignore[call-arg]
            config=self.agents_config["PlotMasterAgent"],
            llm=self.llm,  # Use the Ollama LLM configuration
            verbose=True,
        )

    @agent
    def NarrativeArchitectAgent(self) -> Agent:
        """
        Returns the NarrativeArchitectAgent definition from agents.yaml.

        Note: The method name must match the agent name in the YAML file for CrewAI to properly
        map between tasks and agents.
        """
        logger.info(
            f"Creating NarrativeArchitectAgent with config: {self.agents_config.get('NarrativeArchitectAgent')}"
        )
        return Agent(  # type: ignore[call-arg]
            config=self.agents_config["NarrativeArchitectAgent"],
            llm=self.llm,  # Use the Ollama LLM configuration
            verbose=True,
        )

    @agent
    def PuzzleSmithAgent(self) -> Agent:
        """
        Returns the PuzzleSmithAgent definition from agents.yaml.

        Note: The method name must match the agent name in the YAML file for CrewAI to properly
        map between tasks and agents.
        """
        logger.info(
            f"Creating PuzzleSmithAgent with config: {self.agents_config.get('PuzzleSmithAgent')}"
        )
        return Agent(  # type: ignore[call-arg]
            config=self.agents_config["PuzzleSmithAgent"],
            llm=self.llm,  # Use the Ollama LLM configuration
            verbose=True,
        )

    @agent
    def CreativeScribeAgent(self) -> Agent:
        """
        Returns the CreativeScribeAgent definition from agents.yaml.

        Note: The method name must match the agent name in the YAML file for CrewAI to properly
        map between tasks and agents.
        """
        logger.info(
            f"Creating CreativeScribeAgent with config: {self.agents_config.get('CreativeScribeAgent')}"
        )
        return Agent(  # type: ignore[call-arg]
            config=self.agents_config["CreativeScribeAgent"],
            llm=self.llm,  # Use the Ollama LLM configuration
            verbose=True,
        )

    @agent
    def MechanicsGuruAgent(self) -> Agent:
        """
        Returns the MechanicsGuruAgent definition from agents.yaml.

        Note: The method name must match the agent name in the YAML file for CrewAI to properly
        map between tasks and agents.
        """
        logger.info(
            f"Creating MechanicsGuruAgent with config: {self.agents_config.get('MechanicsGuruAgent')}"
        )
        return Agent(  # type: ignore[call-arg]
            config=self.agents_config["MechanicsGuruAgent"],
            llm=self.llm,  # Use the Ollama LLM configuration
            verbose=True,
        )

    # ---------------------------------
    # Tasks
    # ---------------------------------

    @task
    def GenerateOverarchingPlot(self) -> Task:
        """
        The GenerateOverarchingPlot task from tasks.yaml.

        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(
            f"Creating GenerateOverarchingPlot task with config: {self.tasks_config.get('GenerateOverarchingPlot')}"
        )
        return Task(  # type: ignore[call-arg]
            config=self.tasks_config["GenerateOverarchingPlot"]
        )

    @task
    def CreateNarrativeMap(self) -> Task:
        """
        The CreateNarrativeMap task from tasks.yaml.

        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(
            f"Creating CreateNarrativeMap task with config: {self.tasks_config.get('CreateNarrativeMap')}"
        )
        return Task(  # type: ignore[call-arg]
            config=self.tasks_config["CreateNarrativeMap"]
        )

    @task
    def DesignArtifactsAndPuzzles(self) -> Task:
        """
        The DesignArtifactsAndPuzzles task from tasks.yaml.

        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(
            f"Creating DesignArtifactsAndPuzzles task with config: {self.tasks_config.get('DesignArtifactsAndPuzzles')}"
        )
        return Task(  # type: ignore[call-arg]
            config=self.tasks_config["DesignArtifactsAndPuzzles"]
        )

    @task
    def WriteSceneDescriptionsAndDialogue(self) -> Task:
        """
        The WriteSceneDescriptionsAndDialogue task from tasks.yaml.

        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(
            f"Creating WriteSceneDescriptionsAndDialogue task with config: {self.tasks_config.get('WriteSceneDescriptionsAndDialogue')}"
        )
        return Task(  # type: ignore[call-arg]
            config=self.tasks_config["WriteSceneDescriptionsAndDialogue"]
        )

    @task
    def CreateGameMechanicsPRD(self) -> Task:
        """
        The CreateGameMechanicsPRD task from tasks.yaml.

        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(
            f"Creating CreateGameMechanicsPRD task with config: {self.tasks_config.get('CreateGameMechanicsPRD')}"
        )
        return Task(  # type: ignore[call-arg]
            config=self.tasks_config["CreateGameMechanicsPRD"]
        )

    # Restored for Chunk 0.2 testing (all 11 tasks)
    @task
    def EvaluateNarrativeFoundation(self) -> Task:
        """
        The EvaluateNarrativeFoundation task from tasks.yaml.

        This task evaluates the narrative foundation to ensure it provides sufficient depth
        and direction for subsequent development. It's a critical quality gate.

        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(
            f"Creating EvaluateNarrativeFoundation task with config: {self.tasks_config.get('EvaluateNarrativeFoundation')}"
        )
        return Task(  # type: ignore[call-arg]
            config=self.tasks_config["EvaluateNarrativeFoundation"]
        )

    # Restored for Chunk 0.2 testing (all 11 tasks)
    @task
    def EvaluateNarrativeStructure(self) -> Task:
        """
        The EvaluateNarrativeStructure task from tasks.yaml.

        This task evaluates the narrative structure to ensure it properly develops
        the approved foundation into an implementable blueprint.

        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(
            f"Creating EvaluateNarrativeStructure task with config: {self.tasks_config.get('EvaluateNarrativeStructure')}"
        )
        return Task(  # type: ignore[call-arg]
            config=self.tasks_config["EvaluateNarrativeStructure"]
        )

    # Restored for Chunk 0.2 testing (all 11 tasks)
    @task
    def NarrativeIntegrationCheckPuzzles(self) -> Task:
        """
        The NarrativeIntegrationCheckPuzzles task from tasks.yaml.

        This task evaluates how well the puzzles, artifacts, monsters, and NPCs integrate
        with the established narrative.

        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(
            f"Creating NarrativeIntegrationCheckPuzzles task with config: {self.tasks_config.get('NarrativeIntegrationCheckPuzzles')}"
        )
        return Task(  # type: ignore[call-arg]
            config=self.tasks_config["NarrativeIntegrationCheckPuzzles"]
        )

    # Restored for Chunk 0.2 testing (all 11 tasks)
    @task
    def NarrativeIntegrationCheckScenes(self) -> Task:
        """
        The NarrativeIntegrationCheckScenes task from tasks.yaml.

        This task evaluates how well the scene descriptions and dialogue reflect and
        advance the established narrative.

        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(
            f"Creating NarrativeIntegrationCheckScenes task with config: {self.tasks_config.get('NarrativeIntegrationCheckScenes')}"
        )
        return Task(  # type: ignore[call-arg]
            config=self.tasks_config["NarrativeIntegrationCheckScenes"]
        )

    # Restored for Chunk 0.2 testing (all 11 tasks)
    @task
    def NarrativeIntegrationCheckMechanics(self) -> Task:
        """
        The NarrativeIntegrationCheckMechanics task from tasks.yaml.

        This task evaluates how well the game mechanics support and enhance
        the established narrative.

        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(
            f"Creating NarrativeIntegrationCheckMechanics task with config: {self.tasks_config.get('NarrativeIntegrationCheckMechanics')}"
        )
        return Task(  # type: ignore[call-arg]
            config=self.tasks_config["NarrativeIntegrationCheckMechanics"]
        )

    # Restored for Chunk 0.2 testing (all 11 tasks)
    @task
    def FinalNarrativeIntegration(self) -> Task:
        """
        The FinalNarrativeIntegration task from tasks.yaml.

        This task performs a comprehensive review of all game elements to ensure they
        form a cohesive, narrative-driven whole.

        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(
            f"Creating FinalNarrativeIntegration task with config: {self.tasks_config.get('FinalNarrativeIntegration')}"
        )
        return Task(  # type: ignore[call-arg]
            config=self.tasks_config["FinalNarrativeIntegration"]
        )

    # ---------------------------------
    # Crew Definition
    # ---------------------------------

    def create_hierarchical_crew_simplified(self) -> Crew:
        """
        Create hierarchical crew with simplified task descriptions.

        This version uses much shorter task descriptions to prevent the manager's
        delegation prompts from exceeding the LLM's context window.

        Key differences from create_hierarchical_crew():
        1. Task descriptions are 90% shorter
        2. Removes detailed YAML formatting instructions
        3. Keeps only essential task information
        4. Manager can better handle delegation with less context

        Returns:
            Crew configured for hierarchical process with simplified tasks
        """
        logger.info("Creating hierarchical crew with simplified tasks")

        # Import simplified task configs
        from space_hulk_game.config.hierarchical_tasks import HIERARCHICAL_TASKS

        # Create optimized manager
        manager_llm = LLM(
            model=os.environ.get("OPENAI_MODEL_NAME", "ollama/qwen2.5"),
            base_url="http://localhost:11434"
            if "ollama" in os.environ.get("OPENAI_MODEL_NAME", "ollama")
            else None,
            api_key=os.environ.get("OPENROUTER_API_KEY")
            if os.environ.get("OPENROUTER_API_KEY")
            else None,
            temperature=0.3,
            max_tokens=4000,
        )

        manager = Agent(
            role="Narrative Director",
            goal="Coordinate narrative development efficiently",
            backstory="An experienced game narrative director who efficiently delegates tasks.",
            llm=manager_llm,
            allow_delegation=True,
            verbose=True,
            max_iter=10,
        )

        # Create worker agents
        plot_master = self.PlotMasterAgent()
        narrative_architect = self.NarrativeArchitectAgent()
        puzzle_smith = self.PuzzleSmithAgent()

        worker_agents = [plot_master, narrative_architect, puzzle_smith]

        # Create simplified tasks
        simplified_tasks = []
        for task_key in [
            "GenerateOverarchingPlot",
            "CreateNarrativeMap",
            "DesignArtifactsAndPuzzles",
        ]:
            task_config = HIERARCHICAL_TASKS[task_key]
            agent_method = getattr(self, task_config["agent"])
            simplified_tasks.append(
                Task(
                    description=task_config["description"],
                    expected_output=task_config["expected_output"],
                    agent=agent_method(),
                    output_file=task_config.get("output_file"),
                )
            )

        logger.info(f"Manager: {manager.role}")
        logger.info(f"Workers: {[agent.role for agent in worker_agents]}")
        logger.info(f"Tasks: {len(simplified_tasks)} (simplified descriptions)")

        return Crew(
            agents=cast("list", worker_agents),
            tasks=simplified_tasks,
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True,
        )

    def create_hierarchical_crew(self, max_iter=10, use_simplified_manager=True) -> Crew:
        """
        Alternative crew configuration using hierarchical process with optimizations.

        This method creates a hierarchical crew with configurations optimized to prevent
        the LLM context overflow and excessive delegation that causes failures.

        Args:
            max_iter: Maximum iterations for manager agent (default: 10, reduced from 25)
            use_simplified_manager: Use a simplified manager configuration (default: True)

        Optimizations Applied:
        1. Reduced max_iter to prevent excessive delegation loops
        2. Simplified manager LLM with lower temperature for consistent decisions
        3. Explicit delegation limits to prevent context overflow

        Known Issues (per REVISED_RESTART_PLAN.md):
        - Complex YAML task descriptions can overwhelm the manager LLM
        - Long task descriptions cause delegation prompts to exceed context window
        - Solution: Use simplified manager configuration with iteration limits
        """
        logger.info("Creating optimized hierarchical crew configuration")

        # Create optimized manager LLM configuration
        if use_simplified_manager:
            logger.info("Using simplified manager configuration")
            manager_llm = LLM(
                model=os.environ.get("OPENAI_MODEL_NAME", "ollama/qwen2.5"),
                base_url="http://localhost:11434"
                if "ollama" in os.environ.get("OPENAI_MODEL_NAME", "ollama")
                else None,
                api_key=os.environ.get("OPENROUTER_API_KEY")
                if os.environ.get("OPENROUTER_API_KEY")
                else None,
                temperature=0.3,  # Lower temperature for more consistent manager decisions
                max_tokens=4000,  # Ensure enough tokens for delegation decisions
            )

            # Create manager with simplified backstory to reduce prompt size
            manager = Agent(
                role=self.agents_config["NarrativeDirectorAgent"]["role"],
                goal=self.agents_config["NarrativeDirectorAgent"]["goal"],
                backstory="An experienced narrative director who efficiently coordinates specialists.",
                llm=manager_llm,
                allow_delegation=True,
                verbose=True,
                max_iter=max_iter,  # Limit iterations to prevent excessive delegation
            )
        else:
            # Use standard manager configuration
            manager = self.NarrativeDirectorAgent()
            manager.max_iter = max_iter

        # Get worker agents - all agents except the manager
        worker_agents = [agent for agent in self.agents if agent.role != manager.role]

        logger.info(f"Manager: {manager.role}")
        logger.info(f"Worker agents: {[agent.role for agent in worker_agents]}")
        logger.info(f"Total tasks: {len(self.tasks)}")
        logger.info(f"Max iterations: {max_iter}")

        return Crew(
            agents=worker_agents,  # Worker agents only (manager not in list)
            tasks=self.tasks,  # All tasks
            process=Process.hierarchical,  # Hierarchical with manager delegation
            manager_agent=manager,  # Optimized manager for coordination
            verbose=True,  # Enable detailed logging
        )

    @crew
    def crew(self) -> Crew:
        """
        Returns an instance of the Crew with a sequential process flow.

        Per the REVISED_RESTART_PLAN.md Phase 0 debugging strategy:
        - Start with sequential process (simplest configuration)
        - Test basic functionality before adding hierarchical complexity
        - Avoid memory/planning features until basic generation works

        Once sequential mode is proven to work, we can:
        1. Re-enable hierarchical process with proper manager delegation
        2. Add memory capabilities for context retention
        3. Add planning for strategic task execution
        """
        logger.info("Initializing crew with sequential process")
        logger.info(f"Total agents available: {len(self.agents)}")
        logger.info(f"Total tasks to execute: {len(self.tasks)}")

        # Sequential process - simplest configuration per restart plan
        # All agents work in order without manager coordination
        return Crew(
            agents=self.agents,  # All agents work as peers
            tasks=self.tasks,  # Tasks execute in definition order
            process=Process.sequential,  # Sequential process per Phase 0 plan
            verbose=True,  # Enable detailed logging for debugging
            # Memory and planning disabled per Phase 0 plan
            # Will be re-enabled after basic functionality is proven
        )
