# Mem0 Memory Configuration Guide for Space Hulk Game

This guide explains how to configure mem0 for optimal memory management in the Space Hulk multi-agent narrative generation crew.

## Table of Contents

1. [Overview](#overview)
2. [Memory Benefits for Narrative Generation](#memory-benefits)
3. [Configuration Options](#configuration-options)
4. [Setup Instructions](#setup-instructions)
5. [Automated Configuration](#automated-configuration)
6. [Monitoring and Debugging](#monitoring-and-debugging)
7. [Troubleshooting](#troubleshooting)

## Overview

The Space Hulk crew uses 6 specialized AI agents to collaboratively generate game narratives:

1. **NarrativeDirectorAgent** - Ensures narrative cohesion (evaluator/manager)
2. **PlotMasterAgent** - Creates overarching plot structure
3. **NarrativeArchitectAgent** - Maps plot into detailed scenes
4. **PuzzleSmithAgent** - Designs puzzles, artifacts, NPCs, and monsters
5. **CreativeScribeAgent** - Writes descriptions and dialogue
6. **MechanicsGuruAgent** - Defines game mechanics and systems

Memory management is critical for:
- **Entity consistency**: Artifacts, locations, characters, monsters
- **Cross-agent context**: Each agent builds on previous outputs
- **Narrative cohesion**: Evaluations reference earlier decisions
- **Quality improvement**: Learning patterns across multiple runs

## Memory Benefits

### Token Consumption
- **90% reduction** in context tokens vs. naive context passing
- Agents retrieve relevant information instead of processing full history
- Significant cost savings with cloud LLMs

### Quality Improvements
- **26% accuracy improvement** vs. basic context strategies
- Entity tracking ensures consistency (e.g., artifact names match across agents)
- Long-term memory enables learning from previous generations

### Specific Benefits for Each Agent

| Agent | Memory Benefit |
|-------|---------------|
| **PlotMasterAgent** | Foundation stored for all subsequent agents to reference |
| **NarrativeArchitectAgent** | Retrieves plot elements, ensures scene consistency |
| **PuzzleSmithAgent** | Stores artifacts/NPCs as entities, prevents duplicates |
| **CreativeScribeAgent** | References stored entities for consistent descriptions |
| **MechanicsGuruAgent** | Retrieves all game elements to define appropriate systems |
| **NarrativeDirectorAgent** | Accesses complete history for cohesion evaluation |

## Configuration Options

### Option 1: Basic Memory (Built-in, No Setup)

**Pros:**
- No external dependencies
- Works immediately
- Good for development/testing

**Cons:**
- Limited functionality
- No cross-session learning
- Basic entity tracking

**Configuration:**
```python
# In crew.py crew() method
return Crew(
    agents=self.agents,
    tasks=self.tasks,
    process=Process.sequential,
    verbose=True,
    memory=True  # Enable built-in memory
)
```

### Option 2: Cloud Mem0 (Recommended for Quick Start)

**Pros:**
- Advanced features immediately available
- No infrastructure setup
- Managed service (backups, scaling)

**Cons:**
- Requires API key (subscription)
- Data stored externally
- Ongoing costs

**Setup:**
1. Sign up at [https://mem0.ai/](https://mem0.ai/)
2. Get API key from dashboard
3. Add to `.env`:
   ```bash
   MEM0_API_KEY=m0-your-api-key-here
   ```

**Configuration:**
```python
# In crew.py crew() method
return Crew(
    agents=self.agents,
    tasks=self.tasks,
    process=Process.sequential,
    verbose=True,
    memory=True,
    memory_config={
        "provider": "mem0",
        "config": {
            "user_id": "space_hulk_user",
            "run_id": f"session_{datetime.datetime.now().timestamp()}"
        }
    }
)
```

### Option 3: Local Mem0 (Recommended for Production)

**Pros:**
- Complete data privacy
- No ongoing costs
- Full control over infrastructure
- Works offline

**Cons:**
- Requires Qdrant or ChromaDB setup
- More complex configuration
- Self-managed infrastructure

**Setup:**

#### Step 1: Install Qdrant (Vector Database)

**Using Docker (Recommended):**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Using Docker Compose:**
```yaml
# docker-compose.yml
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage
```

Then run:
```bash
docker-compose up -d
```

**Alternative: ChromaDB (Embedded, No Server)**
- No Docker required
- Stores data in local directory
- Simpler but less performant

#### Step 2: Install Embedding Model

**For Ollama:**
```bash
# Install best embedding model for narratives
ollama pull mxbai-embed-large

# Alternative option
ollama pull nomic-embed-text
```

**For OpenAI:**
- Uses `text-embedding-3-small` via API
- No local installation needed
- Requires `OPENAI_API_KEY`

#### Step 3: Configure in `.env`

```bash
# LLM Configuration (existing)
OPENAI_MODEL_NAME=ollama/qwen2.5
OLLAMA_BASE_URL=http://localhost:11434

# Memory Configuration - Local Mem0
MEM0_PROVIDER=local
MEM0_VECTOR_STORE=qdrant
MEM0_VECTOR_HOST=localhost
MEM0_VECTOR_PORT=6333
MEM0_COLLECTION_NAME=space_hulk_narratives

# Embedding Configuration
MEM0_EMBEDDER_PROVIDER=ollama
MEM0_EMBEDDER_MODEL=mxbai-embed-large
MEM0_EMBEDDER_BASE_URL=http://localhost:11434

# Memory LLM Configuration (for memory processing)
MEM0_LLM_PROVIDER=ollama
MEM0_LLM_MODEL=qwen2.5
MEM0_LLM_BASE_URL=http://localhost:11434
MEM0_LLM_TEMPERATURE=0.2
MEM0_LLM_MAX_TOKENS=2000

# Storage Location (optional)
CREWAI_STORAGE_DIR=./memory_storage
```

#### Step 4: Update crew.py (or use automated configuration)

See "Automated Configuration" section below.

## Setup Instructions

### Phase 1: Test Basic Memory (5 minutes)

This validates memory improves your crew's output quality.

1. **Enable basic memory:**
   ```python
   # In src/space_hulk_game/crew.py, line ~736
   return Crew(
       agents=self.agents,
       tasks=self.tasks,
       process=Process.sequential,
       verbose=True,
       memory=True  # Uncomment/add this line
   )
   ```

2. **Run the crew:**
   ```bash
   crewai run
   ```

3. **Observe improvements:**
   - Check if agents reference previous outputs
   - Look for entity consistency
   - Monitor token usage in logs

### Phase 2: Add Cloud Mem0 (10 minutes)

Once basic memory works, upgrade to mem0 for advanced features.

1. **Get API key:**
   - Sign up at [https://mem0.ai/](https://mem0.ai/)
   - Create API key in dashboard

2. **Add to .env:**
   ```bash
   MEM0_API_KEY=m0-your-actual-key-here
   ```

3. **Update crew.py:**
   ```python
   # In crew() method
   memory_config = {
       "provider": "mem0",
       "config": {
           "user_id": "space_hulk_user",
           "run_id": f"gen_{datetime.datetime.now().timestamp()}"
       }
   }

   return Crew(
       agents=self.agents,
       tasks=self.tasks,
       process=Process.sequential,
       verbose=True,
       memory=True,
       memory_config=memory_config
   )
   ```

4. **Test:**
   ```bash
   crewai run
   ```

### Phase 3: Migrate to Local Mem0 (30 minutes)

For production use with complete data privacy.

1. **Install Qdrant:**
   ```bash
   docker run -d -p 6333:6333 --name qdrant qdrant/qdrant
   ```

2. **Install embedding model:**
   ```bash
   ollama pull mxbai-embed-large
   ```

3. **Configure environment:**
   - Update `.env` with settings from Option 3 above

4. **Use automated configuration:**
   ```bash
   python configure_mem0.py --mode local
   ```

   This script (provided below) will:
   - Validate Qdrant is running
   - Validate Ollama embedding model is available
   - Update crew.py with proper configuration
   - Test the connection

5. **Run the crew:**
   ```bash
   crewai run
   ```

## Automated Configuration

Use the provided `configure_mem0.py` script to automatically set up mem0 integration.

### Usage

```bash
# Test basic memory (no external dependencies)
python configure_mem0.py --mode basic

# Configure cloud mem0 (requires MEM0_API_KEY in .env)
python configure_mem0.py --mode cloud

# Configure local mem0 (requires Qdrant + Ollama)
python configure_mem0.py --mode local

# Validate configuration without modifying crew.py
python configure_mem0.py --mode local --validate-only

# Use ChromaDB instead of Qdrant
python configure_mem0.py --mode local --vector-store chroma
```

### What the Script Does

1. **Validates prerequisites:**
   - Checks if required services are running (Qdrant, Ollama)
   - Verifies API keys are present
   - Tests connectivity

2. **Updates crew.py:**
   - Adds proper memory configuration
   - Enables memory in crew() method
   - Preserves existing code structure

3. **Creates configuration:**
   - Generates optimal settings for your use case
   - Configures embedder, vector store, and LLM
   - Sets appropriate memory scoping (user_id, run_id)

4. **Tests setup:**
   - Validates memory can be initialized
   - Checks entity tracking works
   - Provides diagnostic output

### Script Location

The configuration script is created at:
```
space_hulk_game/
└── configure_mem0.py
```

See the "Automated Configuration" section below for the complete script.

## Monitoring and Debugging

### Memory Storage Locations

**Basic Memory:**
- Windows: `C:\Users\{username}\AppData\Local\CrewAI\space_hulk_game\`
- macOS: `~/Library/Application Support/CrewAI/space_hulk_game/`
- Linux: `~/.local/share/CrewAI/space_hulk_game/`

**Custom Location:**
```bash
# In .env
CREWAI_STORAGE_DIR=./memory_storage
```

**Qdrant Storage:**
- Default: In-memory (lost on restart)
- Persistent: Mount volume in Docker
  ```bash
  docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
  ```

### Checking Memory Contents

**For Cloud Mem0:**
```python
from mem0 import MemoryClient
client = MemoryClient(api_key="your-key")

# List all memories for user
memories = client.get_all(user_id="space_hulk_user")
print(memories)

# Search specific memory
results = client.search("space hulk artifact", user_id="space_hulk_user")
print(results)
```

**For Qdrant:**
```bash
# Access Qdrant web UI
open http://localhost:6333/dashboard

# Or use API
curl http://localhost:6333/collections/space_hulk_narratives
```

### Debug Logging

**Enable verbose memory logs:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In crew.py
crew = Crew(
    agents=self.agents,
    tasks=self.tasks,
    verbose=True,  # Already enabled
    memory=True,
    # ... rest of config
)
```

**Environment variable:**
```bash
# In .env
LOG_LEVEL=DEBUG
CREWAI_VERBOSE=true
```

### Memory Metrics to Monitor

Track these metrics to validate memory is working:

1. **Token Usage:**
   - Compare runs with/without memory
   - Should see 70-90% reduction in context tokens
   - Monitor LLM API costs

2. **Entity Consistency:**
   - Check if artifact names match across tasks
   - Verify location descriptions are consistent
   - Validate character names don't change

3. **Quality Metrics:**
   - Narrative cohesion scores
   - Evaluation task feedback
   - User/tester feedback on consistency

4. **Memory Growth:**
   - Track number of stored entities
   - Monitor vector database size
   - Set retention policies if needed

## Troubleshooting

### Issue: "MEM0_API_KEY not found"

**Solution:**
```bash
# Verify .env file exists and has the key
cat .env | grep MEM0_API_KEY

# If missing, add it:
echo "MEM0_API_KEY=m0-your-key-here" >> .env

# Restart the crew
crewai run
```

### Issue: "Cannot connect to Qdrant at localhost:6333"

**Solution:**
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# If not running, start it:
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant

# Test connectivity:
curl http://localhost:6333/collections
```

### Issue: "Embedding model not found: mxbai-embed-large"

**Solution:**
```bash
# Pull the embedding model
ollama pull mxbai-embed-large

# Verify it's available
ollama list | grep mxbai-embed-large

# Alternative: use a different model
# In .env, change MEM0_EMBEDDER_MODEL to:
MEM0_EMBEDDER_MODEL=nomic-embed-text
```

### Issue: "Memory not persisting between runs"

**Causes and Solutions:**

1. **Using in-memory Qdrant:**
   ```bash
   # Use persistent storage
   docker run -d -p 6333:6333 \
     -v $(pwd)/qdrant_storage:/qdrant/storage \
     --name qdrant qdrant/qdrant
   ```

2. **Different run_id each time:**
   ```python
   # In crew.py, use consistent user_id:
   "config": {
       "user_id": "space_hulk_user",  # Persistent
       "run_id": f"session_{date}"    # Optional, for run-specific
   }
   ```

3. **Collection being recreated:**
   - Check if collection name changes between runs
   - Verify `MEM0_COLLECTION_NAME` is consistent in .env

### Issue: "High token usage despite memory"

**Solutions:**

1. **Verify memory is enabled:**
   ```python
   # Should see this in logs:
   # "Initializing memory system..."
   # "Memory provider: mem0"
   ```

2. **Check retrieval is working:**
   - Enable debug logging
   - Look for "Retrieved N memories" in logs
   - If retrieval count is 0, memory isn't being queried

3. **Adjust retrieval parameters:**
   ```python
   # In memory_config, add:
   "config": {
       "user_id": "space_hulk_user",
       "top_k": 10,  # Retrieve top 10 relevant memories
       "score_threshold": 0.7  # Minimum relevance score
   }
   ```

### Issue: "Inconsistent entity tracking"

**Solutions:**

1. **Improve embedding quality:**
   ```python
   # Use better embedding model
   # For Ollama:
   MEM0_EMBEDDER_MODEL=mxbai-embed-large  # Better than nomic-embed-text

   # For OpenAI:
   MEM0_EMBEDDER_PROVIDER=openai
   MEM0_EMBEDDER_MODEL=text-embedding-3-large  # Better than 3-small
   ```

2. **Structured entity definitions:**
   - Ensure agents output entities in consistent format
   - Use YAML structure in expected_output
   - Add entity validation in tasks

3. **Memory refresh:**
   - Clear old/incorrect memories
   - Rebuild vector database
   ```bash
   # Delete Qdrant collection
   curl -X DELETE http://localhost:6333/collections/space_hulk_narratives

   # Restart crew to recreate
   crewai run
   ```

## Best Practices

### 1. Memory Scoping

Use appropriate identifiers for your use case:

```python
memory_config = {
    "provider": "mem0",
    "config": {
        # Required: Unique per game session
        "user_id": "space_hulk_user",

        # Optional: Unique per generation run
        "run_id": f"gen_{datetime.datetime.now().timestamp()}",

        # Optional: For multi-tenant systems
        "app_id": "space_hulk_game",

        # Optional: Track agent-specific memories
        # "agent_id": "narrative_director"  # Set per-agent if needed
    }
}
```

**Recommendation:** Use `user_id` for persistent learning across runs, `run_id` to isolate individual generations.

### 2. Memory Retention

Set retention policies to prevent unbounded growth:

```python
# In mem0 client (advanced usage)
client = MemoryClient()

# Set retention: keep memories for 30 days
client.add(
    messages,
    user_id="space_hulk_user",
    metadata={"ttl": 2592000}  # 30 days in seconds
)
```

### 3. Entity Schema

Define consistent entity structures in your tasks:

```yaml
# In tasks.yaml
DesignArtifactsAndPuzzles:
  expected_output: >
    A structured YAML document with the following format:

    artifacts:
      - name: "Exact name used elsewhere"
        type: "weapon|tool|key|consumable"
        location: "Exact scene name"
        description: "Detailed description"

    This ensures entity tracking can match entities across agents.
```

### 4. Memory Monitoring

Add logging to track memory usage:

```python
# In crew.py, after_kickoff hook
@after_kickoff
def process_output(self, output):
    logger.info("Processing crew output...")

    # Log memory statistics
    try:
        # Get memory client
        from mem0 import MemoryClient
        client = MemoryClient()

        # Count memories
        memories = client.get_all(user_id="space_hulk_user")
        logger.info(f"Total memories stored: {len(memories)}")

        # Log recent memories
        for memory in memories[-5:]:
            logger.info(f"Recent memory: {memory}")
    except Exception as e:
        logger.warning(f"Could not retrieve memory stats: {e}")

    return output
```

### 5. Performance Optimization

**For large-scale generation:**

1. **Use efficient embeddings:**
   - `mxbai-embed-large` (Ollama) - Good balance
   - `text-embedding-3-small` (OpenAI) - Best quality/cost

2. **Batch processing:**
   - Process multiple games in single session
   - Reuse memory context across related runs

3. **Selective memory:**
   - Only store critical information
   - Filter out verbose intermediate outputs
   - Focus on entities, not full descriptions

4. **Vector database tuning:**
   ```python
   # For Qdrant, tune HNSW parameters
   "vector_store": {
       "provider": "qdrant",
       "config": {
           "collection_name": "space_hulk_narratives",
           "host": "localhost",
           "port": 6333,
           "embedding_model_dims": 1024,
           "hnsw_config": {
               "m": 16,
               "ef_construct": 100
           }
       }
   }
   ```

## Additional Resources

- **Mem0 Documentation:** [https://docs.mem0.ai/](https://docs.mem0.ai/)
- **CrewAI Memory Guide:** [https://docs.crewai.com/concepts/memory](https://docs.crewai.com/concepts/memory)
- **Qdrant Setup:** [https://qdrant.tech/documentation/quick-start/](https://qdrant.tech/documentation/quick-start/)
- **Ollama Embeddings:** [https://ollama.ai/library](https://ollama.ai/library)
- **Project Documentation:** See `docs/` directory

## Next Steps

After setting up memory:

1. **Validate improvement:** Run crew with/without memory, compare outputs
2. **Monitor token usage:** Track context size reduction
3. **Test entity consistency:** Verify artifacts/locations match across agents
4. **Enable hierarchical mode:** Once memory works, test with manager delegation
5. **Iterate and refine:** Adjust memory configuration based on results

For questions or issues, see [CONTRIBUTING.md](../CONTRIBUTING.md) for how to report bugs or request features.
