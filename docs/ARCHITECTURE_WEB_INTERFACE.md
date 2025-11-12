# Web Interface Technical Architecture

## Document Information

**Version**: 1.0  
**Created**: 2025-11-12  
**Related PRD**: PRD_WEB_INTERFACE.md  
**Target Audience**: Engineering Team

---

## Architecture Overview

This document provides detailed technical architecture for the browser-based game creation and play interface. It complements the PRD by focusing on implementation details, system design, and technical patterns.

## System Architecture

### High-Level Architecture Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                        Client Layer                            │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  React Application (TypeScript)                         │  │
│  │  - Story Library (browse, search, filter)              │  │
│  │  - Story Creator (templates, chat, feedback)           │  │
│  │  - Game Player (text interface, commands)              │  │
│  │  - State Management (Context API/Redux)                │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────────────────────────────┘
             │
             │ HTTPS / WebSocket
             │
┌────────────▼──────────────────────────────────────────────────┐
│                     API Gateway Layer                          │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  FastAPI Application                                    │  │
│  │  - REST endpoints                                       │  │
│  │  - WebSocket handlers                                   │  │
│  │  - Request validation                                   │  │
│  │  - Authentication middleware (future)                   │  │
│  └─────────────────────────────────────────────────────────┘  │
└──┬────────────┬─────────────┬────────────────────────────┬────┘
   │            │             │                            │
   │            │             │                            │
┌──▼─────┐  ┌──▼──────┐  ┌──▼──────────┐         ┌───────▼────┐
│ Task   │  │Storage  │  │  CrewAI     │         │Game Engine │
│ Queue  │  │ Layer   │  │  Integration│         │Integration │
│(Celery)│  │         │  │             │         │            │
└──┬─────┘  └──┬──────┘  └──┬──────────┘         └───────┬────┘
   │            │             │                            │
   │            │             │                            │
┌──▼────────────▼─────────────▼────────────────────────────▼────┐
│                    Existing Components Layer                   │
│  - SpaceHulkGame.crew() (CrewAI agents)                       │
│  - TextAdventureEngine (gameplay loop)                         │
│  - ContentLoader (JSON parsing)                                │
│  - GameValidator (content validation)                          │
│  - SaveSystem (persistence)                                    │
└────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend Application (React)

#### Technology Stack
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite or Create React App
- **UI Library**: Material-UI v5 or Chakra UI (decision needed)
- **State Management**: Context API (MVP) → Redux Toolkit (if complexity grows)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **WebSocket**: Socket.io-client or native WebSocket
- **Styling**: CSS Modules or Styled Components
- **Form Handling**: React Hook Form
- **Markdown**: marked or react-markdown (for scene descriptions)

#### Component Structure

```
src/
├── components/
│   ├── common/              # Shared components
│   │   ├── Button/
│   │   ├── Card/
│   │   ├── Modal/
│   │   └── LoadingSpinner/
│   ├── library/             # Story library components
│   │   ├── StoryCard/
│   │   ├── StoryGrid/
│   │   ├── SearchBar/
│   │   └── FilterPanel/
│   ├── creator/             # Story creation components
│   │   ├── TemplateGallery/
│   │   ├── PromptEditor/
│   │   ├── ChatInterface/
│   │   ├── ProgressTracker/
│   │   └── FeedbackForm/
│   └── player/              # Game playing components
│       ├── GameDisplay/
│       ├── CommandInput/
│       ├── InventoryPanel/
│       ├── LocationMap/
│       └── SaveLoadMenu/
├── pages/
│   ├── Home/                # Landing + Library
│   ├── Creator/             # Story creation flow
│   ├── Player/              # Game playing interface
│   └── StoryDetail/         # Individual story details
├── services/
│   ├── api.ts               # API client
│   ├── websocket.ts         # WebSocket manager
│   └── storage.ts           # Local storage utilities
├── hooks/
│   ├── useStories.ts        # Story CRUD operations
│   ├── useGeneration.ts     # Generation job management
│   └── useGameSession.ts    # Game session state
├── contexts/
│   ├── AuthContext.tsx      # User authentication (future)
│   ├── ThemeContext.tsx     # Dark/light theme
│   └── StoryContext.tsx     # Current story state
├── types/
│   ├── story.ts             # Story data types
│   ├── generation.ts        # Generation job types
│   └── game.ts              # Game state types
└── utils/
    ├── validation.ts        # Client-side validation
    └── formatting.ts        # Text formatting helpers
```

