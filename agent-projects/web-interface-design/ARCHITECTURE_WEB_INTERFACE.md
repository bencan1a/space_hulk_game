# Web Interface Architecture Overview

## Browser-Based Game Creation and Play Platform

**Version**: 2.0
**Created**: 2025-11-12
**Status**: High-Level Overview
**Audience**: All stakeholders (technical and non-technical)

---

## Executive Summary

This document provides a high-level architectural overview of the browser-based Space Hulk game creation and play interface. It serves as an accessible introduction for all stakeholders.

**For detailed technical specifications, see:**

- [ARCHITECTURAL_DESIGN.md](./ARCHITECTURAL_DESIGN.md) - Comprehensive technical architecture
- [API_SPECIFICATION.md](./API_SPECIFICATION.md) - Complete REST and WebSocket API reference
- [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) - 6-phase implementation roadmap

### What This System Does

The web interface transforms the existing command-line game creation system into an accessible browser-based platform that enables users to:

1. **Browse** - Explore a visual library of generated stories
2. **Create** - Generate new stories using AI agents through a friendly interface
3. **Refine** - Iteratively improve stories with natural language feedback
4. **Play** - Experience text adventures directly in the browser

### Key Architectural Decisions

- **Deployment**: Single-user (local/personal) with clear path to multi-user scale
- **Integration**: Non-invasive wrapper around existing CrewAI agents and game engine
- **Technology**: Modern Python (FastAPI) backend, React TypeScript frontend
- **Storage**: SQLite for MVP, PostgreSQL-ready for production
- **Design Philosophy**: YAGNI (build for current needs), DRY (reuse existing code), SOLID principles

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT TIER                          │
│  React Single Page Application (TypeScript)             │
│  - Story Library (browse, search, filter)              │
│  - Story Creator (templates, chat, feedback)           │
│  - Game Player (text adventure interface)              │
│  - Theme Engine (runtime multi-genre support)          │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTPS + WebSocket
┌──────────────────▼──────────────────────────────────────┐
│              APPLICATION TIER                            │
│  FastAPI Web Server                                      │
│  - REST API (story CRUD, generation, gameplay)          │
│  - WebSocket (real-time progress updates)              │
│  - Service Layer (business logic)                       │
└──┬────────────┬─────────────┬───────────────────────────┘
   │            │             │
┌──▼─────┐  ┌──▼──────┐  ┌──▼──────────────┐
│ Celery │  │Database │  │ File Storage     │
│ Queue  │  │SQLite/PG│  │ (JSON, saves)    │
└──┬─────┘  └─────────┘  └──────────────────┘
   │
