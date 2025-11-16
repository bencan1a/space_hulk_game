import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatInterface, ChatQuestion } from '../../../components/generation/ChatInterface'
import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockQuestions: ChatQuestion[] = [
  {
    id: 'theme',
    question: 'What theme would you like for your game?',
    minLength: 5,
    maxLength: 100,
  },
  {
    id: 'setting',
    question: 'Describe the setting of your game.',
    minLength: 10,
    maxLength: 200,
  },
  {
    id: 'difficulty',
    question: 'What difficulty level do you prefer?',
    minLength: 3,
    maxLength: 50,
  },
]

describe('ChatInterface', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders with initial question', async () => {
    render(<ChatInterface questions={mockQuestions} />)

    await waitFor(() => {
      expect(screen.getByText('What theme would you like for your game?')).toBeInTheDocument()
    })
  })

  it('displays progress indicator', () => {
    render(<ChatInterface questions={mockQuestions} />)

    expect(screen.getByText('Question 1 of 3')).toBeInTheDocument()
  })

  it('displays chat refinement title and subtitle', () => {
    render(<ChatInterface questions={mockQuestions} />)

    expect(screen.getByText('Chat Refinement')).toBeInTheDocument()
    expect(
      screen.getByText('Answer a few questions to build your perfect game prompt')
    ).toBeInTheDocument()
  })

  it('progresses through questions when user responds', async () => {
    render(<ChatInterface questions={mockQuestions} />)

    // Wait for first question
    await waitFor(() => {
      expect(screen.getByText('What theme would you like for your game?')).toBeInTheDocument()
    })

    const input = screen.getByLabelText('Chat input')

    // Answer first question
    await userEvent.type(input, 'Horror theme')
    fireEvent.submit(input.closest('form')!)

    // Check that user's answer appears
    await waitFor(() => {
      expect(screen.getByText('Horror theme')).toBeInTheDocument()
    })

    // Check that second question appears
    await waitFor(() => {
      expect(screen.getByText('Describe the setting of your game.')).toBeInTheDocument()
    })

    // Verify progress updated
    expect(screen.getByText('Question 2 of 3')).toBeInTheDocument()
  })

  it('displays user and assistant messages with correct roles', async () => {
    render(<ChatInterface questions={mockQuestions} />)

    await waitFor(() => {
      expect(screen.getByText('What theme would you like for your game?')).toBeInTheDocument()
    })

    const input = screen.getByLabelText('Chat input')

    await userEvent.type(input, 'Sci-fi horror')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('Sci-fi horror')).toBeInTheDocument()
    })

    // Check that both assistant and user messages exist
    const assistantMessages = screen.getAllByLabelText('Assistant message')
    const userMessages = screen.getAllByLabelText('User message')

    expect(assistantMessages.length).toBeGreaterThanOrEqual(1)
    expect(userMessages.length).toBeGreaterThanOrEqual(1)
  })

  it('shows final prompt after all questions answered', async () => {
    render(<ChatInterface questions={mockQuestions} />)

    const input = screen.getByLabelText('Chat input')

    // Answer all questions
    await userEvent.type(input, 'Horror theme')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('Describe the setting of your game.')).toBeInTheDocument()
    })

    await userEvent.type(input, 'Abandoned space station')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('What difficulty level do you prefer?')).toBeInTheDocument()
    })

    await userEvent.type(input, 'Hard')
    fireEvent.submit(input.closest('form')!)

    // Check for final prompt message
    await waitFor(() => {
      expect(screen.getByText(/Based on your answers/i)).toBeInTheDocument()
    })

    // Check for action buttons
    expect(screen.getByRole('button', { name: /Start Over/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Generate Story/i })).toBeInTheDocument()
  })

  it('calls onComplete with all answers when confirmed', async () => {
    const onComplete = vi.fn()
    render(<ChatInterface questions={mockQuestions} onComplete={onComplete} />)

    const input = screen.getByLabelText('Chat input')

    // Answer all questions with valid inputs
    await userEvent.clear(input)
    await userEvent.type(input, 'Horror theme')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('Describe the setting of your game.')).toBeInTheDocument()
    })

    await userEvent.clear(input)
    await userEvent.type(input, 'Space hulk derelict')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('What difficulty level do you prefer?')).toBeInTheDocument()
    })

    await userEvent.clear(input)
    await userEvent.type(input, 'Hard mode')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Generate Story/i })).toBeInTheDocument()
    })

    const confirmButton = screen.getByRole('button', { name: /Generate Story/i })
    fireEvent.click(confirmButton)

    expect(onComplete).toHaveBeenCalledWith(
      expect.objectContaining({
        theme: 'Horror theme',
        setting: 'Space hulk derelict',
        difficulty: 'Hard mode',
        finalPrompt: expect.stringContaining('Horror theme'),
      })
    )
  })

  it('calls onCancel when start over is clicked', async () => {
    const onCancel = vi.fn()
    render(<ChatInterface questions={mockQuestions} onCancel={onCancel} />)

    const input = screen.getByLabelText('Chat input')

    // Answer all questions to get to the final prompt
    await userEvent.clear(input)
    await userEvent.type(input, 'Horror theme')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('Describe the setting of your game.')).toBeInTheDocument()
    })

    await userEvent.clear(input)
    await userEvent.type(input, 'Space station abandoned')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('What difficulty level do you prefer?')).toBeInTheDocument()
    })

    await userEvent.clear(input)
    await userEvent.type(input, 'Hard mode')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Start Over/i })).toBeInTheDocument()
    })

    const cancelButton = screen.getByRole('button', { name: /Start Over/i })
    fireEvent.click(cancelButton)

    expect(onCancel).toHaveBeenCalled()
  })

  it('renders with initial messages', () => {
    const initialMessages = [
      { role: 'assistant' as const, content: 'Welcome!' },
      { role: 'user' as const, content: 'Hello!' },
    ]

    render(<ChatInterface questions={mockQuestions} initialMessages={initialMessages} />)

    expect(screen.getByText('Welcome!')).toBeInTheDocument()
    expect(screen.getByText('Hello!')).toBeInTheDocument()
  })

  it('hides input when all questions are answered', async () => {
    render(<ChatInterface questions={mockQuestions} />)

    const input = screen.getByLabelText('Chat input')

    // Answer all questions
    await userEvent.clear(input)
    await userEvent.type(input, 'Horror theme')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('Describe the setting of your game.')).toBeInTheDocument()
    })

    await userEvent.clear(input)
    await userEvent.type(input, 'Space derelict station')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('What difficulty level do you prefer?')).toBeInTheDocument()
    })

    await userEvent.clear(input)
    await userEvent.type(input, 'Hard mode')
    fireEvent.submit(input.closest('form')!)

    // Input should be hidden after all questions answered
    await waitFor(() => {
      expect(screen.queryByLabelText('Chat input')).not.toBeInTheDocument()
    })
  })

  it('generates final prompt from all answers', async () => {
    render(<ChatInterface questions={mockQuestions} />)

    const input = screen.getByLabelText('Chat input')

    await userEvent.type(input, 'Gothic horror')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('Describe the setting of your game.')).toBeInTheDocument()
    })

    await userEvent.type(input, 'An abandoned cathedral in space')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('What difficulty level do you prefer?')).toBeInTheDocument()
    })

    await userEvent.type(input, 'Nightmare')
    fireEvent.submit(input.closest('form')!)

    await waitFor(() => {
      const messages = screen.getAllByRole('article')
      const lastMessage = messages[messages.length - 1]
      expect(lastMessage.textContent).toContain('Gothic horror')
      expect(lastMessage.textContent).toContain('An abandoned cathedral in space')
      expect(lastMessage.textContent).toContain('Nightmare')
    })
  })

  it('applies validation rules from questions', async () => {
    render(<ChatInterface questions={mockQuestions} />)

    const input = screen.getByLabelText('Chat input')
    const submitButton = screen.getByRole('button', { name: 'Send message' })

    // Try to submit with too short answer (minLength is 5 for first question)
    await userEvent.type(input, 'Hi')

    expect(submitButton).toBeDisabled()
  })
})
