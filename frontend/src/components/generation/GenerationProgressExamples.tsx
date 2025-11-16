/**
 * Example usage of GenerationProgress component
 *
 * This file demonstrates how to integrate the GenerationProgress component
 * in your application to track real-time story generation progress.
 */

import React from 'react'
import { GenerationProgress } from './GenerationProgress'

/**
 * Example 1: Basic usage with session ID
 */
export const BasicExample: React.FC = () => {
  // In a real app, you would get this from your state management or routing
  const sessionId = 'my-session-123'

  return (
    <div>
      <h1>Generating Your Story...</h1>
      <GenerationProgress sessionId={sessionId} />
    </div>
  )
}

/**
 * Example 2: With completion and error callbacks
 */
export const WithCallbacksExample: React.FC = () => {
  const sessionId = 'my-session-456'

  const handleComplete = () => {
    console.log('Generation completed!')
    // Navigate to the story page, show success message, etc.
  }

  const handleError = (error: string) => {
    console.error('Generation failed:', error)
    // Show error notification, allow retry, etc.
  }

  return (
    <GenerationProgress
      sessionId={sessionId}
      onComplete={handleComplete}
      onError={handleError}
    />
  )
}

/**
 * Example 3: Full integration with React Router
 */
export const RouterIntegrationExample: React.FC = () => {
  const sessionId = 'my-session-789'

  const handleComplete = () => {
    // In a real app, you might navigate to the story viewer
    // navigate(`/story/${sessionId}`)
    console.log('Redirecting to story...')
  }

  const handleError = (error: string) => {
    // In a real app, you might navigate back to the create page
    // navigate('/create', { state: { error } })
    console.error('Error:', error)
  }

  return (
    <div style={{ maxWidth: '800px', margin: '2rem auto' }}>
      <GenerationProgress
        sessionId={sessionId}
        onComplete={handleComplete}
        onError={handleError}
      />
    </div>
  )
}

/**
 * Example 4: Using the useWebSocket hook directly
 *
 * If you need more control over the WebSocket connection,
 * you can use the useWebSocket hook directly.
 */
import { useWebSocket, WebSocketMessage } from '../../hooks/useWebSocket'

export const CustomWebSocketExample: React.FC = () => {
  const sessionId = 'my-session-custom'

  const { lastMessage, isConnected, isConnecting } = useWebSocket(
    `ws://localhost:8000/ws/progress/${sessionId}`,
    {
      onMessage: (message: WebSocketMessage) => {
        console.log('Received message:', message)
        // Custom handling of messages
        if (message.type === 'progress' && message.status === 'completed') {
          console.log('Generation complete!')
        }
      },
      onOpen: () => console.log('WebSocket connected'),
      onClose: () => console.log('WebSocket disconnected'),
      onError: (error: Event) => console.error('WebSocket error:', error),
      autoReconnect: true,
      maxReconnectAttempts: 5,
    }
  )

  return (
    <div>
      <h2>Custom WebSocket Integration</h2>
      <p>Connection Status: {isConnecting ? 'Connecting...' : isConnected ? 'Connected' : 'Disconnected'}</p>
      {lastMessage && (
        <pre style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
          {JSON.stringify(lastMessage, null, 2)}
        </pre>
      )}
    </div>
  )
}

/**
 * Example 5: Integration with state management (Redux/Context)
 */
export const StateManagementExample: React.FC = () => {
  const [sessionId, setSessionId] = React.useState<string | null>(null)
  const [isGenerating, setIsGenerating] = React.useState(false)

  const startGeneration = async () => {
    // In a real app, you would call your API to start generation
    // const response = await api.startGeneration({ prompt: '...' })
    // setSessionId(response.session_id)

    // For demo purposes:
    const demoSessionId = `session-${Date.now()}`
    setSessionId(demoSessionId)
    setIsGenerating(true)
  }

  const handleComplete = () => {
    setIsGenerating(false)
    console.log('Generation completed for session:', sessionId)
  }

  const handleError = (error: string) => {
    setIsGenerating(false)
    console.error('Generation failed:', error)
  }

  if (!isGenerating || !sessionId) {
    return (
      <div>
        <button onClick={startGeneration}>Start Generation</button>
      </div>
    )
  }

  return (
    <div>
      <GenerationProgress
        sessionId={sessionId}
        onComplete={handleComplete}
        onError={handleError}
      />
    </div>
  )
}

/**
 * Usage in your app:
 *
 * import { GenerationProgress } from '@/components/generation/GenerationProgress'
 *
 * function CreatePage() {
 *   const [sessionId, setSessionId] = useState<string | null>(null)
 *
 *   const handleStartGeneration = async (prompt: string) => {
 *     const response = await fetch('/api/generate', {
 *       method: 'POST',
 *       body: JSON.stringify({ prompt }),
 *     })
 *     const data = await response.json()
 *     setSessionId(data.session_id)
 *   }
 *
 *   if (sessionId) {
 *     return (
 *       <GenerationProgress
 *         sessionId={sessionId}
 *         onComplete={() => navigate(`/story/${sessionId}`)}
 *         onError={(err) => console.error(err)}
 *       />
 *     )
 *   }
 *
 *   return <CreateForm onSubmit={handleStartGeneration} />
 * }
 */
