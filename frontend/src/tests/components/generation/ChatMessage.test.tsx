import { render, screen } from '@testing-library/react'
import { ChatMessage, ChatMessageProps } from '../../../components/generation/ChatMessage'
import { describe, it, expect } from 'vitest'

describe('ChatMessage', () => {
  const defaultProps: ChatMessageProps = {
    role: 'user',
    content: 'This is a test message',
  }

  it('renders user message correctly', () => {
    render(<ChatMessage {...defaultProps} />)

    expect(screen.getByLabelText('User message')).toBeInTheDocument()
    expect(screen.getByText('You')).toBeInTheDocument()
    expect(screen.getByText('This is a test message')).toBeInTheDocument()
  })

  it('renders assistant message correctly', () => {
    const props: ChatMessageProps = {
      role: 'assistant',
      content: 'How can I help you?',
    }

    render(<ChatMessage {...props} />)

    expect(screen.getByLabelText('Assistant message')).toBeInTheDocument()
    expect(screen.getByText('AI Guide')).toBeInTheDocument()
    expect(screen.getByText('How can I help you?')).toBeInTheDocument()
  })

  it('displays timestamp when provided', () => {
    const props: ChatMessageProps = {
      ...defaultProps,
      timestamp: '12:34 PM',
    }

    render(<ChatMessage {...props} />)

    expect(screen.getByText('12:34 PM')).toBeInTheDocument()
  })

  it('does not display timestamp when not provided', () => {
    render(<ChatMessage {...defaultProps} />)

    expect(screen.queryByText(/AM|PM/)).not.toBeInTheDocument()
  })

  it('renders multiline content correctly', () => {
    const props: ChatMessageProps = {
      role: 'user',
      content: 'Line 1\nLine 2\nLine 3',
    }

    const { container } = render(<ChatMessage {...props} />)
    const content = container.querySelector('[class*="content"]')

    expect(content?.textContent).toBe('Line 1\nLine 2\nLine 3')
  })

  it('has correct role attribute', () => {
    const { container } = render(<ChatMessage {...defaultProps} />)

    const message = container.querySelector('[role="article"]')
    expect(message).toBeInTheDocument()
  })

  it('applies correct CSS classes for user message', () => {
    const { container } = render(<ChatMessage {...defaultProps} />)

    const message = container.querySelector('[class*="messageUser"]')
    expect(message).toBeInTheDocument()
  })

  it('applies correct CSS classes for assistant message', () => {
    const props: ChatMessageProps = {
      role: 'assistant',
      content: 'Test',
    }

    const { container } = render(<ChatMessage {...props} />)

    const message = container.querySelector('[class*="messageAssistant"]')
    expect(message).toBeInTheDocument()
  })
})
