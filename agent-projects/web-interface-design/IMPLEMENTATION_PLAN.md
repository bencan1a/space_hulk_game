# Implementation Plan: Browser-Based Game Interface
## Phased Delivery with AI-Agent-Scoped Tasks

**Document Version**: 1.0
**Created**: 2025-11-12
**Author**: Principal Software Engineer
**Related**: ARCHITECTURAL_DESIGN.md, PRD_WEB_INTERFACE.md

---

## Executive Summary

This implementation plan breaks down the web interface project into **6 phases** over **16 weeks**, with each phase containing **AI-agent-scoped tasks**. Each task is designed to be:

- **Self-contained**: Clear inputs, outputs, and success criteria
- **Testable**: Includes specific test requirements
- **Scoped**: 1-3 days of work for an AI coding agent
- **Documented**: Follows project coding and documentation standards

**Total Effort Estimate**: 16 weeks
**Parallel Work Opportunities**: Marked with 🔁
**Critical Path**: Foundation → Story Creation → Gameplay

---

## Task Structure Template

Each task follows this structure:

```markdown
### Task N.M: Task Name [Priority] [Effort]

**Description**: Clear, concise task description

**Inputs**: Required files/data/dependencies

**Outputs**: Deliverable files/features

**Acceptance Criteria**:
- [ ] Specific, testable requirement
- [ ] Code follows project standards (ruff, mypy, docstrings)
- [ ] Tests written with adequate coverage
- [ ] Documentation updated

**Testing**: Unit, integration, or E2E tests required

**Dependencies**: Task IDs this depends on
```

---

## Phase 1: Foundation (Weeks 1-4)

**Objectives**: Backend/frontend scaffolding, database, task queue, CI/CD

**Deliverables**: Functional API server, React app, Docker compose, CI pipeline

### Task 1.1: Backend Project Setup [P0] [1 day]

**Description**: Initialize FastAPI backend with proper Python packaging structure.

**Outputs**:
- `backend/app/` with main.py, config.py, api/, services/, models/
- Health check endpoint `/health`
- OpenAPI docs at `/docs`

**Acceptance Criteria**:
- [ ] Backend starts on localhost:8000
- [ ] /health returns {"status": "healthy"}
- [ ] Config loaded from .env
- [ ] Structured logging (JSON format)
- [ ] Code passes ruff + mypy

**Testing**: Health endpoint test, config loading test

**Dependencies**: None

### Task 1.2: Database Setup with Alembic [P0] [1 day]

**Description**: SQLAlchemy models + Alembic migrations for Story, Iteration, Session.

**Outputs**:
- `backend/app/models/` (Story, Iteration, Session models)
- Alembic migration scripts
- Database session factory

**Acceptance Criteria**:
- [ ] `alembic upgrade head` creates tables
- [ ] Models match schema in ARCHITECTURAL_DESIGN.md Section 4.1
- [ ] Indexes created (created_at, theme_id)
- [ ] Type hints and docstrings

**Testing**: CRUD operations, foreign key relationships

**Dependencies**: Task 1.1

### Task 1.3: Frontend Project Setup [P0] [1 day] 🔁

**Description**: React TypeScript app with Vite, routing, base layout.

**Outputs**:
- `frontend/src/` with App.tsx, components/, contexts/, services/
- Routes: /, /library, /create, /play/:id
- ESLint + Prettier configured

**Acceptance Criteria**:
- [ ] `npm run dev` starts on localhost:3000
- [ ] All routes render placeholder components
- [ ] TypeScript strict mode enabled
- [ ] No console warnings

**Testing**: App renders, routing works

**Dependencies**: None (parallel)

### Task 1.4: Docker Compose Setup [P0] [1 day]

**Description**: Local development environment with all services.

**Outputs**:
- `docker-compose.yml` (frontend, backend, celery, redis, postgres)
- `.env.example`

**Acceptance Criteria**:
- [ ] `docker-compose up` starts all services
- [ ] Hot reload works
- [ ] Services can communicate

**Testing**: All services healthy, backend→redis, backend→db

**Dependencies**: Tasks 1.1, 1.2, 1.3

### Task 1.5: Celery Task Queue Setup [P0] [2 days]

**Description**: Configure Celery with Redis for async tasks.

