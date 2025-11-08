# Space Hulk Game - Project Restart Plan

## Overview

This document provides a practical, actionable plan to restart the Space Hulk text-based adventure game generator project. Based on the architectural analysis, this plan focuses on completing the original vision with modern enhancements rather than starting from scratch.

---

## Current Status

### What's Working ✅
- **Architecture**: Sound hierarchical design with narrative director
- **Foundation**: Phase 1 & 2 complete (syntax fixes, hierarchical structure)
- **Technology**: CrewAI + Ollama + Python stack is solid
- **Configuration**: YAML-driven agent and task definitions
- **Testing**: Basic test infrastructure exists

### What's Missing ⚠️
- **No game engine**: Can't actually play generated games
- **No quality validation**: Outputs not validated against schemas
- **No iteration**: Planned but not implemented
- **Limited memory use**: mem0 configured but underutilized  
- **Incomplete testing**: Only basic unit tests

### Critical Path to Success
```
Phase 3 (Quality) → Game Engine → Phase 4 (Validation) → Phase 5 (Memory) → Polish
     2-3 weeks         2 weeks          2-3 weeks          2 weeks        2 weeks
```

**Total Timeline:** 10-12 weeks (part-time effort)

---

## Restart Strategy

### Philosophy: Evolution, Not Revolution

**Principles:**
1. ✅ Build on existing work
2. ✅ Focus on completing what's planned
3. ✅ Add modern enhancements where valuable
4. ✅ Prioritize working game over perfect code
5. ✅ Test early and often

**Not Doing:**
- ❌ Complete rewrites
- ❌ Framework changes  
- ❌ Architectural overhauls
- ❌ Feature creep

---

## Implementation Plan

### Phase 3: Planning & Quality System (Weeks 1-3)

**Goal:** Enable agents to plan, execute, and iterate based on quality feedback

#### Tasks

1. **Quality Metrics Definition** (Week 1)
   ```python
   # Define measurable quality criteria for each output type
   
   PlotQualityMetrics:
     - Has clear setting (yes/no)
     - Defines 2+ branching paths (count)
     - Includes at least 2 endings (count)
     - Themes clearly stated (yes/no)
     - Word count > 500 (number)
   
   NarrativeMapQualityMetrics:
     - All scenes have descriptions (completeness %)
     - All connections valid (validation)
     - No orphaned scenes (validation)
     - Min 5 scenes (count)
   
   PuzzleQualityMetrics:
     - Clear solution described (yes/no)
     - Ties to narrative (text analysis)
     - Appropriate difficulty stated (yes/no)
   ```

2. **Quality Evaluator Implementation** (Week 1-2)
   ```python
   class QualityEvaluator:
       """Evaluates agent outputs against defined metrics"""
       
       def evaluate_plot(self, plot_output: str) -> QualityScore:
           """Returns quality score and feedback"""
           pass
       
       def evaluate_narrative_map(self, map_output: dict) -> QualityScore:
           """Returns quality score and feedback"""
           pass
       
       # ... etc for each output type
   ```

3. **Retry Logic with Feedback** (Week 2)
   ```python
   @task
   def generate_with_quality_check(self, task_name: str, max_retries: int = 3):
       """Execute task with quality check and retry loop"""
       for attempt in range(max_retries):
           output = self.execute_task(task_name)
           quality = self.evaluate_quality(task_name, output)
           
           if quality.passed:
               return output
           
           # Retry with feedback
           feedback = quality.generate_feedback()
           self.provide_feedback(task_name, feedback)
       
       # Max retries reached - accept with warning
       return output
   ```

4. **Planning Templates** (Week 2-3)
   ```yaml
   # planning_templates/space_horror.yaml
   genre: "space_horror"
   narrative_focus:
     - isolation_and_despair
     - body_horror
     - survival_against_odds
   
   required_elements:
     - confined_space_setting
     - hostile_entities
     - limited_resources
     - moral_choices
   
   tone_keywords:
     - dark
     - oppressive
     - tense
     - desperate
   ```

5. **Testing** (Week 3)
   - Test quality evaluators with sample outputs
   - Test retry logic with intentionally poor outputs
   - Verify planning templates load correctly
   - Integration test: full generation with quality gates

**Deliverables:**
- ✅ Quality metrics for all output types
- ✅ Quality evaluator implementation
- ✅ Retry logic with feedback
- ✅ Planning templates for 3+ game types
- ✅ Tests for quality system

---

