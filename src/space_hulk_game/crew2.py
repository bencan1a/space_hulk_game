# crew.py
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff


@CrewBase
class TextAdventureDesignCrew:
    """
    A specialized crew that designs text-based adventure games, from overarching
    plot creation to puzzle design, world-building, and final PRD documentation.
    """

    # Paths to the YAML configuration files
    agents_config = "agents2.yaml"
    tasks_config = "tasks2.yaml"

    @before_kickoff
    def prepare_inputs(self, inputs):
        """
        Hook method that modifies inputs before the crew starts.
        For example, you might inject extra data or validate the prompt.
        """
        inputs["additional_data"] = "Some extra information for the first task."
        return inputs

    @after_kickoff
    def process_output(self, output):
        """
        Hook method that modifies the final output after the crew finishes all tasks.
        """
        # If your tasks produce text-based outputs, you might do formatting here
        output.raw += "\n\n[Final post-processing complete.]"
        return output

    # ---------------------------------
    # Agents
    # ---------------------------------

    @agent
    def plot_master_agent(self) -> Agent:
        """
        Returns the PlotMasterAgent definition from agents.yaml.
        """
        return Agent(
            config=self.agents_config["PlotMasterAgent"],
            verbose=True
        )

    @agent
    def narrative_architect_agent(self) -> Agent:
        """
        Returns the NarrativeArchitectAgent definition from agents.yaml.
        """
        return Agent(
            config=self.agents_config["NarrativeArchitectAgent"],
            verbose=True
        )

    @agent
    def puzzle_smith_agent(self) -> Agent:
        """
        Returns the PuzzleSmithAgent definition from agents.yaml.
        """
        return Agent(
            config=self.agents_config["PuzzleSmithAgent"],
            verbose=True
        )

    @agent
    def creative_scribe_agent(self) -> Agent:
        """
        Returns the CreativeScribeAgent definition from agents.yaml.
        """
        return Agent(
            config=self.agents_config["CreativeScribeAgent"],
            verbose=True
        )

    @agent
    def mechanics_guru_agent(self) -> Agent:
        """
        Returns the MechanicsGuruAgent definition from agents.yaml.
        """
        return Agent(
            config=self.agents_config["MechanicsGuruAgent"],
            verbose=True
        )

    # ---------------------------------
    # Tasks
    # ---------------------------------

    @task
    def generate_overarching_plot(self) -> Task:
        """
        The GenerateOverarchingPlot task from tasks.yaml.
        """
        return Task(
            config=self.tasks_config["GenerateOverarchingPlot"]
        )

    @task
    def create_narrative_map(self) -> Task:
        """
        The CreateNarrativeMap task from tasks.yaml.
        """
        return Task(
            config=self.tasks_config["CreateNarrativeMap"]
        )

    @task
    def design_artifacts_and_puzzles(self) -> Task:
        """
        The DesignArtifactsAndPuzzles task from tasks.yaml.
        """
        return Task(
            config=self.tasks_config["DesignArtifactsAndPuzzles"]
        )

    @task
    def write_scene_descriptions_and_dialogue(self) -> Task:
        """
        The WriteSceneDescriptionsAndDialogue task from tasks.yaml.
        """
        return Task(
            config=self.tasks_config["WriteSceneDescriptionsAndDialogue"]
        )

    @task
    def create_game_mechanics_prd(self) -> Task:
        """
        The CreateGameMechanicsPRD task from tasks.yaml.
        """
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


