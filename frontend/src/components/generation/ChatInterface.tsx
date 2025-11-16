import React, { useState, useRef, useEffect } from 'react'
import styles from './ChatInterface.module.css'
import { ChatMessage, ChatMessageProps } from './ChatMessage'
import { ChatInput } from './ChatInput'

export interface ChatQuestion {
  id: string
  question: string
  minLength?: number
  maxLength?: number
  validationMessage?: string
}

export interface ChatInterfaceProps {
  questions: ChatQuestion[]
  onComplete?: (answers: Record<string, string>) => void
  onCancel?: () => void
  initialMessages?: ChatMessageProps[]
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  questions,
  onComplete,
  onCancel,
  initialMessages = [],
}) => {
  const [messages, setMessages] = useState<ChatMessageProps[]>(initialMessages)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [showFinalPrompt, setShowFinalPrompt] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const currentQuestion = questions[currentQuestionIndex]
  const isComplete = currentQuestionIndex >= questions.length

  // Add initial question on mount
  useEffect(() => {
    if (messages.length === 0 && questions.length > 0) {
      setMessages([
        {
          role: 'assistant',
          content: questions[0].question,
        },
      ])
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-scroll to latest message
  useEffect(() => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  const handleUserResponse = (response: string) => {
    if (!currentQuestion) return

    // Add user's response to messages
    const userMessage: ChatMessageProps = {
      role: 'user',
      content: response,
    }
    setMessages((prev) => [...prev, userMessage])

    // Store the answer
    const newAnswers = {
      ...answers,
      [currentQuestion.id]: response,
    }
    setAnswers(newAnswers)

    // Move to next question
    const nextIndex = currentQuestionIndex + 1

    if (nextIndex < questions.length) {
      // Add next question
      const nextQuestion = questions[nextIndex]
      const assistantMessage: ChatMessageProps = {
        role: 'assistant',
        content: nextQuestion.question,
      }
      setMessages((prev) => [...prev, assistantMessage])
      setCurrentQuestionIndex(nextIndex)
    } else {
      // All questions answered - generate final prompt
      const finalPrompt = generateFinalPrompt(newAnswers)
      const completionMessage: ChatMessageProps = {
        role: 'assistant',
        content: `Great! Based on your answers, I've generated a detailed prompt for your game:\n\n${finalPrompt}\n\nDoes this look good?`,
      }
      setMessages((prev) => [...prev, completionMessage])
      setCurrentQuestionIndex(nextIndex)
      setShowFinalPrompt(true)
    }
  }

  const generateFinalPrompt = (userAnswers: Record<string, string>): string => {
    // Combine all answers into a cohesive prompt
    const parts: string[] = []

    for (const question of questions) {
      const answer = userAnswers[question.id]
      if (answer) {
        parts.push(answer)
      }
    }

    return parts.join(' ')
  }

  const handleConfirm = () => {
    const finalPrompt = generateFinalPrompt(answers)
    if (onComplete) {
      onComplete({ ...answers, finalPrompt })
    }
  }

  const handleCancel = () => {
    if (onCancel) {
      onCancel()
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Chat Refinement</h2>
        <p className={styles.subtitle}>Answer a few questions to build your perfect game prompt</p>
        <div className={styles.progress} role="progressbar" aria-valuenow={currentQuestionIndex} aria-valuemin={0} aria-valuemax={questions.length}>
          <div className={styles.progressBar} style={{ width: `${(currentQuestionIndex / questions.length) * 100}%` }} />
          <span className={styles.progressText}>
            Question {Math.min(currentQuestionIndex + 1, questions.length)} of {questions.length}
          </span>
        </div>
      </div>

      <div className={styles.messagesContainer} role="log" aria-live="polite" aria-label="Chat messages">
        {messages.map((message, index) => (
          <ChatMessage key={index} {...message} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {!isComplete && currentQuestion && (
        <div className={styles.inputContainer}>
          <ChatInput
            onSubmit={handleUserResponse}
            placeholder="Type your answer..."
            minLength={currentQuestion.minLength}
            maxLength={currentQuestion.maxLength}
            validationMessage={currentQuestion.validationMessage}
            autoFocus
          />
        </div>
      )}

      {showFinalPrompt && (
        <div className={styles.actions}>
          <button
            className={styles.cancelButton}
            onClick={handleCancel}
            aria-label="Cancel and start over"
          >
            Start Over
          </button>
          <button
            className={styles.confirmButton}
            onClick={handleConfirm}
            aria-label="Confirm and generate story"
          >
            Generate Story
          </button>
        </div>
      )}
    </div>
  )
}