### Phase 3.5: Simple Game Engine (Weeks 4-5)

**Goal:** Build minimal text adventure engine to validate generated content

**Why This is Critical:**
Without a game engine, we can't verify that:
- Generated scenes are actually connected
- Puzzles are solvable
- Game flow makes sense
- Player commands work

#### Tasks

1. **Game State Model** (Week 4)
   ```python
   class GameState:
       current_scene: str
       inventory: List[str]
       visited_scenes: Set[str]
       game_flags: Dict[str, bool]
       health: int
       
   class Scene:
       id: str
       description: str
       exits: Dict[str, str]  # direction -> scene_id
       items: List[Item]
       npcs: List[NPC]
       events: List[Event]
   ```

2. **Command Parser** (Week 4)
   ```python
   class CommandParser:
       """Parse player text commands into actions"""
       
       COMMANDS = {
           'go': ['go', 'move', 'walk', 'run'],
           'take': ['take', 'get', 'grab', 'pick'],
           'use': ['use', 'activate', 'operate'],
           'look': ['look', 'examine', 'inspect'],
           'inventory': ['inventory', 'inv', 'i'],
           # ... etc
       }
       
       def parse(self, command: str) -> Action:
           """Convert text to action"""
           pass
   ```

3. **Game Engine** (Week 4-5)
   ```python
   class TextAdventureEngine:
       """Runs generated text adventure games"""
       
       def __init__(self, game_data: dict):
           self.state = GameState()
           self.scenes = self.load_scenes(game_data)
           self.parser = CommandParser()
       
       def run(self):
           """Main game loop"""
           while not self.state.game_over:
               self.display_scene()
               command = self.get_player_input()
               action = self.parser.parse(command)
               self.execute_action(action)
       
       def display_scene(self):
           """Show current scene to player"""
           pass
       
       def execute_action(self, action: Action):
           """Execute player action and update state"""
           pass
   ```

4. **Content Loader** (Week 5)
   ```python
   class ContentLoader:
       """Load generated YAML into game engine format"""
       
       def load_game(self, output_dir: str) -> GameData:
           """Load all generated files into playable game"""
           plot = load_yaml(f"{output_dir}/plot_outline.yaml")
           narrative = load_yaml(f"{output_dir}/narrative_map.yaml")
           puzzles = load_yaml(f"{output_dir}/puzzle_design.yaml")
           scenes = load_yaml(f"{output_dir}/scene_texts.yaml")
           mechanics = load_yaml(f"{output_dir}/prd_document.yaml")
           
           return self.merge_into_game_data(
               plot, narrative, puzzles, scenes, mechanics
           )
   ```

5. **Testing & Validation** (Week 5)
   ```python
   class GameValidator:
       """Validate that generated content can be played"""
       
       def validate_game(self, game_data: GameData) -> ValidationResult:
           """Check for common issues"""
           issues = []
           
           # Check all scenes are reachable
           reachable = self.find_reachable_scenes(game_data)
           if len(reachable) < len(game_data.scenes):
               issues.append("Unreachable scenes exist")
           
           # Check puzzles are solvable
           for puzzle in game_data.puzzles:
               if not self.check_solvable(puzzle):
                   issues.append(f"Puzzle {puzzle.id} may not be solvable")
           
           # Check for dead ends
           dead_ends = self.find_dead_ends(game_data)
           if dead_ends:
               issues.append(f"Dead ends found: {dead_ends}")
           
           return ValidationResult(issues)
   ```

**Deliverables:**
- ✅ Working text adventure engine
- ✅ Command parser with common verbs
- ✅ Content loader from generated YAML
- ✅ Game validator to check playability
- ✅ At least one playable demo game
- ✅ Tests for game engine

---

### Phase 4: Output Validation & Standardization (Weeks 6-8)

**Goal:** Ensure all generated outputs follow defined schemas and are valid

#### Tasks

1. **Define Pydantic Models** (Week 6)
   ```python
   from pydantic import BaseModel, Field, validator
   
   class PlotOutline(BaseModel):
       """Schema for plot outline output"""
       title: str = Field(..., min_length=1, max_length=200)
       setting: str = Field(..., min_length=50)
       themes: List[str] = Field(..., min_items=1)
       tone: str
       main_branches: List[PlotBranch] = Field(..., min_items=2)
       endings: List[Ending] = Field(..., min_items=2)
       
       @validator('main_branches')
       def validate_branches(cls, v):
           if len(v) < 2:
               raise ValueError("Must have at least 2 branching paths")
           return v
   
   class NarrativeMap(BaseModel):
       """Schema for narrative map output"""
       start_scene: str
       scenes: Dict[str, Scene] = Field(..., min_items=5)
       
       @validator('scenes')
       def validate_scenes_connected(cls, v, values):
           # Check all referenced scenes exist
           # Check no orphaned scenes
           # Check start_scene exists
           pass
   
   # ... models for Puzzle, Scene, NPC, Item, etc.
   ```