**Outputs**:
- `backend/app/celery_app.py`
- `backend/app/tasks/` with example task
- Worker entry point

**Acceptance Criteria**:
- [ ] Celery worker starts successfully
- [ ] Example task executes
- [ ] Task results stored in Redis
- [ ] Error handling + retry logic

**Testing**: Task execution, failure handling

**Dependencies**: Task 1.1, Docker Compose

### Task 1.6: CI/CD Pipeline [P1] [1 day] 🔁

**Description**: GitHub Actions for backend/frontend testing and linting.

**Outputs**:
- `.github/workflows/backend-ci.yml`
- `.github/workflows/frontend-ci.yml`

**Acceptance Criteria**:
- [ ] Backend CI: ruff, mypy, pytest
- [ ] Frontend CI: ESLint, TypeScript, tests
- [ ] CI fails on check failure

**Testing**: CI runs successfully on PR

**Dependencies**: Tasks 1.1, 1.3

### Task 1.7: API Client & Error Handling [P0] [1 day]

**Description**: TypeScript API client with error handling.

**Outputs**:
- `frontend/src/services/api.ts` (typed API methods)
- `frontend/src/utils/errorHandler.ts`

**Acceptance Criteria**:
- [ ] Typed methods for all endpoints
- [ ] Axios interceptors
- [ ] Network + HTTP error handling
- [ ] Retry logic for transient failures

**Testing**: Successful call, network error, HTTP 404

**Dependencies**: Task 1.3

---

## Phase 2: Story Library (Weeks 5-6)

**Objectives**: Story CRUD, library UI, theme system, sample data

**Deliverables**: Story API, library page, search/filter, theme loader, sample stories

### Task 2.1: Story Service & Repository [P0] [2 days]

**Description**: Service layer for story CRUD with repository pattern.

**Outputs**:
- `backend/app/services/story_service.py`
- Pydantic schemas for request/response

**Acceptance Criteria**:
- [ ] Methods: create, get, list (with filters), update, delete
- [ ] Search (case-insensitive, multi-field)
- [ ] Pagination support
- [ ] Type hints + docstrings

**Testing**: Full CRUD cycle, search, filters, pagination

**Dependencies**: Task 1.2

### Task 2.2: Story API Endpoints [P0] [1 day]

**Description**: REST endpoints for story management.

**Outputs**:
- `backend/app/api/routes/stories.py`

**Acceptance Criteria**:
- [ ] GET /api/stories (list with query params)
- [ ] GET /api/stories/{id} (details)
- [ ] GET /api/stories/{id}/content (full game.json)
- [ ] DELETE /api/stories/{id}
- [ ] Request validation, proper status codes

**Testing**: Each endpoint with valid/invalid input

**Dependencies**: Task 2.1

### Task 2.3: Theme System - Backend [P0] [2 days]

**Description**: Theme loading with validation.

**Outputs**:
- `backend/app/services/theme_service.py`
- `data/themes/warhammer40k/theme.yaml`
- `data/themes/cyberpunk/theme.yaml`

**Acceptance Criteria**:
- [ ] Methods: load_theme, list_themes, validate_theme
- [ ] Theme caching (in-memory)
- [ ] Default theme fallback
- [ ] Asset serving via static endpoint

**Testing**: Load valid/invalid theme, caching, default fallback

**Dependencies**: Task 1.1

### Task 2.4: Theme API Endpoints [P0] [0.5 days]

**Description**: Expose theme system via API.

**Outputs**:
- `backend/app/api/routes/themes.py`

**Acceptance Criteria**:
- [ ] GET /api/themes (list)
- [ ] GET /api/themes/{theme_id} (config)
- [ ] GET /api/themes/{theme_id}/assets/{path}

**Testing**: List themes, get theme, asset serving

**Dependencies**: Task 2.3

### Task 2.5: Story Library UI - Components [P0] [2 days]

**Description**: React components for story library.

**Outputs**:
- StoryCard, StoryGrid, SearchBar, FilterPanel
- LibraryPage

**Acceptance Criteria**:
- [ ] Responsive grid layout
- [ ] Debounced search (300ms)
- [ ] Loading/empty/error states
- [ ] Accessible (ARIA labels)

**Testing**: Card renders, search triggers, filter works