#### Key Frontend Patterns

**1. Progress Monitoring with WebSocket**
```typescript
// hooks/useGeneration.ts
import { useEffect, useState } from 'react';
import { connectWebSocket } from '../services/websocket';

interface GenerationProgress {
  jobId: string;
  status: 'queued' | 'in_progress' | 'completed' | 'failed';
  currentAgent: string;
  progressPercent: number;
  timeRemaining: number;
}

export const useGeneration = (jobId: string) => {
  const [progress, setProgress] = useState<GenerationProgress | null>(null);
  
  useEffect(() => {
    const ws = connectWebSocket(`/ws/generate/${jobId}`);
    
    ws.on('progress', (data) => {
      setProgress(data);
    });
    
    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
    
    return () => ws.disconnect();
  }, [jobId]);
  
  return progress;
};
```

**2. Optimistic UI Updates**
```typescript
// hooks/useStories.ts
export const useCreateStory = () => {
  const [stories, setStories] = useContext(StoryContext);
  
  const createStory = async (prompt: string) => {
    // Optimistically add to list
    const tempId = `temp-${Date.now()}`;
    const tempStory = { id: tempId, title: 'Generating...', status: 'pending' };
    setStories([tempStory, ...stories]);
    
    try {
      const result = await api.post('/stories', { prompt });
      // Replace temp with real story
      setStories(stories.map(s => s.id === tempId ? result.data : s));
      return result.data;
    } catch (error) {
      // Remove temp on error
      setStories(stories.filter(s => s.id !== tempId));
      throw error;
    }
  };
  
  return { createStory };
};
```

---

### 2. Backend API (FastAPI)

#### Technology Stack
- **Framework**: FastAPI 0.100+
- **ASGI Server**: Uvicorn
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Task Queue**: Celery 5+
- **Message Broker**: Redis
- **WebSocket**: FastAPI native WebSocket support
- **Validation**: Pydantic v2
- **Testing**: pytest + httpx

#### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # Dependency injection
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── stories.py       # Story CRUD
│   │   │   ├── generation.py    # Generation jobs
│   │   │   ├── gameplay.py      # Game sessions
│   │   │   ├── templates.py     # Prompt templates
│   │   │   └── websocket.py     # WebSocket endpoints
│   │   └── deps.py          # Route dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   ├── story.py         # Story SQLAlchemy model
│   │   ├── generation.py    # Generation job model
│   │   └── session.py       # Game session model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── story.py         # Story Pydantic schemas
│   │   ├── generation.py    # Generation schemas
│   │   └── gameplay.py      # Gameplay schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── story_service.py      # Story business logic
│   │   ├── generation_service.py # Generation orchestration
│   │   ├── crew_service.py       # CrewAI integration
│   │   └── game_service.py       # Game engine wrapper
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py    # Celery configuration
│   │   └── tasks.py         # Async tasks
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py      # Database connection
│   │   └── filesystem.py    # File operations
│   └── utils/
│       ├── __init__.py
│       ├── validation.py    # Custom validators
│       └── websocket_manager.py  # WebSocket connection manager
├── tests/
│   ├── api/
│   ├── services/
│   └── workers/
└── alembic/
    └── versions/
```

#### Key Backend Patterns

**1. Story Generation Task (Celery)**
```python
# workers/tasks.py
from celery import Task
from app.services.crew_service import CrewService
from app.storage.database import get_db
from app.utils.websocket_manager import broadcast_progress

