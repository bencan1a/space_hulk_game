# CrewAI API Reference

Token-efficient reference for CrewAI framework components: agents, tasks, tools, flows, knowledge, processes, LLMs, memory, and planning.

## Agents

### Definition

Core entities that perform tasks with specific roles, goals, and backstories.

### Parameters

- `role`: String - Agent's role/title
- `goal`: String - Agent's primary objective
- `backstory`: String - Background context
- `llm`: LLM instance or config - Language model
- `tools`: List[Tool] - Available tools
- `verbose`: Bool - Detailed logging
- `allow_delegation`: Bool - Can assign tasks to others
- `max_iter`: Int - Maximum iterations for task attempts
- `step_callback`: Function - Callback after each step

### Syntax

```python
Agent(role="", goal="", backstory="", tools=[], allow_delegation=False)
Agent(config=agent_config_dict)
@agent def agent_name(self) -> Agent: return Agent(...)
```

### Relationships

- Assigned to Tasks via task.agent=agent_instance
- Can use Tools assigned to them
- Grouped in Crews
- Can delegate Tasks to other Agents (if allow_delegation=True)

### Integration

- YAML configuration: Define agent parameters in YAML
- Decorator pattern: @agent for class-based definition
- Delegation: Agents with allow_delegation=True can delegate tasks
- Config-driven: Both programmatic and YAML-based configuration

### Examples

```python
# Basic definition
agent = Agent(role="Analyst", goal="Analyze data", backstory="Expert analyst")

# YAML config
agents_config = 'config/agents.yaml'
agent = Agent(config=config['analyst_agent'])

# Class-based definition
@agent
def analyst_agent(self) -> Agent:
    return Agent(config=self.agents_config['analyst_agent'])
```

## Tasks

### Definition

Units of work assigned to Agents, with descriptions and expected outputs.

### Parameters

- `description`: String - Task instructions
- `expected_output`: String - Description of desired result
- `agent`: Agent - Agent assigned to task
- `async_execution`: Bool - Run asynchronously
- `output_file`: String - Path to save output
- `tools`: List[Tool] - Additional tools for this task
- `context`: List[str] - Additional context
- `callbacks`: Dict - Task lifecycle callbacks

### Syntax

```python
Task(description="", expected_output="", agent=agent_instance)
Task(config=task_config_dict, agent=agent_instance)
@task def task_name(self) -> Task: return Task(...)
```

### Relationships

- Executed by Agents
- Can be sequenced in Processes
- Can use Tools
- Can pass outputs to other Tasks

### Integration

- YAML configuration: Define task parameters in YAML
- Decorator pattern: @task for class-based definition
- Input interpolation: {placeholder} in descriptions
- Chain tasks through dependencies

### Examples

```python
# Basic definition
task = Task(description="Analyze data", expected_output="Analysis report", agent=analyst)

# YAML config
tasks_config = 'config/tasks.yaml'
task = Task(config=tasks_config['analysis_task'], agent=analyst)

# Class-based definition with dynamic inputs
@task
def analysis_task(self) -> Task:
    return Task(
        config=self.tasks_config['analysis_task'],
        agent=self.analyst_agent()
    )
```

## Tools

### Definition

Capabilities provided to Agents to interact with external systems, APIs, and data.

### Types

- `BaseTool`: Abstract base class for all tools
- `ToolWithActions`: Tools with predefined actions
- `ToolWithLLM`: Tools utilizing LLMs

### Parameters

- `name`: String - Tool identifier
- `description`: String - Tool purpose and usage
- `func`: Function - Implementation function
- `schema`: Dict - Tool's input schema
- `return_direct`: Bool - Return without additional processing

### Syntax

```python
# Function-based tool
@tool
def tool_function(parameter):
    return result

# Class-based tool
class CustomTool(BaseTool):
    name = "tool_name"
    description = "Tool description"

    def _run(self, input_param):
        return result
```

### Relationships

- Used by Agents during Task execution
- Can be shared across multiple Agents
- Can be contextual to specific Tasks

### Integration

- Function decorator: @tool
- Tool registry: Registered at runtime
- Tool chaining: Tools calling other tools
- LangChain compatibility: Can use LangChain tools

### Examples

```python
# Function-based tool
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Implementation
    return results

# Class-based tool
class DatabaseTool(BaseTool):
    name = "database_tool"
    description = "Query the database"

    def _run(self, query: str):
        # Database query implementation
        return results
```

