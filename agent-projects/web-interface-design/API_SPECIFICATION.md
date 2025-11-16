# API Specification: Web Interface

## Canonical REST and WebSocket API Reference

**Version**: 1.0
**Created**: 2025-11-12
**Status**: Canonical Reference
**Purpose**: Single source of truth for all API endpoints

---

## Design Principles

1. **Consistent Versioning**: All REST endpoints use `/api/v1/` prefix
2. **RESTful Design**: Resources as nouns, HTTP methods as verbs
3. **Clear Naming**: Distinguish `generation_job_id` from `game_session_id`
4. **Standard Responses**: Consistent JSON structure across all endpoints
5. **Error Handling**: Standard error format with codes and user messages

---

## Base URL

**Development**: `http://localhost:8000`
**Production**: `https://your-domain.com`

All paths below are relative to base URL.

---

## Standard Response Formats

### Success Response

```json
{
  "data": { /* resource or collection */ },
  "meta": {
    "timestamp": "2025-11-12T20:00:00Z",
    "version": "1.0"
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Technical error message",
    "user_message": "User-friendly message",
    "details": { /* optional additional context */ },
    "retry_possible": true,
    "timestamp": "2025-11-12T20:00:00Z"
  }
}
```

### Pagination Response

```json
{
  "data": [ /* array of items */ ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

---

## Authentication

**Current (MVP)**: No authentication required (single-user deployment)
**Future**: JWT bearer tokens in `Authorization: Bearer <token>` header

---

## REST API Endpoints

### Stories

#### List Stories

**Endpoint**: `GET /api/v1/stories`

**Description**: Retrieve paginated list of stories with filtering and search.

**Query Parameters**:

- `page` (integer, optional, default: 1): Page number
- `per_page` (integer, optional, default: 20, max: 100): Items per page
- `sort` (string, optional, default: "newest"): Sort order
  - Values: `newest`, `oldest`, `most_played`, `title_asc`, `title_desc`
- `search` (string, optional): Case-insensitive search in title and description
- `filter` (string, optional, default: "all"): Filter by type
  - Values: `all`, `samples`, `user_created`
- `theme` (string, optional): Filter by theme_id

**Response**: `200 OK`

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Derelict's Nightmare",
      "description": "A horror-themed exploration...",
      "theme_id": "warhammer40k",
      "is_sample": false,
      "created_at": "2025-11-12T10:00:00Z",
      "updated_at": "2025-11-12T10:00:00Z",
      "current_version": 1,
      "total_iterations": 0,
      "play_count": 5,
      "scene_count": 8,
      "item_count": 12,
      "npc_count": 3,
      "puzzle_count": 2,
      "tags": ["horror", "atmospheric"]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 42,
    "pages": 3
  }
}
```

**Errors**:

- `400 Bad Request`: Invalid query parameters

---

#### Get Story Details

**Endpoint**: `GET /api/v1/stories/{story_id}`

**Description**: Retrieve detailed information about a specific story.

**Path Parameters**:

- `story_id` (string, required): UUID of the story

