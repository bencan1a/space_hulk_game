# Space Hulk Game - Revised Restart Plan

## Critical Feedback Incorporated

**User Feedback:** "The biggest challenge was getting the crew to work effectively together. I could never get them to follow the hierarchy effectively - they would get stuck and become unresponsive after a brief period. So before the game system we need to prove that the basic generator system functions to produce the desired outputs."

**Response:** This is critical feedback that changes our priorities. The plan has been revised to focus on proving the crew works FIRST before building additional systems.

---

## Revised Implementation Approach

### Phase 0: Crew Validation & Debugging (NEW - HIGHEST PRIORITY)

**Duration:** 1-2 weeks  
**Goal:** Prove the basic crew can generate complete game outputs without getting stuck

#### Known Issues to Address

1. **Hierarchical Process Hanging**
   - Current issue: Agents become unresponsive in hierarchical mode
   - Likely causes:
     - Manager agent (NarrativeDirector) not delegating properly
     - Task dependencies causing deadlocks
     - Memory/planning features causing blocks
     - LLM timeouts or errors

2. **Task Dependency Problems**
   - Complex dependency chains might be causing circular waits
   - Context vs. execution dependencies may be misaligned
   - Hierarchical process may not handle dependencies as expected

3. **Agent Communication Breakdown**
   - Manager agent may not be communicating effectively with workers
   - Feedback loops (evaluation tasks) may be causing issues
   - Too many sequential gates slowing down progress

#### Debugging Strategy

**Step 1: Simplify to Prove Basic Function** (Week 1, Days 1-2)

Start with absolute minimum configuration:

```python
# Test 1: Sequential process (no hierarchy)
@crew
def crew(self) -> Crew:
    return Crew(
        agents=self.agents,
        tasks=self.tasks,
        process=Process.sequential,  # Simplest - no manager needed
        verbose=True
    )
```

**Test:** Generate a simple game with just the 5 core agents (no NarrativeDirector, no evaluation tasks)

Expected outcome: Should complete without hanging

**Step 2: Test Hierarchical Without Complex Dependencies** (Week 1, Days 3-4)

```python
# Test 2: Hierarchical with minimal tasks
@crew  
def crew(self) -> Crew:
    manager = self.NarrativeDirectorAgent()
    regular_agents = [agent for agent in self.agents 
                     if agent != manager]
    
    return Crew(
        agents=regular_agents,
        tasks=self.tasks[:3],  # Only first 3 tasks - no evaluation
        process=Process.hierarchical,
        manager_agent=manager,
        verbose=True
    )
```

**Test:** Run with only PlotMaster, NarrativeArchitect, and PuzzleSmith tasks

Expected outcome: Manager should delegate and complete these 3 tasks

**Step 3: Add Tasks Incrementally** (Week 1, Days 5-7)

Add one task at a time, testing after each addition:
1. Add CreativeScribe task → test
2. Add MechanicsGuru task → test
3. Add first evaluation task → test
4. Add remaining evaluation tasks one by one → test

Identify at which point the system starts hanging.

**Step 4: Debug Specific Hanging Point** (Week 2)

Once we identify where it hangs:

1. **Check LLM Logs**
   - Is the LLM being called?
   - Are requests timing out?
   - Are errors being silently swallowed?

2. **Check Task State**
   - Which task is active when it hangs?
   - Is the manager waiting for a response?
   - Are workers waiting for delegation?

3. **Test Different Configurations**
   - Different manager LLM (larger model for complex coordination)
   - Disable memory temporarily
   - Disable planning temporarily
   - Adjust task dependencies

4. **Add Instrumentation**
   ```python
   import time
   
   class InstrumentedCrew(Crew):
       def run(self):
           start = time.time()
           for task in self.tasks:
               task_start = time.time()
               print(f"Starting task: {task.name}")
               result = super().run_task(task)
               print(f"Completed task: {task.name} in {time.time()-task_start}s")
           print(f"Total time: {time.time()-start}s")
   ```

#### Deliverables for Phase 0

- [ ] **Working Sequential Generation**: Prove all 5 core agents can complete their tasks
- [ ] **Working Hierarchical Generation**: Prove manager can coordinate 5 agents  
- [ ] **Root Cause Analysis**: Document exactly why the system was hanging
- [ ] **Fix Implementation**: Apply fix to make hierarchical process reliable
- [ ] **Test Suite**: Automated tests that verify crew doesn't hang
- [ ] **Documentation**: Known issues and workarounds documented

#### Success Criteria

✅ **Sequential mode generates complete game** (plot → narrative → puzzles → scenes → mechanics)  
✅ **Hierarchical mode generates complete game** without hanging  
✅ **Generation completes in < 10 minutes** (with timeout detection)  
✅ **Can run 3 times in a row** without failures  
✅ **Error messages are clear** when something does go wrong

---

## Revised Phase Order

### Phase 0: Crew Validation ⭐ NEW PRIORITY (1-2 weeks)
Prove the basic generation works reliably

### Phase 1: Simple Output Validation (1 week)
Before building complex systems, add basic validation:
- Check outputs are not empty
- Check YAML is valid
- Check required fields exist

### Phase 2: Quality Metrics & Iteration (2 weeks)
Now that we know it works, add quality:
- Define quality metrics
- Implement evaluators
- Add retry logic

