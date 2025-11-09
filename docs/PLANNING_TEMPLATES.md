# Planning Templates Usage Guide

**Version:** 1.0  
**Created:** November 9, 2025  
**Part of:** Phase 3 - Quality & Iteration System (Chunk 3.4)

---

## Overview

Planning templates provide structured guidance for generating different types of Space Hulk adventures. Each template defines narrative focus, required elements, tone guidelines, example scenes, and recommended mechanics for a specific game style.

Templates are automatically loaded based on keywords in your prompt, enriching the context available to AI agents during game generation.

---

## Available Templates

### 1. Space Horror (`space_horror.yaml`)

**Theme:** Gothic horror emphasizing atmosphere, isolation, and psychological dread

**Best For:**
- Oppressive, claustrophobic narratives
- Body horror and corruption themes
- Slow-burn tension and revelations
- Grimdark 40K atmosphere

**Trigger Keywords:** 
`horror`, `scary`, `terrifying`, `dread`, `fear`, `nightmare`, `corruption`

**Example Prompt:**
```
"Generate a terrifying horror scenario where a Space Marine squad investigates 
disturbing reports of corruption aboard an ancient derelict."
```

**Key Features:**
- Emphasis on atmosphere and sensory details
- Required horror elements (body, psychological, cosmic, environmental)
- Mandatory components like darkness segments and moral dilemmas
- Example scenes showcasing gothic horror tone
- Sanity and corruption mechanics

---

### 2. Mystery Investigation (`mystery_investigation.yaml`)

**Theme:** Detective/investigation focusing on clue gathering and deduction

**Best For:**
- Cerebral, puzzle-focused narratives
- Uncovering secrets and conspiracies
- Logical deduction gameplay
- Archaeological or forensic scenarios

**Trigger Keywords:**
`mystery`, `investigation`, `detective`, `clue`, `solve`, `evidence`, `discover`

**Example Prompt:**
```
"Create a mystery investigation where a tech-priest must solve the puzzle of 
why an entire ship's crew died at their stations with no signs of violence."
```

**Key Features:**
- Multiple clue types (physical, documentary, testimonial)
- Deduction mechanics and connection types
- Investigation framework with logical consistency
- Red herrings and breakthrough moments
- Quality targets ensuring fair play

---

### 3. Survival Escape (`survival_escape.yaml`)

**Theme:** Resource management and time pressure in desperate situations

**Best For:**
- High-tension escape scenarios
- Resource scarcity challenges
- Ticking clock narratives
- Difficult moral choices under pressure

**Trigger Keywords:**
`survival`, `escape`, `desperate`, `resource`, `trapped`, `flee`, `running`

**Example Prompt:**
```
"Design a desperate survival scenario where the team must escape a Space Hulk 
before the reactor goes critical, with limited oxygen and ammunition."
```

**Key Features:**
- Critical resource tracking (oxygen, ammo, medical supplies, time)
- Escalating environmental hazards
- Difficult resource allocation decisions
- Multiple path choices with trade-offs
- Pacing structure emphasizing urgency

---

### 4. Combat Focused (`combat_focused.yaml`)

**Theme:** Tactical combat and squad management in military operations

**Best For:**
- Action-oriented narratives
- Tactical decision-making
- Squad-based gameplay
- Military operations and battles

**Trigger Keywords:**
`combat`, `battle`, `tactical`, `squad`, `fight`, `warrior`, `assault`

**Example Prompt:**
```
"Create a tactical combat mission where a Space Marine squad must assault and 
clear a genestealer-infested section of the hulk."
```

**Key Features:**
- Detailed combat framework with encounter types
- Squad composition and management
- Tactical elements (cover, positioning, suppression)
- Enemy variety with different threat levels
- Mission templates and combat doctrine

---

## How Templates Work

### Automatic Detection

When you provide a prompt to the Space Hulk Game crew, the system:

1. **Analyzes** your prompt for template keywords
2. **Loads** the matching template YAML file (if found)
3. **Enriches** the agent context with template guidance
4. **Generates** content aligned with template specifications

### Template Structure

Each template contains:

