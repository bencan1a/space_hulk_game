# Mem0 Quick Reference - Space Hulk Game

Quick reference guide for mem0 memory management in the Space Hulk narrative generation crew.

## Quick Start (3 Options)

### Option 1: Basic Memory (Fastest - 2 minutes)

```bash
# Just enable built-in memory, no setup needed
python configure_mem0.py --mode basic
crewai run
```

### Option 2: Cloud Mem0 (Easy - 10 minutes)

```bash
# 1. Get API key from https://mem0.ai/
# 2. Add to .env
echo "MEM0_API_KEY=m0-your-key-here" >> .env

# 3. Configure and run
python configure_mem0.py --mode cloud
crewai run
```

### Option 3: Local Mem0 (Production - 30 minutes)

```bash
# 1. Start Qdrant
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant

# 2. Install embedding model
ollama pull mxbai-embed-large

# 3. Configure and run
python configure_mem0.py --mode local
crewai run
```

## Common Commands

### Configuration

```bash
# Validate setup without making changes
python configure_mem0.py --mode local --validate-only

# Use ChromaDB instead of Qdrant (no Docker needed)
python configure_mem0.py --mode local --vector-store chroma

# Test current configuration
python -c "from space_hulk_game.crew import SpaceHulkGame; crew = SpaceHulkGame(); print('Memory:', crew.crew().memory)"
```

### Monitoring

```bash
# Check Qdrant collections
curl http://localhost:6333/collections

# View Qdrant dashboard
open http://localhost:6333/dashboard  # macOS
start http://localhost:6333/dashboard # Windows

# Check Ollama models
ollama list

# Monitor crew logs with memory info
crewai run 2>&1 | grep -i memory
```

### Maintenance

```bash
# Clear memory (start fresh)
# For Qdrant:
curl -X DELETE http://localhost:6333/collections/space_hulk_narratives

# For basic memory:
rm -rf ~/Library/Application\ Support/CrewAI/space_hulk_game/  # macOS
rm -rf ~/.local/share/CrewAI/space_hulk_game/                  # Linux
# Windows: Delete C:\Users\{username}\AppData\Local\CrewAI\space_hulk_game\

# Restart services
docker restart qdrant    # Restart Qdrant
ollama serve            # Restart Ollama
```

## Configuration Comparison

| Feature | Basic | Cloud Mem0 | Local Mem0 |
|---------|-------|------------|------------|
| **Setup Time** | 2 min | 10 min | 30 min |
| **External Services** | None | API key | Qdrant + Ollama |
| **Data Privacy** | Local | Cloud | Local |
| **Cost** | Free | Paid | Free |
| **Features** | Limited | Full | Full |
| **Best For** | Development | Quick start | Production |

## Memory Benefits for Your Crew

### Token Reduction
- **Without memory**: Each agent gets full context (10,000+ tokens)
- **With memory**: Relevant info retrieved (1,000-2,000 tokens)
- **Savings**: 70-90% reduction in tokens

### Narrative Consistency

| Agent | Without Memory | With Memory |
|-------|----------------|-------------|
| **PlotMaster** | Creates foundation | Creates foundation + stores entities |
| **NarrativeArchitect** | Reads full plot output | Retrieves relevant plot elements |
| **PuzzleSmith** | May duplicate items | Checks existing entities |
| **CreativeScribe** | Inconsistent names | References stored entities |
| **MechanicsGuru** | Repeats definitions | Builds on stored mechanics |
| **NarrativeDirector** | Reviews full history | Queries specific concerns |

## Troubleshooting Quick Fixes

### "MEM0_API_KEY not found"
```bash
# Add to .env
echo "MEM0_API_KEY=m0-your-actual-key" >> .env
```

### "Cannot connect to Qdrant"
```bash
# Check if running
docker ps | grep qdrant

# If not, start it
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant

# Test connectivity
curl http://localhost:6333/collections
```

### "Embedding model not found"
```bash
# Install the model
ollama pull mxbai-embed-large

# Verify
ollama list | grep mxbai
```

### "Memory not persisting"
```bash
# For Qdrant, use persistent storage
docker run -d -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  --name qdrant qdrant/qdrant
```

### "High token usage despite memory"
```bash
# Verify memory is enabled
python -c "from space_hulk_game.crew import SpaceHulkGame; \
  crew = SpaceHulkGame(); \
  print('Memory enabled:', crew.crew().memory)"

# Check logs for memory operations
crewai run 2>&1 | grep "Retrieved.*memories"
```

## Code Snippets

### Check Memory Contents (Cloud Mem0)