2. **Schema Validators** (Week 6-7)
   ```python
   class OutputValidator:
       """Validate agent outputs against schemas"""
       
       def validate_plot(self, raw_output: str) -> ValidationResult:
           """Parse and validate plot outline"""
           try:
               data = yaml.safe_load(raw_output)
               plot = PlotOutline(**data)
               return ValidationResult(valid=True, data=plot)
           except Exception as e:
               return ValidationResult(
                   valid=False,
                   errors=[str(e)],
                   data=None
               )
   ```

3. **Auto-Correction** (Week 7)
   ```python
   class OutputCorrector:
       """Attempt to auto-correct common issues"""
       
       def correct_plot(self, invalid_plot: dict) -> dict:
           """Fix common plot outline issues"""
           # Add missing required fields with defaults
           # Fix formatting issues
           # Validate and return
           pass
   ```

4. **Integration with Tasks** (Week 7-8)
   ```python
   @task
   def GenerateOverarchingPlot(self) -> Task:
       """Generate plot with validation"""
       task = Task(config=self.tasks_config["GenerateOverarchingPlot"])
       
       # Add post-execution hook for validation
       @task.callback
       def validate_output(output):
           result = self.validator.validate_plot(output)
           if not result.valid:
               # Try auto-correction
               corrected = self.corrector.correct_plot(output)
               result = self.validator.validate_plot(corrected)
               
               if not result.valid:
                   # Log issues and continue with best effort
                   logger.warning(f"Plot validation failed: {result.errors}")
           
           return result.data
       
       return task
   ```

5. **Testing** (Week 8)
   - Test all Pydantic models with valid inputs
   - Test validators with invalid inputs
   - Test auto-correction with common errors
   - Integration test: full generation with validation

**Deliverables:**
- ✅ Pydantic models for all output types
- ✅ Validators for all outputs
- ✅ Auto-correction for common issues
- ✅ Integration with agent tasks
- ✅ Tests for validation system

---

### Phase 5: Enhanced Memory System (Weeks 9-10)

**Goal:** Fully utilize mem0 for cross-agent collaboration and learning

#### Tasks

1. **Memory Schema Design** (Week 9)
   ```python
   class MemorySchema:
       """Define what to store in mem0"""
       
       NARRATIVE_CONTEXT = {
           'themes': List[str],
           'tone': str,
           'setting': str,
           'constraints': List[str]
       }
       
       DESIGN_DECISIONS = {
           'decision': str,
           'rationale': str,
           'agent': str,
           'timestamp': datetime
       }
       
       QUALITY_FEEDBACK = {
           'component': str,
           'issue': str,
           'suggestion': str,
           'resolved': bool
       }
       
       GENERATED_CONTENT = {
           'type': str,  # 'scene', 'puzzle', 'npc', etc.
           'id': str,
           'summary': str,
           'tags': List[str]
       }
   ```

2. **Memory Operations** (Week 9)
   ```python
   class MemoryManager:
       """Manage mem0 operations for agents"""
       
       def __init__(self):
           self.client = MemoryClient()
       
       def store_narrative_context(self, context: dict):
           """Store narrative guidelines for all agents"""
           messages = [{
               "role": "system",
               "content": f"Narrative context: {context}"
           }]
           self.client.add(messages, user_id="space_hulk_game")
       
       def store_design_decision(self, decision: dict):
           """Store design decision with rationale"""
           pass
       
       def get_relevant_context(self, query: str) -> List[dict]:
           """Retrieve relevant context for current task"""
           return self.client.search(query, user_id="space_hulk_game")
       
       def get_feedback_history(self, component: str) -> List[dict]:
           """Get past feedback for similar components"""
           pass
   ```

