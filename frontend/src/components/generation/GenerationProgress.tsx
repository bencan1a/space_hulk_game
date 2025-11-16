import React, { useMemo } from 'react'
import { useWebSocket, WebSocketMessage } from '../../hooks/useWebSocket'
import styles from './GenerationProgress.module.css'

export interface AgentStatus {
  name: string
  status: 'pending' | 'in-progress' | 'completed' | 'error'
}

export interface GenerationProgressProps {
  /**
   * The session ID to track progress for
   */
  sessionId: string

  /**
   * WebSocket base URL (without the path)
   * @default Based on VITE_API_URL or http://localhost:8000
   */
  wsBaseUrl?: string

  /**
   * Callback when generation completes successfully
   */
  onComplete?: () => void

  /**
   * Callback when generation fails
   */
  onError?: (error: string) => void
}

/**
 * Component that displays real-time generation progress via WebSocket
 *
 * Shows:
 * - Overall progress bar (0-100%)
 * - Current step description
 * - List of agents/tasks with their completion status
 * - Final status (Completed/Failed)
 *
 * @example
 * ```tsx
 * <GenerationProgress
 *   sessionId="session-123"
 *   onComplete={() => navigate('/story/123')}
 *   onError={(error) => console.error(error)}
 * />
 * ```
 */
