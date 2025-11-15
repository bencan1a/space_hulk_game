# Phase 4 Agent Prompts: Iteration System Tasks
## Browser-Based Game Interface Implementation

**Phase**: 4 - Iteration System (Weeks 11-12)
**Objective**: Enable users to provide feedback on generated stories, trigger new AI-driven iterations based on that feedback, and compare different versions of a story.
**Deliverables**: A feedback and iteration API, a structured feedback form, and a UI for visualizing iteration history and comparing story versions.

---

## Table of Contents

1. [Task 4.1: Iteration Service](#task-41-iteration-service)
2. [Task 4.2: Iteration API Endpoints](#task-42-iteration-api-endpoints)
3. [Task 4.3: Feedback Form UI](#task-43-feedback-form-ui)
4. [Task 4.4: Iteration History UI](#task-44-iteration-history-ui)
5. [Task 4.5: Version Comparison UI](#task-45-version-comparison-ui)

---

## Task 4.1: Iteration Service

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 3.3 (Generation Service), Task 2.1 (Story Service)

### Context

You are implementing the backend service that powers the story iteration feature. This service will be responsible for taking user feedback, initiating new generation tasks with that feedback as context, and managing the relationship between different versions of a story.

**Project Documentation**:
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 4.1

### Your Mission

Create an `IterationService` in `backend/app/services/iteration_service.py`. This service will handle the logic for submitting feedback and triggering new, context-aware generation runs.

### Deliverables

```
backend/
└── app/
    └── services/
        └── iteration_service.py  # Main service class
tests/
└── test_iteration_service.py
```

### Acceptance Criteria

- [ ] `IterationService` class with methods: `submit_feedback(story_id, feedback_data)`, `start_iteration(story_id)`, `list_iterations(story_id)`.
- [ ] When `start_iteration` is called, it should trigger a new generation task (from Phase 3) and pass the collected feedback into the prompt context.
- [ ] The service must enforce a limit of 5 iterations per story.
- [ ] A new `StoryVersion` or similar model should be created to link the original story with its iterations.
- [ ] Unit tests for submitting feedback, starting an iteration, and verifying the iteration limit is enforced.

---

## Task 4.2: Iteration API Endpoints

**Priority**: P0
**Effort**: 1 day
**Dependencies**: Task 4.1 (Iteration Service)

### Context

You will expose the `IterationService` functionality through a set of REST API endpoints. These endpoints will allow the frontend to submit feedback, start new iterations, and retrieve the history of versions for a story.

**Project Documentation**:
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 4.2

### Your Mission

Implement a new API router in `backend/app/api/routes/iterations.py` for managing story iterations.

### Deliverables

```
backend/
└── app/
    └── api/
        └── routes/
            └── iterations.py    # FastAPI router for iterations
tests/
└── test_iterations_api.py       # API endpoint tests
```

### Acceptance Criteria

- [ ] `POST /api/stories/{story_id}/iterate`: Submits feedback and starts a new iteration task.
- [ ] `GET /api/stories/{story_id}/iterations`: Retrieves a list of all versions/iterations for a given story.
- [ ] Implement Pydantic-based validation for the feedback submission payload.
- [ ] The API should return a clear error message if the maximum number of iterations has been reached.
- [ ] Integration tests for each endpoint.

---

## Task 4.3: Feedback Form UI

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 4.2 (Iteration API), Task 1.7 (Component Library)

### Context

You are building the user-facing form for collecting structured feedback on a generated story. This form will capture both qualitative and quantitative data to guide the next AI iteration.

**Project Documentation**:
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 4.3

### Your Mission

Create the `FeedbackForm` and `FeedbackPage` React components. The form should be intuitive and provide users with multiple ways to express their desired changes.

### Deliverables

```
frontend/
└── src/
    ├── components/
    │   └── iteration/
    │       └── FeedbackForm.tsx
    └── pages/
        └── FeedbackPage.tsx
```

### Acceptance Criteria

- [ ] A `FeedbackForm` component containing:
    - A free-form textarea for detailed comments (minimum 100 characters).
    - Sliders to adjust parameters like "Tone" (e.g., more horror) and "Difficulty".
    - Checkboxes for focus areas (e.g., "More puzzles," "Deeper characters").
- [ ] The form should display the current iteration count (e.g., "This will be iteration 2/5").
- [ ] The `FeedbackPage` hosts the form and handles the submission logic, calling the iteration API.
- [ ] Form validation to ensure all required fields are completed correctly.
- [ ] Storybook stories for the `FeedbackForm` component.

---

## Task 4.4: Iteration History UI

**Priority**: P1
**Effort**: 2 days
**Dependencies**: Task 4.2 (Iteration API)

### Context

To give users a clear overview of a story's evolution, you will create a UI to display the list of all its iterations.

**Project Documentation**:
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 4.4

### Your Mission

Develop the `IterationHistory` and `IterationCard` components to display a timeline of story versions.

### Deliverables

```
frontend/
└── src/
    └── components/
        └── iteration/
            ├── IterationHistory.tsx
            └── IterationCard.tsx
```

### Acceptance Criteria

- [ ] `IterationHistory` fetches and displays a list of iterations for a story in reverse chronological order.
- [ ] `IterationCard` represents a single version, showing its version number, creation date, and status (e.g., Pending, Accepted, Rejected - if applicable).
- [ ] Each `IterationCard` includes "View Game" and "Compare" buttons.
- [ ] "View Game" navigates to the player for that specific version.
- [ ] "Compare" navigates to the version comparison UI.
- [ ] Storybook stories for both components.

---

## Task 4.5: Version Comparison UI

**Priority**: P2
**Effort**: 2 days
**Dependencies**: Task 4.1 (Iteration Service), Task 4.4 (Iteration History UI)

### Context

A key feature of the iteration system is the ability to compare two versions of a story side-by-side. You will build a UI that highlights the differences between two selected versions.

**Project Documentation**:
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 4.5

### Your Mission

Create a `VersionComparison` component and a `ComparePage` that provides a "diff" view of two story files.

### Deliverables

```
frontend/
└── src/
    ├── components/
    │   └── iteration/
    │       └── VersionComparison.tsx
    └── pages/
        └── ComparePage.tsx
```

### Acceptance Criteria

- [ ] The `ComparePage` allows the user to select two versions of a story to compare (e.g., Version 1 and Version 3).
- [ ] `VersionComparison` component displays the content of the two versions in a side-by-side split view.
- [ ] The UI must visually highlight the differences between the two versions (e.g., using a library like `diff-match-patch` or similar).
    - Additions should be highlighted in green.
    - Deletions should be highlighted in red.
    - Modifications should be highlighted in yellow.
- [ ] The comparison should be easy to read and understand.
- [ ] Unit and integration tests to ensure differences are correctly identified and highlighted.