```yaml
# Identification
template_name: "template_id"
template_version: "1.0"
description: "Template purpose"

# Core guidance
narrative_focus:        # Theme, atmosphere, pacing, tone
required_elements:      # Setting, beats, components
tone:                   # Adjectives, avoid, emphasis

# Examples and guidance
example_scenes:         # Opening, middle, climax examples
example_puzzles:        # Puzzle types with solutions
character_suggestions:  # Protagonist and NPC archetypes
story_structure:        # Act breakdown

# Mechanics and quality
mechanics_suggestions:  # Game systems recommendations
ending_guidelines:      # Victory, defeat, neutral endings
quality_targets:        # What makes good content

# Additional context
notes:                  # 40K lore and thematic notes
```

### Context Integration

Once loaded, template content becomes available to all agents:

- **PlotMasterAgent** uses narrative structure and story beats
- **NarrativeArchitectAgent** uses scene examples and pacing
- **PuzzleSmithAgent** uses puzzle examples and mechanics
- **CreativeScribeAgent** uses tone guidelines and sensory details
- **MechanicsGuruAgent** uses mechanics suggestions and systems

---

## Usage Examples

### Example 1: Horror Game

**Prompt:**
```bash
crewai run --inputs "prompt: A lone Tech-Priest investigates terrifying signals 
from a Space Hulk, discovering evidence of daemonic corruption in the ship's 
machine spirits."
```

**Result:** 
- Loads `space_horror.yaml`
- Generates gothic horror atmosphere
- Includes body horror and corruption themes
- Focuses on dread and isolation

---

### Example 2: Mystery Game

**Prompt:**
```bash
crewai run --inputs "prompt: Investigate the mysterious disappearance of an 
entire crew, using clues scattered throughout the derelict to piece together 
what happened in their final hours."
```

**Result:**
- Loads `mystery_investigation.yaml`
- Creates logical clue chains
- Emphasizes deduction and discovery
- Includes red herrings and revelations

---

### Example 3: Survival Game

**Prompt:**
```bash
crewai run --inputs "prompt: Escape from a collapsing Space Hulk before the 
reactor goes critical, managing limited oxygen and medical supplies while 
avoiding genestealer patrols."
```

**Result:**
- Loads `survival_escape.yaml`
- Implements resource scarcity
- Creates time pressure mechanics
- Forces difficult survival choices

---

### Example 4: Combat Game

**Prompt:**
```bash
crewai run --inputs "prompt: Lead a Deathwatch kill-team in a tactical assault 
to clear and secure a strategic sector of the hulk, coordinating squad members 
with different specialties."
```

**Result:**
- Loads `combat_focused.yaml`
- Designs tactical encounters
- Creates squad management mechanics
- Emphasizes combat strategy

---

## Combining Templates

Templates are selected based on the **first matching keyword set**. To blend styles:

### Mixed Keywords Approach

```bash
# Horror + Survival elements
"Survive a terrifying escape from a corrupted hulk section"
# Loads: space_horror (horror keyword matched first)

# Combat + Mystery elements  
"Investigate enemy positions and solve the tactical puzzle of assaulting their fortress"
# Loads: mystery_investigation (investigate matched first)
```

### Explicit Template Override

If you want a specific template regardless of keywords, explicitly name it:

```bash
"Using combat_focused template: Generate a stealth infiltration mission"
# Future feature: explicit template selection
```

---

## Template Customization

### Creating Custom Templates

You can create your own templates by:

1. Copy an existing template from `planning_templates/`
2. Modify the YAML structure to suit your needs
3. Save with a descriptive name (e.g., `stealth_mission.yaml`)
4. Add detection keywords to `crew.py` if needed

### Template Fields

**Required Fields:**
- `template_name`: Unique identifier
- `template_version`: Version tracking
- `description`: Purpose and usage

**Recommended Fields:**
- `narrative_focus`: Core thematic guidance
- `required_elements`: Must-have components
- `tone`: Mood and style guidelines
- `example_scenes`: Concrete examples for agents

**Optional Fields:**
- `mechanics_suggestions`: Game system ideas
- `quality_targets`: Quality criteria
- `notes`: Additional context

---

## Best Practices

### Prompt Engineering with Templates

**Do:**
- ✅ Use clear template keywords in your prompt
- ✅ Describe the type of experience you want
- ✅ Include specific scenario details
- ✅ Combine template style with unique elements

**Don't:**
- ❌ Mix too many conflicting keywords
- ❌ Assume templates restrict creativity
- ❌ Expect templates to replace good prompts
- ❌ Ignore the generated content's unique elements

### Template Selection Tips

