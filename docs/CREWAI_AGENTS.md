# Space Hulk Game - CrewAI Agents

## Overview

The Space Hulk Game uses **7 specialized AI agents** working together through the CrewAI framework to create complete text-based adventure games. These agents are organized into two categories: **Content Creation Agents** and **Quality Assurance Agents**.

This document provides detailed information about each agent, their responsibilities, and how they collaborate.

---

## Agent Architecture

### Content Creation Agents (5)

These agents are responsible for generating the actual game content - plot, scenes, puzzles, writing, and mechanics.

#### 1. Plot Master Agent

**Role**: Lead Plot Designer

**Primary Responsibility**: Create the narrative foundation and branching plot structure

**Key Tasks**:
- Develop overarching story concept
- Design branching narrative paths
- Create multiple endings
- Establish themes and tone
- Define key story moments

**Expertise**:
- Interactive fiction storytelling
- Multi-threaded plots
- Moral dilemmas and player choice
- Story arc design
- Branching narrative structure

**Output**: `plot_outline.yaml` - Comprehensive plot structure with all major branches and endings

**Example Work Product**:
```yaml
plot_outline:
  title: "Derelict in the Void"
  setting: "Abandoned Imperial vessel drifting in the Warp"
  themes: ["isolation", "duty", "corruption"]
  main_branches:
    - exploration_path: "Cautious investigation"
    - combat_path: "Direct confrontation"
    - stealth_path: "Avoid detection"
  endings:
    - escape: "Successfully evacuate"
    - sacrifice: "Destroy vessel to save others"
    - corruption: "Succumb to Chaos influence"
```

---

#### 2. Narrative Architect Agent

**Role**: Narrative Mapper

**Primary Responsibility**: Transform plot structure into detailed, connected scenes

**Key Tasks**:
- Map scenes and locations
- Define scene connections and progression
- Establish navigation paths
- Design decision points
- Create scene flow diagrams

**Expertise**:
- Scene structure and pacing
- Spatial design for text adventures
- Logical progression flow
- Branch point placement
- Connection mapping

**Output**: `narrative_map.yaml` - Detailed scene structure with all connections

**Example Work Product**:
```yaml
narrative_map:
  start_scene: "docking_bay"
  scenes:
    docking_bay:
      description: "Massive abandoned docking bay"
      connections:
        - target: "main_corridor"
          condition: null
        - target: "control_room"
          condition: "has_keycard"
      items: ["flashlight"]
      npcs: []
```

---

#### 3. Puzzle Smith Agent

**Role**: Puzzle and Artifact Designer

**Primary Responsibility**: Design all interactive game elements

**Key Tasks**:
- Create logic puzzles
- Design environmental challenges
- Define items and artifacts
- Create NPC characters
- Design monster encounters

**Expertise**:
- Puzzle design and balance
- Item interaction systems
- NPC personality and dialogue
- Enemy design and tactics
- Challenge difficulty tuning

**Output**: `puzzle_design.yaml` - Complete catalog of puzzles, items, NPCs, and monsters

**Example Work Product**:
```yaml
puzzles:
  - name: "Engine Repair Sequence"
    type: "item_combination"
    requires: ["tool_kit", "spare_fuse"]
    solution: "Repair engine control panel"
    
artifacts:
  - name: "Auspex Scanner"
    function: "Detect hidden passages"
    
npcs:
  - name: "Servitor Unit 7"
    personality: "Monotone, helpful"
    
monsters:
  - name: "Genestealer"
    type: "melee_ambush"
    tactics: "Strike from darkness"
```

---

#### 4. Creative Scribe Agent

**Role**: Creative Writer

**Primary Responsibility**: Write all descriptive text and dialogue

**Key Tasks**:
- Write vivid scene descriptions
- Create atmospheric prose
- Write character dialogue
- Craft item descriptions
- Develop narrative voice

**Expertise**:
- Descriptive writing
- Atmospheric prose
- Dialogue crafting
- Character voice
- Gothic horror tone
- Warhammer 40K style

**Output**: `scene_texts.yaml` - All written content for scenes and dialogue

**Example Work Product**:
```yaml
scenes:
  docking_bay:
    description: |
      The massive entrance hatch groans open, revealing a cavernous docking bay.
      Emergency lights flicker weakly in the stale air, casting long shadows
      across scattered cargo containers. The silence is oppressive.
    
    examination: |
      Signs of hasty evacuation are everywhere. Cargo containers lie overturned,
      their contents spilled. Most escape pods are missing. Something went very
      wrong here.
      
dialogue:
  servitor_unit_7:
    greeting: "QUERY. STATE. PURPOSE."
    help: "DIRECTIVE. ASSIST. PERSONNEL. MAINTENANCE. PROTOCOLS. ACTIVE."
```

---

#### 5. Mechanics Guru Agent

**Role**: Game Mechanics & PRD Specialist

**Primary Responsibility**: Define all game systems and create technical documentation

**Key Tasks**:
- Design game mechanics
- Define rule systems
- Balance combat
- Create skill systems
- Write technical documentation (PRD)

