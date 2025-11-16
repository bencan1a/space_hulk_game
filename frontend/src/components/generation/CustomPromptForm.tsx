import React, { useState } from 'react'
import styles from './CustomPromptForm.module.css'

interface CustomPromptFormProps {
  onSubmit?: (prompt: string) => void
  initialValue?: string
}

export const CustomPromptForm: React.FC<CustomPromptFormProps> = ({
  onSubmit,
  initialValue = '',
}) => {
  const [prompt, setPrompt] = useState(initialValue)
  const [error, setError] = useState<string | null>(null)

  const MIN_LENGTH = 50
  const MAX_LENGTH = 1000

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    setPrompt(value)

    // Validate on change
    if (value.length > 0 && value.length < MIN_LENGTH) {
      setError(`Prompt must be at least ${MIN_LENGTH} characters (currently ${value.length})`)
    } else if (value.length > MAX_LENGTH) {
      setError(`Prompt must not exceed ${MAX_LENGTH} characters (currently ${value.length})`)
    } else {
      setError(null)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Final validation
    if (prompt.length < MIN_LENGTH) {
      setError(`Prompt must be at least ${MIN_LENGTH} characters`)
      return
    }

    if (prompt.length > MAX_LENGTH) {
      setError(`Prompt must not exceed ${MAX_LENGTH} characters`)
      return
    }

    if (onSubmit) {
      onSubmit(prompt)
    }
  }

  const isValid = prompt.length >= MIN_LENGTH && prompt.length <= MAX_LENGTH
  const charCount = prompt.length
  const charCountClass = error
    ? styles.charCountError
    : isValid
      ? styles.charCountValid
      : styles.charCount

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.formGroup}>
        <label htmlFor="custom-prompt" className={styles.label}>
          Custom Prompt
          <span className={styles.labelHint}>Describe your desired game in detail</span>
        </label>

        <textarea
          id="custom-prompt"
          className={`${styles.textarea} ${error ? styles.textareaError : ''}`}
          value={prompt}
          onChange={handleChange}
          placeholder="Create a gothic horror text-based adventure game set in an abandoned space hulk..."
          rows={8}
          aria-describedby="prompt-help prompt-error"
          aria-invalid={error !== null}
        />

        <div className={styles.footer}>
          <div className={charCountClass} aria-live="polite">
            {charCount} / {MAX_LENGTH} characters
            {!isValid && charCount < MIN_LENGTH && ` (minimum ${MIN_LENGTH})`}
          </div>

          {error && (
            <div id="prompt-error" className={styles.error} role="alert">
              {error}
            </div>
          )}
        </div>

        <div id="prompt-help" className={styles.help}>
          Include details about setting, atmosphere, gameplay style, and any specific elements you
          want in your game.
        </div>
      </div>

      <button type="submit" className={styles.submitButton} disabled={!isValid}>
        Continue with Custom Prompt
      </button>
    </form>
  )
}
