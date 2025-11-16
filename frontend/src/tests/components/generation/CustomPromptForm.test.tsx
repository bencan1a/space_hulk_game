import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { CustomPromptForm } from '../../../components/generation/CustomPromptForm'
import { describe, it, expect, vi } from 'vitest'

describe('CustomPromptForm', () => {
  it('renders form correctly', () => {
    render(<CustomPromptForm />)

    expect(screen.getByLabelText(/Custom Prompt/i)).toBeInTheDocument()
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Continue with Custom Prompt/i })).toBeInTheDocument()
  })

  it('displays character count', async () => {
    const user = userEvent.setup()
    render(<CustomPromptForm />)

    const textarea = screen.getByRole('textbox')
    await user.type(textarea, 'Test prompt')

    await waitFor(() => {
      expect(screen.getByText(/11 \/ 1000 characters/i)).toBeInTheDocument()
    })
  })

  it('validates minimum length', async () => {
    const user = userEvent.setup()
    render(<CustomPromptForm />)

    const textarea = screen.getByRole('textbox')
    await user.type(textarea, 'Short')

    await waitFor(() => {
      expect(screen.getByText(/minimum 50/i)).toBeInTheDocument()
    })
  })

  it('validates maximum length', async () => {
    const user = userEvent.setup()
    render(<CustomPromptForm />)

    const textarea = screen.getByRole('textbox')
    const longText = 'a'.repeat(1001)
    await user.type(textarea, longText)

    await waitFor(() => {
      expect(screen.getByText(/must not exceed 1000 characters/i)).toBeInTheDocument()
    })
  })

  it('enables submit button when valid', async () => {
    const user = userEvent.setup()
    render(<CustomPromptForm />)

    const submitButton = screen.getByRole('button', { name: /Continue with Custom Prompt/i })
    expect(submitButton).toBeDisabled()

    const textarea = screen.getByRole('textbox')
    const validText = 'a'.repeat(50)
    await user.type(textarea, validText)

    await waitFor(() => {
      expect(submitButton).not.toBeDisabled()
    })
  })

  it('calls onSubmit with valid prompt', async () => {
    const handleSubmit = vi.fn()
    const user = userEvent.setup()
    render(<CustomPromptForm onSubmit={handleSubmit} />)

    const textarea = screen.getByRole('textbox')
    const validText = 'a'.repeat(50)
    await user.type(textarea, validText)

    const submitButton = screen.getByRole('button', { name: /Continue with Custom Prompt/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith(validText)
    })
  })

  it('does not call onSubmit with invalid prompt', async () => {
    const handleSubmit = vi.fn()
    render(<CustomPromptForm onSubmit={handleSubmit} />)

    const form = screen.getByRole('textbox').closest('form')
    fireEvent.submit(form!)

    expect(handleSubmit).not.toHaveBeenCalled()
  })

  it('uses initial value', () => {
    const initialValue = 'a'.repeat(50)
    render(<CustomPromptForm initialValue={initialValue} />)

    const textarea = screen.getByRole('textbox') as HTMLTextAreaElement
    expect(textarea.value).toBe(initialValue)
  })

  it('shows error state on textarea when invalid', async () => {
    const user = userEvent.setup()
    render(<CustomPromptForm />)

    const textarea = screen.getByRole('textbox')
    await user.type(textarea, 'Short')

    await waitFor(() => {
      expect(textarea).toHaveAttribute('aria-invalid', 'true')
    })
  })
})