**Response**: `200 OK`

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Derelict's Nightmare",
    "description": "A horror-themed exploration of a derelict space station...",
    "theme_id": "warhammer40k",
    "is_sample": false,
    "created_at": "2025-11-12T10:00:00Z",
    "updated_at": "2025-11-12T10:00:00Z",
    "current_version": 1,
    "total_iterations": 0,
    "play_count": 5,
    "last_played": "2025-11-12T15:30:00Z",
    "original_prompt": "Create a horror-themed Space Hulk adventure...",
    "template_id": "horror_infestation",
    "scene_count": 8,
    "item_count": 12,
    "npc_count": 3,
    "puzzle_count": 2,
    "tags": ["horror", "atmospheric", "combat-light"],
    "game_data_path": "/stories/550e8400-e29b-41d4-a716-446655440000/game.json"
  }
}
```

**Errors**:

- `404 Not Found`: Story does not exist

---

#### Get Story Game Content

**Endpoint**: `GET /api/v1/stories/{story_id}/content`

**Description**: Retrieve full game JSON content for a story.

**Path Parameters**:

- `story_id` (string, required): UUID of the story

**Response**: `200 OK`

```json
{
  "data": {
    "plot": { /* plot_outline.json content */ },
    "narrative_map": { /* narrative_map.json content */ },
    "puzzles": { /* puzzle_design.json content */ },
    "scenes": { /* scene_texts.json content */ },
    "prd": { /* prd_document.json content */ }
  }
}
```

**Errors**:

- `404 Not Found`: Story or content not found

---

#### Delete Story

**Endpoint**: `DELETE /api/v1/stories/{story_id}`

**Description**: Delete a story and all associated data. Sample stories cannot be deleted.

**Path Parameters**:

- `story_id` (string, required): UUID of the story

**Response**: `204 No Content`

**Errors**:

- `403 Forbidden`: Cannot delete sample stories
- `404 Not Found`: Story does not exist

---

### Story Generation

#### Create New Story (Start Generation)

**Endpoint**: `POST /api/v1/stories`

**Description**: Start asynchronous story generation process.

**Request Body**:

```json
{
  "prompt": "Create a horror-themed Space Hulk adventure with heavy atmosphere...",
  "template_id": "horror_infestation",  // optional
  "theme_id": "warhammer40k"  // optional, default: "warhammer40k"
}
```

**Validation**:

- `prompt`: Required, 50-1000 characters
- `template_id`: Optional, must exist if provided
- `theme_id`: Optional, must exist if provided

**Response**: `202 Accepted`

```json
{
  "data": {
    "generation_job_id": "660e8400-e29b-41d4-a716-446655440001",
    "story_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "queued",
    "estimated_time_seconds": 300
  }
}
```

**Errors**:

- `400 Bad Request`: Invalid prompt or parameters
- `429 Too Many Requests`: Rate limit exceeded (1 concurrent generation per user)

---

#### Get Generation Job Status

**Endpoint**: `GET /api/v1/generation/{generation_job_id}`

**Description**: Check status of story generation job.

**Path Parameters**:

- `generation_job_id` (string, required): UUID of the generation job

**Response**: `200 OK`

```json
{
  "data": {
    "generation_job_id": "660e8400-e29b-41d4-a716-446655440001",
    "story_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "in_progress",  // queued, in_progress, completed, failed
    "progress_percent": 45,
    "current_agent": "NarrativeArchitect",
    "started_at": "2025-11-12T10:00:00Z",
    "estimated_completion": "2025-11-12T10:05:00Z",
    "error": null  // populated if status is "failed"
  }
}
```

**Errors**:

- `404 Not Found`: Job does not exist

---

#### Submit Iteration Feedback

**Endpoint**: `POST /api/v1/stories/{story_id}/iterate`

**Description**: Submit feedback and start iteration/refinement process.

**Path Parameters**:

- `story_id` (string, required): UUID of the story

**Request Body**:

```json
{
  "feedback": "The puzzle in scene 2 needs better hints. The tone should be darker.",
  "changes": {
    "plot_rating": 5,  // 1-5
    "puzzle_rating": 3,  // 1-5
    "writing_rating": 4,  // 1-5
    "tone_adjustment": "darker",  // darker, lighter, same
    "difficulty_adjustment": "easier",  // easier, harder, same
    "focus_areas": ["puzzles", "atmosphere"]  // array of strings
  }
}
```

**Validation**:

- `feedback`: Required, minimum 20 characters
- Iteration limit: Maximum 5 iterations per story

**Response**: `202 Accepted`

```json
{
  "data": {
    "generation_job_id": "770e8400-e29b-41d4-a716-446655440002",
    "story_id": "550e8400-e29b-41d4-a716-446655440000",
    "iteration_number": 2,
    "status": "queued"
  }
}
```

**Errors**:

- `400 Bad Request`: Invalid feedback
- `409 Conflict`: Iteration limit reached (5 maximum)
- `404 Not Found`: Story does not exist

---

#### Get Story Iterations

**Endpoint**: `GET /api/v1/stories/{story_id}/iterations`

**Description**: List all iterations/versions of a story.

**Path Parameters**:

- `story_id` (string, required): UUID of the story

**Response**: `200 OK`

```json
{
  "data": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "story_id": "550e8400-e29b-41d4-a716-446655440000",
      "version": 1,
      "feedback": null,
      "status": "accepted",
      "created_at": "2025-11-12T10:00:00Z"
    },
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "story_id": "550e8400-e29b-41d4-a716-446655440000",
      "version": 2,
      "feedback": "Puzzle needs better hints...",
      "status": "accepted",
      "created_at": "2025-11-12T10:30:00Z"
    }
  ]
}
```

**Errors**:

- `404 Not Found`: Story does not exist

---

### Templates

#### List Templates

**Endpoint**: `GET /api/v1/templates`

**Description**: Get all available story templates.

**Response**: `200 OK`

```json
{
  "data": [
    {
      "id": "horror_infestation",
      "title": "Horror Infestation",
      "description": "A classic horror scenario with body horror and isolation",
      "recommended_theme": "warhammer40k",
      "example_prompt": "Create a horror-themed adventure...",
      "difficulty": "moderate",
      "estimated_duration": "30-40 minutes"
    }
  ]
}
```

---

#### Get Template Details

**Endpoint**: `GET /api/v1/templates/{template_id}`

**Description**: Get detailed information about a specific template.

**Path Parameters**:

- `template_id` (string, required): Template identifier

**Response**: `200 OK`

```json
{
  "data": {
    "id": "horror_infestation",
    "title": "Horror Infestation",
    "description": "A classic horror scenario with body horror and isolation themes",
    "recommended_theme": "warhammer40k",
    "prompt_template": "Create a {tone} Space Hulk adventure...",
    "variables": ["tone", "difficulty", "combat_focus"],
    "example_output": { /* example game structure */ }
  }
}
```

**Errors**:

- `404 Not Found`: Template does not exist

---

### Themes

#### List Themes

**Endpoint**: `GET /api/v1/themes`

**Description**: Get all available visual themes.

**Response**: `200 OK`

```json
{
  "data": [
    {
      "id": "warhammer40k",
      "name": "Warhammer 40,000",
      "description": "Grimdark sci-fi horror in the far future",
      "is_default": true,
      "colors": {
        "primary": "#8B0000",
        "secondary": "#B8860B"
      },
      "preview_image": "/themes/warhammer40k/preview.jpg"
    }
  ]
}
```

---

#### Get Theme Configuration

**Endpoint**: `GET /api/v1/themes/{theme_id}`

**Description**: Get complete theme configuration including colors, labels, and assets.

**Path Parameters**:

- `theme_id` (string, required): Theme identifier

**Response**: `200 OK`

```json
{
  "data": {
    "id": "warhammer40k",
    "name": "Warhammer 40,000",
    "description": "Grimdark sci-fi horror",
    "colors": { /* full color palette */ },
    "typography": { /* font configuration */ },
    "labels": { /* UI text labels */ },
    "terminology": { /* game terminology */ },
    "assets": { /* asset URLs */ }
  }
}
```

**Errors**:

- `404 Not Found`: Theme does not exist

---

### Gameplay

#### Start Game Session

**Endpoint**: `POST /api/v1/game/{story_id}/start`

**Description**: Initialize a new gameplay session.

**Path Parameters**:

- `story_id` (string, required): UUID of the story to play

**Response**: `200 OK`

```json
{
  "data": {
    "game_session_id": "aa0e8400-e29b-41d4-a716-446655440005",
    "story_id": "550e8400-e29b-41d4-a716-446655440000",
    "initial_scene": "You awaken in darkness aboard a derelict ship...",
    "state": {
      "current_scene": "scene_001",
      "inventory": [],
      "flags": [],
      "health": 100
    }
  }
}
```

**Errors**:

- `404 Not Found`: Story does not exist

---

#### Process Game Command

**Endpoint**: `POST /api/v1/game/{game_session_id}/command`

**Description**: Submit player command and get game response.

**Path Parameters**:

- `game_session_id` (string, required): UUID of the active game session

**Request Body**:

```json
{
  "command": "examine door"
}
```

**Response**: `200 OK`

```json
{
  "data": {
    "output": "The door is heavily reinforced with ancient Imperial markings...",
    "state": {
      "current_scene": "scene_001",
      "inventory": ["keycard"],
      "flags": ["examined_door"],
      "health": 100
    },
    "valid_command": true,
    "game_over": false
  }
}
```

**Errors**:

- `404 Not Found`: Game session does not exist or expired
- `410 Gone`: Game session ended

---

#### Save Game

**Endpoint**: `POST /api/v1/game/{game_session_id}/save`

**Description**: Save current game state.

**Path Parameters**:

- `game_session_id` (string, required): UUID of the active game session

**Request Body**:

```json
{
  "save_name": "Before boss fight"  // optional
}
```

**Response**: `200 OK`

```json
{
  "data": {
    "save_id": "bb0e8400-e29b-41d4-a716-446655440006",
    "game_session_id": "aa0e8400-e29b-41d4-a716-446655440005",
    "save_name": "Before boss fight",
    "saved_at": "2025-11-12T11:00:00Z",
    "scene": "scene_005"
  }
}
```

**Errors**:

- `404 Not Found`: Game session does not exist

---

#### Load Game

**Endpoint**: `POST /api/v1/game/load/{save_id}`

**Description**: Load a previously saved game state.

**Path Parameters**:

- `save_id` (string, required): UUID of the save

**Response**: `200 OK`

```json
{
  "data": {
    "game_session_id": "cc0e8400-e29b-41d4-a716-446655440007",
    "story_id": "550e8400-e29b-41d4-a716-446655440000",
    "output": "Game loaded. You are at...",
    "state": { /* restored game state */ }
  }
}
```

**Errors**:

- `404 Not Found`: Save does not exist

---

#### List Saves for Story

**Endpoint**: `GET /api/v1/game/{story_id}/saves`

**Description**: Get all saved games for a story.

**Path Parameters**:

- `story_id` (string, required): UUID of the story

**Response**: `200 OK`

```json
{
  "data": [
    {
      "save_id": "bb0e8400-e29b-41d4-a716-446655440006",
      "save_name": "Before boss fight",
      "saved_at": "2025-11-12T11:00:00Z",
      "scene": "scene_005",
      "playtime_seconds": 1800
    }
  ]
}
```

**Errors**:

- `404 Not Found`: Story does not exist

---

## WebSocket API

### Progress Updates

**Endpoint**: `WS /ws/generation/{generation_job_id}`

**Description**: Real-time progress updates during story generation.

**Connection**:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/generation/660e8400-...');
```

