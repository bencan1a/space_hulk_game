import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatInput } from '../../../components/generation/ChatInput'
import { describe, it, expect, vi } from 'vitest'

describe('ChatInput', () => {
  it('renders with default props', () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} />)

    expect(screen.getByLabelText('Chat input')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Send message' })).toBeInTheDocument()
  })

  it('displays custom placeholder', () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} placeholder="Enter your answer..." />)

    expect(screen.getByPlaceholderText('Enter your answer...')).toBeInTheDocument()
  })

  it('calls onSubmit when form is submitted with valid input', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} minLength={3} />)

    const input = screen.getByLabelText('Chat input')
    const submitButton = screen.getByRole('button', { name: 'Send message' })

    await userEvent.type(input, 'Valid message')
    fireEvent.click(submitButton)

    expect(onSubmit).toHaveBeenCalledWith('Valid message')
  })

  it('clears input after submission', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} />)

    const input = screen.getByLabelText('Chat input') as HTMLTextAreaElement

    await userEvent.type(input, 'Test message')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(input.value).toBe('')
    })
  })

  it('submits on Enter key (without Shift)', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} />)

    const input = screen.getByLabelText('Chat input')

    await userEvent.type(input, 'Test message')
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false })

    expect(onSubmit).toHaveBeenCalledWith('Test message')
  })

  it('does not submit on Shift+Enter (allows newline)', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} />)

    const input = screen.getByLabelText('Chat input')

    await userEvent.type(input, 'First line')
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: true })

    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('validates minimum length', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} minLength={10} />)

    const input = screen.getByLabelText('Chat input')
    const submitButton = screen.getByRole('button', { name: 'Send message' })

    await userEvent.type(input, 'Short')

    expect(submitButton).toBeDisabled()

    fireEvent.click(submitButton)
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('validates maximum length', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} maxLength={10} />)

    const input = screen.getByLabelText('Chat input')

    await userEvent.type(input, 'This is too long')

    await waitFor(() => {
      expect(screen.getByText(/must not exceed/i)).toBeInTheDocument()
    })
  })

  it('displays custom validation message', async () => {
    const onSubmit = vi.fn()
    render(
      <ChatInput
        onSubmit={onSubmit}
        minLength={5}
        validationMessage="Please provide more details"
      />
    )

    const input = screen.getByLabelText('Chat input')

    await userEvent.type(input, 'Hi')

    await waitFor(() => {
      expect(screen.getByText('Please provide more details')).toBeInTheDocument()
    })
  })

  it('shows character count', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} maxLength={100} />)

    const input = screen.getByLabelText('Chat input')

    await userEvent.type(input, 'Test')

    expect(screen.getByText('4 / 100')).toBeInTheDocument()
  })

  it('trims whitespace before submitting', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} />)

    const input = screen.getByLabelText('Chat input')

    await userEvent.type(input, '  Test message  ')
    fireEvent.submit(input.closest('form')!)

    expect(onSubmit).toHaveBeenCalledWith('Test message')
  })

  it('is disabled when disabled prop is true', () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} disabled />)

    const input = screen.getByLabelText('Chat input')
    const submitButton = screen.getByRole('button', { name: 'Send message' })

    expect(input).toBeDisabled()
    expect(submitButton).toBeDisabled()
  })

  it('auto-focuses when autoFocus prop is true', () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} autoFocus />)

    const input = screen.getByLabelText('Chat input')

    expect(document.activeElement).toBe(input)
  })

  it('does not auto-focus when autoFocus prop is false', () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} autoFocus={false} />)

    const input = screen.getByLabelText('Chat input')

    expect(document.activeElement).not.toBe(input)
  })

  it('shows error state with aria attributes', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} maxLength={5} />)

    const input = screen.getByLabelText('Chat input')

    await userEvent.type(input, 'Too long')

    expect(input).toHaveAttribute('aria-invalid', 'true')
    expect(input).toHaveAttribute('aria-describedby', 'chat-input-error')
  })
})
