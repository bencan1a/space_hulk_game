# Decision Log

This document tracks key decisions made during the Space Hulk Game project, explaining the rationale behind each choice.

## Memory System Implementation (2025-03-02)

**Decision:** Replace `SharedMemory` with mem0 integration for CrewAI memory

**Context:** The crew initialization was failing with an ImportError because `SharedMemory` doesn't exist in the current version of CrewAI. The error message suggested using `ShortTermMemory` instead. Based on user guidance, we implemented mem0 for enhanced memory capabilities.

**Rationale:** After examining the official CrewAI documentation, we found that the current version supports mem0 integration for enhanced user memory. This provides better storage and retrieval capabilities than the built-in memory options.

**Implementation:**
1. Changed the import from `from crewai.memory import SharedMemory` to `from crewai.memory import ShortTermMemory`
2. Added the mem0 import: `from mem0 import MemoryClient`
3. Set the mem0 API key as an environment variable: `os.environ["MEM0_API_KEY"] = "m0-B8baxjzhRRxN8A4t7EoIpHoGAAb5SwhFLqfiY3IK"`
4. Replaced direct memory instantiation with a configuration dictionary:
   ```python
   self.memory_config = {
       "provider": "mem0",
       "config": {
           "user_id": "space_hulk_user"  # User identifier for mem0
       }
   }
   self.shared_memory = None  # Managed by crew configuration
   ```
5. Removed memory parameters from all agent creation methods since memory is now managed at the crew level
6. Updated crew definition to use mem0 configuration:
   ```python
   return Crew(
       agents=self.agents,
       tasks=self.tasks,
       process=Process.hierarchical,
       memory=True,  # Enable memory
       memory_config=self.memory_config,  # Use mem0 configuration 
       planning=True,
       verbose=True
   )
   ```

**Benefits:**
- Ensures compatibility with the current CrewAI version
- Provides enhanced memory capabilities with mem0 integration
- Better long-term memory retention across crew executions
- Reduces code complexity by managing memory at the crew level instead of individual agents

**Alternatives Considered:**
- Using `ShortTermMemory` with no configuration: Would work but lacks advanced features
- Disabling memory completely: Would lose context retention benefits

## Hierarchical Process Configuration (2025-03-02)

**Decision:** Properly configure hierarchical process with NarrativeDirectorAgent as manager

**Context:** After fixing the memory implementation, we encountered errors because the hierarchical process was missing the required manager_agent parameter and we had disabled the process model.

**Rationale:** The implementation plan specifically calls for a hierarchical process with the NarrativeDirectorAgent as the manager. The CrewAI error messages confirmed that either manager_llm or manager_agent is required when using hierarchical process.

**Implementation:**
1. Restored `Process.hierarchical` in the Crew constructor
2. Added `manager_agent=self.NarrativeDirectorAgent()` to the Crew constructor
3. Kept the mem0 memory configuration as previously implemented
4. Excluded the manager agent (NarrativeDirectorAgent) from the regular agents list to avoid validation errors:
   ```python
   # Create the manager agent separately
   manager = self.NarrativeDirectorAgent()
   
   # Get all agents excluding the NarrativeDirectorAgent
   regular_agents = [agent for agent in self.agents if not isinstance(agent, type(manager))]
   ```

**Benefits:**
- Aligns with the implementation plan's intended hierarchical structure
- Properly sets the NarrativeDirectorAgent as the manager for the hierarchical process
- Maintains the narrative-driven development flow as designed
- Resolves the validation errors that were preventing the crew from starting

**Alternatives Considered:**
- Using Process.sequential: Would have simplified dependencies but diverged from the implementation plan
- Using a manager_llm instead of manager_agent: Would require additional configuration and diverge from plan
- Keeping process=None: Would disable the process model completely, contradicting the implementation plan

## Task Dependency Configuration (2025-03-02)

**Decision:** Fix task context dependency conflicts in tasks.yaml

**Context:** After fixing the hierarchical process configuration, we encountered multiple errors about tasks having "context dependency on a future task, which is not allowed". The errors mentioned that CreateNarrativeMap, DesignArtifactsAndPuzzles, WriteSceneDescriptionsAndDialogue, and CreateGameMechanicsPRD all had context dependencies on tasks that were execution dependencies.

**Rationale:** In CrewAI's hierarchical process validation, a task cannot have a context dependency on a task that might be processed later in the workflow. Even though tasks like EvaluateNarrativeFoundation were correctly listed as execution dependencies, having them in the context caused validation errors.

