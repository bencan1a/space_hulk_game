# Glossary

**Version**: 1.0
**Created**: 2025-11-12
**Purpose**: Canonical terminology reference to resolve inconsistencies across web interface documentation
**Status**: Active Reference

---

## How to Use This Glossary

This document defines canonical terminology for the Space Hulk Web Interface project. When writing documentation, code, or user-facing text:

1. **Use the canonical term** from this glossary
2. **Check "Not to be confused with"** to avoid ambiguous usage
3. **Follow the usage examples** for consistency
4. **Consult the "Terminology Usage Guide"** section for quick reference

---

## Project Terminology

### Agent

**Definition**: A specialized AI component in the CrewAI framework responsible for a specific aspect of story generation (e.g., PlotMaster, NarrativeArchitect, PuzzleSmith, CreativeScribe, MechanicsGuru).

**Usage**:

- "The NarrativeArchitect agent is currently designing the story structure"
- "All five agents must complete for full story generation"
- "Agent execution monitoring via file system watching"

**Not to be confused with**:

- Task (which is work assigned to an agent)
- User (person using the system)

**Context**: CrewAI-specific terminology for AI components in the multi-agent story generation system.

---

### Command

**Definition**: User input text during gameplay that directs the player character's actions (e.g., "go north", "examine door", "take keycard").

**Usage**:

- "Process player command and return game response"
- "Invalid command: command not recognized by game engine"
- "Command history stored in game session"

**Not to be confused with**:

- API request (HTTP calls to backend)
- Shell command (terminal operations)

**Context**: Game engine terminology for player input during active gameplay.

---

### Game

**Definition**: An active instance of a story being played, encompassing the current gameplay session, player state, and game engine execution.

**Usage**:

- "Start a new game from this story"
- "The game is currently in Scene 3"
- "Save your game progress"

**Not to be confused with**:

- Story (the content/narrative structure created by AI)
- Game Session (the technical session tracking active gameplay)

**Context**: User-facing term for the playable instance of story content.

**Database Field**: N/A (ephemeral gameplay state)

---

### Game Session

**Definition**: A technical database record or in-memory object tracking an active gameplay instance, including session ID, current state, and metadata.

**Usage**:

- "Create new game session for story ID 123"
- "Game session expired after 1 hour of inactivity"
- "POST /api/v1/game/{game_session_id}/command"

**Not to be confused with**:

- Generation Session (which tracks story creation)
- Game (user-facing term for playing)

**Context**: Backend/API terminology for tracking active gameplay.

**Database Table**: `game_sessions` (future implementation)
**API Parameter**: `game_session_id`

---

### Generation Job

**Definition**: An asynchronous Celery task responsible for executing CrewAI agents to create or iterate on a story.

**Usage**:

- "Queue new generation job with job ID abc-123"
- "Generation job status: in_progress"
- "GET /api/v1/generation/{generation_job_id}"

**Not to be confused with**:

- Generation Session (database record tracking progress)
- Story (the output of the job)
- Task (CrewAI concept)

**Context**: Backend/Celery terminology for async work execution.

**Database Table**: `generation_jobs`
**API Parameter**: `generation_job_id`

---

### Generation Session

**Definition**: A database record tracking the progress and metadata of a story creation or iteration process, linked to a Generation Job.

**Usage**:

- "Generation session shows 45% progress"
- "Update generation session status to 'completed'"
- "Generation session created_at: 2025-11-12T10:00:00Z"

**Not to be confused with**:

- Generation Job (the Celery task doing the work)
- Game Session (which tracks gameplay)

**Context**: Database/persistence terminology for tracking generation progress.

**Database Table**: `sessions` (in ARCHITECTURAL_DESIGN.md schema)
**Related Fields**: `status`, `progress_percent`, `current_step`

---

### Iteration

**Definition**: A refinement cycle where a user provides feedback on an existing story version, triggering AI agents to regenerate content with that feedback incorporated. Maximum 5 iterations per story.

**Usage**:

- "Submit iteration feedback for story"
- "This is iteration 3 of 5"
- "POST /api/v1/stories/{story_id}/iterate"

**Not to be confused with**:

- Version (which is a snapshot/result of an iteration)
- Generation Job (the mechanism executing the iteration)

**Context**: User-facing terminology for story refinement process.

