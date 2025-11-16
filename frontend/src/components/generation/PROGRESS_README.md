# Generation Progress UI - Task 3.8

This directory contains the implementation for Task 3.8: Generation Progress UI, which provides real-time feedback to users while their game content is being generated via WebSocket.

## Components

### GenerationProgress

A React component that displays real-time generation progress by connecting to the WebSocket endpoint.

**Location:** `GenerationProgress.tsx`

**Features:**
- Real-time progress bar (0-100%)
- Current step/status display
- Agent status list with visual indicators (○ → ◐ → ✓)
- Final status display (Completed/Failed)
- WebSocket connection status indicator
- Automatic reconnection on disconnect
- Responsive design
- Full accessibility support (ARIA labels)

**Props:**
```typescript
interface GenerationProgressProps {
  sessionId: string           // Required: Session ID to track
  wsBaseUrl?: string         // Optional: WebSocket base URL (default: from env)
  onComplete?: () => void    // Optional: Callback when generation completes
  onError?: (error: string) => void  // Optional: Callback on error
}
```

**Example Usage:**
```tsx
import { GenerationProgress } from '@/components/generation/GenerationProgress'
import { useNavigate } from 'react-router-dom'

function MyPage() {
  const navigate = useNavigate()
  const sessionId = 'session-123'
  
  return (
    <GenerationProgress
      sessionId={sessionId}
      onComplete={() => navigate('/story/123')}
      onError={(err) => console.error(err)}
    />
  )
}
```

### AgentStatusList

An internal component that displays the status of each agent/task in the generation process.

**Features:**
- Visual status indicators:
  - `○` - Pending (gray)
  - `◐` - In Progress (blue, animated)
  - `✓` - Completed (green)
  - `✗` - Error (red)
- Agent name display
- Hover effects

## Hooks

### useWebSocket

A custom React hook for managing WebSocket connections with automatic reconnection.

**Location:** `../../hooks/useWebSocket.ts`

**Features:**
- Auto-connect on mount (configurable)
- Automatic reconnection with exponential backoff
- Heartbeat message handling
- Message parsing and validation
- Connection state tracking
- Manual connect/disconnect control
- TypeScript type safety

**Options:**
```typescript
interface UseWebSocketOptions {
  autoConnect?: boolean              // Default: true
  autoReconnect?: boolean           // Default: true
  maxReconnectAttempts?: number     // Default: 5
  reconnectDelay?: number           // Default: 1000ms
  maxReconnectDelay?: number        // Default: 30000ms
  onMessage?: (message: WebSocketMessage) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
}
```

**Return Value:**
```typescript
interface UseWebSocketReturn {
  lastMessage: WebSocketMessage | null
  readyState: number
  isConnected: boolean
  isConnecting: boolean
  connect: () => void
  disconnect: () => void
  send: (data: string | object) => void
}
```

**Example Usage:**
```tsx
import { useWebSocket } from '@/hooks/useWebSocket'

function MyComponent() {
  const { lastMessage, isConnected } = useWebSocket(
    'ws://localhost:8000/ws/progress/session-123',
    {
      onMessage: (msg) => console.log('Received:', msg),
      onOpen: () => console.log('Connected'),
    }
  )
  
  return (
    <div>
      Status: {isConnected ? 'Connected' : 'Disconnected'}
      {lastMessage && <pre>{JSON.stringify(lastMessage)}</pre>}
    </div>
  )
}
```

## WebSocket Message Format

Messages from the backend follow this TypeScript interface:

```typescript
interface WebSocketMessage {
  type: 'connection' | 'heartbeat' | 'progress'
  status?: 'connected' | 'started' | 'task_started' | 'task_completed' | 
           'completed' | 'error' | 'timeout'
  session_id: string
  current_step?: string
  progress_percent?: number
  task_name?: string
  task_index?: number
  total_tasks?: number
  error?: string
}
```

### Message Types

**Connection Message:**
```json
{
  "type": "connection",
  "status": "connected",
  "session_id": "session-123"
}
```

**Heartbeat Message:**
```json
{
  "type": "heartbeat",
  "session_id": "session-123"
}
```

**Progress Message:**
```json
{
  "type": "progress",
  "status": "task_started",
  "session_id": "session-123",
  "task_name": "Story Design",
  "task_index": 0,
  "total_tasks": 3,
  "current_step": "Running: Story Design",
  "progress_percent": 30
}
```

## Testing

### Component Tests

**Location:** `../../tests/components/generation/GenerationProgress.test.tsx`

**Coverage:**
- Initial state rendering
- Connection status display
- WebSocket URL construction (http/https → ws/wss)
- Progress updates
- Agent status updates
- Success/error/timeout states
- Callback invocation
- Accessibility (ARIA labels)

**Run Tests:**
```bash
npm test GenerationProgress
```

### Hook Tests

**Location:** `../../tests/hooks/useWebSocket.test.ts`

**Coverage:**
- Initialization states
- Connection/disconnection
- Callback options
- Reconnection behavior
- Error handling

**Run Tests:**
```bash
npm test useWebSocket
```

## Styling

**Location:** `GenerationProgress.module.css`

**Features:**
- Modern, clean design
- Responsive layout (mobile-friendly)
- Smooth animations and transitions
- Status-based color coding:
  - Blue: In progress
  - Green: Success
  - Red: Error
- Accessible contrast ratios

## Integration with Backend

The component connects to the WebSocket endpoint defined in Task 3.4:

**Endpoint:** `ws://localhost:8000/ws/progress/{session_id}`

The backend broadcasts progress updates from the generation tasks using the `ConnectionManager` class defined in `backend/app/api/websocket.py`.

## Environment Configuration

The WebSocket URL is constructed from the API base URL:

```env
VITE_API_URL=http://localhost:8000
```

The component automatically converts:
- `http://` → `ws://`
- `https://` → `wss://`

## Examples

See `GenerationProgressExamples.tsx` for complete usage examples:

1. Basic usage
2. With callbacks
3. React Router integration
4. Direct hook usage
5. State management integration

## Accessibility

The component follows WCAG 2.1 Level AA guidelines:

- Proper ARIA labels on interactive elements
- Progress bar with `role="progressbar"` and aria-value* attributes
- Semantic HTML structure
- Keyboard navigation support
- Sufficient color contrast
- Screen reader friendly status updates

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Opera 74+

(Requires WebSocket support)

## Troubleshooting

### Connection Issues

If the WebSocket fails to connect:

1. Check that the backend is running
2. Verify CORS settings allow WebSocket connections
3. Check the WebSocket URL in browser DevTools
4. Ensure no proxy/firewall blocking WebSocket connections

### Reconnection Failures

If automatic reconnection fails:

- Check backend logs for connection errors
- Verify session_id is valid
- Increase `maxReconnectAttempts` if needed
- Check network connectivity

### No Progress Updates

If connected but no progress updates appear:

- Verify the backend is broadcasting messages
- Check browser console for parsing errors
- Verify message format matches expected schema

## Future Enhancements

Possible improvements for future iterations:

- [ ] Pause/resume generation
- [ ] Estimated time remaining
- [ ] Detailed agent logs/output
- [ ] Cancel generation
- [ ] Progress history/timeline view
- [ ] Notification when generation completes (browser notifications)
- [ ] Sound effects for completion
- [ ] Save progress to localStorage for recovery
