# Implementation Guide: Browser-Based Game Interface

## Document Information

**Version**: 1.0  
**Created**: 2025-11-12  
**Related Documents**: PRD_WEB_INTERFACE.md, ARCHITECTURE_WEB_INTERFACE.md  
**Target Audience**: Development Team

---

## Quick Start for Developers

This guide provides step-by-step instructions for implementing the browser-based game creation and play interface defined in the PRD.

---

## Prerequisites

Before starting implementation, ensure you have:

- [ ] Read PRD_WEB_INTERFACE.md (understand requirements)
- [ ] Read ARCHITECTURE_WEB_INTERFACE.md (understand technical design)
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ and npm/yarn installed
- [ ] Docker installed (for local development)
- [ ] Access to repository and development branch

---

## Development Environment Setup

### 1. Clone and Install Existing System

```bash
# Clone repository
git clone https://github.com/bencan1a/space_hulk_game.git
cd space_hulk_game

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install existing dependencies
pip install -e ".[dev]"

# Verify existing system works
python -m unittest discover -s tests
demo_game  # Test CLI interface
```

### 2. Set Up Backend Development

```bash
# Create backend directory
mkdir -p backend/app

# Install backend dependencies
pip install fastapi uvicorn sqlalchemy alembic celery redis python-multipart

# Or add to pyproject.toml:
# [project.optional-dependencies]
# web = [
#     "fastapi>=0.100.0",
#     "uvicorn[standard]>=0.23.0",
#     "sqlalchemy>=2.0.0",
#     "alembic>=1.12.0",
#     "celery>=5.3.0",
#     "redis>=5.0.0",
#     "python-multipart>=0.0.6",
# ]

# Then install:
pip install -e ".[web]"
```

### 3. Set Up Frontend Development

```bash
# Create frontend directory
mkdir frontend
cd frontend

# Initialize React app with TypeScript
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install
npm install react-router-dom axios socket.io-client
npm install -D @types/react-router-dom

# Or use Material-UI
npm install @mui/material @emotion/react @emotion/styled
```

### 4. Set Up Development Infrastructure (Docker)

```bash
# Create docker-compose.yml in project root
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: spacehulk
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: spacehulk_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app/backend
      - ./src:/app/src
      - ./storage:/app/storage
    environment:
      - DATABASE_URL=postgresql://spacehulk:devpassword@postgres/spacehulk_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  celery:
    build:
      context: .
      dockerfile: backend/Dockerfile
    command: celery -A app.workers.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app/backend
      - ./src:/app/src
      - ./storage:/app/storage
    environment:
      - DATABASE_URL=postgresql://spacehulk:devpassword@postgres/spacehulk_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    command: npm run dev
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000

volumes:
  postgres_data:
EOF

# Start services
docker-compose up -d
```

---

## Implementation Phases

### Phase 1: Backend Foundation (Week 1-2)

#### Step 1.1: Project Structure Setup

```bash
# Create backend structure
mkdir -p backend/app/{api/routes,models,schemas,services,workers,storage,utils}
touch backend/app/__init__.py
touch backend/app/main.py
touch backend/app/config.py
```

#### Step 1.2: FastAPI Application Bootstrap

**File: backend/app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import stories, generation, gameplay, templates, websocket
from app.storage.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Space Hulk Game API",
    description="API for browser-based game creation and play",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stories.router, prefix="/api/v1/stories", tags=["stories"])
