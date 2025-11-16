import { useEffect, useRef, useState, useCallback } from 'react'

/**
 * WebSocket message types based on backend implementation
 */
export interface WebSocketMessage {
  type: 'connection' | 'heartbeat' | 'progress'
  status?:
    | 'connected'
    | 'started'
    | 'task_started'
    | 'task_completed'
    | 'completed'
    | 'error'
    | 'timeout'
  session_id: string
  current_step?: string
  progress_percent?: number
  task_name?: string
  task_index?: number
  total_tasks?: number
  error?: string
}

export interface UseWebSocketOptions {
  /**
   * Whether to automatically connect on mount
   * @default true
   */
  autoConnect?: boolean

  /**
   * Whether to automatically reconnect on disconnect
   * @default true
   */
  autoReconnect?: boolean

  /**
   * Maximum number of reconnection attempts
   * @default 5
   */
  maxReconnectAttempts?: number

  /**
   * Initial reconnection delay in milliseconds
   * @default 1000
   */
  reconnectDelay?: number

  /**
   * Maximum reconnection delay in milliseconds (for exponential backoff)
   * @default 30000
   */
  maxReconnectDelay?: number

  /**
   * Callback for when a message is received
   */
  onMessage?: (message: WebSocketMessage) => void

  /**
   * Callback for when connection is established
   */
  onOpen?: () => void

  /**
   * Callback for when connection is closed
   */
  onClose?: () => void

  /**
   * Callback for when an error occurs
   */
  onError?: (error: Event) => void
}

export interface UseWebSocketReturn {
  /**
   * The latest message received
   */
  lastMessage: WebSocketMessage | null

  /**
   * Current connection state
   */
  readyState: number

  /**
   * Whether the WebSocket is currently connected
   */
  isConnected: boolean

  /**
   * Whether the WebSocket is currently connecting
   */
  isConnecting: boolean

  /**
   * Manually connect to the WebSocket
   */
  connect: () => void

  /**
   * Manually disconnect from the WebSocket
   */
  disconnect: () => void

  /**
   * Send a message through the WebSocket
   */
  send: (data: string | object) => void
}

/**
 * Custom hook for managing WebSocket connections with automatic reconnection
 *
 * @param url - WebSocket URL to connect to (e.g., ws://localhost:8000/ws/progress/session-123)
 * @param options - Configuration options
 * @returns WebSocket state and control functions
 *
 * @example
 * ```tsx
 * const { lastMessage, isConnected, connect, disconnect } = useWebSocket(
 *   `ws://localhost:8000/ws/progress/${sessionId}`,
 *   {
 *     onMessage: (msg) => console.log('Received:', msg),
 *     onOpen: () => console.log('Connected'),
 *   }
 * )
 * ```
 */
export const useWebSocket = (
  url: string | null,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn => {
  const {
    autoConnect = true,
    autoReconnect = true,
    maxReconnectAttempts = 5,
    reconnectDelay = 1000,
    maxReconnectDelay = 30000,
    onMessage,
    onOpen,
    onClose,
    onError,
  } = options

  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [readyState, setReadyState] = useState<number>(WebSocket.CLOSED)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const shouldReconnectRef = useRef(autoReconnect)
  const manualDisconnectRef = useRef(false)
  const connectRef = useRef<(() => void) | null>(null)

  const isConnected = readyState === WebSocket.OPEN
  const isConnecting = readyState === WebSocket.CONNECTING

  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current !== null) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }, [])

  const scheduleReconnect = useCallback(() => {
    if (!shouldReconnectRef.current || manualDisconnectRef.current) {
      return
    }

    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      console.warn(`Max reconnection attempts (${maxReconnectAttempts}) reached`)
      return
    }

    clearReconnectTimeout()

    // Exponential backoff: delay * 2^attempts, capped at maxReconnectDelay
    const delay = Math.min(
      reconnectDelay * Math.pow(2, reconnectAttemptsRef.current),
      maxReconnectDelay
    )

    console.log(
      `Scheduling reconnect attempt ${reconnectAttemptsRef.current + 1} in ${delay}ms`
    )

    reconnectTimeoutRef.current = window.setTimeout(() => {
      reconnectAttemptsRef.current++
      // Note: connect() will be defined after this callback but will be available when this is called
      connectRef.current?.()
    }, delay)
  }, [maxReconnectAttempts, reconnectDelay, maxReconnectDelay, clearReconnectTimeout])

  const connect = useCallback(() => {
    if (!url) {
      return
    }

    clearReconnectTimeout()

    // Close existing connection if any
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    manualDisconnectRef.current = false

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws
      setReadyState(WebSocket.CONNECTING)

      ws.onopen = () => {
        console.log('WebSocket connected:', url)
        setReadyState(WebSocket.OPEN)
        reconnectAttemptsRef.current = 0 // Reset reconnect attempts on successful connection
        clearReconnectTimeout()
        onOpen?.()
      }

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        setReadyState(WebSocket.CLOSED)
        wsRef.current = null
        onClose?.()

        // Attempt to reconnect if not a manual disconnect
        if (!manualDisconnectRef.current && shouldReconnectRef.current) {
          scheduleReconnect()
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        onError?.(error)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage
          setLastMessage(message)
          onMessage?.(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      setReadyState(WebSocket.CLOSED)

      // Attempt to reconnect on creation failure
      if (!manualDisconnectRef.current && shouldReconnectRef.current) {
        scheduleReconnect()
      }
    }
  }, [url, onOpen, onClose, onError, onMessage, scheduleReconnect, clearReconnectTimeout])

  // Store connect in ref so scheduleReconnect can access it
  connectRef.current = connect

  const disconnect = useCallback(() => {
    manualDisconnectRef.current = true
    shouldReconnectRef.current = false
    clearReconnectTimeout()

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setReadyState(WebSocket.CLOSED)
  }, [clearReconnectTimeout])

  const send = useCallback(
    (data: string | object) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        console.warn('Cannot send message: WebSocket is not connected')
        return
      }

      const message = typeof data === 'string' ? data : JSON.stringify(data)
      wsRef.current.send(message)
    },
    []
  )

  // Auto-connect on mount if enabled and URL is provided
  useEffect(() => {
    if (autoConnect && url) {
      connect()
    }

    return () => {
      disconnect()
    }
    // Only reconnect when URL changes - connect/disconnect are stable via useCallback
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url])

  // Update shouldReconnect ref when option changes
  useEffect(() => {
    shouldReconnectRef.current = autoReconnect
  }, [autoReconnect])

  return {
    lastMessage,
    readyState,
    isConnected,
    isConnecting,
    connect,
    disconnect,
    send,
  }
}