class GenerationTask(Task):
    """Custom task for story generation with progress updates."""
    
    def run(self, job_id: str, prompt: str, feedback: str = None):
        """Execute story generation."""
        crew_service = CrewService()
        
        try:
            # Update status: in_progress
            broadcast_progress(job_id, {
                'status': 'in_progress',
                'currentAgent': 'PlotMaster',
                'progressPercent': 10
            })
            
            # Call CrewAI
            result = crew_service.generate_story(
                prompt=prompt,
                feedback=feedback,
                on_agent_start=lambda agent: self._on_agent_start(job_id, agent),
                on_agent_complete=lambda agent: self._on_agent_complete(job_id, agent)
            )
            
            # Save result
            with get_db() as db:
                job = db.query(GenerationJob).filter_by(id=job_id).first()
                job.status = 'completed'
                job.result_data = result
                db.commit()
            
            broadcast_progress(job_id, {
                'status': 'completed',
                'progressPercent': 100
            })
            
        except Exception as e:
            broadcast_progress(job_id, {
                'status': 'failed',
                'error': str(e)
            })
            raise
    
    def _on_agent_start(self, job_id: str, agent_name: str):
        """Called when agent starts work."""
        progress_map = {
            'PlotMaster': 10,
            'NarrativeArchitect': 30,
            'PuzzleSmith': 50,
            'CreativeScribe': 70,
            'MechanicsGuru': 85
        }
        broadcast_progress(job_id, {
            'currentAgent': agent_name,
            'progressPercent': progress_map.get(agent_name, 0)
        })
    
    def _on_agent_complete(self, job_id: str, agent_name: str):
        """Called when agent completes."""
        pass
```

**2. WebSocket Progress Updates**
```python
# utils/websocket_manager.py
from fastapi import WebSocket
from typing import Dict, Set
import json

class ConnectionManager:
    """Manages WebSocket connections for progress updates."""
    
    def __init__(self):
        # job_id -> set of active connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, job_id: str):
        """Accept new WebSocket connection."""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, job_id: str):
        """Remove WebSocket connection."""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
    
    async def broadcast(self, job_id: str, message: dict):
        """Broadcast message to all connections for a job."""
        if job_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Clean up disconnected
            for conn in disconnected:
                self.disconnect(conn, job_id)

manager = ConnectionManager()