**Implementation:**
1. Removed "EvaluateNarrativeFoundation" from the context of CreateNarrativeMap task
2. Removed "EvaluateNarrativeStructure" from the context of:
   - DesignArtifactsAndPuzzles
   - WriteSceneDescriptionsAndDialogue
   - CreateGameMechanicsPRD
3. Kept these references in the dependencies lists to maintain proper execution order
4. Added comments in the tasks.yaml file explaining the changes

**Benefits:**
- Resolves the validation errors while preserving the correct task execution order
- Maintains the narrative-driven hierarchical workflow as designed
- Keeps the dependencies intact to ensure tasks execute in the proper sequence
- Simplifies context dependencies to only include tasks guaranteed to execute before the current task

**Alternatives Considered:**
- Modifying how tasks are loaded in crew.py: More complex and might interfere with CrewAI's internal task handling
- Changing to Process.sequential: Would diverge from the implementation plan and lose hierarchical benefits
- Disabling the process model entirely: Would lose benefits of structured task execution

## OpenAI API Key Configuration (2025-03-02)

**Decision:** Configure OpenAI API key for CrewAI's LLM usage

**Context:** After fixing all task dependency and configuration issues, the crew initialization succeeded but encountered an API authentication error: "The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable".

**Rationale:** CrewAI uses LLMs (specifically OpenAI's models by default) for agent operations, which requires a valid API key. The error indicates the structural syntax of our CrewAI implementation is now correct, but we need to provide API access credentials.

**Implementation:**
1. Create a .env file in the project root to store API keys
2. Add the OpenAI API key using standard environment variable format: OPENAI_API_KEY=your-api-key-here
3. The CrewAI framework will automatically load this environment variable when executing LLM operations

**Benefits:**
- Provides the necessary authentication for CrewAI's LLM operations
- Follows security best practices by storing API keys in environment variables instead of code
- Enables the proper execution of the hierarchical narrative-driven workflow

**Alternatives Considered:**
- Hardcoding the API key in crew.py: Less secure and not recommended
- Using a different LLM provider: Would require additional configuration changes

## Ollama Integration Configuration (2025-03-02)

**Decision:** Update environment variables to properly configure Ollama integration with CrewAI

**Context:** After attempting to configure Ollama as the LLM provider, the crew was still failing at launch with an error: "The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable". Despite having Ollama configuration in the .env file, CrewAI was still attempting to use OpenAI.

**Rationale:** CrewAI uses LiteLLM under the hood, which expects OpenAI-formatted environment variables even when using alternative models like Ollama. The error occurs because we were using `MODEL` and `API_BASE` variables, but CrewAI/LiteLLM specifically looks for `OPENAI_MODEL_NAME`, `OPENAI_API_BASE`, and `OPENAI_API_KEY` regardless of which model provider you're using.

**Implementation:**
1. Updated the .env file to use OpenAI-formatted variable names:
```
OPENAI_MODEL_NAME=ollama/qwen2.5
OPENAI_API_BASE=http://localhost:11434
OPENAI_API_KEY=dummy-value
PYTHONPATH=${workspaceFolder}/src
```

2. Key changes:
   - Changed `MODEL` to `OPENAI_MODEL_NAME`
   - Changed `API_BASE` to `OPENAI_API_BASE`
   - Added `OPENAI_API_KEY` with a dummy value (required by the OpenAI client even when using Ollama)

**Benefits:**
- Allows the use of local Ollama models instead of requiring an OpenAI API key
- Maintains compatibility with CrewAI's LiteLLM backend
- Enables offline operation without external API dependencies
- Provides flexibility to use different Ollama models by changing the model name

**Alternatives Considered:**
- Setting environment variables directly in the code: Less maintainable than using .env file
- Creating a custom LLM provider class: More complex and likely unnecessary
- Modifying the CrewAI source code: Not sustainable for future updates

## Explicit LLM Configuration in Agent Initialization (2025-03-02)

**Decision:** Implement explicit LLM configuration for each agent rather than relying solely on environment variables

**Context:** Despite properly configuring environment variables, debug logs revealed CrewAI was still attempting to use "gpt-4o-mini" instead of the specified Ollama model, resulting in a mismatch between the configured model and the actual API endpoint called by LiteLLM.

**Rationale:** The LiteLLM debug logs showed that environment variables alone were insufficient to override the default model selection. CrewAI requires explicit LLM configuration at the agent level to ensure the correct model is used consistently across all agents.

**Implementation:**
1. Added import for LLM class: `from crewai import Agent, Crew, Task, Process, LLM`
2. Created an explicit LLM configuration object in the __init__ method:
   ```python
   # Define the LLM configuration for Ollama
   self.llm = LLM(
       model="ollama/qwen2.5",
       base_url="http://localhost:11434"
   )
   ```
3. Added the LLM parameter to all agent creation methods:
   ```python
   return Agent(
       config=self.agents_config["AgentName"],
       llm=self.llm,  # Use the Ollama LLM configuration
       verbose=True
   )
   ```
4. Uncommented memory configuration in the crew definition to ensure proper functioning of shared memory.

**Benefits:**
- Ensures consistent model usage across all agents
- Prevents fallback to default models (like gpt-4o-mini)
- Makes the LLM configuration explicit and centralized
- Provides better control over model selection for all agents
- Resolves the mismatch between configured model and API endpoint

**Alternatives Considered:**
- Environment variables only: Proven insufficient as shown by debug logs
- Agent configuration in YAML: Less maintainable and would require schema changes
- Direct LiteLLM configuration: Would bypass CrewAI's configuration system
## Architectural Analysis and Restart Plan (2025-11-08)

**Decision:** Continue with current architecture and complete the project with focused enhancements

**Context:** After the project went dormant for several months, a comprehensive analysis was conducted to evaluate whether to restart from scratch with a new architecture or continue with the existing implementation. The analysis compared the current hierarchical multi-agent approach against modern best practices in multi-agent orchestration (2025).

**Rationale:** 
1. **Architecture is Sound**: The hierarchical orchestration pattern with a Narrative Director coordinating specialized agents is appropriate for this domain. Narrative cohesion requires central oversight, which the current architecture provides.

2. **Technology Stack is Modern**: CrewAI remains the best framework choice for this use case. Alternatives like LangGraph or AutoGen don't provide significant benefits that would justify migration costs. The Ollama + Python stack is privacy-friendly, cost-effective, and actively maintained.

3. **Implementation Quality is Good**: Phases 1-2 are well-executed with proper error handling, validation, and YAML-driven configuration. The code follows best practices.

4. **Main Issue is Incompleteness, Not Incorrectness**: Only 2 of 5 planned phases are complete. The problem is that development stopped, not that the direction was wrong.

5. **Critical Gap Identified**: The most important missing piece is a game engine to validate that generated content actually works. Without this, there's no way to verify that scenes connect, puzzles are solvable, or games are playable.

**Alternatives Considered:**
1. **Complete Rewrite with LangGraph**: Rejected - Would lose 2 phases of good work for marginal architectural benefits
2. **Switch to Autonomous Agent Swarms**: Rejected - Would compromise narrative cohesion
3. **Pure Sequential Pipeline**: Rejected - Too rigid, no feedback loops
4. **Microservices Architecture**: Rejected - Over-engineering for current scale

**Implementation Plan:**
- **Phase 3**: Planning & Quality System (2-3 weeks)
  - Define quality metrics for all output types
  - Implement quality evaluators with scoring
  - Add retry logic with feedback
  - Create planning templates
  
- **Phase 3.5**: Simple Game Engine (2 weeks) - NEW & CRITICAL
  - Build minimal text adventure engine
  - Create command parser and game state
  - Implement content loader for generated YAML
  - Validate games are actually playable
  
- **Phase 4**: Output Validation & Standardization (2-3 weeks)
  - Define Pydantic models for all outputs
  - Implement schema validators
  - Add auto-correction for common errors
  
- **Phase 5**: Enhanced Memory System (2 weeks)
  - Design memory schema for collaboration
  - Fully utilize mem0 capabilities
  - Enable cross-agent context sharing
  - Implement cross-session learning
  
- **Phase 6**: Production Polish (2 weeks)
  - Add structured logging and metrics
  - Create example games
  - Write comprehensive documentation
  - Performance optimization

**Benefits:**
- Respects the solid work already completed
- Provides clear, actionable path to completion
- Adds critical missing component (game engine)
- Aligns with modern best practices
- Achievable timeline (10-12 weeks part-time)
- Minimizes risk and rework

**Supporting Documents:**
- ARCHITECTURAL_ANALYSIS.md: Detailed evaluation and comparison with alternatives
- PROJECT_RESTART_PLAN.md: Week-by-week implementation plan
- RESTART_SUMMARY.md: Executive summary and key findings

**Expected Outcome:** A production-ready text adventure game generator that can create playable, narratively coherent games from simple prompts within 5 minutes, fully validated and documented.