export const GenerationProgress: React.FC<GenerationProgressProps> = ({
  sessionId,
  wsBaseUrl,
  onComplete,
  onError,
}) => {
  const [progressPercent, setProgressPercent] = React.useState(0)
  const [currentStep, setCurrentStep] = React.useState('Initializing...')
  const [agentStatuses, setAgentStatuses] = React.useState<AgentStatus[]>([])
  const [finalStatus, setFinalStatus] = React.useState<'completed' | 'failed' | null>(null)
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null)

  // Construct WebSocket URL
  const wsUrl = useMemo(() => {
    if (!sessionId) return null

    const baseUrl = wsBaseUrl || import.meta.env.VITE_API_URL || 'http://localhost:8000'
    // Convert http(s):// to ws(s)://
    const wsProtocol = baseUrl.startsWith('https') ? 'wss' : 'ws'
    const urlWithoutProtocol = baseUrl.replace(/^https?:\/\//, '')

    return `${wsProtocol}://${urlWithoutProtocol}/ws/progress/${sessionId}`
  }, [sessionId, wsBaseUrl])

  // Handle WebSocket messages
  const handleMessage = React.useCallback(
    (message: WebSocketMessage) => {
      // Ignore heartbeat and connection messages
      if (message.type === 'heartbeat' || message.type === 'connection') {
        return
      }

      if (message.type === 'progress') {
        const { status, progress_percent, current_step, task_name, task_index, total_tasks, error } =
          message

        // Update progress percentage
        if (progress_percent !== undefined) {
          setProgressPercent(progress_percent)
        }

        // Update current step
        if (current_step) {
          setCurrentStep(current_step)
        }

        // Handle different status types
        switch (status) {
          case 'started': {
            setCurrentStep(current_step || 'Starting generation...')
            break
          }

          case 'task_started': {
            if (task_name && task_index !== undefined && total_tasks) {
              // Update agent status to in-progress
              setAgentStatuses((prev) => {
                const updated = [...prev]
                const existingIndex = updated.findIndex((a) => a.name === task_name)

                if (existingIndex >= 0) {
                  updated[existingIndex] = { name: task_name, status: 'in-progress' }
                } else {
                  // Initialize all tasks if this is the first one
                  if (updated.length === 0) {
                    // We'll add tasks as they come in
                  }
                  updated.push({ name: task_name, status: 'in-progress' })
                }

                return updated
              })
            }
            break
          }

          case 'task_completed': {
            if (task_name) {
              // Update agent status to completed
              setAgentStatuses((prev) => {
                const updated = [...prev]
                const existingIndex = updated.findIndex((a) => a.name === task_name)

                if (existingIndex >= 0) {
                  updated[existingIndex] = { name: task_name, status: 'completed' }
                } else {
                  updated.push({ name: task_name, status: 'completed' })
                }

                return updated
              })
            }
            break
          }

          case 'completed': {
            setProgressPercent(100)
            setCurrentStep('Generation completed!')
            setFinalStatus('completed')
            onComplete?.()
            break
          }

          case 'error': {
            setFinalStatus('failed')
            const errMsg = error || 'An error occurred during generation'
            setErrorMessage(errMsg)
            setCurrentStep('Generation failed')
            onError?.(errMsg)
            break
          }

          case 'timeout': {
            setFinalStatus('failed')
            const timeoutMsg = 'Generation timed out'
            setErrorMessage(timeoutMsg)
            setCurrentStep('Generation timed out')
            onError?.(timeoutMsg)
            break
          }
        }
      }
    },
    [onComplete, onError]
  )

  // Connect to WebSocket
  const { isConnected, isConnecting } = useWebSocket(wsUrl, {
    onMessage: handleMessage,
    autoConnect: true,
    autoReconnect: true,
    maxReconnectAttempts: 5,
  })

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Generating Your Story</h2>
        <div className={styles.connectionStatus}>
          {isConnecting && <span className={styles.statusConnecting}>Connecting...</span>}
          {isConnected && <span className={styles.statusConnected}>● Connected</span>}
          {!isConnected && !isConnecting && (
            <span className={styles.statusDisconnected}>● Disconnected</span>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className={styles.progressSection}>
        <div className={styles.progressHeader}>
          <span className={styles.currentStep}>{currentStep}</span>
          <span className={styles.progressPercent}>{progressPercent}%</span>
        </div>
        <div className={styles.progressBarContainer}>
          <div
            className={styles.progressBar}
            style={{ width: `${progressPercent}%` }}
            role="progressbar"
            aria-valuenow={progressPercent}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Generation progress"
          />
        </div>
      </div>

      {/* Agent Status List */}
      {agentStatuses.length > 0 && (
        <div className={styles.agentSection}>
          <h3 className={styles.agentSectionTitle}>AI Agents</h3>
          <AgentStatusList statuses={agentStatuses} />
        </div>
      )}

      {/* Final Status */}
      {finalStatus && (
        <div
          className={`${styles.finalStatus} ${
            finalStatus === 'completed' ? styles.finalStatusSuccess : styles.finalStatusError
          }`}
        >
          {finalStatus === 'completed' ? (
            <>
              <span className={styles.finalStatusIcon}>✓</span>
              <span className={styles.finalStatusText}>Generation Completed Successfully!</span>
            </>
          ) : (
            <>
              <span className={styles.finalStatusIcon}>✗</span>
              <span className={styles.finalStatusText}>
                Generation Failed: {errorMessage || 'Unknown error'}
              </span>
            </>
          )}
        </div>
      )}
    </div>
  )
}

/**
 * Component that displays the status of each agent/task
 */
interface AgentStatusListProps {
  statuses: AgentStatus[]
}

const AgentStatusList: React.FC<AgentStatusListProps> = ({ statuses }) => {
  return (
    <ul className={styles.agentList} role="list">
      {statuses.map((agent, index) => (
        <li key={`${agent.name}-${index}`} className={styles.agentItem}>
          <span
            className={`${styles.agentIcon} ${styles[`agentIcon${capitalize(agent.status)}`]}`}
            aria-label={`${agent.name} ${agent.status}`}
          >
            {getStatusIcon(agent.status)}
          </span>
          <span className={styles.agentName}>{agent.name}</span>
        </li>
      ))}
    </ul>
  )
}

/**
 * Get the appropriate icon for a given status
 */
function getStatusIcon(status: AgentStatus['status']): string {
  switch (status) {
    case 'pending':
      return '○'
    case 'in-progress':
      return '◐'
    case 'completed':
      return '✓'
    case 'error':
      return '✗'
    default:
      return '○'
  }
}

/**
 * Capitalize the first letter of a string
 */
function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1).replace(/-/g, '')
}