### Phase 3: Game Engine (2 weeks)
Validate generated content is playable:
- Build minimal text adventure engine
- Test that outputs actually work

### Phase 4: Advanced Features (2-3 weeks)
Polish and enhance:
- Better memory utilization
- Planning capabilities
- Multi-model support

### Phase 5: Production Ready (1-2 weeks)
Final polish:
- Comprehensive docs
- Example games
- Performance optimization

**Total: 9-12 weeks** (adjusted based on debugging time)

---

## Immediate Action Plan

### This Week: Crew Debugging Sprint

**Day 1: Sequential Test**
```bash
# 1. Simplify crew.py to use sequential process
# 2. Comment out all evaluation tasks
# 3. Run with simple prompt
crewai run --inputs "prompt: A simple space exploration scenario"
# 4. Monitor for completion (set 10 min timeout)
```

**Day 2: Analyze Sequential Results**
- Did it complete?
- What outputs were generated?
- Were they coherent?
- Document findings

**Day 3: Minimal Hierarchical Test**
```bash
# 1. Re-enable hierarchical process
# 2. Use only 3 tasks (no evaluation)
# 3. Run same simple prompt
# 4. Monitor carefully - where does it hang?
```

**Day 4-5: Debug Hanging Point**
- Add detailed logging
- Check LLM calls
- Test different configurations
- Identify root cause

**Day 6-7: Implement Fix**
- Apply fix based on findings
- Test thoroughly
- Document solution

---

## Alternative Approaches to Consider

If hierarchical process continues to be problematic:

### Option A: Sequential with Manual Review Points
```python
# Use sequential process but pause for review
process=Process.sequential
# Add manual checkpoints instead of hierarchical evaluation
```

**Pros:** Simpler, more reliable  
**Cons:** No automatic coordination, less sophisticated

### Option B: Simplified Hierarchy
```python
# Reduce complexity of hierarchical coordination
# Manager only coordinates, doesn't evaluate
# Fewer tasks, simpler dependencies
```

**Pros:** Keep hierarchy benefits, reduce complexity  
**Cons:** May still have issues if core problem isn't task complexity

### Option C: Hybrid Approach
```python
# Use sequential for generation
# Use hierarchical for evaluation/refinement
# Two separate crew runs
```

**Pros:** Separates concerns, more controllable  
**Cons:** More complex to manage

---

## Testing Strategy

### Automated Tests We Need

1. **Smoke Test**
   ```python
   def test_crew_completes():
       """Test that crew can complete a full run"""
       crew = SpaceHulkGame()
       with timeout(600):  # 10 minute timeout
           result = crew.kickoff({"prompt": "Simple test"})
       assert result is not None
       assert "error" not in result
   ```

2. **Output Validation Test**
   ```python
   def test_outputs_generated():
       """Test that all expected outputs exist"""
       result = generate_game("Simple test")
       assert os.path.exists("plot_outline.yaml")
       assert os.path.exists("narrative_map.yaml")
       assert os.path.exists("puzzle_design.yaml")
       assert os.path.exists("scene_texts.yaml")
       assert os.path.exists("prd_document.yaml")
   ```

3. **YAML Validation Test**
   ```python
   def test_yaml_validity():
       """Test that generated YAML is valid"""
       for file in output_files:
           with open(file) as f:
               data = yaml.safe_load(f)
           assert data is not None
   ```

---

## Success Metrics for Phase 0

Before moving to any other phase, we must achieve:

| Metric | Target | Current Status |
|--------|--------|---------------|
| Sequential generation success rate | 100% (3/3 runs) | ❓ Unknown |
| Hierarchical generation success rate | 100% (3/3 runs) | ❓ Likely 0% |
| Average generation time | < 10 minutes | ❓ Unknown (or infinite if hanging) |
| Output file completeness | 100% (5/5 files) | ❓ Unknown |
| YAML validity | 100% | ❓ Unknown |
| Documentation of issues | Complete | ❌ Not started |

---

## Risk Assessment - Updated

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Hierarchical still doesn't work** | **HIGH** | **HIGH** | Fall back to sequential + manual review |
| CrewAI framework limitations | Medium | High | Consider alternative coordination approaches |
| LLM timeouts in Ollama | Medium | Medium | Add timeout handling, cloud fallback |
| Task dependency issues | Medium | Medium | Simplify dependencies |
| Too many evaluation steps | Low | Medium | Reduce evaluation complexity |

---

## Conclusion

**The user is absolutely right.** We must prove the basic system works before adding complexity like game engines, advanced validation, or enhanced features.

**New Priority Order:**
1. ✅ Make crew generation work reliably (Phase 0)
2. ✅ Add basic validation (Phase 1)  
3. ✅ Add quality & iteration (Phase 2)
4. ✅ Build game engine (Phase 3)
5. ✅ Polish (Phase 4-5)

**Next Immediate Steps:**
1. Create test script for sequential generation
2. Run sequential test with simple prompt
3. Document results
4. Test hierarchical if sequential works
5. Debug and fix hanging issues

**Status:** Ready to begin Phase 0 debugging
**Timeline Adjustment:** Add 1-2 weeks at start for crew validation