**Client → Server Messages**:

```json
{
  "type": "subscribe"
}
```

**Server → Client Messages**:

**Progress Update**:

```json
{
  "type": "progress",
  "generation_job_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "in_progress",
  "progress_percent": 45,
  "current_agent": "NarrativeArchitect",
  "message": "Designing story structure...",
  "timestamp": "2025-11-12T10:02:30Z"
}
```

**Completion**:

```json
{
  "type": "complete",
  "generation_job_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "completed",
  "story_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-11-12T10:05:00Z"
}
```

**Error**:

```json
{
  "type": "error",
  "generation_job_id": "660e8400-e29b-41d4-a716-446655440001",
  "error": {
    "code": "GENERATION_TIMEOUT",
    "message": "Story generation timed out after 15 minutes",
    "user_message": "The generation is taking longer than expected. Please try again.",
    "retry_possible": true
  },
  "timestamp": "2025-11-12T10:15:00Z"
}
```

**Heartbeat** (every 30 seconds):

```json
{
  "type": "heartbeat",
  "timestamp": "2025-11-12T10:03:00Z"
}
```

**Connection Handling**:

- Clients should implement exponential backoff reconnection (1s, 2s, 4s, 8s, max 30s)
- Maximum 10 reconnection attempts before falling back to polling
- Server closes connection after generation completes or fails