**Expertise**:
- RPG system design
- Game balance
- Combat mechanics
- Resource management
- Technical documentation

**Output**: `prd_document.yaml` - Product Requirements Document defining all game systems

**Example Work Product**:
```yaml
game_mechanics:
  exploration:
    movement: "Cardinal directions or explicit exits"
    perception: "'examine' command reveals details"
    
  inventory:
    capacity: 10
    commands: ["take", "drop", "use", "examine"]
    
  combat:
    initiative: "Player acts first"
    actions: ["attack", "defend", "use_item", "flee"]
    health: "Tracked 0-100, death at 0"
    
  progression:
    save_system: "Auto-save at scene transitions"
    difficulty: "Fixed, no adjustable settings"
```

---

### Quality Assurance Agents (2)

These agents validate that the content meets quality standards and integrates properly.

#### 6. Narrative Director Agent

**Role**: Narrative Director

**Primary Responsibility**: Ensure narrative quality and thematic consistency

**Key Tasks**:
- Evaluate plot quality and depth
- Assess narrative pacing
- Validate thematic consistency
- Review writing quality
- Check emotional impact

**Expertise**:
- Narrative craft and structure
- Thematic development
- Story pacing
- Writing quality assessment
- Emotional resonance
- Player experience

**Focus Areas**:
- Story quality (not technical validation)
- Thematic coherence
- Pacing and flow
- Writing craft
- Emotional engagement

**Tasks Performed**:
1. **EvaluateNarrativeFoundation** - Review plot quality
2. **EvaluateNarrativeStructure** - Assess scene flow and pacing
3. **EvaluateSceneQuality** - Review writing and dialogue quality

**NOT Responsible For**:
- Technical validation
- Game balance
- Puzzle solvability
- System integration

---

#### 7. Game Integration Agent

**Role**: Game Integration Specialist

**Primary Responsibility**: Ensure technical coherence and playability

**Key Tasks**:
- Validate puzzle solvability
- Check item functionality
- Verify scene connections
- Test game balance
- Ensure completability

**Expertise**:
- Technical validation
- System integration
- Game balance testing
- Playability analysis
- Quality assurance

**Focus Areas**:
- Technical soundness (not narrative quality)
- Puzzle solvability
- System integration
- Game balance
- Player progression

**Tasks Performed**:
1. **ValidatePuzzleIntegration** - Check puzzles, items, NPCs, monsters work correctly
2. **ValidateMechanicsIntegration** - Verify game mechanics are sound and balanced
3. **FinalGameIntegration** - Comprehensive playability check

**Validation Checklist**:
- ✓ All puzzles solvable with available items
- ✓ No dead ends or impossible situations
- ✓ Scenes connect properly
- ✓ Items function within game systems
- ✓ Combat encounters are balanced
- ✓ Game completable from start to finish
- ✓ Mechanics work consistently
- ✓ No rule conflicts

---

## Agent Collaboration

### Workflow Overview

```
1. Plot Master creates narrative foundation
   ↓
2. Narrative Director evaluates story quality
   ↓
3. Narrative Architect maps scenes and connections
   ↓
4. Narrative Director evaluates structure
   ↓
5. Content Agents work in parallel:
   - Puzzle Smith creates interactive elements
   - Creative Scribe writes descriptions/dialogue
   - Mechanics Guru defines game systems
   ↓
6. Quality Agents validate in parallel:
   - Narrative Director evaluates writing quality
   - Game Integration validates technical integration
   ↓
7. Game Integration performs final playability check
   ↓
8. Complete game ready for play
```

### Separation of Concerns

**Narrative Quality (Narrative Director)**:
- Does the story engage emotionally?
- Is the pacing effective?
- Are themes well-developed?
- Is the writing compelling?
- Does dialogue sound authentic?

**Technical Quality (Game Integration)**:
- Can players actually complete the game?
- Are puzzles solvable?
- Do systems work together?
- Is the game balanced?
- Are there dead ends or bugs?

This separation ensures both **story excellence** and **technical soundness**.

---

## Process Modes

### Sequential Mode (Default)

All 7 agents work as peers in a defined order:

```
PlotMaster → NarrativeDirector → NarrativeArchitect → NarrativeDirector →
PuzzleSmith → CreativeScribe → MechanicsGuru → NarrativeDirector →
GameIntegration → GameIntegration → GameIntegration
```

**Advantages**:
- Simple and predictable
- Easy to debug
- No coordination overhead
- Reliable execution

**Use When**:
- First time running the system
- Testing changes
- Debugging issues
- Want consistent behavior

### Hierarchical Mode (Advanced)

NarrativeDirector acts as manager, delegating to worker agents:

```
            NarrativeDirector (Manager)
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
Workers:      Workers:        Workers:
PlotMaster    PuzzleSmith    MechanicsGuru
NarrativeArch CreativeScribe GameIntegration
```

**Advantages**:
- Can request revisions
- Iterative refinement
- Dynamic task delegation
- Quality-driven process

**Use When**:
- Need high quality output
- Want iterative improvement
- Sequential mode proven stable
- Have time for multiple passes

---

## Agent Configuration