**Dependencies**: Task 2.2, Task 1.7

### Task 2.6: Story Library UI - Integration [P0] [1 day]

**Description**: Connect library UI to backend API.

**Outputs**:
- `frontend/src/contexts/StoryContext.tsx`
- `frontend/src/hooks/useStories.ts`

**Acceptance Criteria**:
- [ ] StoryContext provides stories, loading, error
- [ ] Auto-fetch on page load
- [ ] Search/filter trigger API calls

**Testing**: Context data, search/filter API calls, E2E library flow

**Dependencies**: Task 2.5

### Task 2.7: Theme Selector UI [P1] [1 day]

**Description**: Theme selector with runtime CSS variable switching.

**Outputs**:
- ThemeSelector component
- `frontend/src/contexts/ThemeContext.tsx`

**Acceptance Criteria**:
- [ ] ThemeSelector dropdown
- [ ] CSS variables update on theme change
- [ ] Theme persisted in localStorage

**Testing**: Theme selection, CSS variable update, persistence

**Dependencies**: Task 2.4, Task 1.3

### Task 2.8: Sample Story Data & Database Seeding [P1] [1 day]

**Description**: Create sample stories and seed database for development/testing.

**Outputs**:
- `data/samples/sample-001/game.json` through `sample-005/game.json`
- `backend/app/alembic/versions/002_seed_sample_stories.py`
- Sample story metadata in database

**Acceptance Criteria**:
- [ ] 3-5 diverse sample stories (horror, exploration, combat, rescue, mystery)
- [ ] Sample stories cover different themes, difficulties, and durations
- [ ] Alembic seed migration populates database
- [ ] Sample stories marked with `is_sample=True` flag
- [ ] Sample stories cannot be deleted (enforced in API)
- [ ] Each sample includes all game.json components

**Testing**: Migration runs successfully, samples appear in library, deletion blocked

**Dependencies**: Task 2.1, Task 2.2

---

## Phase 3: Story Creation (Weeks 7-10)

**Objectives**: Templates, chat refinement, CrewAI integration, WebSocket progress

**Deliverables**: Template gallery, chat UI, generation workflow, real-time updates

### Task 3.1: Template System [P0] [1 day]

**Description**: Template configuration and loading.

**Outputs**:
- `data/templates/*.yaml` (horror, artifact hunt, rescue)
- `backend/app/services/template_service.py`
- API endpoints for templates

**Acceptance Criteria**:
- [ ] Template YAML with Jinja2 prompt templates
- [ ] Template rendering with variables
- [ ] GET /api/templates endpoints

**Testing**: Load template, render with variables

**Dependencies**: Task 1.1

### Task 3.2: CrewAI Wrapper Implementation [P0] [3 days]

**Description**: Wrapper for executing CrewAI with progress monitoring.

**Outputs**:
- `backend/app/integrations/crewai_wrapper.py`
- Progress callback system

**Acceptance Criteria**:
- [ ] execute_generation(prompt, callback)
- [ ] Progress callback for each agent step
- [ ] Error handling, timeout (15 min)
- [ ] **No changes to existing crew.py**

**Testing**: Execute with mock crew, progress callback, error handling

**Dependencies**: Existing CrewAI, Task 1.5

### Task 3.3: Generation Service & Celery Task [P0] [2 days]

**Description**: Generation service with async Celery task.

**Outputs**:
- `backend/app/services/generation_service.py`
- `backend/app/tasks/generation_tasks.py`

**Acceptance Criteria**:
- [ ] start_generation returns session_id
- [ ] Celery task creates/updates Session
- [ ] Task creates Story on completion
- [ ] game.json saved to filesystem

**Testing**: Start generation, session created, task completes

**Dependencies**: Task 3.2, Task 2.1

### Task 3.4: WebSocket Progress Handler [P0] [2 days]

**Description**: WebSocket for real-time progress updates.

**Outputs**:
- `backend/app/api/websocket.py`
- Connection manager

**Acceptance Criteria**:
- [ ] /ws/progress/{session_id} endpoint
- [ ] Progress messages broadcast
- [ ] Heartbeat every 30s
- [ ] Graceful disconnection

**Testing**: Connect, receive messages, disconnect, load test (10+ connections)