3. **Agent Integration** (Week 9-10)
   ```python
   @agent
   def PlotMasterAgent(self) -> Agent:
       """Enhanced with memory access"""
       agent = Agent(
           config=self.agents_config["PlotMasterAgent"],
           llm=self.llm,
           verbose=True
       )
       
       # Add memory access tool
       @agent.tool
       def access_memory(query: str) -> str:
           """Access shared memory for context"""
           context = self.memory.get_relevant_context(query)
           return self.format_context(context)
       
       return agent
   ```

4. **Cross-Session Learning** (Week 10)
   ```python
   class LearningSystem:
       """Enable improvement across game generations"""
       
       def record_generation_metrics(self, game_id: str, metrics: dict):
           """Record what worked well"""
           self.memory.store_design_decision({
               'game_id': game_id,
               'quality_score': metrics['quality_score'],
               'user_rating': metrics.get('user_rating'),
               'successful_patterns': metrics['patterns']
           })
       
       def get_successful_patterns(self, game_type: str) -> List[dict]:
           """Retrieve patterns that worked in past"""
           return self.memory.search(
               f"successful patterns for {game_type}"
           )
   ```

5. **Testing** (Week 10)
   - Test memory storage and retrieval
   - Test context sharing between agents
   - Test cross-session persistence
   - Integration test: full generation using memory

**Deliverables:**
- ✅ Memory schema definition
- ✅ Memory manager implementation
- ✅ Agent integration with memory access
- ✅ Cross-session learning capability
- ✅ Tests for memory system

---

### Phase 6: Production Polish (Weeks 11-12)

**Goal:** Make the system production-ready with docs, monitoring, and examples

#### Tasks

1. **Structured Logging** (Week 11)
   ```python
   import structlog
   
   logger = structlog.get_logger()
   
   logger.info(
       "task_completed",
       task_name="GenerateOverarchingPlot",
       duration_seconds=45.2,
       quality_score=8.5,
       retry_count=1
   )
   ```

2. **Metrics Collection** (Week 11)
   ```python
   class MetricsCollector:
       """Collect metrics for monitoring and improvement"""
       
       def record_task_execution(
           self,
           task_name: str,
           duration: float,
           token_count: int,
           quality_score: float,
           retry_count: int
       ):
           """Record task metrics"""
           pass
       
       def get_summary(self, time_range: str) -> dict:
           """Get summary statistics"""
           pass
   ```

3. **Example Games** (Week 11-12)
   ```bash
   examples/
     ├── space_horror.yaml          # Classic space hulk horror
     ├── mystery_investigation.yaml # Detective-style adventure
     └── survival_escape.yaml       # Time-pressure escape
   ```

4. **User Documentation** (Week 12)
   ```markdown
   # User Guide
   
   ## Quick Start
   1. Install dependencies
   2. Configure Ollama
   3. Generate your first game
   4. Play the game
   
   ## Advanced Usage
   - Custom planning templates
   - Model selection
   - Quality tuning
   - Memory management
   
   ## Troubleshooting
   - Common errors
   - Performance tips
   - Model selection guide
   ```

5. **Developer Documentation** (Week 12)
   ```markdown
   # Developer Guide
   
   ## Architecture Overview
   ## Adding New Agents
   ## Creating New Tasks
   ## Testing Guidelines
   ## Contributing
   ```

6. **Performance Optimization** (Week 12)
   - Profile slow operations
   - Optimize LLM calls
   - Cache where appropriate
   - Parallel execution where possible

**Deliverables:**
- ✅ Structured logging throughout
- ✅ Metrics collection and reporting
- ✅ 3+ example games with templates
- ✅ Comprehensive user documentation
- ✅ Developer documentation
- ✅ Performance optimizations
- ✅ Production-ready codebase

---

## Success Criteria

### Phase 3 Complete
- [ ] Quality metrics defined for all outputs
- [ ] Quality evaluators working and tested
- [ ] Retry logic with feedback implemented
- [ ] 3+ planning templates created
- [ ] Can generate game with automatic quality improvement

### Phase 3.5 Complete
- [ ] Text adventure engine works
- [ ] Can load generated YAML files
- [ ] Can play generated games via CLI
- [ ] Game validator catches common issues
- [ ] At least 1 complete playable demo

### Phase 4 Complete
- [ ] Pydantic models for all output types
- [ ] All outputs validated against schemas
- [ ] Auto-correction handles common errors
- [ ] 95%+ of generations produce valid output

### Phase 5 Complete
- [ ] mem0 fully utilized for collaboration
- [ ] Agents share context via memory
- [ ] Cross-session learning works
- [ ] Quality improves over multiple runs

