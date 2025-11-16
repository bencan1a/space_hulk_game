# Comprehensive Testing Strategy

## Web Interface Browser-Based Game Platform

**Version**: 1.0
**Created**: 2025-11-12
**Author**: QA Engineer & Testing Architect
**Related**: ARCHITECTURAL_DESIGN.md, IMPLEMENTATION_PLAN.md, API_SPECIFICATION.md

---

## Table of Contents

1. [Testing Philosophy](#1-testing-philosophy)
2. [Unit Testing](#2-unit-testing)
3. [Integration Testing](#3-integration-testing)
4. [End-to-End Testing](#4-end-to-end-testing)
5. [Performance Testing](#5-performance-testing)
6. [Accessibility Testing](#6-accessibility-testing)
7. [Security Testing](#7-security-testing)
8. [Test Data Management](#8-test-data-management)
9. [Continuous Integration](#9-continuous-integration)
10. [Test Execution Plan](#10-test-execution-plan)

---

## 1. Testing Philosophy

### 1.1 Testing Pyramid

```
                 /\
                /  \    E2E Tests (10%)
               /____\   ~15 critical journeys
              /      \
             /        \ Integration Tests (30%)
            /__________\ ~50 API/component integration tests
           /            \
          /              \ Unit Tests (60%)
         /________________\ ~100+ isolated tests
```

**Distribution**:

- **60% Unit Tests**: Fast, isolated, comprehensive coverage
- **30% Integration Tests**: API contracts, database operations, component integration
- **10% E2E Tests**: Critical user journeys, cross-browser validation

### 1.2 Coverage Targets

**Backend (Python)**:

- Overall coverage: **90%+**
- Critical paths (generation, gameplay): **95%+**
- Service layer: **95%+**
- API routes: **85%+**
- Models/repositories: **90%+**

**Frontend (TypeScript/React)**:

- Overall coverage: **80%+**
- Critical components (creation flow, gameplay): **90%+**
- Context providers: **85%+**
- UI components: **75%+**
- Utility functions: **95%+**

**100% Coverage Required For**:

- Authentication logic (future)
- Payment processing (future)
- Data deletion operations
- Security validation
- Critical game state transitions

### 1.3 Test-First Approach

**High-Risk Components** (write tests before implementation):

- CrewAI wrapper integration
- Game engine wrapper
- WebSocket progress handler
- Game state management
- File system operations
- Database migrations

**Standard Components** (test alongside implementation):

- API endpoints
- Service layer methods
- React components
- Data models

### 1.4 Testing Standards

**All Tests Must**:

- Be deterministic (no flaky tests)
- Run in isolation (no shared state)
- Have clear arrange-act-assert structure
- Include descriptive names (what is being tested)
- Be fast (unit: <100ms, integration: <1s, E2E: <30s)
- Clean up after themselves (database, files, mocks)

---

## 2. Unit Testing

### 2.1 Backend Unit Tests (pytest)

**Framework**: pytest with pytest-cov, pytest-mock, pytest-asyncio

**Structure**:

```
tests/
├── unit/
│   ├── services/
│   │   ├── test_story_service.py
│   │   ├── test_generation_service.py
│   │   ├── test_game_service.py
│   │   ├── test_iteration_service.py
│   │   └── test_theme_service.py
│   ├── repositories/
│   │   ├── test_story_repository.py
│   │   └── test_iteration_repository.py
│   ├── integrations/
│   │   ├── test_crewai_wrapper.py
│   │   └── test_game_wrapper.py
│   └── utils/
│       ├── test_validators.py
│       └── test_file_helpers.py
```

#### 2.1.1 StoryService Tests (15 tests)

```python
# tests/unit/services/test_story_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.story_service import StoryService
from app.models.story import Story

@pytest.fixture
def story_service():
    """Fixture providing StoryService with mocked dependencies."""
    mock_db = Mock()
    return StoryService(db=mock_db)

@pytest.fixture
def sample_story():
    """Fixture providing a sample story."""
    return Story(
        id="550e8400-e29b-41d4-a716-446655440000",
        title="Test Story",
        description="A test story",
        theme_id="warhammer40k",
        game_file_path="/stories/test/game.json",
        prompt="Test prompt"
    )

# Test: Create story
def test_create_story_success(story_service):
    """Test successful story creation."""
    # Arrange
    story_data = {
        "title": "New Story",
        "description": "A new story",
        "theme_id": "warhammer40k",
        "prompt": "Create an adventure"
    }

    # Act
    story = story_service.create(story_data)

    # Assert
    assert story.title == "New Story"
    assert story.theme_id == "warhammer40k"
    story_service.db.add.assert_called_once()
    story_service.db.commit.assert_called_once()

def test_create_story_invalid_theme(story_service):
    """Test story creation with invalid theme raises error."""
    # Arrange
    story_data = {
        "title": "New Story",
        "theme_id": "invalid_theme",
        "prompt": "Test"
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid theme"):
        story_service.create(story_data)

# Test: Get story by ID
def test_get_story_by_id_success(story_service, sample_story):
    """Test successful retrieval of story by ID."""
    # Arrange
    story_service.db.query().filter().first.return_value = sample_story

    # Act
    story = story_service.get_by_id("550e8400-e29b-41d4-a716-446655440000")

    # Assert
    assert story.id == sample_story.id
    assert story.title == "Test Story"

def test_get_story_by_id_not_found(story_service):
    """Test retrieval of non-existent story returns None."""
    # Arrange
    story_service.db.query().filter().first.return_value = None

    # Act
    story = story_service.get_by_id("invalid-id")

    # Assert
    assert story is None

# Test: List stories with filters
def test_list_stories_with_search(story_service, sample_story):
    """Test listing stories with search query."""
    # Arrange
    story_service.db.query().filter().offset().limit().all.return_value = [sample_story]
    story_service.db.query().filter().count.return_value = 1

    # Act
    result = story_service.list(search="Test", page=1, per_page=20)

    # Assert
    assert len(result["stories"]) == 1
    assert result["total"] == 1
    assert result["stories"][0].title == "Test Story"

def test_list_stories_with_theme_filter(story_service, sample_story):
    """Test listing stories filtered by theme."""
    # Arrange
    story_service.db.query().filter().offset().limit().all.return_value = [sample_story]

    # Act
    result = story_service.list(theme="warhammer40k")

    # Assert
    assert len(result["stories"]) == 1
    assert result["stories"][0].theme_id == "warhammer40k"

def test_list_stories_pagination(story_service):
    """Test story listing pagination."""
    # Arrange
    stories = [Mock(id=f"id_{i}") for i in range(5)]
    story_service.db.query().filter().offset().limit().all.return_value = stories[2:4]
    story_service.db.query().filter().count.return_value = 5

    # Act
    result = story_service.list(page=2, per_page=2)

    # Assert
    assert len(result["stories"]) == 2
    assert result["pagination"]["page"] == 2
    assert result["pagination"]["pages"] == 3

def test_list_stories_sort_newest(story_service, sample_story):
    """Test story listing sorted by newest first."""
    # Arrange
    story_service.db.query().filter().order_by().offset().limit().all.return_value = [sample_story]

    # Act
    result = story_service.list(sort="newest")

    # Assert
    story_service.db.query().filter().order_by.assert_called()

def test_list_stories_sort_most_played(story_service, sample_story):
    """Test story listing sorted by play count."""
    # Arrange
    story_service.db.query().filter().order_by().offset().limit().all.return_value = [sample_story]

    # Act
    result = story_service.list(sort="most_played")

    # Assert
    story_service.db.query().filter().order_by.assert_called()

# Test: Update story
def test_update_story_success(story_service, sample_story):
    """Test successful story update."""
    # Arrange
    story_service.db.query().filter().first.return_value = sample_story

    # Act
    updated = story_service.update("550e8400-e29b-41d4-a716-446655440000", {"title": "Updated Title"})

    # Assert
    assert updated.title == "Updated Title"
    story_service.db.commit.assert_called_once()

def test_update_story_not_found(story_service):
    """Test updating non-existent story raises error."""
    # Arrange
    story_service.db.query().filter().first.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="Story not found"):
        story_service.update("invalid-id", {"title": "New"})

# Test: Delete story
def test_delete_story_success(story_service, sample_story):
    """Test successful story deletion."""
    # Arrange
    story_service.db.query().filter().first.return_value = sample_story

    # Act
    story_service.delete("550e8400-e29b-41d4-a716-446655440000")

    # Assert
    story_service.db.delete.assert_called_once_with(sample_story)
    story_service.db.commit.assert_called_once()

def test_delete_sample_story_forbidden(story_service, sample_story):
    """Test deleting sample story raises error."""
    # Arrange
    sample_story.is_sample = True
    story_service.db.query().filter().first.return_value = sample_story

    # Act & Assert
    with pytest.raises(ValueError, match="Cannot delete sample"):
        story_service.delete("550e8400-e29b-41d4-a716-446655440000")

def test_delete_story_with_active_session(story_service, sample_story):
    """Test deleting story with active game session."""
    # Arrange
    story_service.db.query().filter().first.return_value = sample_story
    story_service._has_active_sessions = Mock(return_value=True)

    # Act & Assert
    with pytest.raises(ValueError, match="active game sessions"):
        story_service.delete("550e8400-e29b-41d4-a716-446655440000")

# Test: Get story content
def test_get_story_content_success(story_service, sample_story):
    """Test retrieving full story game content."""
    # Arrange
    story_service.db.query().filter().first.return_value = sample_story
    mock_content = {"plot": {}, "narrative_map": {}}

    with patch("builtins.open", mock_open(read_data='{"plot": {}}')) as mock_file:
        # Act
        content = story_service.get_content("550e8400-e29b-41d4-a716-446655440000")

        # Assert
        assert "plot" in content
        mock_file.assert_called()

def test_get_story_content_file_not_found(story_service, sample_story):
    """Test retrieving content when file is missing."""
    # Arrange
    story_service.db.query().filter().first.return_value = sample_story

    with patch("builtins.open", side_effect=FileNotFoundError):
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            story_service.get_content("550e8400-e29b-41d4-a716-446655440000")
```

**Total StoryService Tests**: 15

#### 2.1.2 GenerationService Tests (12 tests)

```python
# tests/unit/services/test_generation_service.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.generation_service import GenerationService

def test_start_generation_success():
    """Test starting a new story generation."""
    # Arrange
    service = GenerationService()
    prompt = "Create a horror adventure"

    # Act
    job = service.start_generation(prompt=prompt, theme_id="warhammer40k")

    # Assert
    assert job.status == "queued"
    assert job.generation_job_id is not None
    assert job.story_id is not None

def test_start_generation_invalid_prompt():
    """Test generation with invalid prompt."""
    # Arrange
    service = GenerationService()

    # Act & Assert
    with pytest.raises(ValueError, match="too short"):
        service.start_generation(prompt="Hi", theme_id="warhammer40k")

def test_start_generation_concurrent_limit():
    """Test concurrent generation limit enforcement."""
    # Arrange
    service = GenerationService()
    service._has_active_generation = Mock(return_value=True)

    # Act & Assert
    with pytest.raises(ValueError, match="already in progress"):
        service.start_generation(prompt="Test prompt", theme_id="warhammer40k")

def test_get_generation_status_queued():
    """Test retrieving status of queued generation."""
    # Arrange
    service = GenerationService()
    job_id = "660e8400-e29b-41d4-a716-446655440001"
    service._get_job = Mock(return_value=Mock(status="queued", progress_percent=0))

    # Act
    status = service.get_status(job_id)

    # Assert
    assert status["status"] == "queued"
    assert status["progress_percent"] == 0

def test_get_generation_status_in_progress():
    """Test retrieving status of in-progress generation."""
    # Arrange
    service = GenerationService()
    job_id = "660e8400-e29b-41d4-a716-446655440001"
    service._get_job = Mock(return_value=Mock(
        status="in_progress",
        progress_percent=45,
        current_agent="NarrativeArchitect"
    ))

    # Act
    status = service.get_status(job_id)

    # Assert
    assert status["status"] == "in_progress"
    assert status["progress_percent"] == 45
    assert status["current_agent"] == "NarrativeArchitect"

def test_get_generation_status_completed():
    """Test retrieving status of completed generation."""
    # Arrange
    service = GenerationService()
    job_id = "660e8400-e29b-41d4-a716-446655440001"
    story_id = "550e8400-e29b-41d4-a716-446655440000"
    service._get_job = Mock(return_value=Mock(
        status="completed",
        progress_percent=100,
        story_id=story_id
    ))

    # Act
    status = service.get_status(job_id)

    # Assert
    assert status["status"] == "completed"
    assert status["story_id"] == story_id

def test_get_generation_status_failed():
    """Test retrieving status of failed generation."""
    # Arrange
    service = GenerationService()
    job_id = "660e8400-e29b-41d4-a716-446655440001"
    service._get_job = Mock(return_value=Mock(
        status="failed",
        error="Agent timeout"
    ))

    # Act
    status = service.get_status(job_id)

    # Assert
    assert status["status"] == "failed"
    assert "timeout" in status["error"].lower()

def test_get_generation_status_not_found():
    """Test retrieving status of non-existent job."""
    # Arrange
    service = GenerationService()
    service._get_job = Mock(return_value=None)

    # Act & Assert
    with pytest.raises(ValueError, match="not found"):
        service.get_status("invalid-job-id")

@patch("app.tasks.generation_tasks.generate_story.delay")
def test_celery_task_queued(mock_delay):
    """Test that Celery task is queued."""
    # Arrange
    service = GenerationService()
    mock_delay.return_value = Mock(id="task-id")

    # Act
    job = service.start_generation(prompt="Test", theme_id="warhammer40k")

    # Assert
    mock_delay.assert_called_once()

@pytest.mark.asyncio
async def test_progress_callback_invoked():
    """Test progress callback is invoked during generation."""
    # Arrange
    service = GenerationService()
    callback_called = []

    def callback(progress):
        callback_called.append(progress)

    # Act
    with patch("app.integrations.crewai_wrapper.CrewAIWrapper.execute_generation") as mock_exec:
        mock_exec.return_value = {"plot": {}}
        await service._execute_with_callback("job-id", "prompt", callback)

    # Assert (callback called at least once)
    assert len(callback_called) > 0

def test_generation_timeout():
    """Test generation timeout after 15 minutes."""
    # Arrange
    service = GenerationService()
    service.TIMEOUT_SECONDS = 1  # Override for testing

    with patch("time.time", side_effect=[0, 2]):  # Simulate timeout
        # Act & Assert
        with pytest.raises(TimeoutError):
            service._wait_for_completion("job-id")

def test_generation_saves_to_filesystem():
    """Test generation saves game.json to filesystem."""
    # Arrange
    service = GenerationService()
    story_id = "550e8400-e29b-41d4-a716-446655440000"
    game_data = {"plot": {}, "narrative_map": {}}

    with patch("builtins.open", mock_open()) as mock_file:
        # Act
        service._save_game_content(story_id, game_data)

        # Assert
        mock_file.assert_called_once()
        handle = mock_file()
        handle.write.assert_called()
```

**Total GenerationService Tests**: 12

#### 2.1.3 ThemeService Tests (8 tests)

```python
# tests/unit/services/test_theme_service.py
def test_load_theme_success():
    """Test loading valid theme configuration."""
    pass

def test_load_theme_invalid_yaml():
    """Test loading theme with invalid YAML."""
    pass

def test_load_theme_missing_required_fields():
    """Test loading theme missing required fields."""
    pass

def test_list_themes():
    """Test listing all available themes."""
    pass

def test_theme_caching():
    """Test theme configuration is cached."""
    pass

def test_theme_cache_invalidation():
    """Test cache invalidation after theme update."""
    pass

def test_default_theme_fallback():
    """Test default theme is used when requested theme not found."""
    pass

def test_theme_asset_serving():
    """Test serving theme assets (images, fonts)."""
    pass
```

#### 2.1.4 GameService Tests (10 tests)

```python
# tests/unit/services/test_game_service.py
def test_start_game_session():
    """Test starting new game session."""
    pass

def test_process_valid_command():
    """Test processing valid game command."""
    pass

def test_process_invalid_command():
    """Test processing invalid game command."""
    pass

def test_game_state_persistence():
    """Test game state is maintained across commands."""
    pass

def test_save_game():
    """Test saving game state to filesystem."""
    pass

def test_load_game():
    """Test loading saved game state."""
    pass

def test_session_timeout():
    """Test game session expires after 1 hour."""
    pass

def test_game_over_detection():
    """Test game over state detection."""
    pass

def test_inventory_management():
    """Test inventory updates during gameplay."""
    pass

def test_concurrent_game_sessions():
    """Test multiple concurrent game sessions."""
    pass
```

#### 2.1.5 IterationService Tests (8 tests)

```python
# tests/unit/services/test_iteration_service.py
def test_submit_feedback():
    """Test submitting iteration feedback."""
    pass

def test_start_iteration():
    """Test starting iteration with feedback context."""
    pass

def test_iteration_limit_enforcement():
    """Test maximum 5 iterations enforced."""
    pass

def test_list_iterations():
    """Test listing all iterations for story."""
    pass

def test_iteration_version_numbering():
    """Test iteration versions numbered sequentially."""
    pass

def test_feedback_validation():
    """Test feedback validation (min 20 chars)."""
    pass

def test_iteration_status_tracking():
    """Test iteration status (pending, accepted, rejected)."""
    pass

def test_iteration_with_structured_changes():
    """Test iteration with structured change requests."""
    pass
```

#### 2.1.6 CrewAIWrapper Tests (7 tests)

```python
# tests/unit/integrations/test_crewai_wrapper.py
def test_execute_generation_success():
    """Test successful CrewAI execution."""
    pass

def test_execute_generation_with_progress_callback():
    """Test progress callback during execution."""
    pass

def test_execute_generation_timeout():
    """Test generation timeout handling."""
    pass

def test_execute_generation_agent_failure():
    """Test handling of agent execution failure."""
    pass

def test_execute_iteration_with_feedback():
    """Test iteration execution with feedback context."""
    pass

def test_no_modification_to_crew():
    """Test wrapper doesn't modify existing crew.py."""
    pass

def test_output_validation():
    """Test generated output structure validation."""
    pass
```

#### 2.1.7 GameWrapper Tests (8 tests)

```python
# tests/unit/integrations/test_game_wrapper.py
def test_initialize_game():
    """Test game engine initialization."""
    pass

def test_process_command():
    """Test command processing."""
    pass

def test_get_game_state():
    """Test retrieving current game state."""
    pass

def test_save_state():
    """Test exporting game state for persistence."""
    pass

def test_load_state():
    """Test restoring game from saved state."""
    pass

def test_invalid_game_file():
    """Test handling of invalid game.json."""
    pass

def test_no_modification_to_engine():
    """Test wrapper doesn't modify existing engine.py."""
    pass

def test_state_consistency():
    """Test state consistency across multiple commands."""
    pass
```

### 2.2 Frontend Unit Tests (Jest + React Testing Library)

**Framework**: Jest, React Testing Library, @testing-library/user-event

**Structure**:

```
frontend/tests/
├── unit/
│   ├── components/
│   │   ├── StoryCard.test.tsx
│   │   ├── StoryGrid.test.tsx
│   │   ├── SearchBar.test.tsx
│   │   ├── TemplateGallery.test.tsx
│   │   ├── ChatInterface.test.tsx
│   │   ├── GenerationProgress.test.tsx
│   │   ├── GameDisplay.test.tsx
│   │   └── CommandInput.test.tsx
│   ├── contexts/
│   │   ├── ThemeContext.test.tsx
│   │   ├── StoryContext.test.tsx
│   │   └── GameContext.test.tsx
│   ├── hooks/
│   │   ├── useStories.test.ts
│   │   ├── useWebSocket.test.ts
│   │   └── useGame.test.ts
│   └── utils/
│       ├── api.test.ts
│       └── errorHandler.test.ts
```

#### 2.2.1 StoryCard Component Tests (8 tests)

```typescript
// frontend/tests/unit/components/StoryCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { StoryCard } from '@/components/StoryCard';

describe('StoryCard', () => {
  const mockStory = {
    id: '550e8400-e29b-41d4-a716-446655440000',
    title: 'Test Story',
    description: 'A test story description',
    theme_id: 'warhammer40k',
    scene_count: 8,
    play_count: 5,
    created_at: '2025-11-12T10:00:00Z'
  };

  it('renders story title and description', () => {
    render(<StoryCard story={mockStory} />);

    expect(screen.getByText('Test Story')).toBeInTheDocument();
    expect(screen.getByText('A test story description')).toBeInTheDocument();
  });

  it('shows play button for complete stories', () => {
    render(<StoryCard story={mockStory} />);

    const playButton = screen.getByRole('button', { name: /play/i });
    expect(playButton).toBeInTheDocument();
  });

  it('shows iteration button with count', () => {
    const storyWithIterations = { ...mockStory, total_iterations: 2 };
    render(<StoryCard story={storyWithIterations} />);

    expect(screen.getByText(/2 iterations/i)).toBeInTheDocument();
  });

  it('displays story statistics', () => {
    render(<StoryCard story={mockStory} />);

    expect(screen.getByText('8 scenes')).toBeInTheDocument();
    expect(screen.getByText('Played 5 times')).toBeInTheDocument();
  });

  it('calls onPlay when play button clicked', () => {
    const onPlay = jest.fn();
    render(<StoryCard story={mockStory} onPlay={onPlay} />);

    fireEvent.click(screen.getByRole('button', { name: /play/i }));
    expect(onPlay).toHaveBeenCalledWith(mockStory.id);
  });

  it('calls onIterate when iterate button clicked', () => {
    const onIterate = jest.fn();
    const storyWithIterations = { ...mockStory, total_iterations: 1 };
    render(<StoryCard story={storyWithIterations} onIterate={onIterate} />);

    fireEvent.click(screen.getByRole('button', { name: /iterate/i }));
    expect(onIterate).toHaveBeenCalledWith(mockStory.id);
  });

  it('shows theme badge', () => {
    render(<StoryCard story={mockStory} />);

    expect(screen.getByText('warhammer40k')).toBeInTheDocument();
  });

  it('disables play button for incomplete stories', () => {
    const incompleteStory = { ...mockStory, status: 'generating' };
    render(<StoryCard story={incompleteStory} />);

    const playButton = screen.getByRole('button', { name: /play/i });
    expect(playButton).toBeDisabled();
  });
});
```

#### 2.2.2 SearchBar Component Tests (6 tests)

```typescript
// frontend/tests/unit/components/SearchBar.test.tsx
describe('SearchBar', () => {
  it('renders search input', () => {});
  it('debounces search input (300ms)', () => {});
  it('calls onSearch with query', () => {});
  it('shows clear button when text entered', () => {});
  it('clears search when clear button clicked', () => {});
  it('submits search on Enter key', () => {});
});
```

#### 2.2.3 TemplateGallery Component Tests (7 tests)

```typescript
// frontend/tests/unit/components/TemplateGallery.test.tsx
describe('TemplateGallery', () => {
  it('renders list of templates', () => {});
  it('highlights selected template', () => {});
  it('shows template details on hover', () => {});
  it('calls onSelect when template clicked', () => {});
  it('filters templates by difficulty', () => {});
  it('shows loading state while fetching', () => {});
  it('shows error state on fetch failure', () => {});
});
```

#### 2.2.4 ChatInterface Component Tests (9 tests)

```typescript
// frontend/tests/unit/components/ChatInterface.test.tsx
describe('ChatInterface', () => {
  it('displays chat messages', () => {});
  it('shows user and AI message styles differently', () => {});
  it('auto-scrolls to latest message', () => {});
  it('disables input during AI response', () => {});
  it('validates input before sending', () => {});
  it('shows typing indicator during AI response', () => {});
  it('displays final prompt preview', () => {});
  it('allows editing previous messages', () => {});
  it('resets chat when starting new conversation', () => {});
});
```

#### 2.2.5 GenerationProgress Component Tests (8 tests)

```typescript
// frontend/tests/unit/components/GenerationProgress.test.tsx
describe('GenerationProgress', () => {
  it('displays progress bar with percentage', () => {});
  it('shows current agent name', () => {});
  it('updates progress on WebSocket message', () => {});
  it('shows checkmarks for completed agents', () => {});
  it('shows spinner for active agent', () => {});
  it('shows error state on generation failure', () => {});
  it('shows completion state when done', () => {});
  it('displays estimated time remaining', () => {});
});
```

#### 2.2.6 GameDisplay Component Tests (10 tests)

```typescript
// frontend/tests/unit/components/GameDisplay.test.tsx
describe('GameDisplay', () => {
  it('renders scene text with Markdown', () => {});
  it('displays inventory items', () => {});
  it('shows output log with scroll', () => {});
  it('auto-scrolls output log on new message', () => {});
  it('applies theme styling', () => {});
  it('shows health/status indicators', () => {});
  it('displays current scene title', () => {});
  it('renders item descriptions on hover', () => {});
  it('shows game over screen', () => {});
  it('handles empty inventory state', () => {});
});
```

#### 2.2.7 CommandInput Component Tests (7 tests)

```typescript
// frontend/tests/unit/components/CommandInput.test.tsx
describe('CommandInput', () => {
  it('renders input field', () => {});
  it('submits command on Enter key', () => {});
  it('navigates command history with up/down arrows', () => {});
  it('clears input after submission', () => {});
  it('disables input during command processing', () => {});
  it('shows command suggestions', () => {});
  it('validates command before submission', () => {});
});
```

### 2.3 Critical Path Coverage Requirements

**Modules Requiring >95% Coverage**:

**Backend**:

- `app/services/generation_service.py`
- `app/services/game_service.py`
- `app/integrations/crewai_wrapper.py`
- `app/integrations/game_wrapper.py`
- `app/api/routes/stories.py`
- `app/api/routes/gameplay.py`
- `app/api/websocket.py`

**Frontend**:

- `src/contexts/GameContext.tsx`
- `src/contexts/StoryContext.tsx`
- `src/hooks/useWebSocket.ts`
- `src/services/api.ts`
- `src/components/GameDisplay.tsx`
- `src/components/GenerationProgress.tsx`

**Total Backend Unit Tests**: 68
**Total Frontend Unit Tests**: 55
**Total Unit Tests**: 123

---

## 3. Integration Testing

### 3.1 API Integration Tests (pytest)

**Framework**: pytest with test database, httpx for async requests

**Structure**:

```
tests/
├── integration/
│   ├── api/
│   │   ├── test_stories_api.py
│   │   ├── test_generation_api.py
│   │   ├── test_gameplay_api.py
│   │   ├── test_iteration_api.py
│   │   └── test_websocket.py
│   └── database/
│       ├── test_migrations.py
│       └── test_transactions.py
```

#### 3.1.1 Story Creation Full Flow (12 steps)

```python
# tests/integration/api/test_generation_api.py
@pytest.mark.integration
async def test_story_creation_full_flow(client, test_db):
    """
    Test complete story creation workflow from prompt to playable game.

    Steps:
    1. POST /api/v1/stories with prompt
    2. Verify 202 Accepted with generation_job_id
    3. GET /api/v1/generation/{job_id} - status: queued
    4. Wait for WebSocket progress updates
    5. Verify progress updates (0% -> 100%)
    6. GET /api/v1/generation/{job_id} - status: in_progress
    7. Verify current_agent updates (PlotMaster -> NarrativeArchitect -> ...)
    8. GET /api/v1/generation/{job_id} - status: completed
    9. Verify story_id returned
    10. GET /api/v1/stories/{story_id} - verify story exists
    11. GET /api/v1/stories/{story_id}/content - verify game.json
    12. Verify game.json structure (plot, narrative_map, puzzles, scenes)
    """
    # Step 1: Create story
    response = await client.post("/api/v1/stories", json={
        "prompt": "Create a horror-themed Space Hulk adventure with heavy atmosphere",
        "template_id": "horror_infestation",
        "theme_id": "warhammer40k"
    })

    assert response.status_code == 202
    data = response.json()["data"]
    generation_job_id = data["generation_job_id"]
    story_id = data["story_id"]

    # Step 2: Check initial status
    response = await client.get(f"/api/v1/generation/{generation_job_id}")
    assert response.status_code == 200
    assert response.json()["data"]["status"] in ["queued", "in_progress"]

    # Step 3: Wait for completion (with timeout)
    max_wait = 600  # 10 minutes
    start = time.time()
    while time.time() - start < max_wait:
        response = await client.get(f"/api/v1/generation/{generation_job_id}")
        status = response.json()["data"]["status"]

        if status == "completed":
            break
        elif status == "failed":
            pytest.fail(f"Generation failed: {response.json()['data']['error']}")

        await asyncio.sleep(5)

    # Step 4: Verify completion
    response = await client.get(f"/api/v1/generation/{generation_job_id}")
    assert response.json()["data"]["status"] == "completed"
    assert response.json()["data"]["story_id"] == story_id

    # Step 5: Verify story exists
    response = await client.get(f"/api/v1/stories/{story_id}")
    assert response.status_code == 200
    story = response.json()["data"]
    assert story["title"]
    assert story["scene_count"] > 0

    # Step 6: Verify game content
    response = await client.get(f"/api/v1/stories/{story_id}/content")
    assert response.status_code == 200
    content = response.json()["data"]
    assert "plot" in content
    assert "narrative_map" in content
    assert "puzzles" in content
    assert "scenes" in content
```

#### 3.1.2 Iteration Flow with Feedback (8 steps)

```python
@pytest.mark.integration
async def test_iteration_flow_with_feedback(client, test_db, sample_story):
    """
    Test story iteration workflow with feedback.

    Steps:
    1. POST /api/v1/stories/{id}/iterate with feedback
    2. Verify 202 Accepted with new generation_job_id
    3. Monitor progress via WebSocket
    4. Wait for completion
    5. GET /api/v1/stories/{id}/iterations - verify new version
    6. GET /api/v1/stories/{id}/content - verify updated content
    7. Verify iteration_number incremented
    8. Verify original version still accessible
    """
    story_id = sample_story.id

    # Step 1: Submit feedback
    response = await client.post(f"/api/v1/stories/{story_id}/iterate", json={
        "feedback": "The puzzle in scene 2 needs better hints. Make the tone darker.",
        "changes": {
            "plot_rating": 5,
            "puzzle_rating": 3,
            "writing_rating": 4,
            "tone_adjustment": "darker",
            "difficulty_adjustment": "easier",
            "focus_areas": ["puzzles", "atmosphere"]
        }
    })

    assert response.status_code == 202
    job_data = response.json()["data"]
    assert job_data["iteration_number"] == 2

    # Step 2-4: Wait for completion (similar to creation flow)
    generation_job_id = job_data["generation_job_id"]
    # ... wait logic ...

    # Step 5: Verify iterations list
    response = await client.get(f"/api/v1/stories/{story_id}/iterations")
    assert response.status_code == 200
    iterations = response.json()["data"]
    assert len(iterations) == 2
    assert iterations[1]["version"] == 2
    assert "puzzle" in iterations[1]["feedback"].lower()
```

#### 3.1.3 Game Session Lifecycle (10 steps)

```python
@pytest.mark.integration
async def test_game_session_lifecycle(client, test_db, sample_story):
    """
    Test complete gameplay session lifecycle.

    Steps:
    1. POST /api/v1/game/{story_id}/start
    2. Verify initial scene and state
    3. POST /api/v1/game/{session_id}/command - examine
    4. Verify command response and state update
    5. POST /api/v1/game/{session_id}/command - take item
    6. Verify inventory updated
    7. POST /api/v1/game/{session_id}/save
    8. Verify save created
    9. POST /api/v1/game/load/{save_id}
    10. Verify state restored correctly
    """
    story_id = sample_story.id

    # Step 1: Start game
    response = await client.post(f"/api/v1/game/{story_id}/start")
    assert response.status_code == 200
    game_data = response.json()["data"]
    game_session_id = game_data["game_session_id"]
    assert game_data["initial_scene"]
    assert game_data["state"]["current_scene"]

    # Step 2: Send command
    response = await client.post(
        f"/api/v1/game/{game_session_id}/command",
        json={"command": "examine door"}
    )
    assert response.status_code == 200
    cmd_data = response.json()["data"]
    assert cmd_data["valid_command"] is True
    assert cmd_data["output"]

    # Step 3: Take item
    response = await client.post(
        f"/api/v1/game/{game_session_id}/command",
        json={"command": "take keycard"}
    )
    state = response.json()["data"]["state"]
    assert "keycard" in state["inventory"]

    # Step 4: Save game
    response = await client.post(
        f"/api/v1/game/{game_session_id}/save",
        json={"save_name": "Test save"}
    )
    assert response.status_code == 200
    save_id = response.json()["data"]["save_id"]

    # Step 5: Load game
    response = await client.post(f"/api/v1/game/load/{save_id}")
    assert response.status_code == 200
    loaded_state = response.json()["data"]["state"]
    assert "keycard" in loaded_state["inventory"]
```

#### 3.1.4 WebSocket Progress Updates (6 steps)

```python
@pytest.mark.integration
async def test_websocket_progress_updates(client, test_db):
    """
    Test WebSocket real-time progress updates.

    Steps:
    1. Start story generation
    2. Connect to WebSocket /ws/generation/{job_id}
    3. Verify connection established
    4. Receive progress updates
    5. Verify progress increases monotonically
    6. Verify completion message received
    """
    # Step 1: Start generation
    response = await client.post("/api/v1/stories", json={
        "prompt": "Test prompt for WebSocket testing",
        "theme_id": "warhammer40k"
    })
    generation_job_id = response.json()["data"]["generation_job_id"]

    # Step 2: Connect WebSocket
    async with client.websocket_connect(
        f"/ws/generation/{generation_job_id}"
    ) as websocket:
        # Step 3: Subscribe
        await websocket.send_json({"type": "subscribe"})

        # Step 4: Receive updates
        progress_values = []
        while True:
            message = await websocket.receive_json()

            if message["type"] == "progress":
                progress_values.append(message["progress_percent"])
                assert message["current_agent"]

            elif message["type"] == "complete":
                assert message["story_id"]
                break

            elif message["type"] == "error":
                pytest.fail(f"Generation failed: {message['error']}")

        # Step 5: Verify monotonic progress
        assert progress_values == sorted(progress_values)
        assert progress_values[-1] == 100
```

### 3.2 Database Integration Tests

```python
# tests/integration/database/test_migrations.py
def test_migrations_up_down():
    """Test database migrations can be applied and rolled back."""
    pass

def test_foreign_key_constraints():
    """Test foreign key relationships enforced."""
    pass

def test_unique_constraints():
    """Test unique constraints enforced."""
    pass

def test_transaction_rollback():
    """Test transaction rollback on error."""
    pass

def test_concurrent_writes():
    """Test concurrent database writes."""
    pass
```

### 3.3 Component Integration Tests (Frontend)

```typescript
// frontend/tests/integration/CreationFlow.test.tsx
describe('Story Creation Flow', () => {
  it('completes full creation workflow', async () => {
    // 1. Navigate to create page
    // 2. Select template
    // 3. Customize prompt
    // 4. Start generation
    // 5. Monitor progress
    // 6. Navigate to completed story
  });
});
```

**Total Integration Tests**: 50

---

## 4. End-to-End Testing

### 4.1 E2E Test Framework

**Tool**: Playwright (recommended) or Cypress
**Browsers**: Chromium, Firefox, WebKit
**Test Environment**: Docker Compose with all services

### 4.2 Critical User Journeys (15 E2E Tests)

#### Journey 1: First-Time User Creates Story from Template

```typescript
// tests/e2e/create-from-template.spec.ts
import { test, expect } from '@playwright/test';

test('First-time user creates story from template', async ({ page }) => {
  // PRECONDITIONS
  // - User has never used the system
  // - Database is empty (no stories)
  // - All services are running

  // STEP 1: Navigate to home page
  await page.goto('/');
  await expect(page.locator('[data-testid="library-empty"]')).toBeVisible();

  // STEP 2: Click "Create New Story"
  await page.click('[data-testid="create-story-button"]');
  await expect(page).toHaveURL('/create');

  // STEP 3: Select horror template
  await page.click('[data-testid="template-horror"]');
  await expect(page.locator('[data-testid="template-horror"]')).toHaveClass(/selected/);

  // STEP 4: Customize prompt in template
  await page.fill(
    '[data-testid="prompt-input"]',
    'A dark atmospheric horror adventure with minimal combat and heavy exploration'
  );

  // STEP 5: Click "Generate Story"
  await page.click('[data-testid="generate-button"]');

  // STEP 6: Verify progress page loads
  await expect(page).toHaveURL(/\/create\/progress\/.+/);
  await expect(page.locator('[data-testid="progress-bar"]')).toBeVisible();

  // STEP 7: Wait for progress updates
  await expect(page.locator('[data-testid="agent-status-PlotMaster"]')).toContainText('✓', {
    timeout: 120000
  });

  // STEP 8: Wait for completion (up to 10 minutes)
  await expect(page.locator('[data-testid="generation-complete"]')).toBeVisible({
    timeout: 600000
  });

  // STEP 9: Verify story details displayed
  await expect(page.locator('[data-testid="story-title"]')).toContainText('horror');
  await expect(page.locator('[data-testid="story-stats"]')).toContainText('scenes');

  // STEP 10: Click "Play Now"
  await page.click('[data-testid="play-now-button"]');

  // EXPECTED OUTCOMES
  // - Story created successfully
  // - Story appears in library
  // - User redirected to game player
  await expect(page).toHaveURL(/\/play\/.+/);
  await expect(page.locator('[data-testid="game-scene"]')).toBeVisible();

  // ERROR SCENARIOS
  // - If generation times out, show user-friendly error
  // - If WebSocket disconnects, reconnect automatically
  // - If browser closes, generation continues server-side
});
```

#### Journey 2: Veteran User Iterates on Existing Story

```typescript
test('Veteran user iterates on existing story', async ({ page }) => {
  // PRECONDITIONS
  // - User has existing story with 1 iteration remaining (4 used)
  // - Story is complete and playable

  // STEPS
  // 1. Navigate to library
  // 2. Find story with "Iterate" button
  // 3. Click "Iterate"
  // 4. Fill feedback form with specific changes
  // 5. Submit feedback
  // 6. Monitor iteration progress
  // 7. Review changes in new version
  // 8. Accept or reject iteration

  // EXPECTED OUTCOMES
  // - New version created with feedback applied
  // - Both versions accessible
  // - Iteration count updated (5/5)
  // - Iterate button disabled after 5th iteration

  // ERROR SCENARIOS
  // - Show error if iteration limit reached
  // - Validate feedback min 20 characters
});
```

#### Journey 3: User Plays Game to Completion

```typescript
test('User plays game to completion', async ({ page }) => {
  // PRECONDITIONS
  // - Sample story exists and is playable
  // - User is on game player page

  // STEPS
  // 1. Read initial scene
  // 2. Type "look around" command
  // 3. Verify output appears
  // 4. Type "examine door"
  // 5. Type "take keycard"
  // 6. Verify keycard in inventory
  // 7. Type "use keycard on door"
  // 8. Progress through multiple scenes
  // 9. Solve puzzle
  // 10. Reach final scene
  // 11. Complete game

  // EXPECTED OUTCOMES
  // - All commands processed correctly
  // - Inventory updates in real-time
  // - Game over screen appears
  // - Play count incremented in library

  // ERROR SCENARIOS
  // - Invalid commands show helpful message
  // - Session timeout warning before expiration
});
```

#### Journey 4: User Saves and Loads Game

```typescript
test('User saves and loads game mid-session', async ({ page }) => {
  // PRECONDITIONS
  // - User is in active game session
  // - User has progressed past initial scene

  // STEPS
  // 1. Progress to scene 3
  // 2. Collect 2 items in inventory
  // 3. Click "Save Game"
  // 4. Enter save name "Before boss fight"
  // 5. Verify save confirmation
  // 6. Continue playing
  // 7. Navigate to library
  // 8. Click "Load Game" on story
  // 9. Select "Before boss fight" save
  // 10. Verify restored to scene 3 with 2 items

  // EXPECTED OUTCOMES
  // - Game state perfectly restored
  // - Inventory preserved
  // - Scene position preserved
  // - Command history cleared

  // ERROR SCENARIOS
  // - Corrupted save shows error
  // - Save slot limit (10) enforced
});
```

#### Journey 5: User Browses Library and Filters

```typescript
test('User browses library with search and filters', async ({ page }) => {
  // PRECONDITIONS
  // - Library has 20+ stories across multiple themes

  // STEPS
  // 1. Navigate to library
  // 2. Verify all stories displayed
  // 3. Type "horror" in search
  // 4. Verify filtered results
  // 5. Select "Warhammer 40k" theme filter
  // 6. Verify combined filter results
  // 7. Sort by "Most Played"
  // 8. Verify sort order
  // 9. Clear filters
  // 10. Verify all stories shown again

  // EXPECTED OUTCOMES
  // - Search is case-insensitive
  // - Filters combine (AND logic)
  // - Sort updates results immediately
  // - No results state handled gracefully
});
```

#### Journey 6: User Switches Themes

```typescript
test('User switches visual theme', async ({ page }) => {
  // STEPS
  // 1. Open theme selector
  // 2. Verify current theme highlighted
  // 3. Select "Cyberpunk" theme
  // 4. Verify CSS variables updated
  // 5. Navigate to different page
  // 6. Verify theme persisted
  // 7. Reload browser
  // 8. Verify theme still applied

  // EXPECTED OUTCOMES
  // - Theme changes immediately
  // - All components styled correctly
  // - Theme persists across sessions
});
```

#### Journey 7: Generation Timeout Error Recovery

```typescript
test('User recovers from generation timeout', async ({ page }) => {
  // Simulate timeout by mocking long-running generation

  // STEPS
  // 1. Start story generation
  // 2. Wait 15+ minutes
  // 3. Verify timeout error displayed
  // 4. Verify "Try Again" button shown
  // 5. Click "Try Again"
  // 6. Verify new generation started

  // EXPECTED OUTCOMES
  // - User-friendly error message
  // - Retry option available
  // - Original prompt preserved
});
```

#### Journey 8: WebSocket Disconnect and Reconnect

```typescript
test('WebSocket reconnects after network interruption', async ({ page }) => {
  // STEPS
  // 1. Start story generation
  // 2. Monitor progress updates
  // 3. Simulate network disconnect
  // 4. Verify "Reconnecting..." message
  // 5. Restore network
  // 6. Verify reconnection successful
  // 7. Verify progress updates resume

  // EXPECTED OUTCOMES
  // - Automatic reconnection with backoff
  // - No progress lost
  // - User notified of connection status
});
```

#### Journey 9: Invalid Prompt Validation

```typescript
test('User receives validation errors for invalid prompt', async ({ page }) => {
  // STEPS
  // 1. Navigate to create page
  // 2. Enter prompt with 10 characters (min 50)
  // 3. Click generate
  // 4. Verify validation error displayed
  // 5. Enter prompt with 1500 characters (max 1000)
  // 6. Verify validation error
  // 7. Enter valid 200-char prompt
  // 8. Verify generation starts

  // EXPECTED OUTCOMES
  // - Clear validation messages
  // - Character count displayed
  // - Submit disabled until valid
});
```

#### Journey 10: Iteration Limit Reached

```typescript
test('User informed when iteration limit reached', async ({ page }) => {
  // PRECONDITIONS
  // - Story has 5 iterations (max reached)

  // STEPS
  // 1. Navigate to story details
  // 2. Verify "5/5 iterations" badge
  // 3. Verify iterate button disabled
  // 4. Hover over button
  // 5. Verify tooltip: "Maximum iterations reached"

  // EXPECTED OUTCOMES
  // - User cannot start 6th iteration
  // - Clear explanation provided
  // - Option to create new story suggested
});
```

#### Journey 11: Concurrent Generation Attempt

```typescript
test('User prevented from starting concurrent generations', async ({ page }) => {
  // STEPS
  // 1. Start first generation
  // 2. Open new tab
  // 3. Attempt to start second generation
  // 4. Verify error: "Generation already in progress"
  // 5. Verify link to active generation
  // 6. Complete first generation
  // 7. Retry second generation
  // 8. Verify success
});
```

#### Journey 12: Sample Story Cannot Be Deleted

```typescript
test('User cannot delete sample stories', async ({ page }) => {
  // STEPS
  // 1. Navigate to library
  // 2. Hover over sample story
  // 3. Verify no delete button shown
  // 4. Right-click sample story
  // 5. Verify no delete context menu

  // EXPECTED OUTCOMES
  // - Sample stories clearly marked
  // - Delete action unavailable
  // - User can duplicate sample stories
});
```

#### Journey 13: Large Story Performance

```typescript
test('User plays large story (100+ scenes) smoothly', async ({ page }) => {
  // PRECONDITIONS
  // - Story with 100 scenes, 50 items, 20 NPCs

  // STEPS
  // 1. Load large story
  // 2. Measure initial load time
  // 3. Execute 50 commands rapidly
  // 4. Measure response times
  // 5. Verify no lag or freezing

  // EXPECTED OUTCOMES
  // - Load time <3s
  // - Command response <500ms (p95)
  // - No memory leaks
});
```

#### Journey 14: Mobile Browser Gameplay

```typescript
test('User plays game on mobile device', async ({ page }) => {
  // Viewport set to mobile (375x667)

  // STEPS
  // 1. Navigate to library on mobile
  // 2. Verify responsive layout
  // 3. Start game
  // 4. Type command on mobile keyboard
  // 5. Verify no layout issues
  // 6. Save game
  // 7. Verify modals responsive

  // EXPECTED OUTCOMES
  // - All features work on mobile
  // - Touch-friendly controls
  // - Readable text sizes
});
```

#### Journey 15: Keyboard Navigation (Accessibility)

```typescript
test('User navigates entire app with keyboard only', async ({ page }) => {
  // STEPS
  // 1. Tab through library page
  // 2. Verify focus indicators visible
  // 3. Navigate to create with Enter
  // 4. Select template with Space
  // 5. Tab through form fields
  // 6. Submit with Enter
  // 7. Navigate progress page with Tab
  // 8. Use arrow keys in game commands

  // EXPECTED OUTCOMES
  // - All interactive elements focusable
  // - Tab order logical
  // - Enter/Space activate buttons
  // - No keyboard traps
});
```

### 4.3 E2E Test Infrastructure

**Setup**:

```typescript
// tests/e2e/setup.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  // Start all services before tests
  page: async ({ page }, use) => {
    // Seed database with test data
    await seedDatabase();

    await use(page);

    // Cleanup after tests
    await cleanupDatabase();
  }
});
```

**Utilities**:

```typescript
// tests/e2e/utils/helpers.ts
export async function waitForGeneration(page, jobId, timeout = 600000) {
  // Poll generation status until complete
}

export async function createSampleStory(page, options) {
  // Helper to quickly create story for testing
}

export async function loginAsUser(page, userId) {
  // Future: Login helper for multi-user
}
```

**Total E2E Tests**: 15 critical journeys

---

## 5. Performance Testing

### 5.1 Load Testing Framework

**Tool**: k6 or Locust
**Target Environment**: Staging with production-like resources

### 5.2 Load Test Scenarios

#### Scenario 1: Concurrent Story Generations

```javascript
// tests/performance/concurrent-generations.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 10 },  // Ramp up to 10 users
    { duration: '5m', target: 10 },  // Stay at 10 users
    { duration: '2m', target: 0 },   // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<15000'], // 95% requests < 15s
    'http_req_failed': ['rate<0.1'],      // <10% failures
  },
};

export default function () {
  // Start story generation
  const payload = JSON.stringify({
    prompt: 'Create a test story for load testing',
    theme_id: 'warhammer40k'
  });

  const response = http.post('http://localhost:8000/api/v1/stories', payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  check(response, {
    'is status 202': (r) => r.status === 202,
    'has job_id': (r) => r.json('data.generation_job_id') !== undefined,
  });

  sleep(1);
}
```

#### Scenario 2: High API Request Rate

```javascript
// tests/performance/api-throughput.js
export const options = {
  stages: [
    { duration: '1m', target: 100 },  // 100 concurrent users
    { duration: '3m', target: 100 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<100'], // 95% requests < 100ms
  },
};

export default function () {
  // GET /api/v1/stories (list)
  http.get('http://localhost:8000/api/v1/stories');

  // GET /api/v1/themes
  http.get('http://localhost:8000/api/v1/themes');

  // GET /api/v1/templates
  http.get('http://localhost:8000/api/v1/templates');

  sleep(1);
}
```

#### Scenario 3: Concurrent Gameplay Sessions

```javascript
// tests/performance/concurrent-gameplay.js
export const options = {
  stages: [
    { duration: '2m', target: 50 },  // 50 concurrent players
    { duration: '5m', target: 50 },
    { duration: '2m', target: 0 },
  ],
};

export default function () {
  // Start game session
  const startResponse = http.post(
    `http://localhost:8000/api/v1/game/${__ENV.STORY_ID}/start`
  );
  const sessionId = startResponse.json('data.game_session_id');

  // Send 10 commands
  for (let i = 0; i < 10; i++) {
    http.post(`http://localhost:8000/api/v1/game/${sessionId}/command`, {
      command: 'look around'
    });
    sleep(2);
  }
}
```

#### Scenario 4: WebSocket Connection Stability

```javascript
// tests/performance/websocket-stability.js
import ws from 'k6/ws';

export const options = {
  stages: [
    { duration: '1m', target: 100 },  // 100 WebSocket connections
    { duration: '10m', target: 100 }, // Hold for 10 minutes
    { duration: '1m', target: 0 },
  ],
};

export default function () {
  const jobId = __ENV.GENERATION_JOB_ID;
  const url = `ws://localhost:8000/ws/generation/${jobId}`;

  const response = ws.connect(url, {}, function (socket) {
    socket.on('open', () => {
      socket.send(JSON.stringify({ type: 'subscribe' }));
    });

    socket.on('message', (data) => {
      const message = JSON.parse(data);
      check(message, {
        'has type': (m) => m.type !== undefined,
        'valid progress': (m) => m.type !== 'progress' || m.progress_percent >= 0,
      });
    });

    socket.on('close', () => {
      // Expected after generation completes
    });

    socket.setTimeout(() => {
      socket.close();
    }, 600000); // 10 minute max
  });
}
```

### 5.3 Performance Benchmarks

**Target Metrics**:

| Operation | p50 | p95 | p99 |
|-----------|-----|-----|-----|
| GET /api/v1/stories | <50ms | <100ms | <200ms |
| POST /api/v1/stories | <200ms | <500ms | <1s |
| GET /api/v1/stories/{id} | <30ms | <100ms | <150ms |
| GET /api/v1/stories/{id}/content | <100ms | <500ms | <1s |
| POST /api/v1/game/{id}/command | <100ms | <500ms | <1s |
| Story generation (full) | <5min | <10min | <15min |
| Library page load | <1s | <2s | <3s |
| Game player initial load | <500ms | <1s | <2s |

**Resource Limits**:

- Memory: <2GB for 10 concurrent generations
- CPU: <80% utilization under load
- Database connections: <50 concurrent
- Open file handles: <1000

**Concurrent Users**:

- 100 concurrent API users supported
- 10 concurrent story generations
- 50 concurrent gameplay sessions
- 100 concurrent WebSocket connections

### 5.4 Performance Monitoring

**Metrics to Collect**:

- Request duration histogram
- Error rate
- Throughput (requests/second)
- Database query time
- Memory usage over time
- CPU usage over time
- WebSocket message latency

**Tools**:

- k6 Cloud for results visualization
- Grafana dashboard for real-time monitoring
- Prometheus for metrics collection

---

## 6. Accessibility Testing

### 6.1 WCAG 2.1 Level AA Compliance

**Standards**: Web Content Accessibility Guidelines 2.1, Level AA

### 6.2 Accessibility Checklist

#### Perceivable

- [ ] **1.1.1 Non-text Content**: All images have alt text
- [ ] **1.2.1 Audio-only and Video-only**: Media alternatives provided (N/A for MVP)
- [ ] **1.3.1 Info and Relationships**: Semantic HTML (headings, lists, forms)
- [ ] **1.3.2 Meaningful Sequence**: Reading order matches visual order
- [ ] **1.3.3 Sensory Characteristics**: Instructions don't rely solely on shape/color
- [ ] **1.4.1 Use of Color**: Color not sole means of conveying information
- [ ] **1.4.3 Contrast (Minimum)**: Text contrast ratio ≥4.5:1 (large text ≥3:1)
- [ ] **1.4.4 Resize Text**: Text resizable to 200% without loss of functionality
- [ ] **1.4.10 Reflow**: Content reflows at 400% zoom (no horizontal scroll)
- [ ] **1.4.11 Non-text Contrast**: UI components contrast ≥3:1
- [ ] **1.4.12 Text Spacing**: Content adapts to increased text spacing

#### Operable

- [ ] **2.1.1 Keyboard**: All functionality via keyboard
- [ ] **2.1.2 No Keyboard Trap**: Focus can move away from all components
- [ ] **2.1.4 Character Key Shortcuts**: Shortcuts can be turned off/remapped
- [ ] **2.4.1 Bypass Blocks**: Skip navigation link provided
- [ ] **2.4.2 Page Titled**: All pages have descriptive titles
- [ ] **2.4.3 Focus Order**: Focus order is logical
- [ ] **2.4.4 Link Purpose**: Link purpose clear from text or context
- [ ] **2.4.5 Multiple Ways**: Multiple ways to find pages (search, navigation)
- [ ] **2.4.6 Headings and Labels**: Headings and labels descriptive
- [ ] **2.4.7 Focus Visible**: Keyboard focus indicator visible
- [ ] **2.5.1 Pointer Gestures**: Complex gestures have simple alternative
- [ ] **2.5.2 Pointer Cancellation**: Functions triggered on up-event
- [ ] **2.5.3 Label in Name**: Visual labels match accessible names
- [ ] **2.5.4 Motion Actuation**: Motion-triggered functions can be disabled

#### Understandable

- [ ] **3.1.1 Language of Page**: Page language identified
- [ ] **3.2.1 On Focus**: Focus doesn't trigger unexpected changes
- [ ] **3.2.2 On Input**: Input doesn't trigger unexpected changes
- [ ] **3.2.3 Consistent Navigation**: Navigation consistent across pages
- [ ] **3.2.4 Consistent Identification**: Components identified consistently
- [ ] **3.3.1 Error Identification**: Errors identified and described
- [ ] **3.3.2 Labels or Instructions**: Form labels/instructions provided
- [ ] **3.3.3 Error Suggestion**: Error correction suggestions provided
- [ ] **3.3.4 Error Prevention**: Important actions can be reversed/confirmed

#### Robust

- [ ] **4.1.1 Parsing**: HTML is valid
- [ ] **4.1.2 Name, Role, Value**: UI components have accessible names/roles
- [ ] **4.1.3 Status Messages**: Status messages announced to assistive tech

### 6.3 Component-Specific Accessibility Requirements

**StoryCard**:

- Semantic article/heading tags
- Play button has aria-label
- Keyboard accessible (Tab, Enter)
- Focus indicator visible

**SearchBar**:

- Label associated with input
- Live region announces results count
- Clear button has aria-label

**ChatInterface**:

- Messages in list with role="log"
- Input has label
- Typing indicator announced

**GameDisplay**:

- Scene content in main landmark
- Inventory list semantic
- Command history navigable with arrows

**GenerationProgress**:

- Progress bar has aria-valuenow/valuemin/valuemax
- Status updates announced (aria-live="polite")

**Modal Dialogs**:

- Focus trapped within modal
- Escape key closes
- Focus returned to trigger on close
- aria-modal="true"

### 6.4 Accessibility Testing Tools

**Automated Testing**:

```typescript
// tests/accessibility/a11y.test.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('Library page has no accessibility violations', async ({ page }) => {
  await page.goto('/library');

  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});

test('Create page keyboard navigable', async ({ page }) => {
  await page.goto('/create');

  // Tab through all interactive elements
  await page.keyboard.press('Tab');
  await expect(page.locator(':focus')).toBeVisible();

  // Verify no keyboard traps
  for (let i = 0; i < 20; i++) {
    await page.keyboard.press('Tab');
  }
});
```

**Manual Testing**:

- NVDA screen reader (Windows)
- JAWS screen reader (Windows)
- VoiceOver screen reader (macOS/iOS)
- TalkBack screen reader (Android)
- Keyboard-only navigation
- High contrast mode
- 200% browser zoom

**Lighthouse Audits**:

```bash
lighthouse http://localhost:3000 --only-categories=accessibility --output=html
```

**Target Scores**:

- Lighthouse accessibility score: ≥95
- axe-core violations: 0
- Color contrast: All elements pass
- Keyboard navigation: 100% functional

### 6.5 Accessibility Test Cases

```typescript
// Test each page for WCAG compliance
describe('Accessibility Compliance', () => {
  test('Library page - WCAG AA', async () => {});
  test('Create page - WCAG AA', async () => {});
  test('Game player - WCAG AA', async () => {});
  test('Settings page - WCAG AA', async () => {});
});

// Test keyboard navigation
describe('Keyboard Navigation', () => {
  test('Tab order is logical', async () => {});
  test('All buttons activatable with Enter/Space', async () => {});
  test('Modals trap focus correctly', async () => {});
  test('Skip navigation link works', async () => {});
});

// Test screen reader announcements
describe('Screen Reader Support', () => {
  test('Page title updates on navigation', async () => {});
  test('Live regions announce dynamic changes', async () => {});
  test('Forms have associated labels', async () => {});
  test('Error messages announced', async () => {});
});
```

**Total Accessibility Tests**: 20

---

## 7. Security Testing

### 7.1 Security Test Scope

**Current (MVP - Single User)**:

- Input validation
- Path traversal prevention
- XSS prevention
- File system security
- Resource limits

**Future (Multi-User)**:

- Authentication bypass
- Authorization vulnerabilities
- CSRF attacks
- SQL injection
- Session hijacking

### 7.2 Security Test Cases

#### Input Validation (10 tests)

```python
# tests/security/test_input_validation.py
def test_sql_injection_in_search():
    """Test SQL injection attempts blocked."""
    # Attempt: search="'; DROP TABLE stories; --"
    # Expected: Input sanitized, query parameterized
    pass

def test_xss_in_story_title():
    """Test XSS injection in story title blocked."""
    # Attempt: title="<script>alert('XSS')</script>"
    # Expected: HTML escaped in output
    pass

def test_path_traversal_in_file_access():
    """Test path traversal blocked."""
    # Attempt: story_id="../../../etc/passwd"
    # Expected: 400 Bad Request
    pass

def test_command_injection_in_game():
    """Test command injection in game commands."""
    # Attempt: command="look; rm -rf /"
    # Expected: Command treated as literal string
    pass

def test_oversized_prompt():
    """Test oversized prompt rejected."""
    # Attempt: prompt with 10,000 characters
    # Expected: 400 Bad Request
    pass

def test_invalid_json_payload():
    """Test malformed JSON rejected."""
    # Attempt: POST with invalid JSON
    # Expected: 400 Bad Request
    pass

def test_special_characters_in_filename():
    """Test special characters in save names."""
    # Attempt: save_name="../../../malicious"
    # Expected: Sanitized filename
    pass

def test_unicode_overflow():
    """Test Unicode overflow attacks."""
    # Attempt: Extremely long Unicode string
    # Expected: Truncated/rejected
    pass

def test_negative_pagination_values():
    """Test negative page numbers."""
    # Attempt: page=-1
    # Expected: 400 Bad Request
    pass

def test_null_byte_injection():
    """Test null byte in file paths."""
    # Attempt: filename="story.json\0.txt"
    # Expected: Rejected or sanitized
    pass
```

#### File System Security (5 tests)

```python
def test_file_access_restricted_to_data_dir():
    """Test file access outside data/ directory blocked."""
    pass

def test_symlink_attack_prevention():
    """Test symlink attacks prevented."""
    pass

def test_file_permissions_correct():
    """Test created files have correct permissions."""
    pass

def test_tmp_file_cleanup():
    """Test temporary files cleaned up."""
    pass

def test_disk_space_limits():
    """Test disk space limits enforced."""
    pass
```

#### Rate Limiting (3 tests)

```python
def test_generation_rate_limit():
    """Test only 1 concurrent generation allowed."""
    pass

def test_api_rate_limit():
    """Test API rate limit enforced (future)."""
    pass

def test_websocket_connection_limit():
    """Test max WebSocket connections enforced."""
    pass
```

#### Resource Limits (4 tests)

```python
def test_max_file_size():
    """Test maximum file size enforced."""
    pass

def test_memory_limit():
    """Test process memory limit."""
    pass

def test_timeout_enforcement():
    """Test long-running operations timeout."""
    pass

def test_database_connection_limit():
    """Test max database connections enforced."""
    pass
```

### 7.3 Security Scanning Tools

**SAST (Static Application Security Testing)**:

```bash
# Bandit for Python
bandit -r backend/app/

# ESLint security plugin for JavaScript
eslint --plugin security frontend/src/

# Semgrep for both
semgrep --config=p/security-audit .
```

**DAST (Dynamic Application Security Testing)**:

```bash
# OWASP ZAP
zap-cli quick-scan --self-contained http://localhost:8000

# Nuclei
nuclei -u http://localhost:8000 -t security/
```

**Dependency Scanning**:

```bash
# Python dependencies
safety check
pip-audit

# JavaScript dependencies
npm audit
snyk test
```

**Secret Scanning**:

```bash
# TruffleHog
trufflehog git file://. --only-verified

# detect-secrets
detect-secrets scan --all-files
```

### 7.4 Security Test Execution

**CI Integration**:

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - name: Run Bandit
        run: bandit -r backend/app/

      - name: Run npm audit
        run: npm audit --audit-level=high

      - name: Run Semgrep
        run: semgrep --config=p/security-audit .

      - name: Upload results
        uses: github/codeql-action/upload-sarif@v2
```

**Manual Penetration Testing**:

- Perform before production deployment
- Test all authentication mechanisms (future)
- Test authorization boundaries (future)
- Test session management (future)

**Total Security Tests**: 22

---

## 8. Test Data Management

### 8.1 Test Fixtures

**Backend Fixtures** (pytest):

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

@pytest.fixture(scope="session")
def test_db_engine():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(test_db_engine):
    """Provide database session, rollback after test."""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_story(db_session):
    """Provide a sample complete story."""
    story = Story(
        id="550e8400-e29b-41d4-a716-446655440000",
        title="Sample Horror Story",
        description="A test horror story for testing",
        theme_id="warhammer40k",
        game_file_path="/stories/sample/game.json",
        prompt="Create a horror adventure",
        is_sample=True,
        scene_count=8,
        item_count=12,
        npc_count=3,
        puzzle_count=2
    )
    db_session.add(story)
    db_session.commit()
    return story

@pytest.fixture
def incomplete_story(db_session):
    """Provide an incomplete story (generating)."""
    story = Story(
        id="660e8400-e29b-41d4-a716-446655440001",
        title="Incomplete Story",
        description="Story in generation",
        theme_id="warhammer40k",
        game_file_path="/stories/incomplete/game.json",
        prompt="Test prompt",
        status="generating"
    )
    db_session.add(story)
    db_session.commit()
    return story

@pytest.fixture
def generation_job_queued(db_session):
    """Provide a queued generation job."""
    job = GenerationJob(
        id="770e8400-e29b-41d4-a716-446655440002",
        story_id="550e8400-e29b-41d4-a716-446655440000",
        status="queued",
        progress_percent=0
    )
    db_session.add(job)
    db_session.commit()
    return job

@pytest.fixture
def game_session_active(db_session, sample_story):
    """Provide an active game session."""
    session = GameSession(
        id="880e8400-e29b-41d4-a716-446655440003",
        story_id=sample_story.id,
        current_scene="scene_001",
        inventory=["flashlight"],
        flags=["examined_door"],
        health=100
    )
    db_session.add(session)
    db_session.commit()
    return session

@pytest.fixture
def sample_game_content():
    """Provide sample game.json content."""
    return {
        "plot": {
            "title": "Test Plot",
            "acts": []
        },
        "narrative_map": {
            "scenes": {
                "scene_001": {
                    "title": "Starting Room",
                    "description": "You are in a dark room.",
                    "items": ["flashlight"],
                    "exits": {"north": "scene_002"}
                }
            }
        },
        "puzzles": [],
        "scenes": {}
    }
```

**Frontend Fixtures** (Jest):

```typescript
// frontend/tests/fixtures/stories.ts
export const mockStory = {
  id: '550e8400-e29b-41d4-a716-446655440000',
  title: 'Mock Story',
  description: 'A mock story for testing',
  theme_id: 'warhammer40k',
  scene_count: 8,
  play_count: 5,
  created_at: '2025-11-12T10:00:00Z'
};

export const mockStoryList = [
  mockStory,
  { ...mockStory, id: 'story-2', title: 'Story 2' },
  { ...mockStory, id: 'story-3', title: 'Story 3' }
];

export const mockGenerationJob = {
  generation_job_id: '770e8400-e29b-41d4-a716-446655440002',
  story_id: '550e8400-e29b-41d4-a716-446655440000',
  status: 'in_progress',
  progress_percent: 45,
  current_agent: 'NarrativeArchitect'
};

export const mockGameSession = {
  game_session_id: '880e8400-e29b-41d4-a716-446655440003',
  story_id: '550e8400-e29b-41d4-a716-446655440000',
  initial_scene: 'You awaken in darkness...',
  state: {
    current_scene: 'scene_001',
    inventory: ['flashlight'],
    flags: [],
    health: 100
  }
};
```

### 8.2 Test Database Strategy

**Unit Tests**: SQLite in-memory

```python
engine = create_engine("sqlite:///:memory:")
```

**Integration Tests**: PostgreSQL test instance

```python
engine = create_engine("postgresql://test:test@localhost:5432/test_db")
```

**Database Reset Between Tests**:

```python
@pytest.fixture(autouse=True)
def reset_database(db_session):
    """Reset database before each test."""
    yield
    db_session.rollback()

    # Truncate all tables
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
```

**Seeding Test Data**:

```python
def seed_test_stories(db_session, count=10):
    """Seed database with test stories."""
    for i in range(count):
        story = Story(
            id=f"story-{i}",
            title=f"Test Story {i}",
            theme_id="warhammer40k" if i % 2 == 0 else "cyberpunk",
            scene_count=random.randint(5, 15)
        )
        db_session.add(story)
    db_session.commit()
```

### 8.3 Test Data Files

**Location**: `tests/data/`

**Files**:

```
tests/data/
├── game-content/
│   ├── valid-game.json
│   ├── minimal-game.json
│   ├── large-game.json
│   └── invalid-game.json
├── themes/
│   ├── valid-theme.yaml
│   └── invalid-theme.yaml
├── templates/
│   ├── horror-template.yaml
│   └── rescue-template.yaml
└── saves/
    ├── scene-1-save.json
    └── mid-game-save.json
```

**Loading Test Data**:

```python
import json
from pathlib import Path

def load_test_game_content(filename):
    """Load game content from test data."""
    path = Path(__file__).parent / "data" / "game-content" / filename
    with open(path) as f:
        return json.load(f)
```

---

## 9. Continuous Integration

### 9.1 CI/CD Pipeline

**GitHub Actions Workflow**:

```yaml
# .github/workflows/test-suite.yml
name: Test Suite
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run unit tests with coverage
        run: |
          pytest tests/unit/ -v --cov=app --cov-report=xml --cov-report=html

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: backend

      - name: Check coverage threshold
        run: |
          pytest --cov=app --cov-fail-under=90

  frontend-unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run unit tests with coverage
        run: |
          cd frontend
          npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/coverage-final.json
          flags: frontend

      - name: Check coverage threshold
        run: |
          cd frontend
          npm run test:coverage -- --coverageThreshold='{"global":{"lines":80}}'

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run database migrations
        run: alembic upgrade head
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db

      - name: Run integration tests
        run: pytest tests/integration/ -v --maxfail=5
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Compose
        run: docker-compose -f docker-compose.test.yml up -d

      - name: Wait for services
        run: |
          timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 2; done'

      - name: Install Playwright
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps

      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e

      - name: Upload E2E artifacts
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-results
          path: frontend/test-results/

      - name: Tear down Docker Compose
        if: always()
        run: docker-compose -f docker-compose.test.yml down

  performance-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Set up k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Start services
        run: docker-compose -f docker-compose.test.yml up -d

      - name: Run load tests
        run: k6 run tests/performance/load-test.js

      - name: Upload k6 results
        uses: actions/upload-artifact@v3
        with:
          name: k6-results
          path: k6-results.json

  accessibility-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start services
        run: docker-compose -f docker-compose.test.yml up -d

      - name: Run axe-core tests
        run: |
          cd frontend
          npm ci
          npm run test:a11y

      - name: Run Lighthouse audit
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            http://localhost:3000
            http://localhost:3000/create
            http://localhost:3000/library
          uploadArtifacts: true
          temporaryPublicStorage: true

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Bandit (Python)
        run: |
          pip install bandit
          bandit -r backend/app/ -f json -o bandit-report.json

      - name: Run npm audit
        run: |
          cd frontend
          npm audit --audit-level=high

      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: p/security-audit

      - name: Upload security results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: semgrep.sarif
```

### 9.2 CI Requirements

**All Tests Must Pass Before Merge**:

- Backend unit tests: ✅ >90% coverage
- Frontend unit tests: ✅ >80% coverage
- Integration tests: ✅ All passing
- E2E tests: ✅ Critical journeys passing
- Security scan: ✅ No high/critical vulnerabilities
- Accessibility: ✅ No blocking violations

**CI Performance Targets**:

- Unit tests: <5 minutes
- Integration tests: <10 minutes
- E2E tests: <30 minutes
- Full pipeline: <45 minutes

**Fail Fast**:

- Unit tests run first (fastest feedback)
- Integration tests only if unit tests pass
- E2E tests only if integration tests pass

### 9.3 Coverage Reporting

**Codecov Integration**:

```yaml
# codecov.yml
coverage:
  status:
    project:
      default:
        target: 85%
        threshold: 2%
    patch:
      default:
        target: 80%
```

**Coverage Badge**:

```markdown
[![codecov](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/username/repo)
```

**Coverage Trends**:

- Track coverage over time
- Alert on coverage decrease
- Block PRs that reduce coverage >2%

---

## 10. Test Execution Plan

### 10.1 Phase-by-Phase Testing

**Phase 1: Foundation** (Weeks 1-4)

- **Unit Tests**: Database models, config loading
- **Integration Tests**: Database migrations, API health checks
- **Target Coverage**: 85% (foundational code)

**Phase 2: Story Library** (Weeks 5-6)

- **Unit Tests**: StoryService, theme loading, UI components
- **Integration Tests**: Story CRUD API, theme API
- **E2E Tests**: Browse library, search/filter
- **Target Coverage**: 90% backend, 80% frontend

**Phase 3: Story Creation** (Weeks 7-10)

- **Unit Tests**: GenerationService, CrewAI wrapper, progress components
- **Integration Tests**: Generation flow, WebSocket
- **E2E Tests**: Create from template, monitor progress
- **Performance Tests**: Concurrent generations
- **Target Coverage**: 95% (critical path)

**Phase 4: Iteration System** (Weeks 11-12)

- **Unit Tests**: IterationService, feedback validation
- **Integration Tests**: Iteration flow with feedback
- **E2E Tests**: Submit feedback, review iteration
- **Target Coverage**: 90%

**Phase 5: Gameplay** (Weeks 13-15)

- **Unit Tests**: GameService, game wrapper, UI components
- **Integration Tests**: Game session lifecycle
- **E2E Tests**: Play game, save/load
- **Performance Tests**: Concurrent gameplay sessions
- **Target Coverage**: 95% (critical path)

**Phase 6: Polish** (Week 16)

- **E2E Tests**: All critical journeys
- **Performance Tests**: Full load testing
- **Accessibility Tests**: Complete WCAG audit
- **Security Tests**: Penetration testing
- **Target Coverage**: 90% overall

### 10.2 Acceptance Criteria by Task

**Updated IMPLEMENTATION_PLAN.md with Test Requirements**:

**Task 1.2: Database Setup**

- [ ] 10 unit tests for CRUD operations
- [ ] 5 integration tests for migrations
- [ ] Coverage >95%

**Task 2.1: Story Service**

- [ ] 15 unit tests (see section 2.1.1)
- [ ] 100% coverage of public methods
- [ ] All error cases tested

**Task 3.2: CrewAI Wrapper**

- [ ] 7 unit tests (see section 2.1.6)
- [ ] Mock CrewAI execution
- [ ] Test progress callbacks
- [ ] Coverage >95%

**Task 3.8: Generation Progress UI**

- [ ] 8 unit tests (see section 2.2.5)
- [ ] WebSocket integration test
- [ ] E2E test for progress monitoring
- [ ] Coverage >90%

**Task 5.2: Game Service**

- [ ] 10 unit tests (see section 2.1.4)
- [ ] Integration test for session lifecycle
- [ ] Coverage >95%

**Task 6.5: End-to-End Testing**

- [ ] All 15 critical journeys implemented
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Mobile viewport testing
- [ ] All tests passing

### 10.3 Test Metrics Dashboard

**KPIs to Track**:

- **Code Coverage**: Backend %, Frontend %
- **Test Count**: Unit, Integration, E2E
- **Test Execution Time**: By category
- **Flaky Test Rate**: % of flaky tests
- **Bug Escape Rate**: Bugs found in production vs. testing
- **Mean Time to Detect**: Time to find bugs
- **Test Maintenance Cost**: Time spent fixing tests

**Dashboard Tools**:

- Codecov for coverage trends
- GitHub Actions for CI metrics
- Grafana for performance trends
- Custom script for flaky test tracking

### 10.4 Test Documentation

**Required Documentation**:

1. **Test Plan**: This document
2. **Test Cases**: Inline in test files with docstrings
3. **Test Data**: README in tests/data/
4. **Bug Reports**: GitHub Issues with `bug` label
5. **Test Results**: CI artifacts and Codecov

**Test Case Documentation Format**:

```python
def test_function_name():
    """
    Test description: What is being tested

    Preconditions:
    - Database has sample story
    - User is authenticated (future)

    Steps:
    1. Call service method with valid input
    2. Verify output matches expected
    3. Verify database updated

    Expected Results:
    - Function returns expected value
    - Database record created
    - No exceptions raised

    Test Data:
    - sample_story fixture
    - valid_prompt = "Create a horror adventure"
    """
    pass
```

---

## Summary

### Test Count Overview

| Category | Tests |
|----------|-------|
| **Backend Unit** | 68 |
| **Frontend Unit** | 55 |
| **Integration** | 50 |
| **End-to-End** | 15 |
| **Performance** | 4 scenarios |
| **Accessibility** | 20 |
| **Security** | 22 |
| **Total** | **230+** |

### Coverage Targets

- **Backend**: 90% overall, 95% critical paths
- **Frontend**: 80% overall, 90% critical components
- **100% Coverage**: Auth, payments, deletion, security

### Testing Tools

**Backend**:

- pytest, pytest-cov, pytest-mock, pytest-asyncio
- Bandit, Safety, Semgrep

**Frontend**:

- Jest, React Testing Library, @testing-library/user-event
- Playwright or Cypress
- axe-core, Lighthouse
- ESLint security plugin

**Performance**:

- k6 or Locust
- Grafana, Prometheus

**CI/CD**:

- GitHub Actions
- Codecov
- Docker Compose

### Next Steps

1. ✅ Review and approve testing strategy
2. ✅ Set up CI/CD pipeline (Task 1.6)
3. ✅ Implement unit tests alongside development
4. ✅ Add integration tests after API endpoints complete
5. ✅ Implement E2E tests in Phase 6
6. ✅ Run performance tests before production
7. ✅ Complete accessibility audit before launch

---

**This testing strategy ensures comprehensive quality coverage across all aspects of the web interface, from individual functions to complete user journeys, performance, accessibility, and security.**

**Version**: 1.0
**Status**: ✅ Ready for Implementation
**Last Updated**: 2025-11-12