1. **Choose by Core Experience**
   - What should players *feel*? → Horror
   - What should players *do*? → Combat, Investigation
   - What should players *manage*? → Survival

2. **Consider Audience**
   - Story-focused players → Mystery, Horror
   - Challenge-focused players → Survival, Combat
   - Exploration-focused players → Mystery

3. **Match 40K Themes**
   - Grimdark atmosphere → Horror
   - Military operations → Combat
   - Tech-archaeology → Mystery
   - Desperate situations → Survival

---

## Technical Details

### Template Loading Process

```python
# 1. Prompt analysis
prompt_lower = prompt.lower()

# 2. Keyword detection
template_keywords = {
    "space_horror": ["horror", "scary", "terrifying", ...],
    "mystery_investigation": ["mystery", "investigation", ...],
    # ... etc
}

# 3. Template loading
template_path = f"planning_templates/{detected_template}.yaml"
template_content = yaml.safe_load(template_file)

# 4. Context enrichment
inputs["planning_template"] = template_content
```

### Template File Location

```
space_hulk_game/
├── planning_templates/          # Template storage
│   ├── space_horror.yaml
│   ├── mystery_investigation.yaml
│   ├── survival_escape.yaml
│   └── combat_focused.yaml
├── src/space_hulk_game/
│   └── crew.py                  # Template loading logic
└── docs/
    └── PLANNING_TEMPLATES.md    # This file
```

### Integration Points

**In `crew.py` (`prepare_inputs` method):**
```python
# Template loading (automatic)
template_context = self._load_planning_template(inputs.get("prompt", ""))
if template_context:
    inputs["planning_template"] = template_context
    logger.info(f"Loaded template: {template_context.get('template_name')}")
```

**Access in Agent Tasks:**
```yaml
# In tasks.yaml, agents can reference:
description: >
  Use the planning_template guidance if provided.
  Focus on {planning_template.narrative_focus} and 
  incorporate {planning_template.required_elements}.
```

---

## Troubleshooting

### Template Not Loading

**Symptoms:** No template detected despite keywords

**Solutions:**
1. Check keyword spelling in prompt
2. Verify template file exists in `planning_templates/`
3. Review logs for detection messages
4. Try more explicit keywords

**Example:**
```bash
# Vague (may not trigger)
"Make a game about a ship"

# Clear (triggers space_horror)
"Make a terrifying horror game about a ship"
```

### Wrong Template Loaded

**Symptoms:** Unexpected template selected

**Solutions:**
1. Review keyword priority in `_load_planning_template()`
2. Use more specific keywords for desired template
3. Remove conflicting keywords from prompt

**Example:**
```bash
# Ambiguous (could load any)
"A scary mystery with combat and survival"

# Clear (loads space_horror)
"A terrifying horror experience with mystery elements"
```

### Template File Error

**Symptoms:** YAML parsing errors in logs

**Solutions:**
1. Validate YAML syntax with online validator
2. Check for special characters or encoding issues
3. Verify file is UTF-8 encoded
4. Review error message for specific line

---

## Future Enhancements

Potential improvements for template system:

1. **Explicit Template Selection**
   ```bash
   crewai run --template survival_escape --inputs "prompt: ..."
   ```

2. **Template Blending**
   ```bash
   # Automatically blend multiple templates
   "horror mystery" → 70% horror + 30% mystery
   ```

3. **User Custom Templates**
   ```bash
   # Load from user directory
   crewai run --template ~/my_templates/stealth.yaml
   ```

4. **Template Inheritance**
   ```yaml
   # In custom template
   extends: "space_horror.yaml"
   overrides:
     tone: "more_action_oriented"
   ```

5. **Template Analytics**
   - Track which templates produce best results
   - Refine templates based on quality metrics
   - A/B testing different template versions

---

## References

- **Phase 3 Documentation:** See `docs/QUALITY_METRICS.md` for quality criteria
- **Chunk Specification:** See `project-plans/restart-project/master_implementation_plan.md` Chunk 3.4
- **YAML Configuration:** See `src/space_hulk_game/config/` for agent/task configs
- **40K Lore:** Each template includes universe-specific notes

---

## Support

For questions or issues:

1. Review template YAML files for examples
2. Check logs for template loading messages
3. Refer to master implementation plan
4. Review example prompts in this guide

---

**Last Updated:** November 9, 2025  
**Contributors:** Chunk 3.4 Implementation Team  
**Status:** Production Ready