```python
from mem0 import MemoryClient
import os

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

# List all memories
memories = client.get_all(user_id="space_hulk_user")
print(f"Total memories: {len(memories)}")

# Search specific topic
results = client.search(
    "artifacts and puzzles",
    user_id="space_hulk_user",
    limit=5
)
for result in results:
    print(f"- {result['memory']}")
```

### Query Qdrant Collection

```python
import requests

# Get collection info
response = requests.get("http://localhost:6333/collections/space_hulk_narratives")
print(response.json())

# Search vectors
search_query = {
    "vector": [0.1] * 1024,  # Replace with actual embedding
    "limit": 5
}
response = requests.post(
    "http://localhost:6333/collections/space_hulk_narratives/points/search",
    json=search_query
)
print(response.json())
```

### Custom Memory Configuration

```python
# In crew.py, customize memory behavior
memory_config = {
    "provider": "mem0",
    "config": {
        "user_id": "space_hulk_user",
        "run_id": f"session_{datetime.datetime.now().timestamp()}",

        # Advanced settings (if using local mem0)
        "local_mem0_config": {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "qwen2.5",
                    "temperature": 0.2,  # Lower = more deterministic
                    "max_tokens": 2000
                }
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "mxbai-embed-large",  # Or "nomic-embed-text"
                    "ollama_base_url": "http://localhost:11434"
                }
            },
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "space_hulk_narratives",
                    "host": "localhost",
                    "port": 6333,
                    "embedding_model_dims": 1024
                }
            }
        }
    }
}
```

## Performance Tuning

### For Faster Generation

```python
# Use smaller embedding model
MEM0_EMBEDDER_MODEL=nomic-embed-text  # Faster than mxbai-embed-large

# Reduce retrieval count
"config": {
    "user_id": "space_hulk_user",
    "top_k": 5  # Default is 10
}
```

### For Better Quality

```python
# Use OpenAI embeddings (requires API key)
MEM0_EMBEDDER_PROVIDER=openai
MEM0_EMBEDDER_MODEL=text-embedding-3-large

# Increase retrieval count
"config": {
    "user_id": "space_hulk_user",
    "top_k": 20,  # More context
    "score_threshold": 0.6  # Lower threshold = more results
}
```

## Memory Scoping Strategies

### Per-Game Session
```python
# Each game generation gets its own memory scope
memory_config = {
    "provider": "mem0",
    "config": {
        "user_id": "space_hulk_user",
        "run_id": f"game_{datetime.datetime.now().timestamp()}"
    }
}
```

### Shared Learning
```python
# All generations share memory (learn from previous games)
memory_config = {
    "provider": "mem0",
    "config": {
        "user_id": "space_hulk_user"
        # No run_id = shared across all runs
    }
}
```

### Agent-Specific Memory
```python
# Each agent has its own memory space
# In agent definition:
memory_config = {
    "provider": "mem0",
    "config": {
        "user_id": "space_hulk_user",
        "agent_id": "plot_master"  # Unique per agent
    }
}
```

## Environment Variables Quick Reference

```bash
# Minimum for cloud mem0
MEM0_API_KEY=m0-your-key-here

# Complete for local mem0
MEM0_PROVIDER=local
MEM0_VECTOR_STORE=qdrant
MEM0_VECTOR_HOST=localhost
MEM0_VECTOR_PORT=6333
MEM0_COLLECTION_NAME=space_hulk_narratives
MEM0_EMBEDDER_PROVIDER=ollama
MEM0_EMBEDDER_MODEL=mxbai-embed-large
MEM0_EMBEDDER_BASE_URL=http://localhost:11434
MEM0_LLM_PROVIDER=ollama
MEM0_LLM_MODEL=qwen2.5
MEM0_LLM_BASE_URL=http://localhost:11434
MEM0_LLM_TEMPERATURE=0.2
MEM0_LLM_MAX_TOKENS=2000
```

## Next Steps

1. **Start simple**: Use basic memory first
2. **Validate improvement**: Compare outputs with/without memory
3. **Upgrade gradually**: Move to cloud, then local mem0
4. **Monitor metrics**: Track token usage and consistency
5. **Tune as needed**: Adjust based on your specific use case

## Resources

- **Full Documentation**: [docs/MEM0_SETUP_GUIDE.md](./MEM0_SETUP_GUIDE.md)
- **Configuration Script**: `configure_mem0.py`
- **Environment Template**: `.env.example`
- **Mem0 Docs**: [https://docs.mem0.ai/](https://docs.mem0.ai/)
- **CrewAI Docs**: [https://docs.crewai.com/concepts/memory](https://docs.crewai.com/concepts/memory)