┌──▼──────────────────────────────────────────────────────┐
│           INTEGRATION TIER                               │
│  - CrewAI Wrapper (existing agents, no changes)         │
│  - Game Engine Wrapper (existing engine, no changes)    │
└──────────────────────────────────────────────────────────┘
```

### Architecture Characteristics

**Monolithic with Clear Boundaries**

- Single deployment unit (simplicity for single user)
- Internal modular structure (services, not microservices)
- Easy migration to distributed architecture when needed

**Asynchronous Task Processing**

- Long-running AI generation runs in background (Celery)
- Real-time progress updates via WebSocket
- Non-blocking user interface

**Stateful Design**

- Server maintains session state (acceptable for single user)
- Database stores story metadata and iteration history
- File system holds game content and saves

---

## Key Components

### 1. Frontend (React TypeScript)

**Purpose**: User interface for all interactions

**Main Features**:

- **Story Library**: Visual grid with search, filter, and pagination
- **Story Creator**: Template gallery, custom prompts, chat refinement
- **Game Player**: Command input, scene rendering, inventory management
- **Progress Tracker**: Real-time updates during AI generation

**State Management**: React Context API (sufficient for MVP)

**Technology**: React 18+, TypeScript, Material-UI or Chakra UI

---

### 2. Backend (FastAPI Python)

**Purpose**: API server and business logic

**Main Responsibilities**:

- **REST API**: Story CRUD, generation orchestration, gameplay sessions
- **WebSocket**: Real-time progress broadcasting
- **Service Layer**: Business logic isolated from API routes
- **Integration**: Wrapper adapters for CrewAI and game engine

**Technology**: FastAPI, SQLAlchemy ORM, Pydantic validation

---

### 3. Task Queue (Celery)

**Purpose**: Asynchronous execution of long-running AI generation

**How It Works**:

1. User submits generation request
2. API queues Celery task and returns job ID
3. Background worker executes CrewAI agents
4. Progress updates broadcast via WebSocket
5. Completed story saved to database and files

**Technology**: Celery 5+, Redis message broker

---

### 4. Data Layer

**Database (SQLite → PostgreSQL)**:

- Story metadata (title, description, tags, stats)
- Iteration history (feedback, versions)
- Generation job status (progress tracking)
- Game sessions (active gameplay)

**File System**:

- Game content JSON files (plot, scenes, puzzles)
- Save game files (serialized state)
- Theme assets (CSS, images, configs)

---

### 5. Integration Wrappers

**CrewAI Wrapper**:

- Executes existing `SpaceHulkGame.crew()` without modification
- Provides progress callbacks for UI updates
- Handles iteration context (feedback from previous versions)

**Game Engine Wrapper**:

- Wraps existing `TextAdventureEngine` for stateful web sessions
- Provides JSON-friendly interface
- Manages save/load operations

**Key Principle**: Zero changes to existing core components

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Frontend** | React 18+ TypeScript | Industry standard, type safety, component reuse |
| **Backend** | FastAPI (Python) | Modern async framework, auto-docs, Pydantic validation |
| **Task Queue** | Celery + Redis | Battle-tested async tasks, distributed-ready |
| **Database** | SQLite (MVP) → PostgreSQL | Zero-config for single user, production-ready migration |
| **ORM** | SQLAlchemy 2.0 | Database portability, pythonic interface |
| **WebSocket** | FastAPI native | Built-in support, no extra dependencies |
| **UI Library** | Material-UI or Chakra | Accessible components, theme support |

---

## Quality Attributes

The architecture prioritizes (in order):

1. **Maintainability** - Clean, documented, testable code
2. **Understandability** - Self-evident architecture, clear patterns
3. **Testability** - Independent component testing
4. **Reliability** - Graceful error handling, consistent state
5. **Performance** - Acceptable for single user (<100ms API, <2s page loads)
6. **Scalability** - Clear migration path to multi-user (future)

---

## Deployment Models

### Local Development

```
docker-compose up
├── frontend:3000      (React dev server)
├── backend:8000       (FastAPI + Uvicorn)
├── celery-worker      (Background tasks)
├── redis:6379         (Message broker)
└── sqlite:database.db (Lightweight DB)
```

### Production (Personal Server)

```
nginx:443 (reverse proxy + HTTPS)
├── frontend (static build)
└── backend:8000 (Gunicorn + Uvicorn workers)
    ├── celery-worker
    ├── redis:6379
    └── postgresql (optional, for scale)
```

---

## Scalability Path

### Current: Single-User (MVP)

- Single web server instance
- Single Celery worker
- SQLite database
- Local file storage

### Future: Multi-User (Phase 2)

**Changes Required**:

1. **Stateless API** - Move session state to Redis
2. **Database Migration** - SQLite → PostgreSQL
3. **File Storage** - Local → S3 or shared NFS
4. **Authentication** - Add JWT-based auth
5. **Horizontal Scaling** - Multiple web servers + workers behind load balancer

**Enablers Already in Place**:

- Service layer separation (can extract to microservices)
- Asynchronous task processing (Celery already distributed)
- SQLAlchemy ORM (database engine swappable)
- Clear component boundaries (containerizable)

---

## Integration Strategy

### No Breaking Changes

The web interface is designed as a **non-invasive wrapper**:

- **CrewAI Agents**: Used as-is via `crew.kickoff()`, no modifications
- **Game Engine**: Wrapped for web sessions, original CLI remains functional
- **JSON Format**: Maintains existing structure for backward compatibility
- **CLI Interface**: Continues to work alongside web interface

### Wrapper Pattern

```python
# Example: CrewAI Wrapper
class CrewAIWrapper:
    def execute_generation(prompt, feedback=None, on_progress=None):
        crew = SpaceHulkGame()
        result = crew.crew().kickoff(inputs={"prompt": prompt})
        return result
