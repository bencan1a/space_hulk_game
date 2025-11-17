# Error Handling Specification

**Version**: 1.0
**Created**: 2025-11-12
**Status**: Implementation Ready
**Purpose**: Comprehensive error catalog and recovery strategies

---

## Design Principles

1. **User-Friendly Messages**: No technical jargon in user-facing messages
2. **Actionable Guidance**: Tell users what they can do to recover
3. **Graceful Degradation**: System remains usable even when features fail
4. **Comprehensive Logging**: All errors logged with context for debugging
5. **Retry Logic**: Transient errors handled automatically when safe
6. **Consistent Format**: Standard error response structure across all APIs

---

## Standard Error Response Format

### REST API Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Technical description for logging",
    "user_message": "User-friendly explanation and guidance",
    "details": {
      "field": "specific_field",
      "constraint": "validation_rule",
      "additional_context": "..."
    },
    "retry_possible": true,
    "retry_strategy": "automatic|manual|none",
    "timestamp": "2025-11-12T20:00:00Z",
    "request_id": "uuid"
  }
}
```

### WebSocket Error Message

```json
{
  "type": "error",
  "generation_job_id": "uuid",
  "error": {
    "code": "ERROR_CODE",
    "message": "Technical description",
    "user_message": "User-friendly message",
    "retry_possible": true,
    "progress_percent": 45,
    "timestamp": "2025-11-12T20:00:00Z"
  }
}
```

---

## Error Categories

### 1. Generation Errors

#### GENERATION_TIMEOUT

**Trigger**: Story generation exceeds 15 minutes

**Technical Message**: `Generation job {job_id} exceeded 15 minute timeout at agent {agent_name}`

**User Message**: `Story generation is taking longer than expected. This usually means the AI agents are struggling with your prompt. Please try again with a simpler prompt or different settings.`

**HTTP Status**: N/A (WebSocket)

**Recovery Strategy**:

- **Retry Possible**: Yes (manual)
- **User Action**: Modify prompt and retry
- **System Action**: Clean up partial files, mark job as failed

**Logging**:

```python
logger.error(
    "Generation timeout",
    extra={
        "job_id": job_id,
        "prompt": prompt[:100],
        "agent": current_agent,
        "elapsed_seconds": 900,
        "files_created": files_found
    }
)
```

**UI Behavior**:

- Show error modal with message
- Provide "Try Again" button (returns to prompt editor)
- Provide "Simplify Prompt" suggestions
- Log timeout for future prompt improvement

---

#### GENERATION_AGENT_FAILED

**Trigger**: CrewAI agent raises exception during execution

**Technical Message**: `Agent {agent_name} failed with exception: {exception_type}: {exception_message}`

**User Message**: `An AI agent encountered an error while creating your story. This is usually temporary. Please try again.`

**HTTP Status**: N/A (WebSocket)

**Recovery Strategy**:

- **Retry Possible**: Yes (automatic once, then manual)
- **User Action**: Retry generation
- **System Action**: Retry job once automatically; if fails again, user intervention needed

**Logging**:

```python
logger.error(
    "Agent execution failed",
    exc_info=True,
    extra={
        "job_id": job_id,
        "agent": agent_name,
        "prompt": prompt[:100],
        "inputs": inputs
    }
)
```

**UI Behavior**:

- Show "Retrying..." for automatic retry
- If second failure, show error with "Try Again" button
- Suggest simplifying prompt or using template

---

#### GENERATION_INCOMPLETE

**Trigger**: Generation completes but not all expected files were created

**Technical Message**: `Generation completed but only {actual}/{expected} files created. Missing: {missing_files}`

**User Message**: `Story generation completed but some content is missing. The story may be playable but incomplete. You can iterate to fill in missing pieces.`

**HTTP Status**: 206 Partial Content

**Recovery Strategy**:

- **Retry Possible**: Yes (via iteration)
- **User Action**: Accept partial story and iterate, or regenerate
- **System Action**: Mark story as "partial", allow play with warnings

**Logging**:

```python
logger.warning(
    "Incomplete generation",
    extra={
        "job_id": job_id,
        "files_created": files_found,
        "files_missing": missing_files,
        "story_id": story_id
    }
)
```

**UI Behavior**:

- Show warning badge on story ("Incomplete")
- Allow playing with warning modal
- Provide "Complete Story" button (triggers iteration)

---

#### GENERATION_INVALID_OUTPUT

**Trigger**: Agent produces malformed JSON or invalid content structure

**Technical Message**: `Agent {agent_name} produced invalid output: {validation_error}`

**User Message**: `An AI agent produced unexpected content. Please try generating again.`

**HTTP Status**: N/A (WebSocket)

**Recovery Strategy**:

- **Retry Possible**: Yes (automatic once)
- **User Action**: Retry
- **System Action**: Validate all JSON output, retry on validation failure

**Logging**:

```python
logger.error(
    "Invalid agent output",
    extra={
        "job_id": job_id,
        "agent": agent_name,
        "validation_errors": validation_errors,
        "output_sample": output[:500]
    }
)
```

---

### 2. API Errors

#### VALIDATION_ERROR

**Trigger**: Request body fails Pydantic validation

**Technical Message**: `Validation error in field {field}: {error_detail}`

**User Message**: `Invalid input: {field_label} {error_description}`

**HTTP Status**: 400 Bad Request

**Examples**:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Field 'prompt' must be between 50-1000 characters",
    "user_message": "Your prompt must be at least 50 characters long.",
    "details": {
      "field": "prompt",
      "current_length": 30,
      "min_length": 50
    },
    "retry_possible": true,
    "retry_strategy": "manual"
  }
}
```