**Dependencies**: Task 3.3

### Task 3.5: Generation API Endpoints [P0] [1 day]

**Description**: REST endpoints for generation.

**Outputs**:
- `backend/app/api/routes/generation.py`

**Acceptance Criteria**:
- [ ] POST /api/generate (start)
- [ ] GET /api/generate/{session_id} (status)
- [ ] Request validation

**Testing**: Start with valid/invalid prompt, get status

**Dependencies**: Task 3.3

### Task 3.6: Template Gallery UI [P0] [2 days]

**Description**: Template selection interface.

**Outputs**:
- TemplateGallery, TemplateCard, CustomPromptForm

**Acceptance Criteria**:
- [ ] Grid of template cards
- [ ] Template selection
- [ ] Custom prompt form with validation (50-1000 chars)

**Testing**: Gallery renders, selection works, validation

**Dependencies**: Task 3.1, Task 1.7

### Task 3.7: Chat Refinement UI [P0] [3 days]

**Description**: Conversational prompt refinement.

**Outputs**:
- ChatInterface, ChatMessage, ChatInput

**Acceptance Criteria**:
- [ ] Chat displays user/AI messages
- [ ] Sequential question flow
- [ ] Input validation
- [ ] Final prompt preview

**Testing**: Chat renders, questions advance, validation

**Dependencies**: Task 3.6

### Task 3.8: Generation Progress UI [P0] [2 days]

**Description**: Real-time progress tracker.

**Outputs**:
- GenerationProgress, AgentStatusList
- `frontend/src/hooks/useWebSocket.ts`

**Acceptance Criteria**:
- [ ] WebSocket connection
- [ ] Progress bar updates real-time
- [ ] Agent status icons (✓ → ○)
- [ ] Reconnection logic

**Testing**: Progress updates, WebSocket reconnection

**Dependencies**: Task 3.4, Task 3.7

### Task 3.9: Story Preview & Review UI [P1] [1 day]

**Description**: Display generated story summary.

**Outputs**:
- StoryPreview, ReviewPage

**Acceptance Criteria**:
- [ ] Display metadata and statistics
- [ ] "Play Now" / "Give Feedback" buttons

**Testing**: Preview renders, buttons navigate

**Dependencies**: Task 3.8

---

## Phase 4: Iteration System (Weeks 11-12)

**Objectives**: Feedback collection, iteration with context, version comparison

**Deliverables**: Feedback form, iteration API, version comparison UI

### Task 4.1: Iteration Service [P0] [2 days]

**Description**: Service for managing iterations with feedback.

**Outputs**:
- `backend/app/services/iteration_service.py`

**Acceptance Criteria**:
- [ ] submit_feedback, start_iteration, list_iterations
- [ ] Iteration task passes feedback to CrewAI
- [ ] Iteration limit enforced (max 5)

**Testing**: Submit feedback, start iteration, limit enforcement

**Dependencies**: Task 3.3, Task 2.1

### Task 4.2: Iteration API Endpoints [P0] [1 day]

**Description**: REST endpoints for iterations.

**Outputs**:
- `backend/app/api/routes/iterations.py`

**Acceptance Criteria**:
- [ ] POST /api/stories/{id}/iterate
- [ ] GET /api/stories/{id}/iterations
- [ ] Feedback validation

**Testing**: Submit feedback, list iterations, max iterations error

**Dependencies**: Task 4.1

### Task 4.3: Feedback Form UI [P0] [2 days]

**Description**: Structured feedback form.

**Outputs**:
- FeedbackForm, FeedbackPage

**Acceptance Criteria**:
- [ ] Free-form textarea (min 100 chars)
- [ ] Tone/difficulty sliders
- [ ] Focus checkboxes
- [ ] "N/5 iterations" display

**Testing**: Form renders, validation, submission

**Dependencies**: Task 4.2, Task 1.7

### Task 4.4: Iteration History UI [P1] [2 days]

**Description**: List of iterations.

**Outputs**:
- IterationHistory, IterationCard

**Acceptance Criteria**:
- [ ] List iterations reverse chronological
- [ ] Status badges (Pending/Accepted/Rejected)
- [ ] "View Game" / "Compare" buttons

**Testing**: History renders, cards navigate