### Phase 6 Complete
- [ ] Production-ready codebase
- [ ] Comprehensive documentation
- [ ] 3+ example games
- [ ] Metrics and monitoring in place
- [ ] Performance optimized

### Overall Project Success
- [ ] Can generate playable games from simple prompts
- [ ] Games are narratively coherent
- [ ] Puzzles are solvable
- [ ] Quality consistently good (8+/10)
- [ ] Generation time < 5 minutes
- [ ] System is maintainable and documented

---

## Weekly Milestones

| Week | Focus | Key Deliverable |
|------|-------|----------------|
| 1 | Quality metrics & evaluators | Quality system working |
| 2 | Retry logic & planning | Iteration loop complete |
| 3 | Testing & refinement | Phase 3 done |
| 4 | Game engine core | Basic engine works |
| 5 | Content loading & validation | Can play generated games |
| 6 | Pydantic models & validators | Validation system complete |
| 7 | Auto-correction & integration | Robust output validation |
| 8 | Testing & refinement | Phase 4 done |
| 9 | Memory schema & operations | Memory system working |
| 10 | Agent integration & learning | Phase 5 done |
| 11 | Logging, metrics, examples | Production features |
| 12 | Documentation & polish | Project complete |

---

## Risk Mitigation

### Risk: Generated content quality varies widely
**Mitigation:**
- Quality metrics with thresholds
- Automatic retry with feedback
- Better prompts and examples
- Model tuning for specific tasks

### Risk: Game engine too complex
**Mitigation:**
- Start with absolute minimum (parser + state)
- Defer complex features (combat, inventory)
- Focus on proving content is valid
- Can enhance later

### Risk: Ollama model limitations
**Mitigation:**
- Support multiple models
- Allow cloud fallback for complex tasks
- Profile which tasks need which models
- Provide model selection guidance

### Risk: Scope creep
**Mitigation:**
- Strict phase definitions
- MVP mindset - working > perfect
- Defer nice-to-haves
- Focus on core value: playable games

### Risk: Timeline overruns
**Mitigation:**
- Buffer time in estimates
- Prioritize phases clearly
- Can ship after Phase 4 if needed
- Phases 5-6 are enhancements

---

## Resource Requirements

### Development Time
- **Total:** 10-12 weeks
- **Effort:** 10-15 hours/week
- **Peak:** Weeks 4-5 (game engine) and 11-12 (polish)

### Compute Resources
- **Local:** Ollama with 8GB+ VRAM recommended
- **Cloud (optional):** API access for cloud models (fallback)
- **Storage:** Minimal (~100MB for generated games)

### External Dependencies
- CrewAI (current version)
- Ollama (latest)
- mem0 (current version)
- Pydantic v2
- PyYAML
- structlog (new)

---

## Next Actions

### Immediate (This Week)
1. ✅ Review and approve architectural analysis
2. ✅ Review and approve this restart plan
3. [ ] Set up development environment
4. [ ] Create Phase 3 branch
5. [ ] Begin quality metrics definition

### Week 1
1. [ ] Define quality metrics for all output types
2. [ ] Implement basic quality evaluator
3. [ ] Write tests for quality evaluation
4. [ ] Document quality criteria

### Month 1 Goal
- [ ] Phase 3 complete
- [ ] Basic game engine working
- [ ] Can generate and play simple game

### Month 2 Goal
- [ ] Phase 4 complete
- [ ] Phase 5 complete
- [ ] Multiple example games working

### Month 3 Goal
- [ ] Phase 6 complete
- [ ] Production-ready release
- [ ] Documentation complete

---

## Communication Plan

### Weekly Updates
- Progress on current phase
- Blockers and issues
- Next week's goals
- Demos of new features

### Monthly Reviews
- Overall progress vs. timeline
- Quality of generated games
- Technical debt assessment
- Plan adjustments if needed

### Phase Completions
- Demo of phase deliverables
- Documentation review
- Decision: continue or adjust

---

## Conclusion

This plan provides a clear, practical path to restarting and completing the Space Hulk game generator project. By building on the solid foundation already in place and focusing on completing the original vision with modern enhancements, we can deliver a working, production-ready system in 10-12 weeks.

The key insight: **The architecture is sound. The technology is good. We just need to finish what was started and add the missing piece (game engine) to prove it works.**

**Status:** Ready to begin Phase 3
**Next Step:** Set up development environment and start quality metrics definition
**Expected Completion:** 10-12 weeks from start