**Recovery Strategy**:

- **Retry Possible**: Yes (immediate)
- **User Action**: Fix validation errors in form
- **System Action**: Return validation errors with field mapping

**Frontend Handling**:

```typescript
if (error.code === "VALIDATION_ERROR") {
  // Map error to form field
  setFieldError(error.details.field, error.user_message);
}
```

---

#### STORY_NOT_FOUND

**Trigger**: Request for non-existent story ID

**Technical Message**: `Story with ID {story_id} not found`

**User Message**: `This story could not be found. It may have been deleted.`

**HTTP Status**: 404 Not Found

**Recovery Strategy**:

- **Retry Possible**: No
- **User Action**: Return to library, select different story
- **System Action**: None

**UI Behavior**:

- Redirect to library with toast notification
- Remove story from any local caches

---

#### ITERATION_LIMIT_REACHED

**Trigger**: User attempts 6th iteration (limit is 5)

**Technical Message**: `Story {story_id} has reached iteration limit (5 iterations)`

**User Message**: `You've reached the maximum of 5 iterations for this story. You can accept this version or create a new story.`

**HTTP Status**: 409 Conflict

**Recovery Strategy**:

- **Retry Possible**: No
- **User Action**: Accept story or create new one
- **System Action**: Enforce iteration limit in database constraint

**UI Behavior**:

- Disable "Iterate" button after 5 iterations
- Show iteration count: "4/5 iterations used"
- Provide "Create New Version" option (duplicates story as new)

---

#### RATE_LIMIT_EXCEEDED

**Trigger**: User exceeds rate limit (future: 100 req/min or 1 concurrent generation)

**Technical Message**: `Rate limit exceeded: {limit_type} limit of {limit_value}`

**User Message**: `You're making requests too quickly. Please wait a moment and try again.`

**HTTP Status**: 429 Too Many Requests

**Response Headers**:

```
Retry-After: 30
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1699804830
```

**Recovery Strategy**:

- **Retry Possible**: Yes (after delay)
- **User Action**: Wait and retry
- **System Action**: Return Retry-After header

**UI Behavior**:

- Show countdown timer: "Please wait 30 seconds..."
- Auto-retry after countdown
- Disable submit buttons during cooldown

---

### 3. WebSocket Errors

#### WEBSOCKET_CONNECTION_FAILED

**Trigger**: WebSocket connection cannot be established

**Technical Message**: `WebSocket connection to {ws_url} failed: {error}`

**User Message**: `Unable to connect for real-time updates. You can still check progress by refreshing the page.`

**Recovery Strategy**:

- **Retry Possible**: Yes (automatic with exponential backoff)
- **User Action**: None (automatic fallback to polling)
- **System Action**: Fallback to polling API every 5 seconds