---

## HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 OK | Success | GET, POST (synchronous operations) |
| 201 Created | Resource created | POST (created new resource) |
| 202 Accepted | Async operation queued | POST (generation, iteration) |
| 204 No Content | Success, no response body | DELETE |
| 400 Bad Request | Invalid input | Validation errors |
| 401 Unauthorized | Authentication required | Future: auth endpoints |
| 403 Forbidden | Action not allowed | Delete sample story |
| 404 Not Found | Resource not found | Invalid ID |
| 409 Conflict | Business rule violation | Iteration limit, duplicate |
| 410 Gone | Resource permanently removed | Expired game session |
| 429 Too Many Requests | Rate limit exceeded | Concurrent generation limit |
| 500 Internal Server Error | Server error | Unexpected failures |
| 503 Service Unavailable | Temporary unavailability | Maintenance, overload |

---

## Rate Limiting

**Current (MVP)**: No rate limiting (single user)

**Future (Multi-user)**:

- **Generation**: 1 concurrent generation per user
- **API Requests**: 100 requests per minute per IP
- **WebSocket Connections**: 5 concurrent connections per user

**Rate Limit Headers**:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699804800
```

---

## Versioning Strategy

**Current**: v1 (stable)

**Future Versions**:

- Breaking changes increment major version (`/api/v2/`)
- Non-breaking changes (new endpoints, optional fields) remain in v1
- Old versions supported for 12 months after deprecation notice
- Deprecation header: `X-API-Deprecated: true, use /api/v2/`

---

## Common Error Codes

| Code | User Message | When |
|------|--------------|------|
| `GENERATION_TIMEOUT` | Generation is taking longer than expected | Agent execution > 15 min |
| `GENERATION_AGENT_FAILED` | AI agent encountered an error | Agent crashes or invalid output |
| `ITERATION_LIMIT_REACHED` | Maximum 5 iterations reached | User tries 6th iteration |
| `STORY_NOT_FOUND` | Story does not exist | Invalid story ID |
| `GAME_SESSION_EXPIRED` | Game session has expired | Session > 1 hour idle |
| `INVALID_COMMAND` | Command not recognized | Game engine doesn't understand |
| `WEBSOCKET_CONNECTION_LOST` | Connection interrupted | Network issues |
| `DATABASE_ERROR` | Temporary database issue | DB connection problems |
| `FILE_SYSTEM_ERROR` | Unable to access story files | Disk full, permissions |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Rate limiting triggered |

---

## Implementation Checklist

For developers implementing API endpoints:

- [ ] Endpoint follows `/api/v1/` convention
- [ ] Uses correct HTTP method (GET/POST/PUT/DELETE)
- [ ] Request validation with Pydantic models
- [ ] Standard response format (data, meta, error)
- [ ] Proper HTTP status codes
- [ ] Error responses include code and user_message
- [ ] Documented in OpenAPI/Swagger
- [ ] Unit tests for success and error cases
- [ ] Integration tests with test database
- [ ] Logging for all operations (INFO/ERROR)

---

## OpenAPI Integration

This specification should be implemented using FastAPI's automatic OpenAPI generation:

```python
from fastapi import FastAPI

app = FastAPI(
    title="Space Hulk Web Interface API",
    description="API for browser-based game creation and play",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)
```

**Documentation URLs**:

- **Swagger UI**: `/api/v1/docs`
- **ReDoc**: `/api/v1/redoc`
- **OpenAPI JSON**: `/api/v1/openapi.json`

---

**This document is the canonical reference for all API implementations. Any discrepancies between this document and code should be resolved by updating the code to match this specification.**

**Version**: 1.0
**Last Updated**: 2025-11-12
**Status**: ✅ Canonical Reference