## Flows

### Definition

Patterns that define how Agents collaborate and how Tasks are executed.

### Types

- `Sequential`: Tasks execute in defined order
- `Hierarchical`: Manager Agent delegates to sub-Agents
- `Custom`: User-defined execution patterns

### Parameters

- `process`: Process - Execution process type
- `manager_llm`: LLM - Model for manager in hierarchical flows
- `execution_mode`: String - Serial or parallel execution
- `verbose`: Bool - Detailed logging

### Syntax

```python
# Sequential flow
crew = Crew(agents=agents, tasks=tasks, process=Process.sequential)

# Hierarchical flow
crew = Crew(agents=agents, tasks=tasks, process=Process.hierarchical)

# Custom flow
crew = Crew(agents=agents, tasks=tasks, process=custom_process_function)
```

### Relationships

- Defines how Agents collaborate
- Controls Task execution order
- Influences Manager-Worker dynamics
- Determines task output handling

### Integration

- Process enum: Process.sequential, Process.hierarchical
- Custom process functions
- RPG mode: role-playing creative execution
- Planning integration: Connects to planning systems

### Examples

```python
# Sequential process where each agent completes their task in order
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential
)

# Hierarchical with manager delegating to specialized agents
crew = Crew(
    agents=[manager, specialist1, specialist2],
    tasks=[complex_task],
    process=Process.hierarchical
)
```

## Knowledge

### Definition

Information sources used by Agents to augment their capabilities.

### Types

- `File-based`: Documents, PDFs, text files
- `Vector stores`: Embeddings for semantic search
- `Databases`: Structured data sources
- `API integrations`: External knowledge services

### Parameters

- `name`: String - Knowledge source identifier
- `description`: String - Knowledge content description
- `retrieval_method`: String - How agents access knowledge
- `embedding_model`: String - Vector embedding model
- `chunk_size`: Int - Text chunking for embeddings

### Syntax

```python
# Direct attachment
agent = Agent(..., knowledge=[document1, document2])

# Knowledge base creation
kb = CrewKnowledgeBase(documents=documents, embedding_model="text-embedding-ada-002")
agent = Agent(..., knowledge=kb)
```

### Relationships

- Used by Agents during reasoning
- Can be shared across Agents
- Augments LLM capabilities
- Integrates with Tools for retrieval

### Integration

- Direct attachment: Assign to agents
- Shared knowledge bases
- RAG patterns: Retrieval-augmented generation
- Dynamic knowledge loading

### Examples

```python
# File-based knowledge
agent = Agent(
    role="Researcher",
    goal="Find information",
    backstory="Expert researcher",
    knowledge=["data/document1.pdf", "data/document2.txt"]
)

# Vector store knowledge base
kb = CrewKnowledgeBase()
kb.load_from_dir("./data/")
agent = Agent(..., knowledge=kb)
```

## Processes

### Definition

Execution models that determine how Tasks and Agents interact.

### Types

- `sequential`: Tasks run in defined order
- `hierarchical`: Manager delegates to workers
- `parallel`: Multiple tasks run concurrently
- `custom`: User-defined execution patterns

### Parameters

- `process_type`: Process - Execution model enum
- `max_iterations`: Int - Maximum execution cycles
- `task_dependencies`: Dict - Task prerequisites
- `error_handling`: String - Error handling strategy

### Syntax

```python
# Using process enum
crew = Crew(
    agents=agents,
    tasks=tasks,
    process=Process.sequential
)

# Custom process function
def custom_process(crew, tasks, agents):
    # Implementation
    return results

crew = Crew(agents=agents, tasks=tasks, process=custom_process)
```

### Relationships

- Controls Task execution flow
- Defines Agent collaboration patterns
- Handles outputs between Tasks
- Manages execution lifecycle

### Integration

- Process enum values
- Custom process functions
- Process callbacks and hooks
- Error handling and recovery

### Examples

```python
# Sequential process
crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    process=Process.sequential
)

# Custom process with special handling
def expert_review_process(crew, tasks, agents):
    # First expert does initial work
    result1 = tasks[0].execute(agents[0])
    # Second expert reviews and enhances
    result2 = tasks[1].execute(agents[1], context=result1)
    return result2

crew = Crew(agents=experts, tasks=analysis_tasks, process=expert_review_process)
```

