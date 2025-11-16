# Playing Space Hulk Games

## Quick Start

Welcome to the Space Hulk text adventure game! This guide will help you get started and master the game mechanics.

### Launching the Game

After installing the package, you can launch the game in several ways:

```bash
# Method 1: Using the installed command
demo_game

# Method 2: Alternative command
play_game

# Method 3: Using Python module
python -m space_hulk_game.demo_game

# Method 4: With custom game directory
demo_game --game-dir path/to/game

# Method 5: With verbose logging (for debugging)
demo_game --verbose
```

### First Time Playing

1. **Launch the game** using one of the methods above
2. **Read the title screen** - soak in the grimdark atmosphere!
3. **Press Enter** to continue to the main menu
4. **Select "New Game"** (option 1)
5. **Start playing!**

## Main Menu

When you start the game, you'll see the main menu with these options:

```
1. New Game     - Start a fresh adventure
2. Load Game    - Continue a saved game
3. Help         - View command reference
4. Quit         - Exit the game
```

## Basic Commands

### Movement

Move between scenes using directional commands:

```
go north        - Move to the north
go south        - Move to the south
go east         - Move to the east
go west         - Move to the west
go up           - Go upstairs or climb up
go down         - Go downstairs or climb down

# Shortcuts
north           - Same as "go north"
n               - Short form for north
s, e, w         - Shortcuts for other directions
```

**Tips:**

- Always `look` when entering a new room to see available exits
- Some exits may be locked and require keys or items
- Pay attention to scene descriptions for clues about hidden exits

### Observation

Examine your surroundings:

```
look            - Look around the current scene
look at <item>  - Examine a specific item
examine <thing> - Closely inspect something
```

**Examples:**

```
look
look at key
look at door
examine terminal
```

### Inventory Management

Manage your equipment and items:

```
inventory       - View your current inventory
i               - Short form for inventory
take <item>     - Pick up an item
drop <item>     - Drop an item from inventory
```

**Examples:**

```
take key
take power sword
drop torch
i
```

**Tips:**

- Some items are too heavy or important to drop
- Check your inventory regularly
- Items may have multiple uses

### Using Items

Interact with items in the game world:

```
use <item>                  - Use an item (context-dependent)
use <item> on <target>      - Use an item on something specific
use <item> with <target>    - Combine items
```

**Examples:**

```
use key
use key on door
use medikit
use power cell on terminal
```

**Tips:**

- Read item descriptions carefully for usage hints
- Some items work automatically when in inventory
- Try different combinations if stuck

### Talking to NPCs

Interact with non-player characters:

```
talk to <npc>           - Start a conversation
talk to <npc> about <topic>  - Ask about specific topic
ask <npc> about <topic>      - Alternative syntax
```

**Examples:**

```
talk to sergeant
talk to tech priest about door
ask marine about mission
```

**Tips:**

- NPCs may provide crucial information or items
- Some conversations unlock new areas or quests
- Talk to everyone you meet!

### Game Control

Manage your game session:

```
help            - Display help information
save            - Save your current progress
quit            - Quit the game (with confirmation)
exit            - Same as quit
```

## Advanced Gameplay

### Understanding the HUD

The game provides information through text descriptions:

- **Scene descriptions** appear in cyan
- **Item descriptions** appear in green
- **NPC dialogue** appears in yellow
- **Warnings/errors** appear in red
- **Success messages** appear in bright green
- **System messages** appear in magenta

### Save System

#### Saving Your Game

1. Type `save` during gameplay
2. Enter a name for your save (e.g., "before_big_battle")
3. Confirm the save

**Save Tips:**

- Save frequently, especially before dangerous situations
- Use descriptive save names (e.g., "engineering_deck_cleared")
- You can have multiple save files
- Saves persist between game sessions

#### Loading a Game

1. Select "Load Game" from the main menu
2. See a list of available saves with timestamps
3. Enter the number or name of the save you want to load
4. Continue from where you left off

### Game Flags and Variables

The game tracks your progress through **flags** and **variables**:

#### Flags (Boolean States)

