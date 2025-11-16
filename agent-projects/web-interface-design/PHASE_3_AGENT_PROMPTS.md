# Phase 3 Agent Prompts: Content Generation Tasks

## Browser-Based Game Interface Implementation

**Phase**: 3 - Content Generation (Weeks 7-10)
**Objective**: Integrate CrewAI to generate new game content based on user prompts and templates.
**Deliverables**: A template-driven generation pipeline, real-time progress updates via WebSockets, and a UI for initiating and monitoring content creation.

---

## Table of Contents

1. [Task 3.1: Prompt Template System](#task-31-prompt-template-system)
2. [Task 3.2: CrewAI Wrapper Implementation](#task-32-crewai-wrapper-implementation)
3. [Task 3.3: Generation Service & Celery Task](#task-33-generation-service--celery-task)
4. [Task 3.4: WebSocket Progress Handler](#task-34-websocket-progress-handler)
5. [Task 3.5: Generation API Endpoints](#task-35-generation-api-endpoints)
6. [Task 3.6: Template Gallery UI](#task-36-template-gallery-ui)
7. [Task 3.7: Chat Refinement UI](#task-37-chat-refinement-ui)
8. [Task 3.8: Generation Progress UI](#task-38-generation-progress-ui)
9. [Task 3.9: Story Preview & Review UI](#task-39-story-preview--review-ui)

---

## Task 3.1: Prompt Template System

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 1.1 (Project Scaffolding)

### Context

You are creating a system for managing prompt templates that will guide the AI in generating game content. These templates, defined in YAML, will use Jinja2 for variable substitution, allowing for dynamic and structured prompt engineering.

**Project Documentation**:

- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 3.1

### Your Mission

Create a `TemplateService` to load, list, and render Jinja2-based prompt templates from a directory of YAML files. You will also create the initial set of templates for different game genres.

### Deliverables

```
backend/
├── app/
│   └── services/
│       └── template_service.py  # Service for managing templates
└── data/
    └── templates/
        ├── horror.yaml
        ├── artifact_hunt.yaml
        └── rescue.yaml
tests/
└── test_template_service.py
```

### Acceptance Criteria

- [ ] YAML files in `data/templates/` define prompt templates with Jinja2 variables.
- [ ] `TemplateService` with methods: `list_templates()`, `get_template(name)`, `render_template(name, context)`.
- [ ] API endpoints (`GET /api/templates`, `GET /api/templates/{name}`) to expose templates to the frontend.
- [ ] Unit tests to verify template loading and correct rendering with a given context.

---

## Task 3.2: CrewAI Wrapper Implementation

**Priority**: P0
**Effort**: 3 days
**Dependencies**: Existing CrewAI setup, Task 1.5 (Logging)

### Context

You are building a wrapper around the existing CrewAI execution logic to provide better control and monitoring. This wrapper will manage the execution of a generation crew, handle long-running processes, and provide real-time feedback via a callback system.

**Project Documentation**:

- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 3.2

### Your Mission

Implement a `CrewAIWrapper` class in `backend/app/integrations/crewai_wrapper.py`. This class will have a primary method to execute a crew with a given prompt and a callback function to report progress.

### Deliverables

```
backend/
└── app/
    └── integrations/
        └── crewai_wrapper.py  # Main wrapper class
tests/
└── test_crewai_wrapper.py
```

### Acceptance Criteria

- [ ] `CrewAIWrapper` class with an `execute_generation(prompt: str, progress_callback: callable)` method.
- [ ] The wrapper must not modify the existing `crew.py` file.
- [ ] The `progress_callback` is called after each agent's task is completed, providing status updates.
- [ ] Implement robust error handling and a timeout mechanism (e.g., 15 minutes) for the generation process.
- [ ] Unit tests using a mock crew to verify that the execution flow, progress callbacks, and error/timeout handling work as expected.

---

## Task 3.3: Generation Service & Celery Task

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 3.2 (CrewAI Wrapper), Task 2.1 (Story Service)

### Context

To handle the long-running nature of AI content generation, you will create an asynchronous task using Celery. A `GenerationService` will act as the interface to start these tasks, which will run the `CrewAIWrapper` in the background.

**Project Documentation**:

- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 3.3

### Your Mission

Create a `GenerationService` that initiates content generation. The core logic will be encapsulated in a Celery task within `backend/app/tasks/generation_tasks.py`. This task will update a `Session` model with progress and create a new `Story` upon completion.

### Deliverables

```
backend/
├── app/
│   ├── services/
│   │   └── generation_service.py
│   └── tasks/
│       └── generation_tasks.py  # Celery task for generation
└── tests/
    └── test_generation_service.py
```

### Acceptance Criteria

- [ ] `GenerationService.start_generation(prompt)` method that returns a unique `session_id`.
- [ ] A Celery task `run_generation_crew(session_id, prompt)` that uses the `CrewAIWrapper`.
- [ ] The task updates a `Session` database model with progress and status (e.g., PENDING, RUNNING, COMPLETED, FAILED).
- [ ] Upon successful completion, the task creates a `Story` record using `StoryService` and saves the generated `game.json` to a file system.
- [ ] Tests to verify that `start_generation` creates a session and enqueues the Celery task.

---

## Task 3.4: WebSocket Progress Handler

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 3.3 (Generation Service)

### Context

To provide a real-time user experience, you will implement a WebSocket endpoint that streams progress updates from the generation task to the frontend.

**Project Documentation**:

- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 3.4

### Your Mission

Create a WebSocket endpoint at `/ws/progress/{session_id}` in `backend/app/api/websocket.py`. This endpoint will be used by the `CrewAIWrapper`'s callback to broadcast progress messages to connected clients.

### Deliverables

```
backend/
└── app/
    └── api/
        └── websocket.py  # WebSocket connection manager and endpoint
tests/
└── test_websocket.py
```

### Acceptance Criteria

- [ ] A WebSocket endpoint `/ws/progress/{session_id}` that accepts client connections.
- [ ] A connection manager to track active connections for each session.
- [ ] The `progress_callback` from the `CrewAIWrapper` will use this handler to broadcast messages to the relevant clients.
- [ ] Implement a heartbeat mechanism to keep connections alive (e.g., send a ping every 30 seconds).
- [ ] Ensure graceful handling of client disconnections.
- [ ] Load tests to ensure the WebSocket can handle at least 10 concurrent connections without issues.

---

## Task 3.5: Generation API Endpoints

**Priority**: P0
**Effort**: 1 day
**Dependencies**: Task 3.3 (Generation Service)

### Context

You will create the REST API endpoints that the frontend will use to start and monitor the content generation process.

**Project Documentation**:

- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 3.5

### Your Mission

Implement a new API router in `backend/app/api/routes/generation.py` with endpoints to start a generation task and check its status.

### Deliverables

```
backend/
└── app/
    └── api/
        └── routes/
            └── generation.py
tests/
└── test_generation_api.py
```

### Acceptance Criteria

- [ ] `POST /api/generate`: Starts a new generation task. Accepts a prompt or template details. Returns a `session_id`.
- [ ] `GET /api/generate/{session_id}`: Retrieves the current status and progress of a generation task.
- [ ] Implement request validation to ensure prompts meet required criteria (e.g., length).
- [ ] Integration tests for starting a generation and polling for status.

---

## Task 3.6: Template Gallery UI

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 3.1 (Template Service), Task 1.7 (Component Library)

### Context

You are building the user interface that allows users to choose how they want to generate a new game. This will include a gallery of predefined templates and an option for a fully custom prompt.

**Project Documentation**:

- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 3.6

### Your Mission

Create the `TemplateGallery`, `TemplateCard`, and `CustomPromptForm` React components.

### Deliverables

```
frontend/
└── src/
    └── components/
        └── generation/
            ├── TemplateGallery.tsx
            ├── TemplateCard.tsx
            └── CustomPromptForm.tsx
```

### Acceptance Criteria

- [ ] `TemplateGallery` fetches and displays a grid of available templates from the API.
- [ ] `TemplateCard` represents a single template and is selectable.
- [ ] `CustomPromptForm` provides a textarea for users to write their own prompt, with validation (e.g., 50-1000 characters).
- [ ] The UI clearly distinguishes between selecting a template and writing a custom prompt.
- [ ] Storybook stories for each component.

---

## Task 3.7: Chat Refinement UI

**Priority**: P0
**Effort**: 3 days
**Dependencies**: Task 3.6 (Template Gallery)

### Context

To help users create better prompts, you will build a conversational interface that guides them through a series of questions. This "chat refinement" process will progressively build a detailed prompt based on user answers.

**Project Documentation**:

- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 3.7

### Your Mission

Develop the `ChatInterface`, `ChatMessage`, and `ChatInput` components to create a guided, conversational form.

### Deliverables

```
frontend/
└── src/
    └── components/
        └── generation/
            ├── ChatInterface.tsx
            ├── ChatMessage.tsx
            └── ChatInput.tsx
```

### Acceptance Criteria

- [ ] `ChatInterface` manages a sequential flow of questions and user responses.
- [ ] `ChatMessage` displays messages from both the user and the "AI" assistant.
- [ ] `ChatInput` captures user input and includes validation based on the current question.
- [ ] After the conversation, a final, formatted prompt is displayed for user confirmation before starting the generation.
- [ ] Storybook stories to test the full conversational flow.

---

## Task 3.8: Generation Progress UI

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 3.4 (WebSocket Handler), Task 3.7 (Chat UI)

### Context

You will build the UI that provides real-time feedback to the user while their game content is being generated. This interface will connect to the WebSocket endpoint and display live progress updates.

**Project Documentation**:

- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 3.8

### Your Mission

Create a `GenerationProgress` component and a custom hook, `useWebSocket`, to manage the WebSocket connection and message handling.

### Deliverables

```
frontend/
└── src/
    ├── components/
    │   └── generation/
    │       └── GenerationProgress.tsx
    └── hooks/
        └── useWebSocket.ts
```

### Acceptance Criteria

- [ ] `useWebSocket` hook to establish and manage a WebSocket connection to the `/ws/progress/{session_id}` endpoint.
- [ ] The hook must handle connection, disconnection, and message receiving, as well as automatic reconnection logic.
- [ ] `GenerationProgress` component displays a progress bar that updates in real-time based on messages from the WebSocket.
- [ ] An `AgentStatusList` within the component shows the status of each agent in the crew, updating from pending to complete (e.g., `○ → ✓`).
- [ ] The UI provides a clear final status (Completed or Failed) once the generation is finished.

---

## Task 3.9: Story Preview & Review UI

**Priority**: P1
**Effort**: 1 day
**Dependencies**: Task 3.8 (Progress UI)

### Context

Once the content generation is complete, the user needs to see a summary of the generated story and decide on the next steps.

**Project Documentation**:

- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 3.9

### Your Mission

Create a `StoryPreview` component and a `ReviewPage` to display the results of the generation.

### Deliverables

```
frontend/
└── src/
    ├── components/
    │   └── generation/
    │       └── StoryPreview.tsx
    └── pages/
        └── ReviewPage.tsx
```

### Acceptance Criteria

- [ ] `StoryPreview` displays key metadata from the generated story (e.g., title, description, tags) and interesting statistics (e.g., number of scenes, items).
- [ ] The `ReviewPage` hosts the `StoryPreview`.
- [ ] The page includes two main calls to action: "Play Now" and "Give Feedback".
- [ ] "Play Now" navigates the user to the gameplay interface for the new story.
- [ ] "Give Feedback" navigates the user to the iteration/feedback form.
- [ ] Storybook stories for the `StoryPreview` component with mock data.