**Database Field**: `iteration_count` in `stories` table
**Business Rule**: Maximum 5 iterations per story

---

### NPC

**Definition**: Non-Player Character; a character in the game controlled by the game engine rather than the player, used for interaction, dialogue, and narrative purposes.

**Usage**:

- "Story contains 3 NPCs"
- "Interact with the NPC to receive mission briefing"
- "NPC dialogue generated by CreativeScribe agent"

**Not to be confused with**:

- Player (the user-controlled character)
- Agent (AI components generating content)

**Context**: Game content terminology.

**Related**: `npc_count` metadata field in Story model

---

### Prompt

**Definition**: User-provided text description that guides AI agents in generating story content. Can be template-based or custom (50-1000 characters).

**Usage**:

- "Enter your story generation prompt"
- "Template prompt: Create a horror-themed adventure..."
- "Original prompt stored in story metadata"

**Not to be confused with**:

- Command (gameplay input)
- Template (pre-defined prompt structure)

**Context**: Story creation terminology for user input to AI.

**Database Field**: `prompt` in `stories` table (original), `feedback` in `iterations` table
**Validation**: 50-1000 characters for custom prompts

---

### Puzzle

**Definition**: A challenge or objective within a game that requires player problem-solving, investigation, or item manipulation to progress the story.

**Usage**:

- "Story contains 2 puzzles"
- "Puzzle Smith agent designs puzzle mechanics"
- "Puzzle difficulty: moderate"

**Not to be confused with**:

- Objective (general goal)
- Scene (location where puzzle may exist)

**Context**: Game content terminology.

**Related**: `puzzle_count` metadata field, `puzzle_design.json` output file

---

### Save/Save File

**Definition**: A serialized snapshot of game state (current scene, inventory, flags, health) that can be persisted to disk and later restored to resume gameplay.

**Usage**:

- "Save your game progress"
- "Load game from save file"
- "Save file corrupted: cannot load"

**Not to be confused with**:

- Story version (snapshot of story content, not gameplay state)
- Database persistence (automatic, not user-initiated)

**Context**: Gameplay persistence terminology.

**File Location**: `/saves/{story_id}/slot_N.json`
**API Endpoints**: `POST /api/v1/game/{game_session_id}/save`, `POST /api/v1/game/load/{save_id}`

---

### Scene

**Definition**: A distinct location or setting within a game where events occur, player actions take place, and narrative unfolds. Scenes are connected to form the story's spatial structure.

**Usage**:

- "Current scene: Derelict Cargo Bay"
- "Story contains 8 scenes"
- "Navigate between scenes using movement commands"

**Not to be confused with**:

- Version (iteration of entire story)
- Chapter (narrative structure, not used in this system)

**Context**: Game content and structure terminology.

**Related**: `scene_count` metadata field, `scene_texts.json` output file, `current_scene` in game state

---

### Story

**Definition**: A complete, user-created game content object stored in the database, encompassing narrative structure, puzzles, scenes, NPCs, and items. The foundational unit of content in the system.

**Usage**:

- "Create a new story"
- "Browse story library"
- "Story metadata: 8 scenes, 5 items, 3 NPCs"

**Not to be confused with**:

- Game (which is the playable instance of a story)
- Template (which helps create a story)
- Version (which is a snapshot of story content)

**Context**: Primary content object, user-facing terminology for created narratives.

**Database Table**: `stories`
**Key Fields**: `id`, `title`, `description`, `current_version`, `iteration_count`
**File Structure**: `/stories/{story_id}/v{N}/game.json`

---

### Template

**Definition**: A pre-defined prompt structure or example that guides users in creating stories, providing a starting point with recommended themes, tone, and content focus (e.g., "Horror Infestation", "Artifact Hunt").

**Usage**:

- "Select a template from the gallery"
- "Template ID: horror_infestation"
- "Use template or write custom prompt"

**Not to be confused with**:

- Prompt (user's actual input text)
- Theme (visual/aesthetic configuration)
- Story (the output created using a template)

**Context**: Story creation assistance terminology.

**API Endpoint**: `GET /api/v1/templates`
**Database Table**: `templates` (if persisted) or static configuration files

---

### Theme

**Definition**: A visual and textual aesthetic configuration that customizes the UI appearance, terminology, and style to match a specific genre (e.g., Warhammer 40K, Cyberpunk, Fantasy). Applied at runtime via CSS variables and configuration.

**Usage**:

- "Select story theme: Warhammer 40K"
- "Theme configuration loaded from themes/warhammer40k.yaml"
- "Switch theme to cyberpunk aesthetic"

**Not to be confused with**:

- Template (content creation guidance)
- Story (content object)
- Tone (narrative quality like "dark" or "light")

**Context**: UI/visual configuration terminology supporting multi-genre design.

**Database Field**: `theme_id` in `stories` table
**API Endpoint**: `GET /api/v1/themes/{theme_id}`
**Default**: `warhammer40k`

---

### Version

**Definition**: A numbered snapshot of story content representing the result of an iteration, stored separately to enable comparison and rollback. Each iteration creates a new version (v1, v2, v3, etc.).

**Usage**:

- "Story is on version 3"
- "Compare version 2 with version 3"
- "Revert to version 1"

**Not to be confused with**:

- Iteration (the process that creates a version)
- Save file (gameplay state, not story content)

**Context**: Version control terminology for story content.

**Database Table**: `story_versions`
**File Structure**: `/stories/{story_id}/v1/`, `/stories/{story_id}/v2/`, etc.
**Related Field**: `current_version` in `stories` table

---

## Technical Terms

### API

**Definition**: Application Programming Interface; the REST and WebSocket endpoints that enable communication between frontend and backend systems.

**Full Name**: Application Programming Interface

**Related Terms**: REST API, WebSocket API, endpoint

---

### Celery

**Definition**: A distributed task queue system for Python that handles asynchronous background job processing (story generation, long-running tasks).

**Type**: Python library/framework

**Use Case**: Executing generation jobs asynchronously without blocking the web server

**Related**: Redis (message broker), generation job

---

### CSS Variables

**Definition**: Custom properties in CSS that can be dynamically updated at runtime to enable theme switching without code changes.

**Example**: `--color-primary`, `--font-heading`

**Use Case**: Theme system implementation

---

### FastAPI

**Definition**: A modern, high-performance Python web framework used to build the backend REST and WebSocket APIs.

**Type**: Python framework

**Features**: Automatic OpenAPI docs, async support, Pydantic validation, WebSocket support

---

### JSON

**Definition**: JavaScript Object Notation; a text-based data interchange format used for game content files, API requests/responses, and configuration.

**File Extension**: `.json`

**Use Cases**: `game.json`, `plot_outline.json`, API payloads

---

### PostgreSQL

**Definition**: A production-grade relational database used for storing story metadata, iterations, and sessions (replaces SQLite in production).

**Type**: Database system

**Development Alternative**: SQLite (for MVP/local development)

---

### Pydantic

**Definition**: A Python library for data validation and settings management using Python type annotations, integrated with FastAPI.

**Use Case**: Request/response validation, configuration management

---

### React

**Definition**: A JavaScript library for building user interfaces using component-based architecture, used for the frontend application.

**Type**: JavaScript framework/library

**Variant Used**: React with TypeScript

---

### Redis

**Definition**: An in-memory data structure store used as a message broker for Celery task queues and caching.

**Type**: Database/cache system

**Use Cases**: Celery broker, session caching (future)

---

### REST

**Definition**: Representational State Transfer; an architectural style for web APIs using HTTP methods and resource-based URLs.

**Full Name**: Representational State Transfer

**HTTP Methods**: GET, POST, PUT, DELETE

**Example**: `GET /api/v1/stories/{story_id}`

---

### SQLAlchemy

**Definition**: A Python SQL toolkit and Object-Relational Mapping (ORM) library that provides database abstraction and portability.

**Type**: Python library

**Use Case**: Database models, queries, migrations

**Benefit**: Swap databases (SQLite to PostgreSQL) without code changes

---

### SQLite

**Definition**: A lightweight, file-based relational database used for local development and MVP deployment.

**Type**: Database system

**Production Alternative**: PostgreSQL

**File**: `database.db`

---

### TypeScript

**Definition**: A statically typed superset of JavaScript that compiles to plain JavaScript, providing type safety and better tooling.

**Type**: Programming language

**Use Case**: Frontend development with React

---

### WebSocket

**Definition**: A communication protocol providing full-duplex communication channels over a single TCP connection, used for real-time progress updates.

**Use Case**: Live progress monitoring during story generation

**Endpoint Example**: `ws://localhost:8000/ws/generation/{job_id}`

**Fallback**: Polling (if WebSocket connection fails)

---

## Domain Terms

### CrewAI

**Definition**: A multi-agent AI orchestration framework that coordinates multiple specialized AI agents to collaborate on complex tasks (story generation in this project).

**Type**: Python framework

**Agents in This Project**: PlotMaster, NarrativeArchitect, PuzzleSmith, CreativeScribe, MechanicsGuru

**Process Modes**: Sequential (default), Hierarchical (advanced)

---

### Grimdark

**Definition**: A subgenre of speculative fiction characterized by dystopian, violent, and morally ambiguous settings where hope is scarce and outcomes are bleak.

**Origin**: Warhammer 40,000 setting

**Aesthetic**: Gothic horror, perpetual war, survival against overwhelming odds

**Related**: Warhammer 40K theme (default theme for this system)

---

### Space Hulk

**Definition**: In Warhammer 40,000 lore, a massive derelict spacecraft or conglomeration of ships adrift in space, often infested with hostile creatures and filled with ancient technology. The primary setting for this game system.

**Context**: Game setting and theme

**Characteristics**: Claustrophobic corridors, failing life support, unknown threats, valuable artifacts

---

### Warhammer 40,000 (40K)

**Definition**: A dystopian science fiction tabletop wargame setting created by Games Workshop, characterized by grimdark themes, gothic aesthetics, and perpetual galactic warfare in the 41st millennium.

**Abbreviation**: 40K, WH40K

**Use in This Project**: Default theme, primary aesthetic inspiration

**Related**: Space Hulk, grimdark, gothic horror

---

## Acronyms

### ADR

**Full Name**: Architecture Decision Record

**Definition**: A document that captures an important architectural decision made along with its context and consequences.

**Location**: `/docs/adr/`

---

### AI

**Full Name**: Artificial Intelligence

**Context**: AI agents (CrewAI components), AI-generated content

---

### API

**Full Name**: Application Programming Interface

**Definition**: Set of endpoints enabling frontend-backend communication.

**Types in This Project**: REST API, WebSocket API

---

### CLI

**Full Name**: Command-Line Interface

**Context**: Original text-based interface for running the game (`crewai run`, `demo_game`)

**Status**: Maintained alongside web interface for backward compatibility

---

### CORS

**Full Name**: Cross-Origin Resource Sharing

**Context**: HTTP header-based mechanism allowing frontend (port 5173) to request backend (port 8000)

---

### CRUD

**Full Name**: Create, Read, Update, Delete

**Context**: Basic database/API operations for stories, iterations, sessions

---

### CSS

**Full Name**: Cascading Style Sheets

**Context**: Styling language for UI, used with CSS variables for theming

---

### DB

**Full Name**: Database

**Context**: SQLite (dev) or PostgreSQL (production)

---

### HTML

**Full Name**: HyperText Markup Language

**Context**: Web page markup

---

### HTTP

**Full Name**: HyperText Transfer Protocol

**Context**: Protocol for REST API communication

**Methods**: GET, POST, PUT, DELETE

---

### HTTPS

**Full Name**: HyperText Transfer Protocol Secure

**Context**: Encrypted HTTP for production deployment

---

### JSON

**Full Name**: JavaScript Object Notation

**Context**: Data format for game files, API payloads

---

### JWT

**Full Name**: JSON Web Token

**Context**: Future authentication mechanism (not in MVP)

---

### MVP

**Full Name**: Minimum Viable Product

**Context**: Initial release scope, single-user deployment

---

### NPC

**Full Name**: Non-Player Character

**Context**: Game content, characters controlled by game engine

---

### ORM

**Full Name**: Object-Relational Mapping

**Context**: SQLAlchemy for database abstraction

---

### PRD

**Full Name**: Product Requirements Document

**Context**: `PRD_WEB_INTERFACE.md`, also generated by MechanicsGuru agent as `prd_document.json`

---

### REST

**Full Name**: Representational State Transfer

**Context**: API architectural style

---

### SQL

**Full Name**: Structured Query Language

**Context**: Database query language

---

### UI

**Full Name**: User Interface

**Context**: Frontend visual components

---

### URL

**Full Name**: Uniform Resource Locator

**Context**: Web addresses, API endpoints

---

### UUID

**Full Name**: Universally Unique Identifier

**Context**: Story IDs, session IDs (36-character string)

**Format**: `550e8400-e29b-41d4-a716-446655440000`

---

### WCAG

**Full Name**: Web Content Accessibility Guidelines

**Context**: Accessibility compliance target (Level AA)

---

### WebSocket

**Full Name**: WebSocket Protocol

**Context**: Real-time bidirectional communication

**Abbreviation**: WS

---

## Terminology Usage Guide

### Quick Reference: When to Use Each Term

| **Use This** | **NOT This** | **Context** |
|--------------|--------------|-------------|
| **Story** | Game content, narrative, mission | Referring to created content object in database |
| **Game** | Story instance, playthrough | Referring to active gameplay |
| **Generation Job** | Task, story generation, job | Referring to Celery async task |
| **Generation Session** | Progress session, job session | Referring to database progress tracking |
| **Game Session** | Play session, active game | Referring to active gameplay technical session |
| **Iteration** | Refinement, update, revision | Referring to feedback-driven regeneration cycle |
| **Version** | Iteration result, snapshot | Referring to numbered story snapshot (v1, v2) |
| **Agent** | AI worker, generator | Referring to CrewAI components |
| **Template** | Preset, example, starter | Referring to prompt starting points |
| **Theme** | Style, appearance, genre | Referring to visual/aesthetic configuration |
| **Prompt** | Input, description | Referring to user's story creation text |
| **Command** | Input, action | Referring to gameplay input |
| **Scene** | Location, room, area | Referring to game spatial unit |
| **Puzzle** | Challenge, objective | Referring to player problem-solving elements |
| **NPC** | Character | Referring to non-player characters |
| **Save/Save File** | Checkpoint, progress | Referring to gameplay state persistence |

---

### Database Field Naming

**Use these exact field names in database schemas and API responses:**

```python
# Story model
stories.id                    # UUID, primary key
stories.title                 # User-facing name
stories.description           # User-facing summary
stories.theme_id              # FK to themes
stories.current_version       # Integer, current version number
stories.iteration_count       # Integer, total iterations (max 5)
stories.prompt                # Original user prompt text

# Generation job model
generation_jobs.id            # UUID (generation_job_id in APIs)
generation_jobs.story_id      # FK to stories
generation_jobs.status        # queued|in_progress|completed|failed

# Game session (future)
game_sessions.id              # UUID (game_session_id in APIs)
game_sessions.story_id        # FK to stories
```

---

### API Endpoint Naming

**Use these exact path patterns:**

```
# Stories
GET    /api/v1/stories
GET    /api/v1/stories/{story_id}
POST   /api/v1/stories
DELETE /api/v1/stories/{story_id}

# Generation
GET    /api/v1/generation/{generation_job_id}
POST   /api/v1/stories/{story_id}/iterate

# Gameplay
POST   /api/v1/game/{story_id}/start                    # Returns game_session_id
POST   /api/v1/game/{game_session_id}/command
POST   /api/v1/game/{game_session_id}/save
POST   /api/v1/game/load/{save_id}

# WebSocket
WS     /ws/generation/{generation_job_id}
```

---

### User-Facing Text

**Examples of correct terminology in UI:**

| Context | Correct | Incorrect |
|---------|---------|-----------|
| Library view | "Browse stories" | "Browse games", "Browse missions" |
| Creation button | "Create new story" | "Create new game", "Generate story" |
| Playing | "Play game" | "Play story", "Start session" |
| Progress | "Generating story..." | "Creating game...", "Running job..." |
| Feedback | "Iteration 3 of 5" | "Revision 3", "Update 3" |
| Content | "Story contains 8 scenes" | "Game has 8 rooms", "8 locations" |
| Saving | "Save game progress" | "Save story", "Create checkpoint" |

---

### Code Comments and Documentation

**Use precise terminology in code:**

```python
# Good
def create_generation_job(story_id: str, prompt: str) -> str:
    """
    Create async generation job to create or iterate on a story.

    Args:
        story_id: UUID of the story to iterate on (or create new)
        prompt: User prompt or feedback text

    Returns:
        generation_job_id: UUID of the created Celery job
    """

# Avoid
def create_job(id: str, text: str) -> str:
    """Make a game."""  # Vague, ambiguous
```

---

### Error Messages

**Use canonical terms in error messages:**

```json
// Good
{
  "error": {
    "code": "STORY_NOT_FOUND",
    "user_message": "This story could not be found. It may have been deleted."
  }
}

// Avoid
{
  "error": {
    "message": "Game not found"  // Ambiguous: story or game session?
  }
}
```

---

## Common Ambiguities Resolved

### "Session" Context

| **Term** | **When to Use** |
|----------|-----------------|
| **Generation Session** | Database record tracking story creation progress |
| **Game Session** | Active gameplay instance with session ID |
| **User Session** | (Future) Authenticated user's login session |

**Rule**: Always qualify "session" with its type (generation/game/user)

---

### "Game" vs "Story"

| **Aspect** | **Story** | **Game** |
|------------|-----------|----------|
| **What it is** | Content object (database record + files) | Active playable instance |
| **Created by** | AI agents via generation job | User clicking "Play" on a story |
| **Stored where** | Database + `/stories/{id}/` | In-memory or `/saves/` |
| **User action** | "Create story", "Iterate story" | "Play game", "Save game" |
| **Lifecycle** | Permanent (until deleted) | Ephemeral (ends when user quits) |

**Rule**: "Story" is the noun (content), "Game" is the verb-turned-noun (playing the content)

---

### "Job" vs "Task"

| **Term** | **Context** | **What it is** |
|----------|-------------|----------------|
| **Generation Job** | Backend/Celery | Async Celery task executing story generation |
| **Task** | CrewAI | Work assigned to a specific agent within CrewAI |
| **Job** (generic) | General | Avoid using alone, always say "generation job" |

**Rule**: Always say "generation job" in backend code, "task" only in CrewAI context

---

### "Version" vs "Iteration"

| **Term** | **What it represents** |
|----------|------------------------|
| **Iteration** | The *process* of providing feedback and regenerating (verb-like) |
| **Version** | The *result* of an iteration, a numbered snapshot (noun) |

**Example**: "After iteration 2, we have version 3 (v1 = original, v2 = iteration 1 result, v3 = iteration 2 result)"

**Rule**:

- User *performs* an **iteration**
- System *creates* a **version**
- Versions are numbered (v1, v2, v3...)
- Iteration count = current_version - 1

---

## Validation Rules

**Use this section to validate terminology in your writing:**

### Checklist for Documentation

- [ ] "Story" used for content objects, not gameplay
- [ ] "Game" used for active play, not content
- [ ] "Generation Job" not shortened to "job"
- [ ] "Generation Session" not confused with "Game Session"
- [ ] "Iteration" refers to process, "Version" refers to result
- [ ] "Agent" capitalized when referring to specific agent (PlotMaster)
- [ ] "Template" not confused with "Theme"
- [ ] "Prompt" used for creation input, "Command" for gameplay input
- [ ] All database field names match canonical names
- [ ] All API endpoints use canonical paths
- [ ] Error messages use canonical terminology

---

## Future Terminology (Not in MVP)

### Authentication & Multi-User

- **User**: Authenticated account (not in MVP, which is single-user)
- **User Session**: JWT-based authentication session
- **User ID**: UUID of authenticated user

### Community Features

- **Published Story**: Story shared publicly
- **Community Library**: Shared story collection
- **Story Rating**: User rating of story quality
- **Fork**: Creating copy of another user's story

### Advanced Features

- **Story Branch**: Alternate narrative path
- **Mod**: User modification to existing story
- **Scenario**: Specific setup within a story
- **Campaign**: Series of linked stories

---

## Glossary Maintenance

**This glossary is a living document. When adding new terms:**

1. **Define clearly** with examples
2. **Distinguish** from similar terms
3. **Document** database fields and API usage
4. **Update** the terminology usage guide
5. **Version** the glossary (increment version number)
6. **Announce** changes to the team

**Last Updated**: 2025-11-12
**Next Review**: When new features are added or ambiguities discovered

---

**This glossary resolves all identified terminology inconsistencies and provides a canonical reference for the project. All documentation, code, and user-facing text should adhere to these definitions.**