- `door_unlocked` - A specific door is unlocked
- `npc_helped` - You've assisted an NPC
- `boss_defeated` - You've defeated a boss enemy

#### Variables (Numeric/String Values)

- `health` - Your current health
- `armor` - Your armor rating
- `quest_stage` - Progress in a quest

You don't interact with these directly, but they affect what you can do.

### Victory and Defeat

#### Winning the Game

Win conditions vary by game but typically include:

- Escaping the Space Hulk
- Completing all objectives
- Defeating the final boss
- Retrieving the MacGuffin

**Signs you're close to winning:**

- NPCs mention "one final task"
- You've explored all areas
- All major puzzles are solved

#### Losing the Game

Defeat conditions may include:

- Health reaches zero
- Critical failure in puzzle
- Time running out (if timed)

**When you lose:**

- Game displays the defeat message
- You can load a save to try again
- Learn from mistakes!

### Puzzle-Solving Strategies

#### General Approach

1. **Explore thoroughly**
   - Check every scene
   - Examine all items
   - Talk to all NPCs

2. **Take notes**
   - Remember NPC hints
   - Track locked doors and requirements
   - Map the game world mentally (or on paper!)

3. **Experiment safely**
   - Save before trying risky actions
   - Try item combinations
   - Test different dialogue options

#### Common Puzzle Types

**Key and Lock Puzzles**

- Find the key item
- Use it on the locked exit/container
- Remember: not all keys are physical objects!

**Information Gathering**

- Talk to NPCs for clues
- Read item descriptions
- Piece together the story

**Sequence Puzzles**

- Actions must be performed in order
- Pay attention to sequence clues
- Trial and error with saves

**Resource Management**

- Limited items or uses
- Choose wisely what to use where
- Some items have multiple uses

## Tips for New Players

### General Tips

1. **Read everything** - Descriptions often contain vital clues
2. **Save often** - Before major decisions or risky actions
3. **Explore systematically** - Check every scene thoroughly
4. **Talk to everyone** - NPCs are your best source of information
5. **Examine items** - Understanding items is key to solving puzzles

### Combat Tips (if applicable)

1. **Use armor and weapons** - Equipment matters
2. **Healing items** - Use them strategically
3. **Retreat when needed** - Sometimes running is wise
4. **Target weaknesses** - Read enemy descriptions

### Efficiency Tips

1. **Use shortcuts** - `n` instead of `go north`, `i` instead of `inventory`
2. **Tab completion** - Many terminals support tab completion
3. **Command history** - Use up arrow to repeat previous commands
4. **Save states** - Create saves at key decision points

## Troubleshooting

### Common Issues

#### "I don't understand that command"

**Cause:** Command not recognized or malformed

**Solutions:**

- Type `help` to see available commands
- Check spelling and syntax
- Try simpler phrasing (e.g., "north" instead of "walk to the north")
- Use `look` to see what's available in the scene

#### "You can't go that way"

**Cause:** Invalid exit or locked door

**Solutions:**

- Type `look` to see available exits
- Check if the exit is locked
- Look for keys or items to unlock it
- Some paths become available later in the game

#### "You don't have that item"

**Cause:** Item not in inventory

**Solutions:**

- Type `inventory` to check what you have
- Go back to where you saw the item
- The item might be in a different scene
- Some items must be unlocked first

#### "Nothing happens"

**Cause:** Action not applicable in current context

**Solutions:**

- Read the scene description again
- Try a different approach
- Some items only work in specific locations
- Talk to NPCs for hints

### Getting Unstuck

If you're stuck and don't know what to do:

1. **Review your objectives**
   - What were you trying to accomplish?
   - What clues have you found?

2. **Revisit all scenes**
   - Did you miss something?
   - Has anything changed since you were last there?

3. **Talk to all NPCs again**
   - Dialogue may change based on your progress
   - New conversation options may appear

4. **Check your inventory**
   - Do you have items you haven't used?
   - Try combining or using items in different scenes

5. **Load an earlier save**
   - If you think you made a wrong choice
   - Try a different approach

6. **Take a break**
   - Sometimes stepping away helps
   - Fresh perspective can reveal solutions

## Game Lore and Setting

