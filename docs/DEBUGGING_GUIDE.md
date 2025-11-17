# Crew Debugging Quick Start Guide

## Problem

The multi-agent crew gets stuck and becomes unresponsive when running in hierarchical mode. This needs to be fixed before adding any new features.

## Solution Approach

Test and fix in stages, from simplest to most complex.

---

## Prerequisites

1. **Ollama running:**

   ```bash
   ollama list  # Check Ollama is installed
   ollama pull qwen2.5  # Ensure model is available
   ollama serve  # Start server if not running
   ```

2. **Environment configured:**
   Create `.env` file:

   ```
   OPENAI_MODEL_NAME=ollama/qwen2.5
   OPENAI_API_BASE=http://localhost:11434
   OPENAI_API_KEY=dummy-value
   ```

3. **Dependencies installed:**

   ```bash
   crewai install
   ```

---

## Stage 1: Test Sequential Mode (Week 1)

**Goal:** Prove basic agents work without hierarchy complexity

**Steps:**

1. **Switch to sequential crew:**

   ```bash
   # Backup current crew
   mv src/space_hulk_game/crew.py src/space_hulk_game/crew_hierarchical.py

   # Use sequential version
   cp crew_sequential.py src/space_hulk_game/crew.py
   ```

2. **Run test:**

   ```bash
   python test_crew_generation.py --mode sequential --timeout 600
   ```

3. **Expected Result:**
   - All 5 agents complete their tasks
   - All 5 YAML files generated
   - Completes in < 10 minutes
   - No hanging or timeouts

4. **If it fails:**
   - Check Ollama logs: `journalctl -u ollama -f`
   - Check Python errors in output
   - Try with larger timeout: `--timeout 1200`
   - Try cloud LLM to rule out Ollama issues

---

## Stage 2: Test Hierarchical Mode (Week 1-2)

**Goal:** Identify exactly where hierarchical mode hangs

**Steps:**

1. **Restore hierarchical crew:**

   ```bash
   mv src/space_hulk_game/crew_hierarchical.py src/space_hulk_game/crew.py
   ```

2. **Run test with monitoring:**

   ```bash
   # In terminal 1: Watch logs
   tail -f run_log.txt

   # In terminal 2: Run test
   python test_crew_generation.py --mode hierarchical --timeout 600
   ```

3. **Watch for:**
   - Last task that completed successfully
   - Last log message before hang
   - Any error messages (even if swallowed)
   - CPU/memory usage patterns

4. **Expected Result:**
   - Likely times out (confirms the issue)
   - Note: WHEN it hangs tells us WHERE the problem is

---

## Stage 3: Debug the Hang (Week 2)

**Common Issues and Fixes:**

### Issue A: Manager Agent Not Delegating

**Symptoms:** Hangs immediately, no tasks start

**Fix:** Try larger model for manager

```python
# In crew.py __init__:
self.manager_llm = LLM(
    model="ollama/llama2:13b",  # Larger model
    base_url="http://localhost:11434"
)

# In crew() method:
return Crew(
    agents=regular_agents,
    tasks=self.tasks,
    process=Process.hierarchical,
    manager_llm=self.manager_llm,  # Use larger model
    verbose=True
)
```

### Issue B: Task Dependencies Deadlock

**Symptoms:** Hangs after first few tasks

**Fix:** Simplify dependencies

```python
# Remove complex evaluation tasks temporarily
@crew
def crew(self) -> Crew:
    # Only use core 5 tasks, skip evaluation tasks
    core_tasks = [
        self.GenerateOverarchingPlot(),
        self.CreateNarrativeMap(),
        self.DesignArtifactsAndPuzzles(),
        self.WriteSceneDescriptionsAndDialogue(),
        self.CreateGameMechanicsPRD()
    ]

    return Crew(
        agents=self.agents,
        tasks=core_tasks,  # Skip evaluation tasks
        process=Process.hierarchical,
        manager_agent=self.NarrativeDirectorAgent(),
        verbose=True
    )
```

### Issue C: Memory/Planning Causing Issues

**Symptoms:** Hangs randomly during execution

**Fix:** They're already commented out - keep them disabled for now

### Issue D: LLM Timeouts

**Symptoms:** Long pauses, eventually fails

**Fix:** Increase timeouts or use faster model

```python
self.llm = LLM(
    model="ollama/qwen2.5:7b",  # Smaller = faster
    base_url="http://localhost:11434",
    timeout=300  # 5 minute timeout
)
```

---

## Stage 4: Validate Fix (Week 2)

Once you've applied a fix:

```bash
# Test 3 times to ensure it's reliable
for i in {1..3}; do
    echo "=== RUN $i ==="
    python test_crew_generation.py --mode hierarchical --timeout 600
    echo ""
done
```

**Success Criteria:**

- ✅ 3/3 runs complete successfully
- ✅ All 5 outputs generated each time
- ✅ Completes in < 10 minutes
- ✅ No hangs or errors

---

## Alternative: Use Sequential Mode

If hierarchical continues to be problematic, **sequential mode is a valid solution**:

**Advantages:**

- ✅ Proven to work
- ✅ Simpler, more predictable
- ✅ Easier to debug
- ✅ Still generates all outputs

**Disadvantages:**

- ⚠️ No central quality oversight
- ⚠️ No automatic iteration/refinement
- ⚠️ Less sophisticated coordination

**To use permanently:**

```bash
# Keep sequential version
cp crew_sequential.py src/space_hulk_game/crew.py
```

This is fine! Get it working first, optimize later.

---

## Next Steps After Crew Works

Once the crew reliably generates outputs:

1. **Add basic validation** (Phase 1)
   - Check outputs exist
   - Validate YAML format
   - Check required fields

2. **Add quality metrics** (Phase 2)
   - Define what "good" looks like
   - Implement scoring
   - Add retry logic

3. **Build game engine** (Phase 3)
   - Minimal text adventure engine
   - Prove generated games are playable

4. **Polish** (Phase 4-5)
   - Documentation
   - Examples
   - Optimization

---

## Getting Help

If stuck, provide:

1. Which test failed (sequential or hierarchical)
2. Where it hung (last log message)
3. Error messages (if any)
4. Ollama version and model
5. Output from: `ollama ps` and `ollama list`

---

## Quick Reference

| Command                                              | Purpose                |
| ---------------------------------------------------- | ---------------------- |
| `ollama serve`                                       | Start Ollama server    |
| `ollama list`                                        | Check models installed |
| `ollama pull qwen2.5`                                | Download model         |
| `python test_crew_generation.py --mode sequential`   | Test simple mode       |
| `python test_crew_generation.py --mode hierarchical` | Test complex mode      |
| `python test_crew_generation.py --mode both`         | Run both tests         |
| `python test_crew_generation.py --timeout 1200`      | Use longer timeout     |

---

## Status Tracking

- [ ] Ollama installed and running
- [ ] Model downloaded (qwen2.5)
- [ ] .env file configured
- [ ] Dependencies installed
- [ ] Sequential test passes
- [ ] Hierarchical test passes (or alternative chosen)
- [ ] Root cause documented
- [ ] Solution implemented
- [ ] 3/3 validation runs pass

**Once all checked:** Ready to proceed to Phase 1 (validation)