## LLMs

### Definition

Language models that power Agents' reasoning and responses.

### Types

- `OpenAI`: GPT models (3.5-turbo, 4, etc.)
- `Anthropic`: Claude models
- `Local`: Local LLMs (Llama, etc.)
- `Custom`: User-implemented LLMs

### Parameters

- `model`: String - Model identifier
- `api_key`: String - API authentication
- `temperature`: Float - Response randomness
- `max_tokens`: Int - Response length limit
- `streaming`: Bool - Stream responses
- `context_window`: Int - Token context size

### Syntax

```python
# OpenAI LLM
from crewai import OpenAILLM
llm = OpenAILLM(model="gpt-4")

# Local LLM
from crewai import LocalLLM
llm = LocalLLM(model="llama2")

# Using with agent
agent = Agent(..., llm=llm)
```

### Relationships

- Powers Agent reasoning
- Used in Tools for processing
- Influences Task execution quality
- Can be shared across Agents

### Integration

- Direct instantiation
- Environment variables
- Custom LLM classes
- Provider-specific parameters

### Examples

```python
# OpenAI with custom parameters
from crewai import OpenAILLM
llm = OpenAILLM(
    model="gpt-4",
    temperature=0.7,
    api_key="sk-..."
)

# Anthropic model
from crewai import AnthropicLLM
llm = AnthropicLLM(model="claude-2")

# Using different LLMs for different agents
researcher = Agent(..., llm=gpt4_llm)
writer = Agent(..., llm=claude_llm)
```

## Memory

### Definition

Storage mechanisms that allow Agents to retain information between actions.

### Types

- `ConversationMemory`: Chat history
- `TaskMemory`: Task-specific information
- `SharedMemory`: Cross-agent information
- `PersistentMemory`: Saved between sessions

### Parameters

- `memory_type`: String - Memory implementation
- `max_tokens`: Int - Memory size limit
- `relevance_threshold`: Float - Memory retrieval threshold
- `storage_backend`: String - Where memories are saved

### Syntax

```python
# Conversation memory
from crewai import ConversationMemory
memory = ConversationMemory()

# Task memory
from crewai import TaskMemory
memory = TaskMemory()

# Using with agent
agent = Agent(..., memory=memory)
```

### Relationships

- Used by Agents to maintain context
- Shared between Task executions
- Can persist across Crew sessions
- Integrated with Knowledge retrieval

### Integration

- Memory class instantiation
- Agent.memory attribute
- Task output storage
- Persistent storage backends

### Examples

```python
# Conversation memory with token limit
memory = ConversationMemory(max_tokens=4000)

# Shared memory between agents
shared_memory = SharedMemory()
agent1 = Agent(..., memory=shared_memory)
agent2 = Agent(..., memory=shared_memory)

# Persistent memory with file storage
memory = PersistentMemory(storage_path="./memories/")
```

## Planning

### Definition

Mechanisms for Agents to create execution plans for complex Tasks.

### Types

- `SimplePlanner`: Basic sequential planning
- `HierarchicalPlanner`: Manager-worker plans
- `ReactivePlanner`: Adapts plans during execution
- `CustomPlanner`: User-defined planning logic

### Parameters

- `planner_type`: String - Planning implementation
- `planning_prompt`: String - Guide for plan creation
- `max_steps`: Int - Maximum plan steps
- `verbose`: Bool - Detailed planning logs

### Syntax

```python
# Enable planning
crew = Crew(
    agents=agents,
    tasks=tasks,
    process=Process.sequential,
    planning=True
)

# Custom planning
crew = Crew(
    agents=agents,
    tasks=tasks,
    process=Process.sequential,
    planning=custom_planning_function
)
```

### Relationships

- Guides Agent task execution
- Can span multiple Tasks
- Works with Process flows
- Affects delegation patterns

### Integration

- Boolean flag activation
- Custom planning functions
- Planning lifecycle callbacks
- Plan revision mechanisms

### Examples

```python
# Basic planning enabled
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, write_task, edit_task],
    process=Process.sequential,
    planning=True
)

# Custom planning function
def research_planning(crew, task):
    # Implementation
    return plan

crew = Crew(
    agents=[researcher],
    tasks=[complex_research_task],
    planning=research_planning
)
