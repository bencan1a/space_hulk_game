# Web Interface Architectural Design
## Browser-Based Game Creation and Play Platform

**Document Version**: 1.0  
**Created**: 2025-11-12  
**Author**: Principal Software Engineer (Architectural Review)  
**Status**: Ready for Engineering Review

---

## Executive Summary

This document provides a comprehensive architectural design for the browser-based Space Hulk game creation and play interface. The architecture is optimized for **single-user deployment** while maintaining clear paths for **horizontal scalability** in future iterations.

**Key Architectural Decisions**:
- **Deployment Model**: Single-user (local/personal) with containerized components
- **Scalability Path**: Modular design allows transition to distributed architecture
- **Integration Strategy**: Non-invasive wrapper around existing CrewAI and game engine
- **Technology Stack**: Modern Python (FastAPI) backend, React TypeScript frontend
- **Storage Strategy**: Lightweight SQLite for MVP, PostgreSQL for production scale

---

## Table of Contents

1. [Architectural Principles](#architectural-principles)
2. [System Architecture](#system-architecture)
3. [Component Design](#component-design)
4. [Data Architecture](#data-architecture)
5. [API Design](#api-design)
6. [Security Architecture](#security-architecture)
7. [Scalability & Performance](#scalability--performance)
8. [Quality Attributes](#quality-attributes)
9. [Technology Stack Rationale](#technology-stack-rationale)
10. [Risk Assessment](#risk-assessment)
11. [Implementation Phases](#implementation-phases)

---

## 1. Architectural Principles

### 1.1 Core Principles

**YAGNI (You Aren't Gonna Need It)**
- Build for current single-user requirements
- Avoid premature optimization for multi-user scenarios
- Add complexity only when needed

**DRY (Don't Repeat Yourself)**
- Leverage existing CrewAI agents without duplication
- Reuse game engine logic through wrapper pattern
- Single source of truth for game content (JSON files)

**SOLID Principles**
- **Single Responsibility**: Each component has one clear purpose
- **Open/Closed**: Extensible for themes/features without modifying core
- **Liskov Substitution**: Components can be swapped (SQLite → PostgreSQL)
- **Interface Segregation**: Minimal, focused API contracts
- **Dependency Inversion**: Depend on abstractions (interfaces), not implementations

**KISS (Keep It Simple, Stupid)**
- Minimize architectural layers for single-user scenario
- Direct integration with existing Python components
- Straightforward request/response model

### 1.2 Design Constraints

**Must Haves**:
- Zero changes to existing CrewAI agents or game engine
- Backward compatibility with CLI interface
- Support for runtime theme configuration
- Real-time progress updates during generation
- Local file system storage for game content

**Must Not Haves**:
- User authentication (MVP scope - single user)
- Multi-tenancy complexity (future phase)
- Distributed transactions (single database)
- Complex orchestration (no microservices yet)

### 1.3 Quality Attributes (Prioritized)

1. **Maintainability** - Code must be clean, well-documented, testable
2. **Understandability** - Architecture should be self-evident
3. **Testability** - Each component independently testable
4. **Reliability** - Graceful error handling, consistent state
5. **Performance** - Acceptable response times for single user
6. **Scalability** - Clear path to multi-user (future)

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT TIER                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  React Single Page Application (TypeScript)                   │  │
│  │  - Story Library UI (browse, search, filter)                  │  │
│  │  - Story Creator UI (templates, chat, feedback)               │  │
│  │  - Game Player UI (text adventure interface)                  │  │
│  │  - Theme Engine (runtime CSS variable switching)              │  │
│  │  - State Management (React Context API)                       │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────────────────────────────────────┘
             │ HTTPS (REST) + WebSocket
             │
┌────────────▼──────────────────────────────────────────────────────────┐
│                      APPLICATION TIER                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  FastAPI Web Application Server                               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐          │  │
│  │  │   REST API  │  │  WebSocket  │  │  Static Files│          │  │
│  │  │  Endpoints  │  │   Handler   │  │   (Themes)   │          │  │
│  │  └─────────────┘  └─────────────┘  └──────────────┘          │  │
│  │                                                                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐          │  │
│  │  │Story Service│  │Game Service │  │Generation Svc│          │  │
│  │  └─────────────┘  └─────────────┘  └──────────────┘          │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────┬────────────────────────────┬────────────────────────────┬─────┘
       │                            │                            │
       │                            │                            │
┌──────▼─────────┐         ┌────────▼────────┐        ┌─────────▼───────┐
│  Task Queue    │         │  Data Layer     │        │  File Storage   │
│  (Celery)      │         │  (SQLite/PG)    │        │  (JSON/Saves)   │
│                │         │                 │        │                 │
│  - Async jobs  │         │  - Story meta   │        │  - game.json    │
│  - Generation  │         │  - Sessions     │        │  - save.json    │
│  - Progress    │         │  - Iterations   │        │  - themes/      │
└──────┬─────────┘         └─────────────────┘        └─────────────────┘
       │
       │ Invokes
       │
┌──────▼──────────────────────────────────────────────────────────────┐
│                    INTEGRATION TIER                                  │
│  ┌────────────────────┐          ┌────────────────────┐             │
│  │  CrewAI Wrapper    │          │ Game Engine Wrapper│             │
│  │                    │          │                     │             │
│  │  Existing:         │          │  Existing:          │             │
│  │  - crew.py         │          │  - engine.py        │             │
│  │  - agents.yaml     │          │  - loader.py        │             │
│  │  - tasks.yaml      │          │  - game_state.py    │             │
│  └────────────────────┘          └────────────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Architecture Characteristics

**Monolithic with Clear Boundaries**
- Single deployment unit (Docker container or systemd service)
- Internal modular structure (services, not microservices)
- Shared database and file system
- Simpler for single-user, easier to maintain

**Asynchronous Task Processing**
- Background Celery worker for long-running generation
- WebSocket for real-time progress updates
- Non-blocking UI during AI agent execution

**Stateful Design**
- Server maintains session state
- Database stores story metadata and iteration history
- File system holds game content and saves
- Acceptable for single user, must refactor for multi-user

### 2.3 Deployment Architecture (Single User)

**Local Development**:
```
docker-compose up
  ├── frontend:3000      (React dev server)
  ├── backend:8000       (FastAPI + Uvicorn)
  ├── celery-worker      (Background tasks)
  ├── redis:6379         (Message broker)
  └── sqlite:database.db (Lightweight DB)
```

**Production (Personal Server)**:
```
nginx:443 (reverse proxy + HTTPS)
  ├── frontend (static build)
  └── backend:8000 (Gunicorn + Uvicorn workers)
      ├── celery-worker
      └── redis:6379
      └── sqlite OR postgresql
```

---

## 3. Component Design

### 3.1 Frontend Components (React TypeScript)

#### Component Hierarchy

```
App (Theme Provider, Router)
├── LibraryPage
│   ├── StoryGrid
│   │   └── StoryCard (x N)
│   ├── SearchBar
│   └── FilterPanel
│
├── CreatorPage
│   ├── PromptSetup
│   │   ├── TemplateGallery
│   │   └── CustomPromptForm
│   ├── ChatRefinement
│   │   ├── ChatMessage (x N)
│   │   └── ChatInput
│   ├── GenerationProgress
│   │   ├── AgentStatusList
│   │   └── ProgressBar
│   └── ReviewFeedback
│       ├── StoryPreview
│       └── FeedbackForm
│
├── PlayerPage
│   ├── GameDisplay
│   │   ├── SceneRenderer
│   │   └── InventoryPanel
│   ├── CommandInput
│   └── GameControls (save/load)
│
└── Common
    ├── ThemeSelector
    ├── Modal
    ├── LoadingSpinner
    └── ErrorBoundary
```

#### State Management Strategy

**Context API** (MVP - sufficient for single user):
```typescript
// Contexts
- ThemeContext         // Active theme configuration
- StoryContext         // Library data, active story
- SessionContext       // Creation session, iterations
- GameContext          // Active game state
- WebSocketContext     // Real-time connection
```

**Future**: Migrate to Redux Toolkit if state complexity grows (multi-user)

#### Key Design Patterns

**Container/Presenter Pattern**:
- Containers: Connect to context, handle business logic
- Presenters: Purely presentational, receive props

**Error Boundary Pattern**:
- Each major feature wrapped in error boundary
- Graceful degradation on component failure

**Higher-Order Component (HOC) for Theming**:
```typescript
withTheme(Component) => Themed Component
```

### 3.2 Backend Components (FastAPI Python)

#### Service Layer Architecture

```python
# Service layer (business logic)
services/
├── story_service.py       # CRUD for stories, metadata
├── generation_service.py  # CrewAI integration, task queue
├── game_service.py        # Game engine wrapper
├── iteration_service.py   # Feedback & regeneration
└── theme_service.py       # Theme config loader

# API layer (HTTP/WebSocket)
api/
├── routes/
│   ├── stories.py         # /api/stories/* endpoints
│   ├── generation.py      # /api/generate/* endpoints
│   ├── gameplay.py        # /api/game/* endpoints
│   └── themes.py          # /api/themes/* endpoints
└── websocket.py           # WebSocket handler

# Data layer (ORM models)
models/
├── story.py               # Story metadata
├── iteration.py           # Iteration history
└── session.py             # Creation sessions

# Integration layer (existing code wrappers)
integrations/
├── crewai_wrapper.py      # Wrapper for crew.py
└── game_wrapper.py        # Wrapper for engine.py
```

#### Service Responsibilities

**StoryService**:
- CRUD operations for story metadata
- Search and filter logic
- File system interactions (read game.json)

**GenerationService**:
- Queue Celery task for CrewAI execution
- Track generation progress via WebSocket
- Handle iteration requests

**GameService**:
- Initialize game from game.json
- Process player commands
- Manage save/load operations

**IterationService**:
- Store feedback
- Trigger regeneration with context
- Version comparison logic

**ThemeService**:
- Load theme configurations from YAML
- Validate theme structure
- Serve theme assets

### 3.3 Integration Wrappers

#### CrewAI Wrapper Pattern

**Goal**: Execute existing crew without modification

```python
# integrations/crewai_wrapper.py
from space_hulk_game.crew import SpaceHulkGame

class CrewAIWrapper:
    """Wrapper for executing CrewAI agents asynchronously."""
    
    @staticmethod
    def execute_generation(
        prompt: str,
        iteration_context: dict | None = None,
        progress_callback: callable | None = None
    ) -> dict:
        """
        Execute CrewAI story generation.
        
        Args:
            prompt: User prompt or template-based prompt
            iteration_context: Previous feedback for iterations
            progress_callback: Function to call on agent progress
            
        Returns:
            dict: Game content structure (game.json)
        """
        crew = SpaceHulkGame()
        
        # Use existing crew.crew() method
        inputs = {"prompt": prompt}
        if iteration_context:
            inputs["feedback"] = iteration_context.get("feedback")
            
        # Execute with optional progress hooks
        result = crew.crew().kickoff(inputs=inputs)
        
        return result
```

**Pattern**: Adapter/Facade
- Provides clean interface to existing complex system
- Allows progress monitoring via callbacks
- No changes to original crew code

#### Game Engine Wrapper Pattern

**Goal**: Enable web-based gameplay with existing engine

```python
# integrations/game_wrapper.py
from space_hulk_game.engine import TextAdventureEngine

class GameEngineWrapper:
    """Wrapper for game engine enabling stateful web sessions."""
    
    def __init__(self, game_file: str):
        """Initialize engine with game JSON."""
        self.engine = TextAdventureEngine(game_file)
        
    def process_command(self, command: str) -> dict:
        """
        Process player command and return response.
        
        Returns:
            dict: {
                "output": str,       # Game response text
                "state": dict,       # Current game state
                "valid": bool,       # Was command valid
                "game_over": bool    # Has game ended
            }
        """
        result = self.engine.process_command(command)
        return {
            "output": result.output,
            "state": self.engine.get_state(),
            "valid": result.valid,
            "game_over": self.engine.is_game_over()
        }
    
    def save_state(self) -> dict:
        """Export current state for persistence."""
        return self.engine.save_game()
    
    def load_state(self, state: dict):
        """Restore game from saved state."""
        self.engine.load_game(state)
```

**Pattern**: Proxy/Wrapper
- Stateful wrapper around stateless engine calls
- Provides web-friendly interface (JSON in/out)
- Enables save/load functionality

---

## 4. Data Architecture

### 4.1 Database Schema (SQLite → PostgreSQL)

**Design Philosophy**: 
- Minimal schema for MVP (single user)
- Clear migration path to PostgreSQL (multi-user)
- Use SQLAlchemy ORM for database portability

#### Schema Definition

```python
# models/story.py
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Story(Base):
    """Story metadata and file references."""
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    theme_id = Column(String(50), default="warhammer40k")
    
    # File system reference
    game_file_path = Column(String(500), nullable=False, unique=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    play_count = Column(Integer, default=0)
    last_played = Column(DateTime, nullable=True)
    
    # Generation info
    prompt = Column(Text, nullable=False)
    template_id = Column(String(50), nullable=True)
    iteration_count = Column(Integer, default=0)
    
    # Statistics (extracted from game.json)
    scene_count = Column(Integer, nullable=True)
    item_count = Column(Integer, nullable=True)
    npc_count = Column(Integer, nullable=True)
    puzzle_count = Column(Integer, nullable=True)
    
    # Optional tags for search/filter
    tags = Column(JSON, default=list)  # ["horror", "combat-heavy"]


class Iteration(Base):
    """Iteration history for story refinement."""
    __tablename__ = "iterations"
    
    id = Column(Integer, primary_key=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    
    iteration_number = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=False)
    changes_requested = Column(JSON, nullable=True)  # Structured feedback
    
    # Result
    game_file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    # Was this iteration accepted or rejected
    status = Column(String(20), default="pending")  # pending, accepted, rejected


class Session(Base):
    """Active creation sessions (for progress tracking)."""
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True)  # UUID
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=True)
    
    status = Column(String(20), nullable=False)  # creating, iterating, complete, error
    current_step = Column(String(50), nullable=True)  # agent name
    progress_percent = Column(Integer, default=0)
    
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    error_message = Column(Text, nullable=True)
```

**Indexes for Performance**:
```python
# For single user, basic indexes sufficient
Index("idx_stories_created", "created_at")
Index("idx_stories_theme", "theme_id")
Index("idx_iterations_story", "story_id", "iteration_number")
```

### 4.2 File System Structure

```
data/
├── stories/
│   ├── story_001/
│   │   ├── game.json          # Generated game content
│   │   ├── iteration_1.json   # Previous versions
│   │   ├── iteration_2.json
│   │   └── metadata.json      # Duplicates DB for redundancy
│   ├── story_002/
│   └── ...
│
├── saves/
│   ├── story_001_save_1.json
│   ├── story_001_save_2.json
│   └── ...
│
├── themes/
│   ├── warhammer40k/
│   │   ├── theme.yaml
│   │   ├── assets/
│   │   │   ├── logo.png
│   │   │   └── background.jpg
│   │   └── icons/
│   ├── cyberpunk/
│   └── fantasy/
│
└── database.db  (SQLite for MVP)
```

**Design Rationale**:
- **Filesystem for game content**: Large JSON files, not suitable for DB BLOBs
- **Database for metadata**: Fast queries, relationships, indexes
- **Redundancy**: metadata.json mirrors DB for disaster recovery
- **Theme isolation**: Each theme self-contained for easy addition/removal

### 4.3 Data Flow Patterns

**Story Creation Flow**:
```
User Input → API → GenerationService → Celery Task → CrewAI Wrapper
                                                         ↓
                                                    game.json
                                                         ↓
Database ← StoryService ← API ← User (game.json path stored)
```

**Iteration Flow**:
```
Feedback → API → IterationService → Store feedback in DB
                                  → Queue Celery task with context
                                  → CrewAI Wrapper (with feedback)
                                  → New game.json (iteration_N.json)
                                  → Update DB with new version
```

**Gameplay Flow**:
```
Command → API → GameService (in-memory engine) → Process → Response
                     ↓ (periodic)
                  Save state to filesystem
```

---

## 5. API Design

### 5.1 REST API Endpoints

**Design Principles**:
- RESTful resource-based URLs
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response bodies
- Consistent error response format

#### Story Management

```http
# List stories
GET /api/stories?search={query}&theme={theme_id}&sort={field}&order={asc|desc}
Response: {
  "stories": [StoryMetadata],
  "total": int,
  "page": int,
  "page_size": int
}

# Get story details
GET /api/stories/{story_id}
Response: StoryMetadata + game content summary

# Get full game content
GET /api/stories/{story_id}/content
Response: Full game.json

# Delete story
DELETE /api/stories/{story_id}
Response: 204 No Content
```

#### Story Generation

```http
# Start new story generation
POST /api/generate
Body: {
  "prompt": str,
  "template_id": str | null,
  "theme_id": str
}
Response: {
  "session_id": str,
  "status": "queued",
  "estimated_time": int  # seconds
}

# Get generation status
GET /api/generate/{session_id}
Response: {
  "session_id": str,
  "status": "creating|complete|error",
  "progress": int,  # 0-100
  "current_step": str,
  "story_id": int | null,
  "error": str | null
}

# Submit iteration feedback
POST /api/stories/{story_id}/iterate
Body: {
  "feedback": str,
  "changes": {
    "tone": str | null,
    "difficulty": str | null,
    "focus": str | null
  }
}
Response: {
  "session_id": str,
  "iteration_number": int
}
```

#### Gameplay

```http
# Start game session
POST /api/game/{story_id}/start
Response: {
  "session_id": str,
  "initial_scene": str,
  "state": GameState
}

# Process command
POST /api/game/{session_id}/command
Body: {
  "command": str
}
Response: {
  "output": str,
  "state": GameState,
  "valid": bool,
  "game_over": bool
}

# Save game
POST /api/game/{session_id}/save
Body: {
  "save_name": str | null
}
Response: {
  "save_id": str,
  "saved_at": datetime
}

# Load game
POST /api/game/load/{save_id}
Response: {
  "session_id": str,
  "state": GameState
}
```

#### Themes

```http
# List available themes
GET /api/themes
Response: {
  "themes": [ThemeMetadata]
}

# Get theme configuration
GET /api/themes/{theme_id}
Response: ThemeConfiguration (YAML parsed to JSON)
```

### 5.2 WebSocket Protocol

**Connection**: `ws://localhost:8000/ws/progress/{session_id}`

**Message Format**:
```json
{
  "type": "progress_update",
  "session_id": "uuid",
  "status": "creating",
  "progress": 35,
  "current_step": "NarrativeArchitect",
  "message": "Designing story structure...",
  "timestamp": "2025-11-12T21:00:00Z"
}
```

**Message Types**:
- `progress_update`: Agent progress (sent every 5-10 seconds)
- `complete`: Generation finished successfully
- `error`: Generation failed
- `heartbeat`: Keep connection alive

**Error Handling**:
- Client reconnection logic with exponential backoff
- Server gracefully handles dropped connections
- Progress stored in DB, can resume after reconnect

---

## 6. Security Architecture

### 6.1 Security Requirements (Single User)

**Threat Model**:
- **Low risk**: Single user on local/personal server
- **No authentication** (MVP scope)
- **Future**: Add authentication before any network exposure

**Current Security Measures**:

1. **Input Validation**:
   - Pydantic models for all API inputs
   - Path traversal prevention (file access)
   - Command injection prevention (game commands)

2. **File System Protection**:
   - Restrict file access to data/ directory
   - Validate file paths before read/write
   - No direct user access to system files

3. **Resource Limits**:
   - Max file upload size (themes, if user-provided)
   - Rate limiting on generation requests (prevent DOS)
   - Timeout on long-running tasks

4. **Error Handling**:
   - No sensitive info in error messages
   - Structured logging (not exposed to user)
   - Graceful degradation

### 6.2 Future Security (Multi-User)

**Authentication & Authorization**:
```python
# Future implementation
- JWT tokens for API authentication
- Role-based access control (creator, player, admin)
- User isolation (can't access other users' stories)
- Session management
```

**Data Security**:
- HTTPS only (no HTTP)
- Database encryption at rest
- Secure credential storage (environment variables)
- CORS policies

---

## 7. Scalability & Performance

### 7.1 Single-User Performance Targets

**Response Times**:
- API requests: < 100ms (p95)
- Story library load: < 2 seconds (p95)
- Command processing: < 500ms (p95)
- WebSocket latency: < 50ms

**Throughput**:
- Single concurrent generation (Celery worker)
- Multiple concurrent gameplay sessions (stateful, in-memory)
- 100+ stories in library (tested)

**Resource Limits**:
- Memory: 512MB - 1GB typical
- CPU: 1-2 cores (2-4 for faster generation)
- Disk: 10GB for 100 stories
- Database: < 50MB for 1000 stories

### 7.2 Horizontal Scalability Path

**Phase 1 → Phase 2 Migration Plan**:

**Current (Single User)**:
```
Monolith (FastAPI + Celery + SQLite)
├── Single web server
├── Single Celery worker
├── Single Redis instance
└── Local SQLite database
```

**Future (Multi-User)**:
```
Load Balancer
├── Web Servers (N instances) [stateless]
├── Celery Workers (M instances) [task queue scales]
├── Redis Cluster [message broker scales]
└── PostgreSQL (Primary + Replicas) [database scales]
```

**Refactoring Required**:
1. **Externalize State**: Move session state from memory to Redis
2. **Stateless API**: No in-memory game sessions, use DB
3. **Database Migration**: SQLite → PostgreSQL
4. **File Storage**: Local filesystem → S3 or shared NFS
5. **Authentication**: Add user auth & multi-tenancy

**Design Decisions Enabling Scale**:
- ✅ Service layer separation (can extract to microservices)
- ✅ Asynchronous task processing (Celery already distributed)
- ✅ SQLAlchemy ORM (DB engine swappable)
- ✅ Stateless API design (except game sessions - fixable)
- ✅ Clear component boundaries (can containerize separately)

### 7.3 Caching Strategy

**Current (Minimal)**:
- In-memory theme config cache (rarely changes)
- No other caching needed for single user

**Future (Performance)**:
- Redis cache for story metadata (reduce DB reads)
- CDN for theme assets (if served over network)
- HTTP caching headers for static content

---

## 8. Quality Attributes

### 8.1 Testability

**Unit Testing Strategy**:
- Service layer: Mock database and integrations
- API layer: Mock services, test request/response
- Integration layer: Mock CrewAI and game engine
- Frontend: Jest + React Testing Library

**Integration Testing**:
- API integration tests with test database
- End-to-end tests with Playwright or Cypress
- Celery task execution tests

**Test Coverage Goals**:
- Service layer: 90%+
- API routes: 80%+
- Critical paths (generation, gameplay): 95%+

### 8.2 Maintainability

**Code Organization**:
- Clear separation of concerns (layers)
- Small, focused modules (SRP)
- Consistent naming conventions
- Comprehensive docstrings

**Documentation**:
- API documentation (OpenAPI/Swagger)
- Architecture diagrams (C4 model)
- Code examples for common tasks
- Deployment guides

**Dependency Management**:
- Minimal external dependencies
- Pin versions in requirements.txt
- Regular security updates

### 8.3 Reliability

**Error Handling**:
- Graceful degradation on component failure
- Retry logic for transient errors
- Clear error messages for users

**Data Integrity**:
- Database transactions for consistency
- File system redundancy (metadata.json)
- Validation before persistence

**Monitoring**:
- Structured logging (JSON format)
- Error tracking (future: Sentry)
- Performance metrics (future: Prometheus)

---

## 9. Technology Stack Rationale

### 9.1 Backend: FastAPI

**Rationale**:
- ✅ Modern, async Python framework (performance)
- ✅ Automatic OpenAPI documentation (developer experience)
- ✅ Pydantic validation (type safety, fewer bugs)
- ✅ WebSocket support (real-time updates)
- ✅ Excellent developer experience (fast iteration)

**Alternatives Considered**:
- Flask: Older, sync-only, lacks modern features
- Django: Too heavy for single-user, opinionated ORM
- Node.js: Different ecosystem, Python integration harder

### 9.2 Frontend: React + TypeScript

**Rationale**:
- ✅ Industry standard (large community, resources)
- ✅ Component reusability (DRY principle)
- ✅ TypeScript (type safety, fewer runtime errors)
- ✅ Rich ecosystem (UI libraries, tools)
- ✅ Virtual DOM (performance for dynamic UIs)

**Alternatives Considered**:
- Vue.js: Smaller ecosystem, less corporate backing
- Svelte: Newer, less mature, smaller community
- Angular: Too heavy, steep learning curve

### 9.3 Task Queue: Celery

**Rationale**:
- ✅ De facto standard for Python async tasks
- ✅ Robust, battle-tested (10+ years)
- ✅ Good monitoring tools (Flower)
- ✅ Supports distributed workers (scalability)

**Alternatives Considered**:
- RQ: Simpler but less features, no distributed mode
- Dramatiq: Newer, less ecosystem, no Windows support
- Python asyncio: Not designed for distributed tasks

### 9.4 Database: SQLite → PostgreSQL

**Rationale**:
- ✅ SQLite for MVP: Zero config, single file, perfect for one user
- ✅ PostgreSQL for scale: Production-grade, JSON support, full-text search
- ✅ SQLAlchemy ORM: Portable, swap DB without code changes

**Alternatives Considered**:
- MySQL: No advantages over PostgreSQL for this use case
- MongoDB: Overkill, schema flexibility not needed
- JSON files only: No queries, no relationships, not scalable

---

## 10. Risk Assessment

### 10.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| CrewAI integration complexity | Medium | High | Wrapper pattern, extensive testing |
| Game engine state management | Medium | Medium | Stateful wrapper, clear save/load |
| WebSocket connection drops | High | Low | Reconnection logic, DB-backed state |
| Theme system complexity | Low | Medium | Clear contract, validation, examples |
| Performance (large stories) | Medium | Medium | Lazy loading, pagination, caching |

### 10.2 Architectural Technical Debt

**Intentional Debt (YAGNI)**:
- No user authentication (defer until multi-user)
- No distributed architecture (single server sufficient)
- In-memory game sessions (refactor for scale)
- No CDN for assets (local access)

**Mitigation**: Document all design decisions, clear upgrade path in Phase 2

**Unintentional Debt (Watch For)**:
- Tight coupling between API and services (enforce interfaces)
- Insufficient error handling (comprehensive testing)
- Poor test coverage (enforce minimum coverage)
- Inadequate documentation (require docstrings)

### 10.3 Risk Register

**Create GitHub Issues for**:
1. ⚠️ **CrewAI Progress Monitoring**: May require modifications to crew.py for detailed progress
2. ⚠️ **Large Game File Performance**: JSON parsing performance for 1MB+ game files
3. ⚠️ **Theme Validation**: Malformed theme configs could break UI
4. ⚠️ **Concurrent Generation Requests**: Single Celery worker, need queuing strategy
5. ⚠️ **Save File Corruption**: Need backup strategy for game saves

---

## 11. Implementation Phases

### 11.1 Phase Overview (16 weeks total)

**Phase 1: Foundation** (Weeks 1-4)
- Backend infrastructure setup
- Database schema and migrations
- Basic API endpoints
- Frontend scaffolding

**Phase 2: Story Library** (Weeks 5-6)
- Story CRUD operations
- Search and filter UI
- Theme system implementation

**Phase 3: Story Creation** (Weeks 7-10)
- Template gallery
- Chat-based refinement
- Generation workflow
- Progress tracking (WebSocket)

**Phase 4: Iteration System** (Weeks 11-12)
- Feedback mechanism
- Version management
- Comparison UI

**Phase 5: Gameplay** (Weeks 13-15)
- Game session management
- Command processing
- Save/load system

**Phase 6: Polish** (Week 16)
- Performance optimization
- Error handling
- Documentation
- Deployment

### 11.2 Detailed Implementation Plan (Next Section)

See [IMPLEMENTATION_PLAN.md](#) for:
- Task breakdown by phase
- Acceptance criteria per task
- Dependencies and prerequisites
- Effort estimates (AI agent-scoped tasks)

---

## 12. Appendices

### 12.1 Design Patterns Used

**Architectural Patterns**:
- Layered Architecture (Presentation → Application → Integration)
- Repository Pattern (Data access abstraction)
- Service Layer Pattern (Business logic encapsulation)

**Component Patterns**:
- Adapter/Facade (CrewAI and Game Engine wrappers)
- Proxy (GameEngineWrapper for state management)
- Strategy (Theme loading and application)
- Observer (WebSocket progress updates)
- Factory (Theme instance creation)

### 12.2 Glossary

- **Iteration**: Refinement cycle where user provides feedback on generated story
- **Session**: Active creation or gameplay instance with progress tracking
- **Theme**: Visual and textual configuration for multi-genre support
- **Template**: Pre-defined story prompt with structure
- **Wrapper**: Adapter class providing clean interface to existing components

### 12.3 References

- **Internal**:
  - PRD_WEB_INTERFACE.md (Requirements)
  - ARCHITECTURE_WEB_INTERFACE.md (Technical details)
  - THEMING_SYSTEM.md (Multi-genre support)
  - CONTRIBUTING.md (Coding standards)

- **External**:
  - FastAPI Documentation: https://fastapi.tiangolo.com/
  - React TypeScript: https://react-typescript-cheatsheet.netlify.app/
  - Celery Documentation: https://docs.celeryproject.org/
  - SQLAlchemy ORM: https://docs.sqlalchemy.org/

---

## Document Approval

**Reviewed By**:
- [ ] Engineering Lead
- [ ] Product Owner
- [ ] Security Team (future, before network deployment)
- [ ] DevOps Team

**Status**: ✅ Ready for implementation planning

---

**Next Steps**:
1. Review and approve this architectural design
2. Create detailed implementation plan (task breakdown)
3. Set up development environment
4. Begin Phase 1 implementation

---

*End of Architectural Design Document*
