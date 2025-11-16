import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { GenerationProgress } from '../../../components/generation/GenerationProgress'
import * as useWebSocketModule from '../../../hooks/useWebSocket'

// Mock the useWebSocket hook
vi.mock('../../../hooks/useWebSocket')

describe('GenerationProgress', () => {
  const mockUseWebSocket = vi.mocked(useWebSocketModule.useWebSocket)
  const defaultSessionId = 'test-session-123'

  beforeEach(() => {
    vi.clearAllMocks()

    // Default mock implementation
    mockUseWebSocket.mockReturnValue({
      lastMessage: null,
      readyState: WebSocket.OPEN,
      isConnected: true,
      isConnecting: false,
      connect: vi.fn(),
      disconnect: vi.fn(),
      send: vi.fn(),
    })
  })

  it('renders initial state correctly', () => {
    render(<GenerationProgress sessionId={defaultSessionId} />)

    expect(screen.getByText('Generating Your Story')).toBeInTheDocument()
    expect(screen.getByText('Initializing...')).toBeInTheDocument()
    expect(screen.getByText('0%')).toBeInTheDocument()
    expect(screen.getByText('● Connected')).toBeInTheDocument()
  })

  it('shows connecting status when WebSocket is connecting', () => {
    mockUseWebSocket.mockReturnValue({
      lastMessage: null,
      readyState: WebSocket.CONNECTING,
      isConnected: false,
      isConnecting: true,
      connect: vi.fn(),
      disconnect: vi.fn(),
      send: vi.fn(),
    })

    render(<GenerationProgress sessionId={defaultSessionId} />)

    expect(screen.getByText('Connecting...')).toBeInTheDocument()
  })

  it('shows disconnected status when WebSocket is not connected', () => {
    mockUseWebSocket.mockReturnValue({
      lastMessage: null,
      readyState: WebSocket.CLOSED,
      isConnected: false,
      isConnecting: false,
      connect: vi.fn(),
      disconnect: vi.fn(),
      send: vi.fn(),
    })

    render(<GenerationProgress sessionId={defaultSessionId} />)

    expect(screen.getByText('● Disconnected')).toBeInTheDocument()
  })

  it('constructs correct WebSocket URL with http base URL', () => {
    render(<GenerationProgress sessionId={defaultSessionId} wsBaseUrl="http://localhost:8000" />)

    expect(mockUseWebSocket).toHaveBeenCalledWith(
      `ws://localhost:8000/ws/progress/${defaultSessionId}`,
      expect.any(Object)
    )
  })

  it('constructs correct WebSocket URL with https base URL', () => {
    render(<GenerationProgress sessionId={defaultSessionId} wsBaseUrl="https://api.example.com" />)

    expect(mockUseWebSocket).toHaveBeenCalledWith(
      `wss://api.example.com/ws/progress/${defaultSessionId}`,
      expect.any(Object)
    )
  })

  it('handles progress updates correctly', () => {
    const { rerender } = render(<GenerationProgress sessionId={defaultSessionId} />)

    // Get the onMessage callback that was passed to useWebSocket
    const onMessageCallback = mockUseWebSocket.mock.calls[0][1]?.onMessage

    // Simulate progress message
    onMessageCallback?.({
      type: 'progress',
      status: 'started',
      session_id: defaultSessionId,
      current_step: 'Starting AI crew',
      progress_percent: 10,
    })

    rerender(<GenerationProgress sessionId={defaultSessionId} />)

    expect(screen.getByText('Starting AI crew')).toBeInTheDocument()
    expect(screen.getByText('10%')).toBeInTheDocument()
  })

  it('displays agent status when task_started message is received', () => {
    const { rerender } = render(<GenerationProgress sessionId={defaultSessionId} />)

    const onMessageCallback = mockUseWebSocket.mock.calls[0][1]?.onMessage

    // Simulate task started
    onMessageCallback?.({
      type: 'progress',
      status: 'task_started',
      session_id: defaultSessionId,
      task_name: 'Story Design',
      task_index: 0,
      total_tasks: 3,
      current_step: 'Running: Story Design',
      progress_percent: 30,
    })

    rerender(<GenerationProgress sessionId={defaultSessionId} />)

    expect(screen.getByText('AI Agents')).toBeInTheDocument()
    expect(screen.getByText('Story Design')).toBeInTheDocument()
  })

  it('updates agent status from in-progress to completed', () => {
    const { rerender } = render(<GenerationProgress sessionId={defaultSessionId} />)

    const onMessageCallback = mockUseWebSocket.mock.calls[0][1]?.onMessage

    // Start a task
    onMessageCallback?.({
      type: 'progress',
      status: 'task_started',
      session_id: defaultSessionId,
      task_name: 'Story Design',
      task_index: 0,
      total_tasks: 3,
      current_step: 'Running: Story Design',
      progress_percent: 30,
    })

    rerender(<GenerationProgress sessionId={defaultSessionId} />)

    // Complete the task
    onMessageCallback?.({
      type: 'progress',
      status: 'task_completed',
      session_id: defaultSessionId,
      task_name: 'Story Design',
      task_index: 0,
      total_tasks: 3,
      current_step: 'Completed: Story Design',
      progress_percent: 50,
    })

    rerender(<GenerationProgress sessionId={defaultSessionId} />)

    expect(screen.getByText('Story Design')).toBeInTheDocument()
    expect(screen.getByText('50%')).toBeInTheDocument()
  })

  it('shows success status when generation completes', () => {
    const onComplete = vi.fn()
    const { rerender } = render(
      <GenerationProgress sessionId={defaultSessionId} onComplete={onComplete} />
    )

    const onMessageCallback = mockUseWebSocket.mock.calls[0][1]?.onMessage

    // Simulate completion
    onMessageCallback?.({
      type: 'progress',
      status: 'completed',
      session_id: defaultSessionId,
      current_step: 'Finalizing generation',
      progress_percent: 100,
    })

    rerender(<GenerationProgress sessionId={defaultSessionId} onComplete={onComplete} />)

    expect(screen.getByText('100%')).toBeInTheDocument()
    expect(screen.getByText('Generation Completed Successfully!')).toBeInTheDocument()
    expect(onComplete).toHaveBeenCalledTimes(1)
  })

  it('shows error status when generation fails', () => {
    const onError = vi.fn()
    const { rerender } = render(
      <GenerationProgress sessionId={defaultSessionId} onError={onError} />
    )

    const onMessageCallback = mockUseWebSocket.mock.calls[0][1]?.onMessage

    // Simulate error
    onMessageCallback?.({
      type: 'progress',
      status: 'error',
      session_id: defaultSessionId,
      error: 'Something went wrong',
    })

    rerender(<GenerationProgress sessionId={defaultSessionId} onError={onError} />)

    expect(screen.getByText(/Generation Failed:/)).toBeInTheDocument()
    expect(screen.getByText(/Something went wrong/)).toBeInTheDocument()
    expect(onError).toHaveBeenCalledWith('Something went wrong')
  })

  it('shows timeout status when generation times out', () => {
    const onError = vi.fn()
    const { rerender } = render(
      <GenerationProgress sessionId={defaultSessionId} onError={onError} />
    )

    const onMessageCallback = mockUseWebSocket.mock.calls[0][1]?.onMessage

    // Simulate timeout
    onMessageCallback?.({
      type: 'progress',
      status: 'timeout',
      session_id: defaultSessionId,
    })

    rerender(<GenerationProgress sessionId={defaultSessionId} onError={onError} />)

    expect(screen.getByText(/Generation Failed:/)).toBeInTheDocument()
    expect(screen.getAllByText(/Generation timed out/)[0]).toBeInTheDocument()
    expect(onError).toHaveBeenCalledWith('Generation timed out')
  })

  it('ignores heartbeat messages', () => {
    const { rerender } = render(<GenerationProgress sessionId={defaultSessionId} />)

    const onMessageCallback = mockUseWebSocket.mock.calls[0][1]?.onMessage

    // Initial state should show Initializing...
    expect(screen.getByText('Initializing...')).toBeInTheDocument()

    // Simulate heartbeat
    onMessageCallback?.({
      type: 'heartbeat',
      session_id: defaultSessionId,
    })

    rerender(<GenerationProgress sessionId={defaultSessionId} />)

    // Should still show Initializing...
    expect(screen.getByText('Initializing...')).toBeInTheDocument()
  })

  it('ignores connection messages', () => {
    const { rerender } = render(<GenerationProgress sessionId={defaultSessionId} />)

    const onMessageCallback = mockUseWebSocket.mock.calls[0][1]?.onMessage

    // Simulate connection message
    onMessageCallback?.({
      type: 'connection',
      status: 'connected',
      session_id: defaultSessionId,
    })

    rerender(<GenerationProgress sessionId={defaultSessionId} />)

    // Should still show initial state
    expect(screen.getByText('Initializing...')).toBeInTheDocument()
    expect(screen.getByText('0%')).toBeInTheDocument()
  })

  it('has accessible progress bar', () => {
    render(<GenerationProgress sessionId={defaultSessionId} />)

    const progressBar = screen.getByRole('progressbar', { name: 'Generation progress' })
    expect(progressBar).toBeInTheDocument()
    expect(progressBar).toHaveAttribute('aria-valuenow', '0')
    expect(progressBar).toHaveAttribute('aria-valuemin', '0')
    expect(progressBar).toHaveAttribute('aria-valuemax', '100')
  })

  it('passes reconnection options to useWebSocket', () => {
    render(<GenerationProgress sessionId={defaultSessionId} />)

    expect(mockUseWebSocket).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        autoConnect: true,
        autoReconnect: true,
        maxReconnectAttempts: 5,
      })
    )
  })
})