app.include_router(generation.router, prefix="/api/v1/generation", tags=["generation"])
app.include_router(gameplay.router, prefix="/api/v1/play", tags=["gameplay"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### Step 1.3: Database Models

**File: backend/app/models/story.py**

```python
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.storage.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    current_version = Column(Integer, default=1)
    total_iterations = Column(Integer, default=0)
    play_count = Column(Integer, default=0)
    original_prompt = Column(Text)
    game_data_path = Column(String(500))
    tags = Column(JSON)
    
    versions = relationship("StoryVersion", back_populates="story", cascade="all, delete-orphan")
    generation_jobs = relationship("GenerationJob", back_populates="story", cascade="all, delete-orphan")

class StoryVersion(Base):
    __tablename__ = "story_versions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    story_id = Column(String(36), ForeignKey("stories.id", ondelete="CASCADE"))
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    feedback = Column(Text)
    
    story = relationship("Story", back_populates="versions")

class GenerationJob(Base):
    __tablename__ = "generation_jobs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    story_id = Column(String(36), ForeignKey("stories.id", ondelete="CASCADE"))
    status = Column(String(20), default="queued")
    current_agent = Column(String(100))
    progress_percent = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error = Column(Text)
    
    story = relationship("Story", back_populates="generation_jobs")
```

#### Step 1.4: API Routes - Stories

**File: backend/app/api/routes/stories.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.storage.database import get_db
from app.models.story import Story
from app.schemas.story import StoryCreate, StoryResponse, StoryList
from app.services.story_service import StoryService

router = APIRouter()

@router.get("/", response_model=StoryList)
async def list_stories(
    page: int = 1,
    per_page: int = 20,
    sort: str = "newest",
    search: str = None,
    db: Session = Depends(get_db)
):
    """List all stories with pagination and filtering."""
    service = StoryService(db)
    return service.list_stories(page, per_page, sort, search)

@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str, db: Session = Depends(get_db)):
    """Get details of a specific story."""
    service = StoryService(db)
    story = service.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.post("/", response_model=dict)
async def create_story(
    story_data: StoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new story (starts generation job)."""
    service = StoryService(db)
    job_id, story_id = service.create_story(story_data.prompt, story_data.template_id)
    return {"job_id": job_id, "story_id": story_id}

@router.delete("/{story_id}")
async def delete_story(story_id: str, db: Session = Depends(get_db)):
    """Delete a story."""
    service = StoryService(db)
    success = service.delete_story(story_id)
    if not success:
        raise HTTPException(status_code=404, detail="Story not found")
    return {"success": True}
```

#### Step 1.5: Celery Task Queue Setup

**File: backend/app/workers/celery_app.py**

```python
from celery import Celery
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "space_hulk_game",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Import tasks
from app.workers import tasks  # noqa
```

**File: backend/app/workers/tasks.py**

```python
from app.workers.celery_app import celery_app
from app.services.crew_service import CrewService
from app.storage.database import SessionLocal
from app.models.story import GenerationJob
from datetime import datetime

@celery_app.task(bind=True)
def generate_story_task(self, job_id: str, prompt: str, feedback: str = None):
    """Background task for story generation."""
    db = SessionLocal()
    
    try:
        # Update job status
        job = db.query(GenerationJob).filter_by(id=job_id).first()
        job.status = "in_progress"
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Call CrewAI service
        crew_service = CrewService()
        result = crew_service.generate_story(
            prompt=prompt,
            feedback=feedback,
            job_id=job_id
        )
        
        # Update job status
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.progress_percent = 100
        db.commit()
        
        return result
        
    except Exception as e:
        # Update job with error
        job = db.query(GenerationJob).filter_by(id=job_id).first()
        job.status = "failed"
        job.error = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()
        raise
    finally:
        db.close()
```

---

### Phase 2: Frontend Foundation (Week 3-4)

#### Step 2.1: React Project Structure

```bash
cd frontend
mkdir -p src/{components/{common,library,creator,player},pages,services,hooks,contexts,types,utils}
```

#### Step 2.2: API Service

**File: frontend/src/services/api.ts**

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Story API
export const storyAPI = {
  list: (params: { page?: number; per_page?: number; sort?: string; search?: string }) =>
    api.get('/api/v1/stories', { params }),
  
  get: (storyId: string) =>
    api.get(`/api/v1/stories/${storyId}`),
  
  create: (prompt: string, templateId?: string) =>
    api.post('/api/v1/stories', { prompt, template_id: templateId }),
  
  delete: (storyId: string) =>
    api.delete(`/api/v1/stories/${storyId}`),
  
  iterate: (storyId: string, feedback: object) =>
    api.put(`/api/v1/stories/${storyId}/iterate`, { feedback }),
};

// Generation API
export const generationAPI = {
  getStatus: (jobId: string) =>
    api.get(`/api/v1/generation/${jobId}`),
  
  cancel: (jobId: string) =>
    api.post(`/api/v1/generation/${jobId}/cancel`),
};

// Template API
export const templateAPI = {
  list: () =>
    api.get('/api/v1/templates'),
  
  get: (templateId: string) =>
    api.get(`/api/v1/templates/${templateId}`),
};
```

#### Step 2.3: Story Library Component

**File: frontend/src/pages/Home.tsx**

```typescript
import React, { useEffect, useState } from 'react';
import { storyAPI } from '../services/api';
import StoryGrid from '../components/library/StoryGrid';
import SearchBar from '../components/library/SearchBar';

interface Story {
  id: string;
  title: string;
  description: string;
  created_at: string;
  play_count: number;
}

const Home: React.FC = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('newest');

  useEffect(() => {
    loadStories();
  }, [search, sort]);

  const loadStories = async () => {
    setLoading(true);
    try {
      const response = await storyAPI.list({ search, sort });
      setStories(response.data.stories);
    } catch (error) {
      console.error('Failed to load stories:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      <header>
        <h1>Space Hulk Game Library</h1>
        <SearchBar value={search} onChange={setSearch} />
      </header>
      
      {loading ? (
        <div>Loading...</div>
      ) : stories.length === 0 ? (
        <div className="empty-state">
          <h2>No stories yet</h2>
          <p>Create your first Space Hulk adventure!</p>
          <button onClick={() => window.location.href = '/create'}>
            Create First Story
          </button>
        </div>
      ) : (
        <StoryGrid stories={stories} onStoryClick={(id) => window.location.href = `/story/${id}`} />
      )}
    </div>
  );
};

export default Home;
```

---

### Phase 3: Story Creation Flow (Week 5-8)

#### Step 3.1: Template Gallery

**File: frontend/src/components/creator/TemplateGallery.tsx**

```typescript
import React, { useEffect, useState } from 'react';
import { templateAPI } from '../../services/api';

interface Template {
  id: string;
  title: string;
  description: string;
  prompt: string;
}

interface Props {
  onSelectTemplate: (template: Template) => void;
}

const TemplateGallery: React.FC<Props> = ({ onSelectTemplate }) => {
  const [templates, setTemplates] = useState<Template[]>([]);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await templateAPI.list();
      setTemplates(response.data.templates);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  return (
    <div className="template-gallery">
      <h2>Choose a Template</h2>
      <div className="template-grid">
        {templates.map(template => (
          <div 
            key={template.id} 
            className="template-card"
            onClick={() => onSelectTemplate(template)}
          >
            <h3>{template.title}</h3>
            <p>{template.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TemplateGallery;
```

#### Step 3.2: WebSocket Progress Tracking

**File: frontend/src/hooks/useGeneration.ts**

```typescript
import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface GenerationProgress {
  status: 'queued' | 'in_progress' | 'completed' | 'failed';
  currentAgent: string;
  progressPercent: number;
  timeRemaining: number;
  error?: string;
}

export const useGeneration = (jobId: string) => {
  const [progress, setProgress] = useState<GenerationProgress | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const wsUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const newSocket = io(wsUrl, {
      path: `/ws/generate/${jobId}`,
    });

    newSocket.on('connect', () => {
      console.log('WebSocket connected');
    });

    newSocket.on('progress', (data: GenerationProgress) => {
      setProgress(data);
    });

    newSocket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [jobId]);

  return { progress, socket };
};
```

---

### Phase 4: Testing Strategy

#### Backend Tests

**File: backend/tests/test_stories.py**

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_list_stories():
    response = client.get("/api/v1/stories")
    assert response.status_code == 200
    assert "stories" in response.json()

def test_create_story():
    response = client.post("/api/v1/stories", json={
        "prompt": "A dark horror story on a derelict ship"
    })
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert "story_id" in response.json()
```

#### Frontend Tests

**File: frontend/src/components/library/__tests__/StoryCard.test.tsx**

```typescript
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import StoryCard from '../StoryCard';

describe('StoryCard', () => {
  const mockStory = {
    id: '1',
    title: 'Test Story',
    description: 'A test story description',
    created_at: '2025-11-12',
    play_count: 5,
  };

  it('renders story title', () => {
    render(<StoryCard story={mockStory} />);
    expect(screen.getByText('Test Story')).toBeInTheDocument();
  });

  it('renders play count', () => {
    render(<StoryCard story={mockStory} />);
    expect(screen.getByText(/5 plays/i)).toBeInTheDocument();
  });
});
```

---

## Checklist for Developers

### Pre-Development
- [ ] Read and understand PRD_WEB_INTERFACE.md
- [ ] Read and understand ARCHITECTURE_WEB_INTERFACE.md
- [ ] Set up development environment (Python, Node.js, Docker)
- [ ] Familiarize yourself with existing codebase
- [ ] Run existing tests to ensure baseline functionality

### Backend Development
- [ ] Set up FastAPI project structure
- [ ] Implement database models (Story, StoryVersion, GenerationJob)
- [ ] Create Alembic migrations
- [ ] Implement API routes (stories, generation, gameplay, templates)
- [ ] Set up Celery task queue
- [ ] Integrate with CrewAI (CrewService)
- [ ] Integrate with game engine (GameService)
- [ ] Implement WebSocket for progress updates
- [ ] Add input validation and error handling
- [ ] Write unit tests (>80% coverage)
- [ ] Write integration tests for API endpoints

### Frontend Development
- [ ] Set up React project with TypeScript
- [ ] Create component library (common components)
- [ ] Implement story library page (list, search, filter)
- [ ] Implement story creation flow (templates, chat, progress)
- [ ] Implement iteration/feedback system
- [ ] Implement game player interface
- [ ] Set up WebSocket client for real-time updates
- [ ] Add error boundaries and error handling
- [ ] Implement responsive design
- [ ] Write component tests
- [ ] Write E2E tests for critical flows

### Integration & Testing
- [ ] Test backend-frontend integration
- [ ] Test WebSocket communication
- [ ] Test Celery task execution
- [ ] Test CrewAI integration
- [ ] Load testing (concurrent generations/gameplay)
- [ ] Security testing (input validation, SQL injection)
- [ ] Accessibility testing (WCAG AA compliance)
- [ ] Cross-browser testing

### Deployment
- [ ] Set up CI/CD pipeline
- [ ] Configure production database
- [ ] Configure Redis for production
- [ ] Set up environment variables
- [ ] Deploy backend to hosting platform
- [ ] Deploy frontend to static hosting
- [ ] Configure CORS and security headers
- [ ] Set up monitoring and logging
- [ ] Create deployment documentation

---

## Troubleshooting

### Common Issues

**Issue**: CrewAI integration hangs during generation  
**Solution**: Ensure timeouts are configured, check LLM service availability, review agent configuration

**Issue**: WebSocket connections drop frequently  
**Solution**: Check nginx/proxy timeout settings, implement reconnection logic, verify WebSocket protocol support

**Issue**: Database migrations fail  
**Solution**: Check for schema conflicts, review migration order, ensure database permissions

**Issue**: Frontend can't connect to backend  
**Solution**: Verify CORS configuration, check API_BASE_URL environment variable, ensure backend is running

---

## Resources

### Documentation
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- SQLAlchemy: https://www.sqlalchemy.org/
- Celery: https://docs.celeryq.dev/

### Code Examples
- See `backend/examples/` for backend code samples
- See `frontend/examples/` for frontend code samples

### Support
- Internal: #space-hulk-dev Slack channel
- GitHub Issues: https://github.com/bencan1a/space_hulk_game/issues

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-12  
**Status**: Ready for Development

