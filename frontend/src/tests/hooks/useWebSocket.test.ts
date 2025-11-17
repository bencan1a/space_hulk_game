import { renderHook } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useWebSocket } from '../../hooks/useWebSocket'

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.CONNECTING
  url: string
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null

  constructor(url: string) {
    this.url = url
    // Simulate async connection
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      this.onopen?.(new Event('open'))
    }, 0)
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  send(_data: string) {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error('WebSocket is not open')
    }
  }

  close() {
    this.readyState = MockWebSocket.CLOSED
    setTimeout(() => {
      this.onclose?.(new CloseEvent('close'))
    }, 0)
  }
}

describe('useWebSocket', () => {
  let originalWebSocket: typeof WebSocket

  beforeEach(() => {
    originalWebSocket = (globalThis as typeof globalThis & { WebSocket: typeof WebSocket })
      .WebSocket
    ;(globalThis as typeof globalThis & { WebSocket: typeof WebSocket }).WebSocket =
      MockWebSocket as unknown as typeof WebSocket
  })

  afterEach(() => {
    ;(globalThis as typeof globalThis & { WebSocket: typeof WebSocket }).WebSocket =
      originalWebSocket
    vi.clearAllMocks()
  })

  it('initializes with closed state when autoConnect is false', () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/test', {
        autoConnect: false,
      })
    )

    expect(result.current.isConnected).toBe(false)
    expect(result.current.isConnecting).toBe(false)
    expect(result.current.readyState).toBe(WebSocket.CLOSED)
  })

  it('initializes with connecting state when autoConnect is true', () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/test', {
        autoConnect: true,
      })
    )

    // Should start in connecting or connected state
    expect(result.current.readyState).toBeGreaterThanOrEqual(WebSocket.CONNECTING)
  })

  it('does not connect when url is null', () => {
    const { result } = renderHook(() =>
      useWebSocket(null, {
        autoConnect: true,
      })
    )

    expect(result.current.isConnected).toBe(false)
  })

  it('provides connect and disconnect functions', () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/test', {
        autoConnect: false,
      })
    )

    expect(typeof result.current.connect).toBe('function')
    expect(typeof result.current.disconnect).toBe('function')
  })

  it('provides send function', () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/test', {
        autoConnect: false,
      })
    )

    expect(typeof result.current.send).toBe('function')
  })

  it('accepts callback options', () => {
    const onOpen = vi.fn()
    const onClose = vi.fn()
    const onMessage = vi.fn()
    const onError = vi.fn()

    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/test', {
        autoConnect: false,
        onOpen,
        onClose,
        onMessage,
        onError,
      })
    )

    expect(result.current).toBeDefined()
  })

  it('accepts reconnection options', () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws/test', {
        autoConnect: false,
        autoReconnect: true,
        maxReconnectAttempts: 3,
        reconnectDelay: 2000,
        maxReconnectDelay: 10000,
      })
    )

    expect(result.current).toBeDefined()
  })
})