All agents are defined in `/src/space_hulk_game/config/agents.yaml`:

```yaml
AgentName:
  role: "Human-readable role"
  goal: "What the agent aims to achieve"
  description: "Brief description"
  backstory: >
    Multi-line backstory explaining the agent's
    expertise and experience.
  allow_delegation: true/false
  verbose: true
```

### Key Parameters

- **role**: Agent's job title (shown in logs)
- **goal**: Specific objective the agent pursues
- **description**: One-line summary
- **backstory**: Context about expertise (helps LLM understand agent)
- **allow_delegation**: Enable for manager agents (hierarchical mode)
- **verbose**: Enable detailed logging

---

## Task Assignment

Tasks are defined in `/src/space_hulk_game/config/tasks.yaml` and assigned to specific agents:

| Task | Agent | Type |
|------|-------|------|
| GenerateOverarchingPlot | PlotMasterAgent | Generation |
| EvaluateNarrativeFoundation | NarrativeDirectorAgent | Quality |
| CreateNarrativeMap | NarrativeArchitectAgent | Generation |
| EvaluateNarrativeStructure | NarrativeDirectorAgent | Quality |
| DesignArtifactsAndPuzzles | PuzzleSmithAgent | Generation |
| WriteSceneDescriptionsAndDialogue | CreativeScribeAgent | Generation |
| CreateGameMechanicsPRD | MechanicsGuruAgent | Generation |
| EvaluateSceneQuality | NarrativeDirectorAgent | Quality |
| ValidatePuzzleIntegration | GameIntegrationAgent | Validation |
| ValidateMechanicsIntegration | GameIntegrationAgent | Validation |
| FinalGameIntegration | GameIntegrationAgent | Validation |

---

## Workload Balance

| Agent | Tasks | % of Total | Type |
|-------|-------|------------|------|
| PlotMasterAgent | 1 | 9% | Generation |
| NarrativeArchitectAgent | 1 | 9% | Generation |
| PuzzleSmithAgent | 1 | 9% | Generation |
| CreativeScribeAgent | 1 | 9% | Generation |
| MechanicsGuruAgent | 1 | 9% | Generation |
| NarrativeDirectorAgent | 3 | 27% | Quality |
| GameIntegrationAgent | 3 | 27% | Validation |

This balanced distribution ensures:
- No single agent is overwhelmed
- Specialists focus on their expertise
- Both narrative and technical quality are prioritized
- Work can proceed efficiently

---

## Future Enhancements

### Potential Additional Agents

If the system proves successful and higher specialization is needed:

1. **Environmental Puzzle Agent** - Logic puzzles, environmental challenges
2. **Enemy Designer Agent** - Monsters, combat encounters, tactics
3. **Artifact Curator Agent** - Items, equipment, collectibles
4. **Dialogue Specialist Agent** - Conversations, branching dialogue trees
5. **Lore Keeper Agent** - Warhammer 40K authenticity and consistency

These would increase total agents to 11-12 with even more focused specializations.

---

## Best Practices

### When Adding New Agents

1. **Define clear scope** - Each agent should have distinct responsibility
2. **Avoid overlap** - Don't duplicate existing agent expertise
3. **Balance workload** - Aim for even task distribution
4. **Separate concerns** - Keep generation separate from validation
5. **Update documentation** - Keep this file current

### When Modifying Agent Roles

1. **Check task assignments** - Update tasks.yaml to match
2. **Update backstory** - Ensure it reflects current role
3. **Test both modes** - Verify sequential and hierarchical work
4. **Update tests** - Reflect changes in test files
5. **Document changes** - Update this file and comments

---

## Troubleshooting

### Agent Not Working

1. Check YAML syntax in `agents.yaml`
2. Verify agent name matches method in `crew.py`
3. Check LLM configuration (Ollama running?)
4. Review logs for errors
5. Test in sequential mode first

### Tasks Not Executing

1. Verify task name matches method in `crew.py`
2. Check agent assignment in `tasks.yaml`
3. Review task dependencies (no circular deps)
4. Check context references are valid
5. Verify agent exists in `agents.yaml`

### Poor Quality Output

1. Review agent backstory (is expertise clear?)
2. Check task description (is goal specific?)
3. Review expected_output (is format defined?)
4. Consider adding quality validation task
5. Try hierarchical mode for iterative improvement

---

## Related Documentation

- **SETUP.md** - Installation and configuration
- **QUICKSTART.md** - Quick start guide
- **CONTRIBUTING.md** - Development guidelines
- **crewai-api-reference.md** - CrewAI framework reference

---

## Summary

The Space Hulk Game uses **7 specialized agents** organized into:

**Content Creation (5 agents)**:
1. Plot Master - Narrative foundation
2. Narrative Architect - Scene structure
3. Puzzle Smith - Interactive elements
4. Creative Scribe - Descriptive writing
5. Mechanics Guru - Game systems

**Quality Assurance (2 agents)**:
6. Narrative Director - Story quality
7. Game Integration - Technical validation

This architecture ensures both **narrative excellence** and **technical soundness** through dedicated specialists working in harmony.
