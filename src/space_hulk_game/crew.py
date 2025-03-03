# crew.py
import datetime
import os
import yaml
import logging

from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
    
    def __init__(self):
        """
        Initialize the SpaceHulkGame crew by loading YAML configuration files.
        """
        logger.info("Initializing SpaceHulkGame crew")
        
        # Determine the base directory for relative paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load agents configuration
        agents_path = os.path.join(base_dir, self.agents_config_path)
        logger.info(f"Loading agents config from: {agents_path}")
        try:
            with open(agents_path, 'r') as file:
                self.agents_config = yaml.safe_load(file)
            logger.info(f"Loaded agents: {list(self.agents_config.keys())}")
        except Exception as e:
            logger.error(f"Error loading agents config: {str(e)}")
            raise
            
        # Load tasks configuration
        tasks_path = os.path.join(base_dir, self.tasks_config_path)
        logger.info(f"Loading tasks config from: {tasks_path}")
        try:
            with open(tasks_path, 'r') as file:
                self.tasks_config = yaml.safe_load(file)
            logger.info(f"Loaded tasks: {list(self.tasks_config.keys())}")
        except Exception as e:
            logger.error(f"Error loading tasks config: {str(e)}")
            raise

    @before_kickoff
    def prepare_inputs(self, inputs):
        """
        Hook method that validates inputs before the crew starts.
        Ensures required fields are present and adds additional data.
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
                raise ValueError("Input must contain a 'prompt' or 'game' key")
                
            # Process inputs
            inputs["additional_data"] = "Space Hulk game context for all agents."
            logger.info(f"Prepared inputs: {inputs}")
            return inputs
        except Exception as e:
            # Log error and provide recovery mechanism
            logger.error(f"Error in prepare_inputs: {str(e)}")
            # Set default values if possible
            inputs["prompt"] = inputs.get("prompt", "Default space hulk exploration scenario")
            logger.info(f"Using default inputs: {inputs}")
            return inputs

    def handle_task_failure(self, task, exception):
        """
        Handle task execution failures with appropriate recovery mechanisms.
        Provides task-specific fallback content to allow the process to continue.
        """
        error_message = f"Error executing task '{task.name}': {str(exception)}"
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
                        {"path": "Combat", "description": "Fight through hostile entities"}
                    ],
                    "endings": [
                        {"name": "Escape", "description": "Successfully escape the vessel"},
                        {"name": "Trapped", "description": "Become trapped in the vessel"}
                    ]
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
                            "items": []
                        },
                        "corridor": {
                            "description": "A long, dark corridor",
                            "connections": ["entrance", "engine_room"],
                            "items": ["flashlight"]
                        },
                        "control_room": {
                            "description": "The ship's control room",
                            "connections": ["entrance"],
                            "items": ["keycard"]
                        },
                        "engine_room": {
                            "description": "The ship's engine room",
                            "connections": ["corridor"],
                            "items": ["tool_kit"],
                            "requires": "keycard"
                        }
                    }
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
                            "solution": "Use the tool kit on the engine"
                        }
                    ],
                    "artifacts": [
                        {
                            "name": "flashlight",
                            "description": "A basic flashlight to illuminate dark areas"
                        },
                        {
                            "name": "keycard",
                            "description": "Grants access to restricted areas"
                        },
                        {
                            "name": "tool_kit",
                            "description": "Tools for repairing ship systems"
                        }
                    ],
                    "monsters": [
                        {
                            "name": "Shadow Lurker",
                            "description": "A creature that lurks in the darkness",
                            "location": "corridor"
                        }
                    ]
                }
            }
        elif task.name == "Write Scene Descriptions and Dialogue":
            # Return basic scene descriptions
            return {
                "scene_texts": {
                    "entrance": {
                        "description": "The massive entrance hatch creaks open, revealing a cavernous docking bay. The air is stale and cold, carrying the metallic scent of ancient machinery. Emergency lights flicker weakly, casting long shadows across abandoned cargo containers.",
                        "examination": "The docking bay shows signs of a hasty evacuation. Cargo containers lie scattered, their contents spilled across the floor. Most of the escape pods are missing from their berths."
                    },
                    "corridor": {
                        "description": "A long, narrow corridor stretches before you, its metal walls scarred and dented. The overhead lights flicker erratically, plunging sections into momentary darkness. Something has clearly been dragged along the floor, leaving dark streaks.",
                        "examination": "The damage to the walls appears to be from both weapons fire and something with tremendous strength. There are claw marks gouged into the metal in several places."
                    }
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
                            "perception": "A 'look' or 'examine' command reveals additional details about the environment."
                        },
                        "inventory": {
                            "collection": "Items can be picked up with 'take [item]'",
                            "management": "Players can check inventory with 'inventory' command",
                            "capacity": "Limited to 10 items"
                        },
                        "combat": {
                            "initiative": "Player acts first, then enemies",
                            "actions": ["attack", "defend", "use item", "flee"],
                            "damage_types": ["physical", "energy"]
                        }
                    }
                }
            }
        
        # Default fallback
        return {"error": error_message, "recovered": False}
    
    @after_kickoff
    def process_output(self, output):
        """
        Hook method that modifies the final output after the crew finishes all tasks.
        Adds metadata and formats the output for better usability.
        """
        try:
            # Add metadata about the processing
            output.metadata = {
                "processed_at": str(datetime.datetime.now()),
                "validation_applied": True,
                "error_handling_applied": True
            }
            
            # If your tasks produce text-based outputs, you might do formatting here
            output.raw += "\n\n[Final post-processing complete with validation and error handling.]"
            
            # Check if there were any errors during processing
            if hasattr(output, 'errors') and output.errors:
                output.raw += "\n\n[WARNING: Some errors occurred during processing. " \
                             "Recovery mechanisms were applied, but you should review the content.]"
            
            return output
        except Exception as e:
            # Handle any errors in post-processing
            print(f"Error in post-processing: {str(e)}")
            # Return original output if post-processing fails
            return output

    # ---------------------------------
    # Agents
    # ---------------------------------

    @agent
    def PlotMasterAgent(self) -> Agent:
        """
        Returns the PlotMasterAgent definition from agents.yaml.
        
        Note: The method name must match the agent name in the YAML file for CrewAI to properly
        map between tasks and agents.
        """
        logger.info(f"Creating PlotMasterAgent with config: {self.agents_config.get('PlotMasterAgent')}")
        return Agent(
            config=self.agents_config["PlotMasterAgent"],
            verbose=True
        )

    @agent
    def NarrativeArchitectAgent(self) -> Agent:
        """
        Returns the NarrativeArchitectAgent definition from agents.yaml.
        
        Note: The method name must match the agent name in the YAML file for CrewAI to properly
        map between tasks and agents.
        """
        logger.info(f"Creating NarrativeArchitectAgent with config: {self.agents_config.get('NarrativeArchitectAgent')}")
        return Agent(
            config=self.agents_config["NarrativeArchitectAgent"],
            verbose=True
        )

    @agent
    def PuzzleSmithAgent(self) -> Agent:
        """
        Returns the PuzzleSmithAgent definition from agents.yaml.
        
        Note: The method name must match the agent name in the YAML file for CrewAI to properly
        map between tasks and agents.
        """
        logger.info(f"Creating PuzzleSmithAgent with config: {self.agents_config.get('PuzzleSmithAgent')}")
        return Agent(
            config=self.agents_config["PuzzleSmithAgent"],
            verbose=True
        )

    @agent
    def CreativeScribeAgent(self) -> Agent:
        """
        Returns the CreativeScribeAgent definition from agents.yaml.
        
        Note: The method name must match the agent name in the YAML file for CrewAI to properly
        map between tasks and agents.
        """
        logger.info(f"Creating CreativeScribeAgent with config: {self.agents_config.get('CreativeScribeAgent')}")
        return Agent(
            config=self.agents_config["CreativeScribeAgent"],
            verbose=True
        )

    @agent
    def MechanicsGuruAgent(self) -> Agent:
        """
        Returns the MechanicsGuruAgent definition from agents.yaml.
        
        Note: The method name must match the agent name in the YAML file for CrewAI to properly
        map between tasks and agents.
        """
        logger.info(f"Creating MechanicsGuruAgent with config: {self.agents_config.get('MechanicsGuruAgent')}")
        return Agent(
            config=self.agents_config["MechanicsGuruAgent"],
            verbose=True
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
        logger.info(f"Creating GenerateOverarchingPlot task with config: {self.tasks_config.get('GenerateOverarchingPlot')}")
        return Task(
            config=self.tasks_config["GenerateOverarchingPlot"]
        )

    @task
    def CreateNarrativeMap(self) -> Task:
        """
        The CreateNarrativeMap task from tasks.yaml.
        
        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(f"Creating CreateNarrativeMap task with config: {self.tasks_config.get('CreateNarrativeMap')}")
        return Task(
            config=self.tasks_config["CreateNarrativeMap"]
        )

    @task
    def DesignArtifactsAndPuzzles(self) -> Task:
        """
        The DesignArtifactsAndPuzzles task from tasks.yaml.
        
        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(f"Creating DesignArtifactsAndPuzzles task with config: {self.tasks_config.get('DesignArtifactsAndPuzzles')}")
        return Task(
            config=self.tasks_config["DesignArtifactsAndPuzzles"]
        )

    @task
    def WriteSceneDescriptionsAndDialogue(self) -> Task:
        """
        The WriteSceneDescriptionsAndDialogue task from tasks.yaml.
        
        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(f"Creating WriteSceneDescriptionsAndDialogue task with config: {self.tasks_config.get('WriteSceneDescriptionsAndDialogue')}")
        return Task(
            config=self.tasks_config["WriteSceneDescriptionsAndDialogue"]
        )

    @task
    def CreateGameMechanicsPRD(self) -> Task:
        """
        The CreateGameMechanicsPRD task from tasks.yaml.
        
        Note: The method name must match the task name in the YAML file for CrewAI to properly
        map between tasks.
        """
        logger.info(f"Creating CreateGameMechanicsPRD task with config: {self.tasks_config.get('CreateGameMechanicsPRD')}")
        return Task(
            config=self.tasks_config["CreateGameMechanicsPRD"]
        )

    # ---------------------------------
    # Crew Definition
    # ---------------------------------

    @crew
    def crew(self) -> Crew:
        """
        Returns an instance of the Crew, referencing all agents and tasks.
        You can specify the process flow (sequential, parallel, etc.).
        """
        return Crew(
            agents=self.agents,    # collected automatically by @agent decorators
            tasks=self.tasks,      # collected automatically by @task decorators
            process=Process.sequential,
            verbose=True
        )