def broadcast_progress(job_id: str, progress: dict):
    """Synchronous wrapper for task use."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(manager.broadcast(job_id, progress))
```

**3. CrewAI Service Integration**
```python
# services/crew_service.py
from space_hulk_game.crew import SpaceHulkGame
from typing import Callable, Optional

class CrewService:
    """Service layer for CrewAI integration."""
    
    def generate_story(
        self,
        prompt: str,
        feedback: Optional[str] = None,
        on_agent_start: Optional[Callable] = None,
        on_agent_complete: Optional[Callable] = None
    ) -> dict:
        """Generate story using CrewAI agents."""
        
        # Prepare inputs
        inputs = {"game": prompt}
        if feedback:
            inputs["feedback"] = feedback
        
        # Create crew instance
        crew_instance = SpaceHulkGame()
        crew = crew_instance.crew()
        
        # Monkey-patch agent execution for progress callbacks
        if on_agent_start or on_agent_complete:
            self._inject_callbacks(crew, on_agent_start, on_agent_complete)
        
        # Execute crew
        result = crew.kickoff(inputs=inputs)
        
        # Parse and return result
        return self._parse_crew_output(result)
    
    def _inject_callbacks(self, crew, on_start, on_complete):
        """Inject progress callbacks into crew execution."""
        # This would require modifying CrewAI execution
        # or wrapping agent methods to call callbacks
        # Implementation depends on CrewAI internals
        pass
    
    def _parse_crew_output(self, result) -> dict:
        """Parse CrewAI output into structured format."""
        # Result parsing logic
        # Read generated JSON files from game-config/
        # Validate and structure data
        return {
            "plot": {},
            "narrative_map": {},
            "puzzles": {},
            "scene_texts": {},
            "prd": {}
        }
```

**4. Game Engine Service**
```python
# services/game_service.py
from space_hulk_game.engine import (
    TextAdventureEngine,
    ContentLoader,
    GameState,
    SaveSystem
)
from pathlib import Path
import uuid

class GameService:
    """Service layer for game engine integration."""
    
    def __init__(self):
        self.save_system = SaveSystem()
        self.active_sessions = {}  # session_id -> engine instance
    
    def start_game(self, story_id: str) -> str:
        """Start new game session."""
        # Load game data
        game_data_path = Path(f"storage/stories/{story_id}/game_data.json")
        loader = ContentLoader()
        game_data = loader.load_game(str(game_data_path))
        
        # Create engine instance
        engine = TextAdventureEngine(game_data)
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = engine
        
        return session_id
    
    def process_command(self, session_id: str, command: str) -> dict:
        """Process player command."""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session")
        
        engine = self.active_sessions[session_id]
        
        # Execute command
        output = engine.process_input(command)
        
        # Return state
        return {
            "output": output,
            "state": {
                "scene": engine.state.current_scene,
                "inventory": [item.to_dict() for item in engine.state.inventory],
                "flags": list(engine.state.flags),
                "isGameOver": engine.is_game_over()
            }
        }
    
    def save_game(self, session_id: str, slot_name: str) -> str:
        """Save game to slot."""
        engine = self.active_sessions[session_id]
        save_path = self.save_system.save_game(
            engine.state,
            slot_name
        )
        return save_path
    
    def load_game(self, story_id: str, save_path: str) -> str:
        """Load game from save."""
        # Load state
        state = self.save_system.load_game(save_path)
        
        # Recreate engine
        game_data_path = Path(f"storage/stories/{story_id}/game_data.json")
        loader = ContentLoader()
        game_data = loader.load_game(str(game_data_path))
        engine = TextAdventureEngine(game_data, initial_state=state)
        
        # Create session
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = engine
        
        return session_id
```

---

### 3. Data Layer

#### Database Schema (SQLAlchemy)

```python
# models/story.py
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.storage.database import Base

class Story(Base):
    """Story metadata model."""
    __tablename__ = "stories"
    
    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    current_version = Column(Integer, default=1)
    total_iterations = Column(Integer, default=0)
    play_count = Column(Integer, default=0)
    original_prompt = Column(Text)
    game_data_path = Column(String(500))
    tags = Column(JSON)  # List of tags
    
    # Relationships
    versions = relationship("StoryVersion", back_populates="story")
    generation_jobs = relationship("GenerationJob", back_populates="story")


class StoryVersion(Base):
    """Story version/iteration model."""
    __tablename__ = "story_versions"
    
    id = Column(String(36), primary_key=True)
    story_id = Column(String(36), ForeignKey("stories.id"))
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    feedback = Column(Text)  # User feedback that prompted this iteration
    game_data = Column(JSON)  # Snapshot of game data
    
    story = relationship("Story", back_populates="versions")


class GenerationJob(Base):
    """Background generation job model."""
    __tablename__ = "generation_jobs"
    
    id = Column(String(36), primary_key=True)
    story_id = Column(String(36), ForeignKey("stories.id"))
    status = Column(String(20))  # queued, in_progress, completed, failed
    current_agent = Column(String(100))
    progress_percent = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error = Column(Text)
    
    story = relationship("Story", back_populates="generation_jobs")
```

#### File System Structure

```
storage/
├── stories/
│   ├── {story-uuid-1}/
│   │   ├── v1/
│   │   │   ├── game_data.json
│   │   │   ├── plot_outline.json
│   │   │   ├── narrative_map.json
│   │   │   ├── puzzle_design.json
│   │   │   └── scene_texts.json
│   │   ├── v2/
│   │   │   └── [same files]
│   │   └── current -> v2/  # Symlink to current version
│   └── {story-uuid-2}/
│       └── ...
└── saves/
    ├── {story-uuid-1}/
    │   ├── slot_1.json
    │   ├── slot_2.json
    │   └── slot_3.json
    └── {story-uuid-2}/
        └── ...
```

---

## API Specification

### REST Endpoints

#### Stories

```
GET    /api/v1/stories
       Query: ?page=1&per_page=20&sort=newest&search=keyword
       Response: { stories: [...], total: 100, page: 1, pages: 5 }

GET    /api/v1/stories/{story_id}
       Response: { id, title, description, created_at, ... }

POST   /api/v1/stories
       Body: { prompt, template_id? }
       Response: { job_id, story_id }

PUT    /api/v1/stories/{story_id}/iterate
       Body: { feedback: { plot, puzzles, writing, tone, difficulty } }
       Response: { job_id, version }

DELETE /api/v1/stories/{story_id}
       Response: { success: true }

GET    /api/v1/stories/{story_id}/versions
       Response: { versions: [...] }
```

#### Generation

```
GET    /api/v1/generation/{job_id}
       Response: { status, progress_percent, current_agent, ... }

POST   /api/v1/generation/{job_id}/cancel
       Response: { success: true }
```

#### Templates

```
GET    /api/v1/templates
       Response: { templates: [ { id, title, description, prompt } ] }

GET    /api/v1/templates/{template_id}
       Response: { id, title, description, prompt, example_output }
```

#### Gameplay

```
POST   /api/v1/play/{story_id}/start
       Response: { session_id, initial_output, state }

POST   /api/v1/play/{session_id}/command
       Body: { command: "go north" }
       Response: { output, state }

POST   /api/v1/play/{session_id}/save
       Body: { slot_name: "slot_1" }
       Response: { save_path }

GET    /api/v1/play/{session_id}/saves
       Response: { saves: [ { slot, timestamp, scene } ] }

POST   /api/v1/play/{session_id}/load
       Body: { save_path }
       Response: { output, state }
```

### WebSocket Protocol

```
WS     /ws/generate/{job_id}

Client -> Server:
  { type: "subscribe" }

Server -> Client (progress updates):
  {
    type: "progress",
    status: "in_progress",
    current_agent: "PlotMaster",
    progress_percent: 30,
    time_remaining: 180
  }

Server -> Client (completion):
  {
    type: "complete",
    status: "completed",
    story_id: "uuid"
  }

Server -> Client (error):
  {
    type: "error",
    error: "Generation failed: ..."
  }
```

---

## Security Considerations

### Input Validation
- Sanitize all user input (prompts, commands, feedback)
- Validate file paths to prevent directory traversal
- Limit prompt length (500 chars)
- Rate limit API requests (100 req/min per IP)

### Authentication (Future Phase)
- JWT tokens for session management
- OAuth2 for third-party login
- CORS configuration for allowed origins

### File System Security
- Store user files outside web root
- Use UUID-based paths (not user-controlled names)
- Validate JSON schema on load
- Implement file size limits

---

## Performance Optimization

### Caching Strategy
- **Redis Cache**:
  - Story metadata (5 min TTL)
  - Template list (1 hour TTL)
  - Game data (10 min TTL)

### Database Optimization
- Index on `stories.created_at`, `stories.play_count`
- Pagination for large result sets
- Lazy loading of relationships

### Frontend Optimization
- Code splitting by route
- Lazy load game data
- Debounce search input (300ms)
- Virtual scrolling for long lists

---

## Deployment Architecture

### Development
```
docker-compose.yaml:
  - frontend (Vite dev server, port 5173)
  - backend (FastAPI, port 8000)
  - redis (port 6379)
  - postgres (port 5432)
  - celery worker
```

### Production
```
Cloud Infrastructure:
  - Frontend: Static hosting (Vercel/Netlify)
  - Backend: Container hosting (Railway/Render)
  - Database: Managed PostgreSQL
  - Redis: Managed Redis
  - Celery: Container with autoscaling
```

---

## Testing Strategy

### Frontend Tests
- **Unit**: Component logic (Jest/Vitest)
- **Integration**: User flows (React Testing Library)
- **E2E**: Critical paths (Playwright/Cypress)

### Backend Tests
- **Unit**: Service layer (pytest)
- **Integration**: API endpoints (httpx)
- **E2E**: Full workflows (pytest + test DB)

### Load Testing
- Concurrent story generations (10 simultaneous)
- Gameplay sessions (50 concurrent)
- API response times (<500ms p95)

---

## Monitoring and Observability

### Metrics
- Story generation success rate
- Average generation time
- API response times (p50, p95, p99)
- WebSocket connection stability
- Celery queue length

### Logging
- Structured JSON logs
- Log levels: DEBUG (dev), INFO (prod)
- Sensitive data redaction

### Error Tracking
- Sentry integration
- Error grouping by type
- Performance monitoring

---

## Migration Strategy

### Phase 1: Parallel Development
- Keep CLI functional
- Build web interface alongside
- No breaking changes to core engine

### Phase 2: Beta Testing
- Internal testing with subset of users
- Collect feedback on UX
- Performance tuning

### Phase 3: Gradual Rollout
- Announce web interface
- Keep CLI as alternative
- Monitor adoption metrics

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-12  
**Status**: Ready for Implementation