### Warhammer 40,000 Universe

The game is set in the grimdark universe of Warhammer 40,000:

- **Space Marines**: Genetically enhanced super-soldiers
- **Space Hulks**: Massive derelict spacecraft conglomerations
- **The Emperor**: God-like leader of humanity
- **Chaos**: Corrupting force from the Warp
- **Genestealers**: Alien infiltrators

### Themes

The game explores classic Warhammer 40K themes:

- **Gothic horror** - Dark, oppressive atmosphere
- **Grimdark** - No good choices, only survival
- **Body horror** - Mutations and corruption
- **Military duty** - Honor, sacrifice, and loyalty
- **Ancient technology** - Failing machine spirits

### Immersion Tips

To get the most out of the experience:

1. **Read flavor text** - It builds the world
2. **Imagine the scenes** - Picture the dark corridors
3. **Stay in character** - You're a Space Marine!
4. **Embrace the atmosphere** - The game is meant to be tense

## Command Reference

### Quick Command List

```
Movement:
  go <direction>, <direction>, <dir>

Observation:
  look, look at <target>, examine <target>

Inventory:
  inventory, i, take <item>, drop <item>

Items:
  use <item>, use <item> on <target>

NPCs:
  talk to <npc>, ask <npc> about <topic>

Meta:
  help, save, quit, exit
```

### Command Aliases

Many commands have shortcuts:

```
go north    → north, n
go south    → south, s
go east     → east, e
go west     → west, w
inventory   → i
look        → l
examine     → x, ex
quit        → exit, q
```

## Advanced Features

### Custom Game Directories

You can play custom games by specifying the game directory:

```bash
demo_game --game-dir path/to/custom/game
```

The directory should contain the required JSON files:

- `plot_outline.json`
- `narrative_map.json`
- `puzzle_design.json`
- `scene_texts.json`
- `prd_document.json`

### Custom Save Directories

Store saves in a custom location:

```bash
demo_game --save-dir path/to/my/saves
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
demo_game --verbose
```

This shows detailed information about:

- Command parsing
- State changes
- Action execution
- Error details

## FAQ

**Q: How long does a typical playthrough take?**
A: 30 minutes to 2 hours, depending on exploration and puzzle difficulty.

**Q: Can I break the game by making wrong choices?**
A: The game tries to avoid unwinnable states, but save frequently to be safe.

**Q: Are there multiple endings?**
A: This depends on the specific game generated by the AI agents.

**Q: Can I replay with different choices?**
A: Yes! Load a save or start a new game to try different approaches.

**Q: What if I find a bug?**
A: Enable verbose mode (`--verbose`), reproduce the issue, and report it with the log output.

**Q: Can I create my own games?**
A: Yes! Use the CrewAI agents to generate new game content, or manually create JSON files following the schema.

## Getting Help

### In-Game Help

Type `help` at any time during the game to see the command reference.

### Documentation

- [Game Engine Architecture](GAME_ENGINE.md) - Technical details
- [Setup Guide](SETUP.md) - Installation and configuration
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

### Community

- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and share experiences

## Keyboard Shortcuts

### Terminal Shortcuts (Unix/Linux/Mac)

```
Ctrl+C          - Interrupt/quit game
Ctrl+D          - End of input (quit)
Up/Down Arrow   - Command history
Tab             - Auto-complete (if supported)
Ctrl+L          - Clear screen
```

### Terminal Shortcuts (Windows)

```
Ctrl+C          - Interrupt/quit game
Ctrl+Z          - End of input (quit)
Up/Down Arrow   - Command history
Ctrl+L          - Clear screen (Windows Terminal)
```

## Conclusion

You're now ready to explore the dark corridors of the Space Hulk! Remember:

- **Save frequently**
- **Explore thoroughly**
- **Talk to everyone**
- **Read everything**
- **Don't give up!**

In the grim darkness of the far future, there is only war... and adventure!

---

**Good luck, Space Marine. The Emperor protects.**

---

**Last Updated**: 2024-11-10
**Version**: 1.0
**For technical documentation, see**: [GAME_ENGINE.md](GAME_ENGINE.md)