**Dependencies**: Task 4.2

### Task 4.5: Version Comparison UI [P2] [2 days]

**Description**: Side-by-side version comparison.

**Outputs**:
- VersionComparison, ComparePage

**Acceptance Criteria**:
- [ ] Split view (version A | version B)
- [ ] Highlight differences (green/red/yellow)

**Testing**: Comparison renders, differences highlighted

**Dependencies**: Task 4.1, Task 4.4

---

## Phase 5: Gameplay (Weeks 13-15)

**Objectives**: Game engine integration, gameplay UI, save/load

**Deliverables**: Game session API, player UI, save system

### Task 5.1: Game Engine Wrapper [P0] [2 days]

**Description**: Wrapper for stateful game sessions.

**Outputs**:
- `backend/app/integrations/game_wrapper.py`

**Acceptance Criteria**:
- [ ] __init__(game_file), process_command, get_state, save/load_state
- [ ] **No changes to existing engine**

**Testing**: Initialize, commands, save/load round-trip

**Dependencies**: Existing game engine

### Task 5.2: Game Service & Session Management [P0] [2 days]

**Description**: Service for gameplay sessions.

**Outputs**:
- `backend/app/services/game_service.py`
- GameSession model

**Acceptance Criteria**:
- [ ] start_game, process_command, save_game, load_game
- [ ] In-memory session storage
- [ ] Session timeout (1 hour)

**Testing**: Session lifecycle, timeout cleanup

**Dependencies**: Task 5.1

### Task 5.3: Game API Endpoints [P0] [1 day]

**Description**: REST endpoints for gameplay.

**Outputs**:
- `backend/app/api/routes/gameplay.py`

**Acceptance Criteria**:
- [ ] POST /api/game/{story_id}/start
- [ ] POST /api/game/{session_id}/command
- [ ] POST /api/game/{session_id}/save
- [ ] POST /api/game/load/{save_id}

**Testing**: Start, command, save, load

**Dependencies**: Task 5.2

### Task 5.4: Game Player UI - Display [P0] [2 days]

**Description**: Game display components.

**Outputs**:
- GameDisplay, SceneRenderer, InventoryPanel, OutputLog

**Acceptance Criteria**:
- [ ] Scene displays Markdown
- [ ] Inventory shows items
- [ ] Output log with auto-scroll
- [ ] Theme-based styling

**Testing**: Scene renders, inventory displays, log appends

**Dependencies**: Task 1.3, Task 2.7

### Task 5.5: Game Player UI - Input & Controls [P0] [2 days]

**Description**: Command input and controls.

**Outputs**:
- CommandInput, GameControls, PlayerPage

**Acceptance Criteria**:
- [ ] Command input with Enter to submit
- [ ] Command history (up/down arrows)
- [ ] Save/Load/Quit buttons
- [ ] Keyboard shortcuts

**Testing**: Command submit, history, controls

**Dependencies**: Task 5.4, Task 5.3

### Task 5.6: Game State Management [P0] [1 day]

**Description**: Frontend state for active game.

**Outputs**:
- `frontend/src/contexts/GameContext.tsx`

**Acceptance Criteria**:
- [ ] GameContext provides session, scene, inventory, commands

**Testing**: Context state, sendCommand updates

**Dependencies**: Task 5.5

### Task 5.7: Save/Load System [P0] [2 days]

**Description**: Complete save/load UI.

**Outputs**:
- SaveModal, LoadModal, SaveCard

**Acceptance Criteria**:
- [ ] SaveModal prompts for name
- [ ] LoadModal displays saves with metadata
- [ ] Delete save functionality

**Testing**: Save, load round-trip, delete

**Dependencies**: Task 5.3, Task 5.6

---

## Phase 6: Polish & Launch (Week 16)

**Objectives**: Performance, error handling, documentation, deployment

**Deliverables**: Optimized app, docs, production config

### Task 6.1: Performance Optimization [P1] [2 days]

**Description**: Optimize for performance targets.

**Outputs**:
- Optimized queries, code splitting, caching

**Acceptance Criteria**:
- [ ] Library loads <2s (p95)
- [ ] API <100ms (p95)
- [ ] Commands <500ms (p95)
- [ ] Bundle <500KB gzipped

**Testing**: Load tests, Lighthouse score >90

