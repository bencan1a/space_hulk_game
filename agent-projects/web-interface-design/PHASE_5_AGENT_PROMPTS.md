# Phase 5 Agent Prompts: Gameplay Tasks
## Browser-Based Game Interface Implementation

**Phase**: 5 - Gameplay (Weeks 13-15)
**Objective**: Integrate the core game engine, build the gameplay UI, and implement a save/load system.
**Deliverables**: A stateful game session API, a functional player UI for interacting with the game, and a persistent save/load system.

---

## Table of Contents

1. [Task 5.1: Game Engine Wrapper](#task-51-game-engine-wrapper)
2. [Task 5.2: Game Service & Session Management](#task-52-game-service--session-management)
3. [Task 5.3: Game API Endpoints](#task-53-game-api-endpoints)
4. [Task 5.4: Game Player UI - Display](#task-54-game-player-ui---display)
5. [Task 5.5: Game Player UI - Input & Controls](#task-55-game-player-ui---input--controls)
6. [Task 5.6: Game State Management](#task-56-game-state-management)
7. [Task 5.7: Save/Load System](#task-57-saveload-system)

---

## Task 5.1: Game Engine Wrapper

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Existing Game Engine

### Context

You are building a wrapper around the existing text-based game engine to manage stateful game sessions. This wrapper will be the primary integration point between the web backend and the core game logic. It must encapsulate game state and expose methods for command processing and state serialization without modifying the original engine.

**Project Documentation**:
- Architecture: `ARCHITECTURAL_DESIGN.md`
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 5.1

### Your Mission

Create a `GameWrapper` class in `backend/app/integrations/game_wrapper.py`. This class will initialize a game from a file, process player commands, expose the current game state, and handle saving and loading of that state.

### Deliverables

```
backend/
└── app/
    └── integrations/
        ├── __init__.py
        └── game_wrapper.py    # Main wrapper class
tests/
└── test_game_wrapper.py       # Wrapper tests
```

### Acceptance Criteria

- [ ] `GameWrapper` class with methods: `__init__(game_file_path)`, `process_command(command)`, `get_state()`, `save_state()`, `load_state(state_data)`.
- [ ] The wrapper must not modify the existing game engine code.
- [ ] `get_state()` returns a serializable representation of the current game view (e.g., scene text, inventory, available commands).
- [ ] `save_state()` and `load_state()` correctly serialize and deserialize the entire game state for persistence.
- [ ] Comprehensive docstrings and type hints for all methods.
- [ ] Unit tests demonstrating a full command processing and save/load round-trip.

### Technical Requirements

**Game Wrapper (`integrations/game_wrapper.py`)**:
```python
"""Wrapper for managing stateful game engine sessions."""
import logging
from typing import Any, Dict

# Assuming the original game engine has a main class to instantiate
# from game_engine import Game

logger = logging.getLogger(__name__)


class GameWrapper:
    """Manages a single, stateful instance of the game engine."""

    def __init__(self, game_file_path: str):
        """Initializes the game session from a story file."""
        # self.game = Game(game_file_path)
        # self.state = self.game.get_initial_state()
        pass

    def process_command(self, command: str) -> Dict[str, Any]:
        """Processes a player command and returns the new game state."""
        # self.state = self.game.process(command)
        # return self.get_state()
        pass

    def get_state(self) -> Dict[str, Any]:
        """Returns the current, serializable game state."""
        # return self.state.to_dict()
        pass

    def save_state(self) -> Dict[str, Any]:
        """Serializes the current game state for saving."""
        # return self.game.serialize()
        pass

    def load_state(self, state_data: Dict[str, Any]):
        """Deserializes game state to load a session."""
        # self.game.deserialize(state_data)
        # self.state = self.game.get_current_state()
        pass
```

---

## Task 5.2: Game Service & Session Management

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 5.1 (Game Engine Wrapper)

### Context

You are creating a service to manage active gameplay sessions. This `GameService` will be responsible for starting new games, handling player commands by delegating to the `GameWrapper`, and managing the lifecycle of game sessions, including persistence and timeouts.

**Project Documentation**:
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 5.2

### Your Mission

Implement the `GameService` in `backend/app/services/game_service.py`. This service will use an in-memory dictionary to store active sessions, identified by a unique session ID. You will also define a `GameSession` database model for persisting saved games.

### Deliverables

```
backend/
├── app/
│   ├── services/
│   │   └── game_service.py    # Main service class
│   ├── models/
│   │   └── game_session.py    # SQLAlchemy model for saved games
│   └── schemas/
│       └── game.py            # Pydantic schemas for game API
└── tests/
    └── test_game_service.py   # Service tests
```

### Acceptance Criteria

- [ ] `GameService` class with methods: `start_game(story_id)`, `process_command(session_id, command)`, `save_game(session_id, user_id, name)`, `load_game(save_id, user_id)`.
- [ ] An in-memory dictionary (`active_sessions`) to store `GameWrapper` instances.
- [ ] A `GameSession` SQLAlchemy model to store saved game data, linked to a user and story.
- [ ] Sessions in the in-memory cache should time out and be removed after 1 hour of inactivity.
- [ ] `save_game` persists the game state from the wrapper into the database.
- [ ] `load_game` retrieves a saved state and creates a new active session from it.
- [ ] Unit tests covering the full session lifecycle, including start, command, save, load, and timeout.

---

## Task 5.3: Game API Endpoints

**Priority**: P0
**Effort**: 1 day
**Dependencies**: Task 5.2 (Game Service)

### Context

With the game service layer in place, you will now expose its functionality through a set of REST API endpoints. These endpoints will allow the frontend to start games, send commands, and manage save/load operations.

**Project Documentation**:
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 5.3

### Your Mission

Create a new API router in `backend/app/api/routes/gameplay.py` and implement the endpoints for all gameplay interactions. Use the `GameService` to handle the business logic.

### Deliverables

```
backend/
└── app/
    └── api/
        └── routes/
            └── gameplay.py    # FastAPI router for gameplay
tests/
└── test_gameplay_api.py       # API endpoint tests
```

### Acceptance Criteria

- [ ] `POST /api/game/{story_id}/start`: Starts a new game session and returns the initial state and session ID.
- [ ] `POST /api/game/{session_id}/command`: Sends a command to a session and returns the updated game state.
- [ ] `POST /api/game/{session_id}/save`: Saves the current state of a session.
- [ ] `GET /api/game/load/{save_id}`: Loads a saved game into a new session and returns its state.
- [ ] All endpoints should be protected and require user authentication.
- [ ] Use Pydantic schemas for request bodies and responses to ensure type safety and validation.
- [ ] Integration tests for each endpoint, mocking the service layer where appropriate.

---

## Task 5.4: Game Player UI - Display

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 1.3 (UI Component Library), Task 2.7 (Theme Selector UI)

### Context

You are building the core display components for the gameplay interface. This includes rendering the main scene description, the player's inventory, and a log of game output. These components should be dynamic and update based on the game state provided by the backend.

**Project Documentation**:
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 5.4

### Your Mission

Create a set of React components for the game display. The `GameDisplay` component will be the main container, orchestrating the `SceneRenderer`, `InventoryPanel`, and `OutputLog`.

### Deliverables

```
frontend/
└── src/
    └── components/
        └── game/
            ├── GameDisplay.tsx
            ├── SceneRenderer.tsx
            ├── InventoryPanel.tsx
            └── OutputLog.tsx
```

### Acceptance Criteria

- [ ] `SceneRenderer`: Renders Markdown-formatted scene descriptions.
- [ ] `InventoryPanel`: Displays a list of the player's items.
- [ ] `OutputLog`: Shows a history of messages from the game engine, with auto-scrolling to the latest message.
- [ ] `GameDisplay`: Composes the above components into a cohesive layout.
- [ ] All components must be styled according to the currently active theme.
- [ ] Storybook stories for each component to test rendering with various game states.

---

## Task 5.5: Game Player UI - Input & Controls

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 5.3 (Game API), Task 5.4 (Game Display UI)

### Context

You will implement the user interaction elements for the gameplay screen. This includes the command input field and buttons for essential game actions like saving, loading, and quitting.

**Project Documentation**:
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 5.5

### Your Mission

Create the `CommandInput` and `GameControls` components, and integrate them into a new `PlayerPage` that combines the display and input elements into the final gameplay interface.

### Deliverables

```
frontend/
└── src/
    ├── components/
    │   └── game/
    │       ├── CommandInput.tsx
    │       └── GameControls.tsx
    └── pages/
        └── PlayerPage.tsx
```

### Acceptance Criteria

- [ ] `CommandInput`: A text field where users can type commands. Submits the command on "Enter".
- [ ] Command history is implemented, allowing users to navigate previous commands with the up and down arrow keys.
- [ ] `GameControls`: Buttons for "Save", "Load", and "Quit".
- [ ] Keyboard shortcuts for core actions (e.g., `Ctrl+S` for Save).
- [ ] `PlayerPage`: The main page component that assembles the `GameDisplay`, `CommandInput`, and `GameControls`.
- [ ] Storybook stories for `CommandInput` and `GameControls`.

---

## Task 5.6: Game State Management

**Priority**: P0
**Effort**: 1 day
**Dependencies**: Task 5.5 (Player UI)

### Context

To connect the UI components to the backend API, you need a centralized state management solution for the active game session. A React Context will provide the game state and actions to all gameplay-related components.

**Project Documentation**:
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 5.6

### Your Mission

Create a `GameContext` using React's Context API. This context will hold the current game state (session ID, scene data, inventory, etc.) and provide a function to send commands to the backend.

### Deliverables

```
frontend/
└── src/
    └── contexts/
        └── GameContext.tsx
```

### Acceptance Criteria

- [ ] `GameContext` provides the active game session data: `session`, `scene`, `inventory`, `log`.
- [ ] It exposes a `sendCommand(command: string)` function that calls the backend API and updates the state with the response.
- [ ] The `PlayerPage` and its children consume this context to display data and handle user input.
- [ ] The context provider is wrapped around the `PlayerPage`.
- [ ] Unit tests for the context provider, mocking API calls, to verify state updates correctly.

---

## Task 5.7: Save/Load System

**Priority**: P0
**Effort**: 2 days
**Dependencies**: Task 5.3 (Game API), Task 5.6 (Game State Management)

### Context

The final piece of the gameplay loop is the user interface for saving and loading games. You will create modals that allow players to save their progress with a descriptive name and load a previous save from a list.

**Project Documentation**:
- Implementation Plan: `IMPLEMENTATION_PLAN.md` Task 5.7

### Your Mission

Develop the `SaveModal`, `LoadModal`, and `SaveCard` components. The `GameControls` component will trigger these modals.

### Deliverables

```
frontend/
└── src/
    └── components/
        └── game/
            ├── SaveModal.tsx
            ├── LoadModal.tsx
            └── SaveCard.tsx
```

### Acceptance Criteria

- [ ] `SaveModal`: A dialog that prompts the user for a save name and calls the save API endpoint.
- [ ] `LoadModal`: A dialog that fetches and displays a list of the user's saved games for the current story.
- [ ] `SaveCard`: A component used within `LoadModal` to display information about a single save (name, timestamp).
- [ ] The `LoadModal` allows the user to select a save to load or delete a save.
- [ ] The UI provides feedback during save/load operations (e.g., loading spinners, success/error messages).
- [ ] End-to-end tests for the save/load flow: save a game, see it in the load modal, load it, and verify the game state is restored.
