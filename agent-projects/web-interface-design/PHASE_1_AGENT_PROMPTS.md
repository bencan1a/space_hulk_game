# Phase 1 Agent Prompts: Foundation Tasks
## Browser-Based Game Interface Implementation

**Phase**: 1 - Foundation (Weeks 1-4)
**Objective**: Backend/frontend scaffolding, database, task queue, CI/CD
**Deliverables**: Functional API server, React app, Docker compose, CI pipeline

---

## Table of Contents

1. [Task 1.1: Backend Project Setup](#task-11-backend-project-setup)
2. [Task 1.2: Database Setup with Alembic](#task-12-database-setup-with-alembic)
3. [Task 1.3: Frontend Project Setup](#task-13-frontend-project-setup)
4. [Task 1.4: Docker Compose Setup](#task-14-docker-compose-setup)
5. [Task 1.5: Celery Task Queue Setup](#task-15-celery-task-queue-setup)
6. [Task 1.6: CI/CD Pipeline](#task-16-cicd-pipeline)
7. [Task 1.7: API Client & Error Handling](#task-17-api-client--error-handling)

---

## Task 1.1: Backend Project Setup

**Priority**: P0
**Effort**: 1 day
**Dependencies**: None

### Context

You are implementing the backend for a browser-based game creation and play interface. This is the foundational task that establishes the FastAPI backend structure. The system will wrap existing CrewAI agents and a game engine **without modifying them**.

**Project Documentation**:
- Architecture: [ARCHITECTURAL_DESIGN.md](./ARCHITECTURAL_DESIGN.md)
- Implementation Plan: [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)
- API Specification: [API_SPECIFICATION.md](./API_SPECIFICATION.md)

### Your Mission

Initialize a FastAPI backend with proper Python packaging structure, health check endpoint, configuration management, and structured logging.

### Deliverables

Create the following structure:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app initialization
│   ├── config.py         # Configuration management (pydantic-settings)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── models/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── test_health.py
│   └── test_config.py
├── .env.example
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

### Acceptance Criteria

- [ ] Backend starts on `localhost:8000` with `uvicorn backend.app.main:app --reload`
- [ ] Health check endpoint `GET /health` returns `{"status": "healthy", "version": "1.0.0", "timestamp": "ISO8601"}`
- [ ] OpenAPI docs accessible at `/docs` and `/redoc`
- [ ] Configuration loaded from `.env` file (use `pydantic-settings`)
- [ ] Structured logging in JSON format with timestamps
- [ ] Code passes `ruff check .` (zero errors)
- [ ] Code passes `mypy .` with `--strict` (zero errors)
- [ ] Type hints on all functions
- [ ] Docstrings on all public classes and functions (Google style)
- [ ] Test for health endpoint passes with `pytest`
- [ ] Test for config loading passes

### Technical Requirements

**FastAPI Application (`main.py`)**:
```python
"""FastAPI application initialization and configuration."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import settings

# Setup structured logging
logging.basicConfig(
    level=settings.log_level,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    logger.info("Starting Space Hulk Game API", extra={"version": "1.0.0"})
    yield
    logger.info("Shutting down Space Hulk Game API")


app = FastAPI(
    title="Space Hulk Game API",
    description="Browser-based game creation and play interface",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        dict: Health status, version, and timestamp
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
```

**Configuration (`config.py`)**:
```python
"""Application configuration management."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_environment: Literal["development", "staging", "production"] = "development"

    # Logging
    log_level: str = "INFO"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database (placeholder)
    database_url: str = "sqlite:///./data/database.db"


settings = Settings()
```

**Dependencies (`requirements.txt`)**:
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
```

**Dev Dependencies (`requirements-dev.txt`)**:
```txt
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0
ruff>=0.1.0
mypy>=1.7.0
```

**Environment Template (`.env.example`)**:
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Database (placeholder)
DATABASE_URL=sqlite:///./data/database.db
```

### Testing Requirements

**`tests/test_health.py`**:
```python
"""Tests for health check endpoint."""
import pytest
from httpx import AsyncClient
from datetime import datetime

from backend.app.main import app


@pytest.mark.asyncio
async def test_health_endpoint_returns_200():
    """Test health endpoint returns 200 status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_structure():
    """Test health response has correct structure."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_timestamp_format():
    """Test timestamp is valid ISO 8601 format."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        data = response.json()

        # Should not raise exception
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
```

**`tests/test_config.py`**:
```python
"""Tests for configuration management."""
import os
import pytest
from backend.app.config import Settings


def test_config_defaults():
    """Test config has sensible defaults."""
    settings = Settings()
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.api_environment == "development"
    assert settings.log_level == "INFO"


def test_config_from_env(monkeypatch):
    """Test config loads from environment variables."""
    monkeypatch.setenv("API_PORT", "9000")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()
    assert settings.api_port == 9000
    assert settings.log_level == "DEBUG"
```

### Validation Commands

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. Copy environment template
cp .env.example .env

# 3. Start the server
uvicorn app.main:app --reload
# Visit: http://localhost:8000/health
# Visit: http://localhost:8000/docs

# 4. Run linting
ruff check .

# 5. Run type checking
mypy . --strict

# 6. Run tests
pytest -v
```

### Success Indicators

✅ Server starts without errors
✅ Health endpoint returns valid JSON
✅ OpenAPI docs are accessible
✅ All tests pass
✅ No linting or type errors
✅ Logs are structured and readable

---

## Task 1.2: Database Setup with Alembic

**Priority**: P0
**Effort**: 1 day
**Dependencies**: Task 1.1

### Context

Establish the database layer with SQLAlchemy ORM and Alembic migrations. Create models for Story, Iteration, and Session based on the schema defined in ARCHITECTURAL_DESIGN.md Section 4.1.

### Your Mission

Set up SQLAlchemy models, Alembic migrations, and database session management for the three core entities: Story, Iteration, and Session.

### Deliverables

```
backend/
├── app/
│   ├── database.py         # Database session factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py         # SQLAlchemy Base
│   │   ├── story.py        # Story model
│   │   ├── iteration.py    # Iteration model
│   │   └── session.py      # Session model
│   └── alembic/
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
│           └── 001_initial_schema.py
├── alembic.ini
└── tests/
    └── test_models.py
```

### Acceptance Criteria

- [ ] `alembic upgrade head` creates all tables without errors
- [ ] Models match schema in ARCHITECTURAL_DESIGN.md Section 4.1
- [ ] Indexes created on `created_at` and `theme_id` fields
- [ ] All models have type hints and docstrings
- [ ] Foreign key relationships work correctly
- [ ] Test CRUD operations for all models
- [ ] Test foreign key constraints
- [ ] Database session factory provides proper connection
- [ ] Code passes ruff and mypy checks

### Technical Requirements

**Database Session Factory (`database.py`)**:
```python
"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes to get database session.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Base Model (`models/base.py`)**:
```python
"""SQLAlchemy declarative base."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass
```

**Story Model (`models/story.py`)**:
```python
"""Story model for game metadata."""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index
from datetime import datetime

from .base import Base


class Story(Base):
    """
    Story metadata and file references.

    Attributes:
        id: Primary key
        title: Story title (max 200 chars)
        description: Story description
        theme_id: Theme identifier (default: warhammer40k)
        game_file_path: Path to game.json file
        created_at: Creation timestamp
        updated_at: Last update timestamp
        play_count: Number of times played
        last_played: Last play timestamp
        prompt: Original user prompt
        template_id: Template identifier if used
        iteration_count: Number of iterations performed
        scene_count: Number of scenes in game
        item_count: Number of items in game
        npc_count: Number of NPCs in game
        puzzle_count: Number of puzzles in game
        tags: List of tags for search/filter
    """
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    theme_id = Column(String(50), default="warhammer40k", nullable=False)

    # File system reference
    game_file_path = Column(String(500), nullable=False, unique=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    play_count = Column(Integer, default=0, nullable=False)
    last_played = Column(DateTime, nullable=True)

    # Generation info
    prompt = Column(Text, nullable=False)
    template_id = Column(String(50), nullable=True)
    iteration_count = Column(Integer, default=0, nullable=False)

    # Statistics (extracted from game.json)
    scene_count = Column(Integer, nullable=True)
    item_count = Column(Integer, nullable=True)
    npc_count = Column(Integer, nullable=True)
    puzzle_count = Column(Integer, nullable=True)

    # Optional tags for search/filter
    tags = Column(JSON, default=list, nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_stories_created", "created_at"),
        Index("idx_stories_theme", "theme_id"),
    )
```

**Iteration Model (`models/iteration.py`)**:
```python
"""Iteration model for story refinement history."""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Index
from datetime import datetime

from .base import Base


class Iteration(Base):
    """
    Iteration history for story refinement.

    Attributes:
        id: Primary key
        story_id: Foreign key to Story
        iteration_number: Iteration sequence number
        feedback: User feedback text
        changes_requested: Structured feedback data
        game_file_path: Path to iteration game.json
        created_at: Creation timestamp
        status: pending, accepted, or rejected
    """
    __tablename__ = "iterations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)

    iteration_number = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=False)
    changes_requested = Column(JSON, nullable=True)

    # Result
    game_file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Status
    status = Column(String(20), default="pending", nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_iterations_story", "story_id", "iteration_number"),
    )
```

**Session Model (`models/session.py`)**:
```python
"""Session model for tracking active creation sessions."""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from datetime import datetime

from .base import Base


class Session(Base):
    """
    Active creation sessions for progress tracking.

    Attributes:
        id: UUID primary key
        story_id: Foreign key to Story (nullable until story created)
        status: creating, iterating, complete, or error
        current_step: Current agent name
        progress_percent: Progress percentage (0-100)
        created_at: Creation timestamp
        completed_at: Completion timestamp
        error_message: Error message if status is error
    """
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)  # UUID
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="SET NULL"), nullable=True)

    status = Column(String(20), nullable=False)  # creating, iterating, complete, error
    current_step = Column(String(50), nullable=True)
    progress_percent = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    error_message = Column(Text, nullable=True)
```

**Alembic Configuration (`alembic.ini`)**:
```ini
[alembic]
script_location = app/alembic
prepend_sys_path = .
sqlalchemy.url = sqlite:///./data/database.db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**Initial Migration (`alembic/versions/001_initial_schema.py`)**:
```python
"""Initial schema

Revision ID: 001
Create Date: 2025-11-12
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial tables."""
    # Stories table
    op.create_table(
        'stories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('theme_id', sa.String(length=50), nullable=False),
        sa.Column('game_file_path', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('play_count', sa.Integer(), nullable=False),
        sa.Column('last_played', sa.DateTime(), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('template_id', sa.String(length=50), nullable=True),
        sa.Column('iteration_count', sa.Integer(), nullable=False),
        sa.Column('scene_count', sa.Integer(), nullable=True),
        sa.Column('item_count', sa.Integer(), nullable=True),
        sa.Column('npc_count', sa.Integer(), nullable=True),
        sa.Column('puzzle_count', sa.Integer(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_file_path')
    )
    op.create_index('idx_stories_created', 'stories', ['created_at'])
    op.create_index('idx_stories_theme', 'stories', ['theme_id'])

    # Iterations table
    op.create_table(
        'iterations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('story_id', sa.Integer(), nullable=False),
        sa.Column('iteration_number', sa.Integer(), nullable=False),
        sa.Column('feedback', sa.Text(), nullable=False),
        sa.Column('changes_requested', sa.JSON(), nullable=True),
        sa.Column('game_file_path', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['story_id'], ['stories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_iterations_story', 'iterations', ['story_id', 'iteration_number'])

    # Sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('story_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('current_step', sa.String(length=50), nullable=True),
        sa.Column('progress_percent', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['story_id'], ['stories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('sessions')
    op.drop_table('iterations')
    op.drop_table('stories')
```

### Testing Requirements

**`tests/test_models.py`**:
```python
"""Tests for database models."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from backend.app.models.base import Base
from backend.app.models.story import Story
from backend.app.models.iteration import Iteration
from backend.app.models.session import Session


@pytest.fixture
def db_session():
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_story(db_session):
    """Test creating a story."""
    story = Story(
        title="Test Story",
        description="Test description",
        theme_id="warhammer40k",
        game_file_path="/path/to/game.json",
        prompt="Test prompt",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(story)
    db_session.commit()

    assert story.id is not None
    assert story.title == "Test Story"
    assert story.play_count == 0


def test_create_iteration(db_session):
    """Test creating an iteration linked to a story."""
    story = Story(
        title="Test Story",
        game_file_path="/path/to/game.json",
        prompt="Test prompt",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(story)
    db_session.commit()

    iteration = Iteration(
        story_id=story.id,
        iteration_number=1,
        feedback="Make it scarier",
        game_file_path="/path/to/iteration_1.json",
        created_at=datetime.utcnow()
    )
    db_session.add(iteration)
    db_session.commit()

    assert iteration.id is not None
    assert iteration.story_id == story.id
    assert iteration.status == "pending"


def test_cascade_delete(db_session):
    """Test that deleting a story cascades to iterations."""
    story = Story(
        title="Test Story",
        game_file_path="/path/to/game.json",
        prompt="Test prompt",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(story)
    db_session.commit()

    iteration = Iteration(
        story_id=story.id,
        iteration_number=1,
        feedback="Test feedback",
        game_file_path="/path/to/iteration.json",
        created_at=datetime.utcnow()
    )
    db_session.add(iteration)
    db_session.commit()

    # Delete story
    db_session.delete(story)
    db_session.commit()

    # Iteration should be deleted due to CASCADE
    assert db_session.query(Iteration).count() == 0
```

### Validation Commands

```bash
# 1. Initialize Alembic
cd backend
alembic init app/alembic

# 2. Create data directory
mkdir -p data

# 3. Run migrations
alembic upgrade head

# 4. Verify tables created
sqlite3 data/database.db ".schema"

# 5. Run tests
pytest tests/test_models.py -v

# 6. Check code quality
ruff check .
mypy . --strict
```

### Success Indicators

✅ Alembic migrations run without errors
✅ All three tables created with correct schema
✅ Indexes exist on specified columns
✅ Foreign key relationships work
✅ Cascade delete works for iterations
✅ All tests pass
✅ No linting or type errors

---

## Task 1.3: Frontend Project Setup

**Priority**: P0
**Effort**: 1 day
**Dependencies**: None (parallel with backend)
**Can Run in Parallel**: 🔁 Yes

### Context

Initialize a React TypeScript application with Vite build tool, routing, base layout, and proper development environment configuration. This will serve as the foundation for the web interface.

### Your Mission

Create a modern React + TypeScript frontend with Vite, React Router, ESLint, Prettier, and a basic application structure with placeholder components for all main routes.

### Deliverables

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── main.tsx          # Entry point
│   ├── App.tsx           # Root component with routing
│   ├── components/
│   │   ├── Layout.tsx    # Main layout wrapper
│   │   └── common/
│   │       ├── Header.tsx
│   │       └── Footer.tsx
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── LibraryPage.tsx
│   │   ├── CreatePage.tsx
│   │   └── PlayPage.tsx
│   ├── contexts/
│   │   └── .gitkeep
│   ├── services/
│   │   └── .gitkeep
│   ├── styles/
│   │   └── index.css
│   └── types/
│       └── index.ts
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── .eslintrc.cjs
├── .prettierrc
└── README.md
```

### Acceptance Criteria

- [ ] `npm run dev` starts development server on `localhost:3000` or `localhost:5173`
- [ ] All routes render placeholder components: `/`, `/library`, `/create`, `/play/:id`
- [ ] TypeScript strict mode enabled with no errors
- [ ] ESLint configured with React + TypeScript rules
- [ ] Prettier configured for consistent formatting
- [ ] No console warnings when running dev server
- [ ] React Router v6 configured correctly
- [ ] Basic layout with header and main content area
- [ ] Hot module replacement (HMR) works

### Technical Requirements

**Vite Configuration (`vite.config.ts`)**:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
```

**TypeScript Configuration (`tsconfig.json`)**:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**App Component with Routing (`App.tsx`)**:
```typescript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LibraryPage from './pages/LibraryPage'
import CreatePage from './pages/CreatePage'
import PlayPage from './pages/PlayPage'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/create" element={<CreatePage />} />
          <Route path="/play/:id" element={<PlayPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
```

**Layout Component (`components/Layout.tsx`)**:
```typescript
import { ReactNode } from 'react'
import Header from './common/Header'
import Footer from './common/Footer'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  return (
    <div className="app-container">
      <Header />
      <main className="main-content">
        {children}
      </main>
      <Footer />
    </div>
  )
}

export default Layout
```

**Header Component (`components/common/Header.tsx`)**:
```typescript
import { Link } from 'react-router-dom'

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <h1>Space Hulk Game</h1>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/library">Library</Link>
          <Link to="/create">Create</Link>
        </nav>
      </div>
    </header>
  )
}

export default Header
```

**Placeholder Page (`pages/HomePage.tsx`)**:
```typescript
function HomePage() {
  return (
    <div className="page">
      <h2>Welcome to Space Hulk Game</h2>
      <p>Browser-based game creation and play interface</p>
    </div>
  )
}

export default HomePage
```

**Package.json**:
```json
{
  "name": "space-hulk-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\""
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.55.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "prettier": "^3.1.1",
    "typescript": "^5.2.2",
    "vite": "^5.0.8"
  }
}
```

**ESLint Configuration (`.eslintrc.cjs`)**:
```javascript
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
  },
}
```

**Prettier Configuration (`.prettierrc`)**:
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

**Basic Styles (`styles/index.css`)**:
```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  background-color: #1a1a1a;
  color: white;
  padding: 1rem 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header nav {
  display: flex;
  gap: 1.5rem;
}

.header nav a {
  color: white;
  text-decoration: none;
}

.header nav a:hover {
  text-decoration: underline;
}

.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}

.page {
  padding: 2rem 0;
}
```

### Validation Commands

```bash
# 1. Create project
cd frontend
npm install

# 2. Start dev server
npm run dev
# Visit: http://localhost:3000

# 3. Test routing
# Navigate to /, /library, /create in browser

# 4. Run linter
npm run lint

# 5. Check TypeScript
npx tsc --noEmit

# 6. Format code
npm run format

# 7. Build for production
npm run build
```

### Success Indicators

✅ Development server starts without errors
✅ All routes accessible and render correctly
✅ No TypeScript errors
✅ ESLint passes with no warnings
✅ Hot reload works when editing files
✅ Build command produces optimized bundle
✅ Browser console has no errors

---

## Task 1.4: Docker Compose Setup

**Priority**: P0
**Effort**: 1 day
**Dependencies**: Tasks 1.1, 1.2, 1.3

### Context

Create a Docker Compose configuration for local development that orchestrates all services: frontend, backend, Redis (for Celery), and PostgreSQL (optional, SQLite for MVP). This enables one-command startup of the entire development environment.

### Your Mission

Configure Docker Compose with services for frontend, backend, Redis, and optional PostgreSQL. Ensure hot reload works for development, services can communicate, and health checks verify all components are running.

### Deliverables

```
project-root/
├── docker-compose.yml
├── docker-compose.prod.yml  # Future production config
├── .env.example
├── .dockerignore
├── backend/
│   └── Dockerfile
└── frontend/
    └── Dockerfile
```

### Acceptance Criteria

- [ ] `docker-compose up` starts all services without errors
- [ ] Frontend accessible at `http://localhost:3000`
- [ ] Backend accessible at `http://localhost:8000`
- [ ] Backend can connect to Redis
- [ ] Backend can connect to database
- [ ] Hot reload works for both frontend and backend
- [ ] Services can communicate (frontend → backend → redis → db)
- [ ] Health checks pass for all services
- [ ] Logs are visible with `docker-compose logs`
- [ ] `docker-compose down` stops all services cleanly

### Technical Requirements

**Docker Compose (`docker-compose.yml`)**:
```yaml
version: '3.8'

services:
  # Frontend (React + Vite)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
    networks:
      - app-network

  # Backend (FastAPI)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./data:/app/data
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - DATABASE_URL=sqlite:///./data/database.db
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=INFO
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - app-network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Celery Worker (for async tasks)
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    volumes:
      - ./backend:/app
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./data/database.db
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=INFO
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - app-network
    command: celery -A app.celery_app worker --loglevel=info

  # Redis (message broker for Celery)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  # PostgreSQL (optional, for production)
  # postgres:
  #   image: postgres:15-alpine
  #   environment:
  #     - POSTGRES_USER=space_hulk
  #     - POSTGRES_PASSWORD=space_hulk_password
  #     - POSTGRES_DB=space_hulk_db
  #   ports:
  #     - "5432:5432"
  #   volumes:
  #     - postgres-data:/var/lib/postgresql/data
  #   networks:
  #     - app-network
  #   healthcheck:
  #     test: ["CMD-SHELL", "pg_isready -U space_hulk"]
  #     interval: 5s
  #     timeout: 3s
  #     retries: 5

networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
```

**Backend Dockerfile (`backend/Dockerfile`)**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile (`frontend/Dockerfile`)**:
```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

**Docker Ignore (`.dockerignore`)**:
```
# Backend
backend/__pycache__
backend/.pytest_cache
backend/.mypy_cache
backend/.ruff_cache
backend/*.pyc
backend/*.pyo
backend/*.pyd
backend/.env
backend/venv
backend/.venv

# Frontend
frontend/node_modules
frontend/dist
frontend/.env
frontend/.env.local

# Common
.git
.gitignore
*.md
docker-compose*.yml
.DS_Store
```

**Environment Template (`.env.example`)**:
```env
# Backend Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_ENVIRONMENT=development
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./data/database.db
# DATABASE_URL=postgresql://space_hulk:space_hulk_password@postgres:5432/space_hulk_db

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

### Testing Requirements

**Test Script (`test_docker_setup.sh`)**:
```bash
#!/bin/bash
set -e

echo "Testing Docker Compose setup..."

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Test backend health
echo "Testing backend health endpoint..."
curl -f http://localhost:8000/health || exit 1

# Test frontend
echo "Testing frontend..."
curl -f http://localhost:3000 || exit 1

# Test Redis connection
echo "Testing Redis..."
docker-compose exec -T redis redis-cli ping | grep -q "PONG" || exit 1

# Check service logs for errors
echo "Checking for errors in logs..."
docker-compose logs backend | grep -i "error" && exit 1 || true
docker-compose logs frontend | grep -i "error" && exit 1 || true

# Test backend-redis communication
echo "Testing backend-redis communication..."
docker-compose exec -T backend python -c "import redis; r = redis.from_url('redis://redis:6379/0'); r.ping()" || exit 1

echo "All tests passed!"

# Stop services
docker-compose down
```

### Validation Commands

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Build and start all services
docker-compose up --build

# 3. In separate terminal, check service status
docker-compose ps

# 4. Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs
# Visit http://localhost:3000 in browser

# 5. Check logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs redis

# 6. Test hot reload (edit a file and see if it reloads)

# 7. Run test script
chmod +x test_docker_setup.sh
./test_docker_setup.sh

# 8. Stop services
docker-compose down

# 9. Clean up volumes (if needed)
docker-compose down -v
```

### Success Indicators

✅ All services start without errors
✅ Frontend accessible in browser
✅ Backend health check returns 200
✅ Redis ping responds with PONG
✅ Backend can read/write to Redis
✅ Hot reload works for code changes
✅ Services communicate correctly
✅ Logs are visible and readable
✅ Services stop cleanly with docker-compose down

---

## Task 1.5: Celery Task Queue Setup

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 1.1, Docker Compose (Redis)

### Context

Configure Celery with Redis as the message broker for asynchronous task processing. This will enable long-running CrewAI generation tasks to run in the background without blocking the API.

### Your Mission

Set up Celery task queue with Redis broker, create example task, implement task result storage, and add proper error handling and retry logic.

### Deliverables

```
backend/
├── app/
│   ├── celery_app.py       # Celery application configuration
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── example_task.py  # Example task for testing
│   └── config.py           # Update with Celery settings
└── tests/
    └── test_celery.py
```

### Acceptance Criteria

- [ ] Celery worker starts successfully with `celery -A app.celery_app worker --loglevel=info`
- [ ] Example task executes and returns result
- [ ] Task results stored in Redis and retrievable
- [ ] Task status can be queried (pending, started, success, failure)
- [ ] Error handling works (task fails gracefully)
- [ ] Retry logic implemented with exponential backoff
- [ ] Task progress tracking works
- [ ] Integration with FastAPI works (can trigger tasks from API)
- [ ] Tests pass for task execution and failure scenarios

### Technical Requirements

**Celery Application (`celery_app.py`)**:
```python
"""Celery application configuration."""
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "space_hulk_game",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.example_task"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=900,  # 15 minutes
    task_soft_time_limit=840,  # 14 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,  # 1 hour
)


@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Log when task starts."""
    logger.info(f"Task started: {task.name} [{task_id}]")


@task_postrun.connect
def task_postrun_handler(task_id, task, *args, **kwargs):
    """Log when task completes."""
    logger.info(f"Task completed: {task.name} [{task_id}]")


@task_failure.connect
def task_failure_handler(task_id, exception, *args, **kwargs):
    """Log when task fails."""
    logger.error(f"Task failed: {task_id} - {exception}")
```

**Configuration Update (`config.py`)**:
```python
# Add to Settings class:

    # Redis & Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = Field(default="", validate_default=True)
    celery_result_backend: str = Field(default="", validate_default=True)

    @model_validator(mode='after')
    def set_celery_urls(self) -> 'Settings':
        """Set Celery URLs from Redis URL if not provided."""
        if not self.celery_broker_url:
            self.celery_broker_url = self.redis_url
        if not self.celery_result_backend:
            self.celery_result_backend = self.redis_url
        return self
```

**Example Task (`tasks/example_task.py`)**:
```python
"""Example Celery task for testing."""
import time
from celery import Task
from typing import Any

from ..celery_app import celery_app


class CallbackTask(Task):
    """Base task with callback support for progress tracking."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute task with progress tracking."""
        return super().__call__(*args, **kwargs)


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="app.tasks.example_task",
    max_retries=3,
    default_retry_delay=60,
)
def example_long_task(self, duration: int = 10) -> dict[str, Any]:
    """
    Example long-running task with progress tracking.

    Args:
        duration: How long the task should run (seconds)

    Returns:
        dict: Task result with status and data

    Raises:
        Exception: If task fails
    """
    try:
        total_steps = 5
        for i in range(total_steps):
            # Update task progress
            progress = int((i + 1) / total_steps * 100)
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": i + 1,
                    "total": total_steps,
                    "progress": progress,
                    "status": f"Processing step {i + 1}/{total_steps}"
                }
            )

            # Simulate work
            time.sleep(duration / total_steps)

        return {
            "status": "complete",
            "result": f"Task completed successfully after {duration} seconds",
            "data": {"steps_completed": total_steps}
        }

    except Exception as exc:
        # Retry with exponential backoff
        self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(name="app.tasks.example_failure_task")
def example_failure_task() -> None:
    """Example task that always fails (for testing error handling)."""
    raise ValueError("This task intentionally fails")


@celery_app.task(name="app.tasks.simple_add")
def simple_add(x: int, y: int) -> int:
    """Simple addition task for basic testing."""
    return x + y
```

**FastAPI Integration (`main.py` - add endpoints)**:
```python
from celery.result import AsyncResult

@app.post("/api/v1/tasks/example")
async def trigger_example_task(duration: int = 10) -> dict[str, str]:
    """
    Trigger an example long-running task.

    Args:
        duration: How long the task should run (seconds)

    Returns:
        dict: Task ID for status checking
    """
    from .tasks.example_task import example_long_task
    task = example_long_task.delay(duration)
    return {"task_id": task.id, "status": "started"}


@app.get("/api/v1/tasks/{task_id}/status")
async def get_task_status(task_id: str) -> dict[str, Any]:
    """
    Get status of a running task.

    Args:
        task_id: Celery task ID

    Returns:
        dict: Task status and result/progress
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state == "PENDING":
        response = {
            "state": task_result.state,
            "status": "Task is waiting to start"
        }
    elif task_result.state == "PROGRESS":
        response = {
            "state": task_result.state,
            "progress": task_result.info.get("progress", 0),
            "status": task_result.info.get("status", "")
        }
    elif task_result.state == "SUCCESS":
        response = {
            "state": task_result.state,
            "result": task_result.result
        }
    elif task_result.state == "FAILURE":
        response = {
            "state": task_result.state,
            "error": str(task_result.info)
        }
    else:
        response = {
            "state": task_result.state,
            "status": "Unknown state"
        }

    return response
```

### Testing Requirements

**`tests/test_celery.py`**:
```python
"""Tests for Celery task execution."""
import pytest
from celery import Celery
from celery.result import AsyncResult

from backend.app.celery_app import celery_app
from backend.app.tasks.example_task import simple_add, example_failure_task


@pytest.fixture
def celery_config():
    """Celery test configuration."""
    return {
        "broker_url": "redis://localhost:6379/1",  # Use different DB for tests
        "result_backend": "redis://localhost:6379/1",
        "task_always_eager": True,  # Execute tasks synchronously for testing
        "task_eager_propagates": True,
    }


def test_simple_task_execution():
    """Test basic task execution."""
    result = simple_add.apply_async(args=[4, 6])
    assert result.get() == 10


def test_task_failure_handling():
    """Test task failure is handled correctly."""
    with pytest.raises(ValueError):
        result = example_failure_task.apply_async()
        result.get()


def test_task_status_tracking():
    """Test task status can be queried."""
    result = simple_add.apply_async(args=[2, 3])

    assert result.state in ["PENDING", "SUCCESS"]
    assert result.get() == 5
    assert result.state == "SUCCESS"


def test_task_result_storage():
    """Test task results are stored and retrievable."""
    result = simple_add.apply_async(args=[10, 20])
    task_id = result.id

    # Retrieve result using task ID
    retrieved = AsyncResult(task_id, app=celery_app)
    assert retrieved.get() == 30
```

**Integration Test (`tests/test_celery_integration.py`)**:
```python
"""Integration tests for Celery with FastAPI."""
import pytest
from httpx import AsyncClient
import asyncio

from backend.app.main import app


@pytest.mark.asyncio
async def test_trigger_task_via_api():
    """Test triggering Celery task through API endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/tasks/example?duration=1")
        assert response.status_code == 200

        data = response.json()
        assert "task_id" in data
        assert data["status"] == "started"


@pytest.mark.asyncio
async def test_check_task_status_via_api():
    """Test checking task status through API endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Trigger task
        response = await client.post("/api/v1/tasks/example?duration=1")
        task_id = response.json()["task_id"]

        # Wait a bit
        await asyncio.sleep(0.5)

        # Check status
        status_response = await client.get(f"/api/v1/tasks/{task_id}/status")
        assert status_response.status_code == 200

        status_data = status_response.json()
        assert "state" in status_data
        assert status_data["state"] in ["PENDING", "PROGRESS", "SUCCESS"]
```

### Validation Commands

```bash
# 1. Start Redis (if not in Docker)
docker-compose up redis -d

# 2. Start Celery worker
cd backend
celery -A app.celery_app worker --loglevel=info

# 3. In another terminal, test task execution
python -c "
from app.tasks.example_task import simple_add
result = simple_add.delay(4, 6)
print(f'Task ID: {result.id}')
print(f'Result: {result.get()}')
"

# 4. Test via API (start backend first)
# Start backend: uvicorn app.main:app --reload
curl -X POST http://localhost:8000/api/v1/tasks/example?duration=5
# Copy task_id from response
curl http://localhost:8000/api/v1/tasks/{task_id}/status

# 5. Run tests
pytest tests/test_celery.py -v

# 6. Monitor Celery tasks with Flower (optional)
pip install flower
celery -A app.celery_app flower
# Visit: http://localhost:5555
```

### Success Indicators

✅ Celery worker starts and connects to Redis
✅ Tasks execute successfully
✅ Task results are stored and retrievable
✅ Task status updates correctly
✅ Error handling works (retries, failures)
✅ Progress tracking works
✅ API integration works
✅ All tests pass

---

## Task 1.6: CI/CD Pipeline

**Priority**: P1
**Effort**: 1 day
**Dependencies**: Tasks 1.1, 1.3
**Can Run in Parallel**: 🔁 Yes (with other tasks)

### Context

Set up GitHub Actions workflows for continuous integration and continuous deployment. Automate testing, linting, type checking, and building for both backend and frontend.

### Your Mission

Create GitHub Actions workflows that run on pull requests and pushes to main branch. Workflows should test backend (pytest, ruff, mypy) and frontend (ESLint, TypeScript, tests), and optionally build Docker images.

### Deliverables

```
.github/
└── workflows/
    ├── backend-ci.yml      # Backend testing pipeline
    ├── frontend-ci.yml     # Frontend testing pipeline
    └── docker-build.yml    # Docker image building (optional)
```

### Acceptance Criteria

- [ ] Backend CI runs: ruff, mypy, pytest on every PR
- [ ] Frontend CI runs: ESLint, TypeScript check, tests on every PR
- [ ] CI fails if any check fails
- [ ] CI runs on pull requests and pushes to main
- [ ] Test results are reported in PR
- [ ] CI completes in < 5 minutes
- [ ] Workflows are properly documented
- [ ] Status badges can be added to README

### Technical Requirements

**Backend CI Workflow (`.github/workflows/backend-ci.yml`)**:
```yaml
name: Backend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/**'
      - '.github/workflows/backend-ci.yml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'backend/**'
      - '.github/workflows/backend-ci.yml'

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.10', '3.11']

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache pip dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        working-directory: backend
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt -r requirements-dev.txt

      - name: Run ruff linting
        working-directory: backend
        run: ruff check .

      - name: Run mypy type checking
        working-directory: backend
        run: mypy . --strict

      - name: Run pytest
        working-directory: backend
        run: |
          pytest --verbose --cov=app --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: backend/coverage.xml
          flags: backend
          fail_ci_if_error: false

  lint-formatting:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install ruff
        run: pip install ruff

      - name: Check formatting
        working-directory: backend
        run: ruff format --check .
```

**Frontend CI Workflow (`.github/workflows/frontend-ci.yml`)**:
```yaml
name: Frontend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18, 20]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}

      - name: Cache node modules
        uses: actions/cache@v3
        with:
          path: frontend/node_modules
          key: ${{ runner.os }}-node-${{ matrix.node-version }}-${{ hashFiles('frontend/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-node-${{ matrix.node-version }}-

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Run ESLint
        working-directory: frontend
        run: npm run lint

      - name: Run TypeScript check
        working-directory: frontend
        run: npx tsc --noEmit

      - name: Run tests (if configured)
        working-directory: frontend
        run: npm test -- --passWithNoTests

      - name: Build application
        working-directory: frontend
        run: npm run build

  formatting:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Check formatting with Prettier
        working-directory: frontend
        run: npx prettier --check "src/**/*.{ts,tsx,css}"
```

**Docker Build Workflow (`.github/workflows/docker-build.yml`)**:
```yaml
name: Docker Build

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-backend:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: false
          tags: space-hulk-backend:test
          cache-from: type=gha
          cache-to: type=gha,mode=max

  build-frontend:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: false
          tags: space-hulk-frontend:test
          cache-from: type=gha
          cache-to: type=gha,mode=max

  test-docker-compose:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Create .env file
        run: cp .env.example .env

      - name: Start services with docker-compose
        run: docker-compose up -d

      - name: Wait for services
        run: sleep 15

      - name: Check backend health
        run: curl --fail http://localhost:8000/health

      - name: Check frontend
        run: curl --fail http://localhost:3000

      - name: Show logs on failure
        if: failure()
        run: |
          docker-compose logs backend
          docker-compose logs frontend

      - name: Stop services
        run: docker-compose down
```

**README Status Badges**:
```markdown
# Add to project README.md

[![Backend CI](https://github.com/YOUR_USERNAME/space_hulk_game/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/space_hulk_game/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/YOUR_USERNAME/space_hulk_game/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/space_hulk_game/actions/workflows/frontend-ci.yml)
[![Docker Build](https://github.com/YOUR_USERNAME/space_hulk_game/actions/workflows/docker-build.yml/badge.svg)](https://github.com/YOUR_USERNAME/space_hulk_game/actions/workflows/docker-build.yml)
```

### Testing Requirements

**Test Workflow Locally with Act** (optional):
```bash
# Install act (GitHub Actions local runner)
# macOS: brew install act
# Linux: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Test backend CI locally
act -W .github/workflows/backend-ci.yml

# Test frontend CI locally
act -W .github/workflows/frontend-ci.yml
```

### Validation Commands

```bash
# 1. Commit and push workflow files
git add .github/workflows/
git commit -m "Add CI/CD workflows"
git push

# 2. Create a test PR to trigger workflows
git checkout -b test-ci
# Make a small change
echo "# Test" >> backend/README.md
git add backend/README.md
git commit -m "Test CI workflow"
git push origin test-ci

# 3. Open PR on GitHub and check Actions tab

# 4. Verify workflows appear and run

# 5. Check that all checks pass (green checkmarks)

# 6. Test failure case (introduce a linting error)
# Edit a file to violate linting rules
# Push and verify CI fails

# 7. Fix the error and verify CI passes again
```

### Success Indicators

✅ Workflows appear in GitHub Actions tab
✅ All checks run on PR creation
✅ Tests pass with green checkmarks
✅ Failures are reported clearly
✅ Test results shown in PR
✅ Workflows complete in < 5 minutes
✅ Status badges work in README

---

## Task 1.7: API Client & Error Handling

**Priority**: P0
**Effort**: 1 day
**Dependencies**: Task 1.3

### Context

Create a TypeScript API client for the frontend that handles all communication with the backend. Include proper error handling, retry logic, request/response type safety, and interceptors for common concerns.

### Your Mission

Build a typed API client using Axios with error handling, retry logic for transient failures, request/response interceptors, and TypeScript interfaces for all API endpoints.

### Deliverables

```
frontend/
└── src/
    ├── services/
    │   ├── api.ts              # Main API client
    │   └── types.ts            # API type definitions
    ├── utils/
    │   ├── errorHandler.ts     # Error handling utilities
    │   └── retryLogic.ts       # Retry logic utilities
    └── tests/
        ├── api.test.ts
        └── errorHandler.test.ts
```

### Acceptance Criteria

- [ ] Typed methods for all planned endpoints (stories, generation, gameplay, themes)
- [ ] Axios interceptors for requests and responses
- [ ] Network error handling (timeout, connection refused, etc.)
- [ ] HTTP error handling (404, 500, etc.)
- [ ] Retry logic for transient failures (503, network errors)
- [ ] Request timeout configuration
- [ ] User-friendly error messages
- [ ] Loading states management
- [ ] Tests for successful calls, network errors, HTTP errors
- [ ] All code typed with TypeScript
- [ ] No console errors or warnings

### Technical Requirements

**API Types (`services/types.ts`)**:
```typescript
// Common types
export interface ApiResponse<T> {
  data: T
  meta?: {
    timestamp: string
    version: string
  }
}

export interface ApiError {
  code: string
  message: string
  user_message: string
  retry_possible: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_next: boolean
}

// Story types
export interface Story {
  id: number
  title: string
  description: string | null
  theme_id: string
  created_at: string
  updated_at: string
  play_count: number
  last_played: string | null
  prompt: string
  template_id: string | null
  iteration_count: number
  scene_count: number | null
  item_count: number | null
  npc_count: number | null
  puzzle_count: number | null
  tags: string[]
}

export interface CreateStoryRequest {
  prompt: string
  template_id?: string
  theme_id?: string
}

export interface IterationRequest {
  story_id: number
  feedback: string
  changes_requested?: Record<string, any>
}

// Generation types
export interface GenerationSession {
  id: string
  story_id: number | null
  status: 'creating' | 'iterating' | 'complete' | 'error'
  current_step: string | null
  progress_percent: number
  created_at: string
  completed_at: string | null
  error_message: string | null
}

// Game types
export interface GameSession {
  session_id: string
  story_id: number
  current_scene: string
  inventory: string[]
  game_over: boolean
}

export interface GameCommand {
  command: string
}

export interface GameResponse {
  output: string
  state: Record<string, any>
  valid: boolean
  game_over: boolean
}

// Theme types
export interface Theme {
  id: string
  name: string
  description: string
  colors: Record<string, string>
  fonts: Record<string, string>
}
```

**API Client (`services/api.ts`)**:
```typescript
import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios'
import { retryRequest } from '../utils/retryLogic'
import { handleApiError } from '../utils/errorHandler'
import type {
  ApiResponse,
  PaginatedResponse,
  Story,
  CreateStoryRequest,
  GenerationSession,
  GameSession,
  GameCommand,
  GameResponse,
  Theme,
} from './types'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add timestamp to requests
        config.headers['X-Request-Time'] = new Date().toISOString()

        // Add any auth tokens here in future
        // const token = localStorage.getItem('auth_token')
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`
        // }

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Log successful responses in dev mode
        if (import.meta.env.DEV) {
          console.log(`API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
        }
        return response
      },
      async (error: AxiosError) => {
        // Handle errors
        if (error.response) {
          // Server responded with error status
          console.error('API Error Response:', error.response.status, error.response.data)
        } else if (error.request) {
          // Request made but no response received
          console.error('API No Response:', error.request)
        } else {
          // Error in request setup
          console.error('API Request Error:', error.message)
        }

        // Retry logic for specific errors
        if (this.shouldRetry(error)) {
          return retryRequest(this.client, error.config!, 3)
        }

        throw handleApiError(error)
      }
    )
  }

  private shouldRetry(error: AxiosError): boolean {
    // Retry on network errors or 503 Service Unavailable
    if (!error.response) return true
    if (error.response.status === 503) return true
    return false
  }

  // Story endpoints
  async getStories(params?: {
    page?: number
    page_size?: number
    search?: string
    theme_id?: string
    tags?: string[]
  }): Promise<PaginatedResponse<Story>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<Story>>>('/api/v1/stories', { params })
    return response.data.data
  }

  async getStory(id: number): Promise<Story> {
    const response = await this.client.get<ApiResponse<Story>>(`/api/v1/stories/${id}`)
    return response.data.data
  }

  async createStory(data: CreateStoryRequest): Promise<GenerationSession> {
    const response = await this.client.post<ApiResponse<GenerationSession>>('/api/v1/stories', data)
    return response.data.data
  }

  async deleteStory(id: number): Promise<void> {
    await this.client.delete(`/api/v1/stories/${id}`)
  }

  // Generation endpoints
  async getGenerationStatus(sessionId: string): Promise<GenerationSession> {
    const response = await this.client.get<ApiResponse<GenerationSession>>(`/api/v1/generate/${sessionId}`)
    return response.data.data
  }

  // Game endpoints
  async startGame(storyId: number): Promise<GameSession> {
    const response = await this.client.post<ApiResponse<GameSession>>(`/api/v1/game/${storyId}/start`)
    return response.data.data
  }

  async sendCommand(sessionId: string, command: GameCommand): Promise<GameResponse> {
    const response = await this.client.post<ApiResponse<GameResponse>>(
      `/api/v1/game/${sessionId}/command`,
      command
    )
    return response.data.data
  }

  async saveGame(sessionId: string, saveName: string): Promise<{ save_id: string }> {
    const response = await this.client.post<ApiResponse<{ save_id: string }>>(
      `/api/v1/game/${sessionId}/save`,
      { name: saveName }
    )
    return response.data.data
  }

  // Theme endpoints
  async getThemes(): Promise<Theme[]> {
    const response = await this.client.get<ApiResponse<Theme[]>>('/api/v1/themes')
    return response.data.data
  }

  async getTheme(themeId: string): Promise<Theme> {
    const response = await this.client.get<ApiResponse<Theme>>(`/api/v1/themes/${themeId}`)
    return response.data.data
  }
}

export const apiClient = new ApiClient()
export default apiClient
```

**Error Handler (`utils/errorHandler.ts`)**:
```typescript
import { AxiosError } from 'axios'
import type { ApiError } from '../services/types'

export class AppError extends Error {
  code: string
  userMessage: string
  retryPossible: boolean
  status?: number

  constructor(
    code: string,
    message: string,
    userMessage: string,
    retryPossible: boolean = false,
    status?: number
  ) {
    super(message)
    this.name = 'AppError'
    this.code = code
    this.userMessage = userMessage
    this.retryPossible = retryPossible
    this.status = status
  }
}

export function handleApiError(error: AxiosError): AppError {
  if (error.response) {
    // Server responded with error
    const status = error.response.status
    const errorData = error.response.data as ApiError | undefined

    if (errorData?.user_message) {
      return new AppError(
        errorData.code,
        errorData.message,
        errorData.user_message,
        errorData.retry_possible,
        status
      )
    }

    // Default error messages by status code
    switch (status) {
      case 400:
        return new AppError(
          'BAD_REQUEST',
          error.message,
          'Invalid request. Please check your input and try again.',
          false,
          status
        )
      case 404:
        return new AppError(
          'NOT_FOUND',
          error.message,
          'The requested resource was not found.',
          false,
          status
        )
      case 500:
        return new AppError(
          'SERVER_ERROR',
          error.message,
          'A server error occurred. Please try again later.',
          true,
          status
        )
      case 503:
        return new AppError(
          'SERVICE_UNAVAILABLE',
          error.message,
          'The service is temporarily unavailable. Please try again.',
          true,
          status
        )
      default:
        return new AppError(
          'UNKNOWN_ERROR',
          error.message,
          'An unexpected error occurred. Please try again.',
          true,
          status
        )
    }
  } else if (error.request) {
    // Request made but no response
    return new AppError(
      'NETWORK_ERROR',
      'No response from server',
      'Unable to connect to the server. Please check your internet connection.',
      true
    )
  } else {
    // Error in request setup
    return new AppError(
      'REQUEST_ERROR',
      error.message,
      'An error occurred while making the request. Please try again.',
      true
    )
  }
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof AppError) {
    return error.userMessage
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unknown error occurred'
}
```

**Retry Logic (`utils/retryLogic.ts`)**:
```typescript
import { AxiosInstance, AxiosRequestConfig } from 'axios'

export async function retryRequest(
  client: AxiosInstance,
  config: AxiosRequestConfig,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<any> {
  let lastError: any

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await client.request(config)
    } catch (error) {
      lastError = error

      if (i < maxRetries - 1) {
        // Exponential backoff
        const waitTime = delay * Math.pow(2, i)
        console.log(`Retry ${i + 1}/${maxRetries} after ${waitTime}ms...`)
        await new Promise((resolve) => setTimeout(resolve, waitTime))
      }
    }
  }

  throw lastError
}
```

### Testing Requirements

**`tests/api.test.ts`**:
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { apiClient } from '../services/api'

// Mock axios
vi.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should fetch stories successfully', async () => {
    const mockStories = {
      items: [
        { id: 1, title: 'Test Story', description: 'Test', theme_id: 'warhammer40k' },
      ],
      total: 1,
      page: 1,
      page_size: 20,
      has_next: false,
    }

    mockedAxios.get.mockResolvedValueOnce({
      data: { data: mockStories },
    })

    const stories = await apiClient.getStories()
    expect(stories).toEqual(mockStories)
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/stories', { params: undefined })
  })

  it('should handle network errors', async () => {
    mockedAxios.get.mockRejectedValueOnce({
      request: {},
      message: 'Network Error',
    })

    await expect(apiClient.getStories()).rejects.toThrow('Unable to connect to the server')
  })

  it('should handle 404 errors', async () => {
    mockedAxios.get.mockRejectedValueOnce({
      response: {
        status: 404,
        data: {},
      },
      message: 'Not Found',
    })

    await expect(apiClient.getStory(999)).rejects.toThrow('The requested resource was not found')
  })
})
```

**Add to `package.json`**:
```json
{
  "scripts": {
    "test": "vitest"
  },
  "devDependencies": {
    "vitest": "^1.0.0",
    "@vitest/ui": "^1.0.0"
  }
}
```

### Validation Commands

```bash
# 1. Install dependencies
cd frontend
npm install axios

# 2. Run TypeScript check
npx tsc --noEmit

# 3. Test API client (with backend running)
# Create a test file: test-api.ts
# Run: npx tsx test-api.ts

# 4. Run tests
npm test

# 5. Build to ensure no errors
npm run build

# 6. Test in browser
npm run dev
# Open console and test API calls
```

### Success Indicators

✅ API client compiles without TypeScript errors
✅ All endpoints are typed correctly
✅ Error handling works for different scenarios
✅ Retry logic works for transient failures
✅ Interceptors log requests/responses
✅ Tests pass for success and error cases
✅ No console warnings in browser

---

## Phase 1 Completion Checklist

After completing all 7 tasks, verify the following:

### Infrastructure
- [ ] Backend API server runs on port 8000
- [ ] Frontend dev server runs on port 3000
- [ ] Docker Compose starts all services
- [ ] Redis is accessible and working
- [ ] Database migrations run successfully

### Code Quality
- [ ] All backend code passes `ruff check`
- [ ] All backend code passes `mypy --strict`
- [ ] All frontend code passes ESLint
- [ ] All frontend code passes TypeScript check
- [ ] All tests pass (backend and frontend)

### CI/CD
- [ ] GitHub Actions workflows run on PR
- [ ] All CI checks pass
- [ ] Status badges work in README

### Integration
- [ ] Frontend can call backend API
- [ ] Backend can connect to Redis
- [ ] Celery worker can execute tasks
- [ ] API client handles errors gracefully

### Documentation
- [ ] README updated with setup instructions
- [ ] Environment variables documented
- [ ] API endpoints documented (OpenAPI)
- [ ] Docker Compose documented

---

## Next Steps After Phase 1

Once Phase 1 is complete, you're ready to move on to:

**Phase 2: Story Library (Weeks 5-6)**
- Task 2.1: Story Service & Repository
- Task 2.2: Story API Endpoints
- Task 2.3: Theme System - Backend
- Task 2.4: Theme API Endpoints
- Task 2.5: Story Library UI - Components
- Task 2.6: Story Library UI - Integration
- Task 2.7: Theme Selector UI

---

**Document Version**: 1.0
**Last Updated**: 2025-11-12
**Status**: Ready for Implementation
