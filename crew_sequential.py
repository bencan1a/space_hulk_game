# crew_sequential.py - Simplified crew for testing
"""
Simplified version of the Space Hulk Game crew using sequential process.

This is a test configuration to validate that the basic agent coordination
works without the complexity of hierarchical management.

To use:
1. Rename crew.py to crew_hierarchical.py
2. Rename this file to crew.py
3. Run the test script
"""
import datetime
import os
import yaml
import logging

from crewai import Agent, Crew, Task, Process, LLM
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@CrewBase
class SpaceHulkGame:
    """
    SIMPLIFIED VERSION: Sequential process for testing
    
    A specialized crew that designs text-based adventure games, from overarching
    plot creation to puzzle design, world-building, and final PRD documentation.
    
    This version uses sequential process instead of hierarchical to prove
    the basic agent coordination works.
    """

    # Paths to the YAML configuration files
    agents_config_path = "config/agents.yaml"
    tasks_config_path = "config/tasks.yaml"
    
    def __init__(self):
        """
        Initialize the SpaceHulkGame crew by loading YAML configuration files.
        """
        logger.info("Initializing SpaceHulkGame crew (SEQUENTIAL MODE)")
        
        # Define the LLM configuration for Ollama
        logger.info("Initializing Ollama LLM configuration")
        self.llm = LLM(
            model="ollama/qwen2.5",
            base_url="http://localhost:11434"
        )
        
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
                
            logger.info(f"Prepared inputs: {inputs}")
            return inputs
        except Exception as e:
            logger.error(f"Error in prepare_inputs: {str(e)}")
            inputs["prompt"] = inputs.get("prompt", "Default space hulk exploration scenario")
            logger.info(f"Using default inputs: {inputs}")
            return inputs
    
    @after_kickoff
    def process_output(self, output):
        """
        Hook method that processes the final output after the crew finishes.
        """
        try:
            logger.info("Processing output...")
            
            # Add metadata about the processing
            if hasattr(output, 'raw'):
                output.raw += "\n\n[Sequential process completed successfully]"
            
            logger.info("Output processing complete")
            return output
        except Exception as e:
            logger.error(f"Error in post-processing: {str(e)}")
            return output

    # ---------------------------------
    # Agents (Only core 5, no NarrativeDirector)
    # ---------------------------------
    
    @agent
    def PlotMasterAgent(self) -> Agent:
        """Plot Master Agent - Creates narrative foundation"""
        logger.info(f"Creating PlotMasterAgent")
        return Agent(
            config=self.agents_config["PlotMasterAgent"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def NarrativeArchitectAgent(self) -> Agent:
        """Narrative Architect Agent - Maps narrative structure"""
        logger.info(f"Creating NarrativeArchitectAgent")
        return Agent(
            config=self.agents_config["NarrativeArchitectAgent"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def PuzzleSmithAgent(self) -> Agent:
        """Puzzle Smith Agent - Designs puzzles and artifacts"""
        logger.info(f"Creating PuzzleSmithAgent")
        return Agent(
            config=self.agents_config["PuzzleSmithAgent"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def CreativeScribeAgent(self) -> Agent:
        """Creative Scribe Agent - Writes scenes and dialogue"""
        logger.info(f"Creating CreativeScribeAgent")
        return Agent(
            config=self.agents_config["CreativeScribeAgent"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def MechanicsGuruAgent(self) -> Agent:
        """Mechanics Guru Agent - Defines game mechanics"""
        logger.info(f"Creating MechanicsGuruAgent")
        return Agent(
            config=self.agents_config["MechanicsGuruAgent"],
            llm=self.llm,
            verbose=True
        )

    # ---------------------------------
    # Tasks (Only core 5, no evaluation tasks)
    # ---------------------------------

    @task
    def GenerateOverarchingPlot(self) -> Task:
        """Generate plot foundation task"""
        logger.info(f"Creating GenerateOverarchingPlot task")
        return Task(
            config=self.tasks_config["GenerateOverarchingPlot"]
        )

    @task
    def CreateNarrativeMap(self) -> Task:
        """Create narrative structure task"""
        logger.info(f"Creating CreateNarrativeMap task")
        # Remove dependencies for sequential - they're implicit
        task_config = self.tasks_config["CreateNarrativeMap"].copy()
        task_config.pop('dependencies', None)
        return Task(config=task_config)

    @task
    def DesignArtifactsAndPuzzles(self) -> Task:
        """Design puzzles and artifacts task"""
        logger.info(f"Creating DesignArtifactsAndPuzzles task")
        task_config = self.tasks_config["DesignArtifactsAndPuzzles"].copy()
        task_config.pop('dependencies', None)
        return Task(config=task_config)

    @task
    def WriteSceneDescriptionsAndDialogue(self) -> Task:
        """Write scene descriptions task"""
        logger.info(f"Creating WriteSceneDescriptionsAndDialogue task")
        task_config = self.tasks_config["WriteSceneDescriptionsAndDialogue"].copy()
        task_config.pop('dependencies', None)
        return Task(config=task_config)

    @task
    def CreateGameMechanicsPRD(self) -> Task:
        """Create game mechanics PRD task"""
        logger.info(f"Creating CreateGameMechanicsPRD task")
        task_config = self.tasks_config["CreateGameMechanicsPRD"].copy()
        task_config.pop('dependencies', None)
        return Task(config=task_config)

    # ---------------------------------
    # Crew Definition - SEQUENTIAL MODE
    # ---------------------------------

    @crew
    def crew(self) -> Crew:
        """
        Returns an instance of the Crew with SEQUENTIAL process flow.
        
        This is a simplified version for testing. Sequential mode means:
        - Tasks execute in order: Plot → Narrative → Puzzles → Scenes → Mechanics
        - No manager agent needed
        - No complex dependencies
        - More predictable execution
        """
        logger.info("Creating crew with SEQUENTIAL process")
        
        return Crew(
            agents=self.agents,      # All 5 core agents
            tasks=self.tasks,        # All 5 core tasks
            process=Process.sequential,  # Simple sequential execution
            verbose=True
        )