**Reconnection Logic**:

```typescript
const reconnectDelays = [1000, 2000, 4000, 8000, 16000, 30000]; // ms
let reconnectAttempt = 0;

function reconnect() {
  if (reconnectAttempt < reconnectDelays.length) {
    const delay = reconnectDelays[reconnectAttempt];
    setTimeout(() => {
      connectWebSocket();
      reconnectAttempt++;
    }, delay);
  } else {
    // Fallback to polling
    startPolling();
  }
}
```

---

#### WEBSOCKET_CONNECTION_LOST

**Trigger**: Active WebSocket connection drops

**Technical Message**: `WebSocket connection lost after {duration} seconds`

**User Message**: `Connection interrupted. Reconnecting...`

**Recovery Strategy**:

- **Retry Possible**: Yes (automatic)
- **User Action**: None (show reconnecting indicator)
- **System Action**: Exponential backoff reconnection

**UI Behavior**:

- Show "Reconnecting..." banner at top
- Progress bar continues with last known state
- On reconnect, request current progress from API

---

#### WEBSOCKET_MESSAGE_LOST

**Trigger**: Client disconnected, missed progress updates

**Technical Message**: `Client missed progress updates from {start_time} to {end_time}`

**User Message**: None (transparent recovery)

**Recovery Strategy**:

- **Retry Possible**: N/A (transparent)
- **User Action**: None
- **System Action**: On reconnect, fetch current progress, fill in gap

**Implementation**:

```python
@app.websocket('/ws/generation/{job_id}')
async def websocket_progress(websocket: WebSocket, job_id: str):
    await websocket.accept()

    # Send current state immediately on connection
    current_state = get_generation_state(job_id)
    await websocket.send_json(current_state)

    # Then send real-time updates
    async for update in progress_stream(job_id):
        await websocket.send_json(update)
```

---

### 4. Database Errors

#### DATABASE_CONNECTION_FAILED

**Trigger**: Cannot connect to PostgreSQL/SQLite

**Technical Message**: `Database connection failed: {error_message}`

**User Message**: `We're experiencing technical difficulties. Please try again in a few moments.`

**HTTP Status**: 503 Service Unavailable

**Recovery Strategy**:

- **Retry Possible**: Yes (automatic with backoff)
- **User Action**: Wait and retry
- **System Action**: Connection pool retry (3 attempts, 1s, 2s, 4s delays)

**Logging**:

```python
logger.critical(
    "Database connection failed",
    exc_info=True,
    extra={
        "database_url": database_url_safe,  # redacted password
        "retry_attempt": retry_attempt
    }
)
```

**Circuit Breaker Pattern**:

```python
if consecutive_failures > 5:
    circuit_breaker_open = True
    # Return 503 immediately for 60 seconds
    # Then try half-open (1 request)
```

---

#### DATABASE_CONSTRAINT_VIOLATION

**Trigger**: Unique constraint, foreign key, or check constraint violated

**Technical Message**: `Database constraint violation: {constraint_name}: {detail}`

**User Message**: Depends on constraint:

- **Unique**: `This {field} is already in use`
- **Foreign Key**: `Referenced item no longer exists`
- **Check**: `Invalid value for {field}`

**HTTP Status**: 409 Conflict

**Recovery Strategy**:

- **Retry Possible**: Yes (after fixing input)
- **User Action**: Change conflicting value
- **System Action**: Map constraint names to user-friendly messages

**Constraint Mapping**:

```python
CONSTRAINT_MESSAGES = {
    'stories_title_key': 'A story with this title already exists',
    'iterations_story_id_fkey': 'The story for this iteration no longer exists',
    'stories_iteration_count_check': 'Maximum 5 iterations per story'
}
```

---

#### DATABASE_DEADLOCK

**Trigger**: Concurrent transactions deadlock (rare in single-user)

**Technical Message**: `Database deadlock detected: {detail}`

**User Message**: `Your request conflicted with another operation. Retrying...`

**HTTP Status**: 409 Conflict (after retries exhausted)

**Recovery Strategy**:

- **Retry Possible**: Yes (automatic 3 times)
- **User Action**: None (automatic retry)
- **System Action**: Retry transaction with exponential backoff

