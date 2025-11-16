import React, { useState, useRef, useEffect } from 'react'
import styles from './ChatInput.module.css'

export interface ChatInputProps {
  onSubmit: (message: string) => void
  placeholder?: string
  disabled?: boolean
  minLength?: number
  maxLength?: number
  validationMessage?: string
  autoFocus?: boolean
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSubmit,
  placeholder = 'Type your response...',
  disabled = false,
  minLength = 1,
  maxLength = 500,
  validationMessage,
  autoFocus = false,
}) => {
  const [message, setMessage] = useState('')
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus()
    }
  }, [autoFocus])

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    setMessage(value)

    // Validate on change
    if (value.length > maxLength) {
      setError(`Response must not exceed ${maxLength} characters`)
    } else if (validationMessage && value.length > 0 && value.length < minLength) {
      setError(validationMessage)
    } else {
      setError(null)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const trimmed = message.trim()

    // Final validation
    if (trimmed.length < minLength) {
      setError(validationMessage ?? `Please provide a response (minimum ${minLength} characters)`)
      return
    }

    if (trimmed.length > maxLength) {
      setError(`Response must not exceed ${maxLength} characters`)
      return
    }

    onSubmit(trimmed)
    setMessage('')
    setError(null)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter, but allow Shift+Enter for new lines
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const isValid = message.trim().length >= minLength && message.length <= maxLength
  const charCount = message.length

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.inputGroup}>
        <textarea
          ref={inputRef}
          className={`${styles.input} ${error ? styles.inputError : ''}`}
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={3}
          aria-label="Chat input"
          aria-describedby={error ? 'chat-input-error' : undefined}
          aria-invalid={error !== null}
        />

        <div className={styles.footer}>
          <div className={styles.charCount} aria-live="polite">
            {charCount} / {maxLength}
          </div>

          {error && (
            <div id="chat-input-error" className={styles.error} role="alert">
              {error}
            </div>
          )}
        </div>
      </div>

      <button
        type="submit"
        className={styles.submitButton}
        disabled={!isValid || disabled}
        aria-label="Send message"
      >
        Send
      </button>
    </form>
  )
}