```

This pattern:

- Provides clean interface to existing systems
- Allows progress monitoring without changing core code
- Enables future enhancements without risk to existing functionality

---

## API Overview

For complete specifications, see [API_SPECIFICATION.md](./API_SPECIFICATION.md).

**REST Endpoints**:

- `GET /api/v1/stories` - List stories with search/filter
- `POST /api/v1/stories` - Start story generation
- `POST /api/v1/stories/{id}/iterate` - Submit feedback for iteration
- `POST /api/v1/game/{story_id}/start` - Start game session
- `POST /api/v1/game/{session_id}/command` - Process player command

**WebSocket**:

- `WS /ws/generation/{job_id}` - Real-time generation progress

**Design Principles**:

- RESTful resource-based URLs
- Standard HTTP methods and status codes
- JSON request/response bodies
- Consistent error response format

---

## Security Considerations

### Current (Single User MVP)

- **No authentication** (single user on local/personal server)
- **Input validation** (Pydantic models for all API inputs)
- **File system protection** (restrict access to data directory)
- **Resource limits** (rate limiting, timeouts, max file sizes)

### Future (Multi-User)

- **Authentication**: JWT tokens
- **Authorization**: Role-based access control
- **Data isolation**: Users cannot access others' stories
- **HTTPS only**: No unencrypted connections
- **CORS policies**: Restrict allowed origins

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-4)

Backend infrastructure, database schema, basic API, frontend scaffolding

### Phase 2: Story Library (Weeks 5-6)

Story CRUD, search/filter UI, theme system

### Phase 3: Story Creation (Weeks 7-10)

Template gallery, chat refinement, generation workflow, progress tracking

### Phase 4: Iteration System (Weeks 11-12)

Feedback mechanism, version management, comparison UI

### Phase 5: Gameplay (Weeks 13-15)

Game sessions, command processing, save/load

### Phase 6: Polish (Week 16)

Performance optimization, error handling, documentation, deployment

**Detailed Plan**: See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) for 41 AI-agent-scoped tasks.

---

## Document Navigation

This document provides a **high-level overview** accessible to all stakeholders.

**For more detail, refer to:**

- **[ARCHITECTURAL_DESIGN.md](./ARCHITECTURAL_DESIGN.md)** - Comprehensive technical architecture
  - Detailed component design with code examples
  - Complete data architecture and schemas
  - Design patterns and quality attributes
  - Risk assessment and technical debt tracking

- **[API_SPECIFICATION.md](./API_SPECIFICATION.md)** - Complete API reference
  - All REST endpoints with request/response examples
  - WebSocket protocol specifications
  - Error codes and status codes
  - Rate limiting and versioning strategy

- **[IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)** - Implementation roadmap
  - 6 phases, 41 tasks, 16-week timeline
  - Acceptance criteria and effort estimates
  - Dependencies and prerequisites

- **[PRD_WEB_INTERFACE.md](./PRD_WEB_INTERFACE.md)** - Product requirements
  - User stories and personas
  - Success metrics and KPIs
  - Feature specifications

- **[THEMING_SYSTEM.md](./THEMING_SYSTEM.md)** - Multi-genre theming
  - Runtime theme configuration
  - Support for multiple game genres
  - CSS variable architecture

---

## Questions and Next Steps

### For Engineering Teams

**Start with**:

1. Read this overview
2. Review [ARCHITECTURAL_DESIGN.md](./ARCHITECTURAL_DESIGN.md) for technical details
3. See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) for task breakdown
4. Refer to [API_SPECIFICATION.md](./API_SPECIFICATION.md) during development

### For Product Teams

**Start with**:

1. Read this overview
2. Review [PRD_WEB_INTERFACE.md](./PRD_WEB_INTERFACE.md) for requirements
3. See [USER_JOURNEYS_DIAGRAMS.md](./USER_JOURNEYS_DIAGRAMS.md) for user flows
4. Refer to [THEMING_SYSTEM.md](./THEMING_SYSTEM.md) for multi-genre support

### For All Stakeholders

**Approval Checklist**:

- [ ] Architecture aligns with product vision
- [ ] Technology stack is appropriate
- [ ] Scalability path is clear
- [ ] No breaking changes to existing systems
- [ ] Implementation timeline is realistic
- [ ] Security considerations are adequate

---

**Version**: 2.0
**Last Updated**: 2025-11-12
**Status**: ✅ High-Level Overview (Refer to ARCHITECTURAL_DESIGN.md for technical details)
**Next**: Review and approve architecture, proceed to Phase 1 implementation

---

*This document consolidates the essential architectural overview. For comprehensive technical specifications, code examples, and detailed design decisions, refer to ARCHITECTURAL_DESIGN.md.*
