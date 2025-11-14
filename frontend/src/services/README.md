# API Client Documentation

## Overview

A fully-typed TypeScript API client for the Space Hulk Game frontend, built with Axios. Features comprehensive error handling, automatic retry logic, and request/response interceptors.

## Installation

Dependencies are already installed. The API client is ready to use.

```bash
npm install  # Installs axios, vitest, and other dependencies
```

## Quick Start

```typescript
import { apiClient } from './services/api'
import { getErrorMessage } from './utils/errorHandler'

// Fetch stories
try {
  const stories = await apiClient.getStories({ page: 1, page_size: 10 })
  console.log(stories.items)
} catch (error) {
  console.error(getErrorMessage(error))
}
```

## API Endpoints

### Story Endpoints

#### Get Stories (Paginated)
```typescript
const stories = await apiClient.getStories({
  page: 1,
  page_size: 20,
  search: 'space marine',
  theme_id: 'warhammer40k',
  tags: ['action', 'horror']
})
```

#### Get Single Story
```typescript
const story = await apiClient.getStory(1)
```

#### Create Story
```typescript
const session = await apiClient.createStory({
  prompt: 'A story about exploring a derelict ship',
  theme_id: 'warhammer40k',
  template_id: 'basic'  // optional
})
```

#### Delete Story
```typescript
await apiClient.deleteStory(1)
```

### Generation Endpoints

#### Check Generation Status
```typescript
const status = await apiClient.getGenerationStatus('session-id')
console.log(`Progress: ${status.progress_percent}%`)
```

### Game Endpoints

#### Start Game
```typescript
const gameSession = await apiClient.startGame(1)
console.log(`Session ID: ${gameSession.session_id}`)
```

#### Send Command
```typescript
const response = await apiClient.sendCommand('session-id', {
  command: 'look around'
})
console.log(response.output)
```

#### Save Game
```typescript
const saveData = await apiClient.saveGame('session-id', 'My Save')
console.log(`Save ID: ${saveData.save_id}`)
```

### Theme Endpoints

#### Get All Themes
```typescript
const themes = await apiClient.getThemes()
```

#### Get Single Theme
```typescript
const theme = await apiClient.getTheme('warhammer40k')
```

## Error Handling

The API client provides rich error information through the `AppError` class:

```typescript
import { AppError, getErrorMessage } from './utils/errorHandler'

try {
  const story = await apiClient.getStory(999)
} catch (error) {
  if (error instanceof AppError) {
    console.log(error.code)          // Error code (e.g., 'NOT_FOUND')
    console.log(error.userMessage)   // User-friendly message
    console.log(error.retryPossible) // Whether retry is possible
    console.log(error.status)        // HTTP status code
  }
  
  // Or use the helper function
  console.error(getErrorMessage(error))
}
```

### Error Types

- **BAD_REQUEST (400)**: Invalid input
- **NOT_FOUND (404)**: Resource not found
- **SERVER_ERROR (500)**: Server error (retryable)
- **SERVICE_UNAVAILABLE (503)**: Service unavailable (retryable)
- **NETWORK_ERROR**: No response from server (retryable)
- **REQUEST_ERROR**: Error in request setup (retryable)

## Retry Logic

The client automatically retries failed requests for transient errors:

- Network errors (no response)
- 503 Service Unavailable
- Uses exponential backoff (1s, 2s, 4s)
- Maximum 3 retry attempts

## Configuration

### Base URL
Set via environment variable:
```bash
VITE_API_URL=http://localhost:8000
```

Default: `http://localhost:8000`

### Timeout
Default: 30 seconds

Can be modified in `src/services/api.ts`:
```typescript
this.client = axios.create({
  timeout: 30000, // 30 seconds
})
```

## Interceptors

### Request Interceptor
- Adds `X-Request-Time` header to all requests
- Ready for authentication token support

### Response Interceptor
- Logs responses in development mode
- Handles errors with detailed logging
- Implements automatic retry logic

## Testing

Run the test suite:

```bash
npm test
```

Test files:
- `src/tests/api.test.ts` - API client tests
- `src/tests/errorHandler.test.ts` - Error handling tests

## Type Definitions

All types are defined in `src/services/types.ts`:

```typescript
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
} from './services/types'
```

## React Integration Example

```tsx
import { useState, useEffect } from 'react'
import { apiClient } from './services/api'
import { getErrorMessage } from './utils/errorHandler'
import type { Story } from './services/types'

function StoriesPage() {
  const [stories, setStories] = useState<Story[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadStories() {
      try {
        setLoading(true)
        const data = await apiClient.getStories({ page: 1, page_size: 10 })
        setStories(data.items)
        setError(null)
      } catch (err) {
        setError(getErrorMessage(err))
      } finally {
        setLoading(false)
      }
    }

    loadStories()
  }, [])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  
  return (
    <div>
      {stories.map((story) => (
        <div key={story.id}>{story.title}</div>
      ))}
    </div>
  )
}
```

## Development

### TypeScript Check
```bash
npx tsc --noEmit
```

### Linting
```bash
npm run lint
```

### Build
```bash
npm run build
```

## Files Structure

```
src/
├── services/
│   ├── api.ts              # Main API client
│   ├── types.ts            # Type definitions
│   └── api-examples.tsx    # Usage examples
├── utils/
│   ├── errorHandler.ts     # Error handling
│   └── retryLogic.ts       # Retry logic
└── tests/
    ├── api.test.ts         # API tests
    └── errorHandler.test.ts # Error handler tests
```

## License

Part of the Space Hulk Game project.