**Dependencies**: All previous phases

### Task 6.2: Comprehensive Error Handling [P0] [1 day]

**Description**: Graceful error handling everywhere.

**Outputs**:
- `frontend/src/utils/errorMessages.ts`
- Error boundaries

**Acceptance Criteria**:
- [ ] User-friendly error messages
- [ ] Error boundaries catch React errors
- [ ] No sensitive info in errors

**Testing**: Each error type, network errors

**Dependencies**: All phases

### Task 6.3: User Documentation [P0] [2 days]

**Description**: Comprehensive user guides.

**Outputs**:
- `docs/USER_GUIDE.md`
- `docs/API_REFERENCE.md`
- `docs/DEPLOYMENT.md`

**Acceptance Criteria**:
- [ ] USER_GUIDE covers all features
- [ ] Screenshots/GIFs for workflows
- [ ] API docs auto-generated

**Testing**: Manual walkthrough of guide

**Dependencies**: All features

### Task 6.4: Production Deployment Setup [P0] [2 days]

**Description**: Production Docker config.

**Outputs**:
- `docker-compose.prod.yml`
- `nginx.conf`
- Deployment docs

**Acceptance Criteria**:
- [ ] Production compose with nginx, Gunicorn
- [ ] HTTPS reverse proxy
- [ ] Database migration instructions

**Testing**: Deploy to staging

**Dependencies**: All phases

### Task 6.5: End-to-End Testing [P1] [2 days]

**Description**: E2E test suite for critical journeys.

**Outputs**:
- `frontend/tests/e2e/` (Playwright/Cypress)

**Acceptance Criteria**:
- [ ] E2E tests for: library, creation, gameplay, iteration
- [ ] CI integration

**Testing**: E2E suite passes

**Dependencies**: All features

### Task 6.6: Final Bug Fixes & QA [P0] [2 days]

**Description**: Final QA and bug fixes.

**Outputs**:
- Bug fixes, QA sign-off

**Acceptance Criteria**:
- [ ] All P0/P1 bugs fixed
- [ ] Cross-browser tested
- [ ] WCAG AA compliance
- [ ] Security audit

**Testing**: Manual QA checklist, automated tests pass

**Dependencies**: All tasks

---

## Testing Strategy

### Unit Testing
- **Backend**: pytest, 90%+ coverage
- **Frontend**: Jest + RTL, 80%+ coverage

### Integration Testing
- API integration tests with test DB
- Component integration tests

### E2E Testing
- Playwright/Cypress for critical journeys
- Cross-browser compatibility

### Performance Testing
- Load testing (k6/Locust)
- Lighthouse audits

---

## Documentation Requirements

Every task must include:

1. **Code Documentation**: Docstrings, type hints
2. **README Updates**: New features documented
3. **API Documentation**: OpenAPI annotations
4. **ADRs**: Major design decisions

---

## Risk Mitigation

### High-Risk Tasks

1. **Task 3.2: CrewAI Wrapper** - Integration complexity
   - Mitigation: Extensive testing, mock mode

2. **Task 3.4: WebSocket Progress** - Real-time complexity
   - Mitigation: Reconnection logic, fallback to polling

3. **Task 5.1: Game Engine Wrapper** - State management
   - Mitigation: Clear contract, state validation

### Technical Debt Tracking

Create GitHub issues for:
- In-memory game sessions (Task 5.2)
- No authentication (MVP)
- SQLite default (Task 1.2)

Label: `technical-debt`

---

## Effort Summary

| Phase | Tasks | Days |
|-------|-------|------|
| 1: Foundation | 7 | 8 |
| 2: Story Library | 8 | 10.5 |
| 3: Story Creation | 9 | 17 |
| 4: Iteration | 5 | 9 |
| 5: Gameplay | 7 | 12 |
| 6: Polish | 6 | 11 |
| **Total** | **42** | **67.5** |

At 5 days/week, 67.5 days ≈ 13.5 weeks, rounded to 16 weeks for buffer.

---

## Next Steps

1. Review and approve plan
2. Confirm P0/P1/P2 priorities
3. Assign tasks to AI agents
4. Track progress with GitHub Issues/Projects
5. Iterate based on learnings

---

*End of Implementation Plan*