**Implementation**:

```python
from sqlalchemy.exc import OperationalError

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def execute_transaction(db_session, operations):
    try:
        operations()
        db_session.commit()
    except OperationalError as e:
        if 'deadlock' in str(e).lower():
            db_session.rollback()
            raise  # Retry
        else:
            raise  # Don't retry other errors
```

---

### 5. File System Errors

#### FILE_SYSTEM_WRITE_ERROR

**Trigger**: Cannot write game.json to disk (permissions, disk full)

**Technical Message**: `Failed to write file {file_path}: {error}`

**User Message**: `Unable to save story content. Please ensure there is sufficient disk space.`

**HTTP Status**: 507 Insufficient Storage (if disk full), 500 otherwise

**Recovery Strategy**:

- **Retry Possible**: Yes (after admin fixes storage)
- **User Action**: Contact admin or retry later
- **System Action**: Log error with disk usage metrics

**Logging**:

```python
import shutil

disk_usage = shutil.disk_usage('/')
logger.error(
    "File write failed",
    extra={
        "file_path": file_path,
        "disk_free_gb": disk_usage.free / (1024**3),
        "disk_percent_used": (disk_usage.used / disk_usage.total) * 100
    }
)
```

---

#### FILE_SYSTEM_CORRUPTED

**Trigger**: Existing game.json is malformed and cannot be parsed

**Technical Message**: `Corrupted file {file_path}: {parse_error}`

**User Message**: `This story's data appears to be corrupted. It may not be playable.`

**HTTP Status**: 200 OK (with warning flag)

**Recovery Strategy**:

- **Retry Possible**: Via iteration (regenerate)
- **User Action**: Iterate to regenerate, or delete
- **System Action**: Mark story with corruption flag, attempt partial recovery

**Implementation**:

```python
try:
    with open(game_file) as f:
        game_data = json.load(f)
except json.JSONDecodeError as e:
    # Mark as corrupted
    story.status = 'corrupted'
    db.commit()

    # Attempt partial recovery
    with open(game_file) as f:
        content = f.read()
        # Try to extract valid JSON sections
        partial_data = attempt_partial_recovery(content)

    return {
        "data": partial_data,
        "warning": "Story data partially recovered, may be incomplete"
    }
```

---

### 6. Integration Errors

#### CREWAI_INITIALIZATION_ERROR

**Trigger**: Cannot initialize CrewAI crew instance

**Technical Message**: `Failed to initialize CrewAI crew: {error}`

**User Message**: `Unable to start story generation. Please try again or contact support.`

**HTTP Status**: 503 Service Unavailable

**Recovery Strategy**:

- **Retry Possible**: Yes (automatic)
- **User Action**: Retry or contact admin
- **System Action**: Check CrewAI dependencies, log error

---

#### GAME_ENGINE_ERROR

**Trigger**: Game engine raises exception during command processing

**Technical Message**: `Game engine error in command {command}: {error}`

**User Message**: `The game encountered an error processing your command. Try a different command or restart the game.`

**HTTP Status**: 500 Internal Server Error

**Recovery Strategy**:

- **Retry Possible**: Yes (with different command)
- **User Action**: Try different command or reload game
- **System Action**: Log command history, rollback game state

**Implementation**:

```python
try:
    result = game_engine.process_command(command)
except GameEngineException as e:
    # Rollback to last valid state
    game_engine.restore_state(last_valid_state)

    return {
        "error": {
            "code": "GAME_ENGINE_ERROR",
            "message": str(e),
            "user_message": "Command caused an error. Game state restored to before command.",
            "retry_possible": True
        }
    }
```

---

## Error Logging Strategy

### Log Levels

| Level        | When to Use                     | Example                                 |
| ------------ | ------------------------------- | --------------------------------------- |
| **DEBUG**    | Detailed flow for debugging     | `Checking for file plot_outline.json`   |
| **INFO**     | Normal operations               | `Story 123 created successfully`        |
| **WARNING**  | Unexpected but handled          | `Incomplete generation, missing 1 file` |
| **ERROR**    | Operation failed, user impacted | `Agent timeout after 15 minutes`        |
| **CRITICAL** | System-level failure            | `Database connection lost`              |

### Structured Logging Format

```python
import logging
import json

logger = logging.getLogger(__name__)

# Use structured logging (JSON format)
logger.error(
    "Generation failed",
    extra={
        "error_code": "GENERATION_TIMEOUT",
        "job_id": job_id,
        "story_id": story_id,
        "user_prompt": prompt[:100],  # Truncate
        "agent": "PuzzleSmith",
        "elapsed_seconds": 900,
        "files_created": 3,
        "files_expected": 5,
        "request_id": request_id,
        "user_id": user_id  # Future
    }
)
```

**Output** (JSON format for log aggregation):

```json
{
  "timestamp": "2025-11-12T20:00:00Z",
  "level": "ERROR",
  "message": "Generation failed",
  "error_code": "GENERATION_TIMEOUT",
  "job_id": "uuid",
  "story_id": "uuid",
  "user_prompt": "Create a horror-themed...",
  "agent": "PuzzleSmith",
  "elapsed_seconds": 900,
  "files_created": 3,
  "files_expected": 5,
  "request_id": "uuid"
}
```

---

## Frontend Error Handling

### React Error Boundary

```typescript
class ErrorBoundary extends React.Component<Props, State> {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log to error tracking service
    logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback
          error={this.state.error}
          resetError={() => this.setState({ hasError: false })}
        />
      );
    }

    return this.props.children;
  }
}

// Wrap major features
<ErrorBoundary>
  <StoryCreatorPage />
</ErrorBoundary>
```

### API Error Handler

```typescript
async function apiCall(endpoint: string, options: RequestInit) {
  try {
    const response = await fetch(endpoint, options);

    if (!response.ok) {
      const errorData = await response.json();
      throw new APIError(errorData.error);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      // Show user-friendly message
      showToast(error.user_message, "error");

      // Log technical details
      console.error(`API Error [${error.code}]:`, error.message);

      // Retry if appropriate
      if (error.retry_possible && error.retry_strategy === "automatic") {
        return retryWithBackoff(apiCall, endpoint, options);
      }
    } else {
      // Network error or other unexpected error
      showToast("Network error. Please check your connection.", "error");
      console.error("Unexpected error:", error);
    }

    throw error;
  }
}
```

---

## Error Testing Strategy

### Unit Tests

```python
def test_generation_timeout():
    # Mock crew execution that takes > 15 minutes
    with patch('time.time', side_effect=[0, 901]):
        with pytest.raises(TimeoutError):
            monitor.execute_with_monitoring(crew, inputs)

def test_validation_error_response():
    response = client.post('/api/v1/stories', json={'prompt': 'short'})
    assert response.status_code == 400
    error = response.json()['error']
    assert error['code'] == 'VALIDATION_ERROR'
    assert 'prompt' in error['details']['field']

def test_websocket_reconnection():
    ws = connect_websocket()
    ws.close()  # Simulate disconnect
    time.sleep(2)
    # Should auto-reconnect
    assert ws_manager.is_connected(job_id)
```

### Integration Tests

```python
@pytest.mark.integration
def test_full_error_recovery_flow():
    # Start generation
    job_id = create_generation_job(prompt)

    # Simulate agent failure
    with patch('crew.kickoff', side_effect=ValueError("Agent error")):
        # Should auto-retry once
        time.sleep(10)

        # Check error logged
        assert 'GENERATION_AGENT_FAILED' in logs

        # Check user notified via WebSocket
        messages = get_websocket_messages(job_id)
        assert any(m['type'] == 'error' for m in messages)
```

---

## Success Criteria

- [ ] All error codes defined with user messages
- [ ] Standard error response format implemented
- [ ] Logging for all error types with structured format
- [ ] WebSocket reconnection logic with exponential backoff
- [ ] Database retry logic for transient failures
- [ ] Frontend error boundaries catch React errors
- [ ] API error handler shows user-friendly messages
- [ ] Error testing coverage > 80%
- [ ] User documentation includes common errors and solutions

---

**This comprehensive error handling specification ensures graceful degradation, clear user communication, and robust recovery mechanisms across the entire web interface.**

**Status**: ✅ Ready for Implementation
**Next Steps**: Implement error handlers in Phase 1-2, test in Phase 6
