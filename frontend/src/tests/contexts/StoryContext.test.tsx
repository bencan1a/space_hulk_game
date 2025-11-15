import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { StoryProvider, useStoryContext } from '../../contexts/StoryContext'
import { storyApi } from '../../services/storyApi'
import type { StoryListResponse } from '../../types/story'

vi.mock('../../services/storyApi')

const TestComponent = () => {
  const { stories, loading, error, fetchStories } = useStoryContext()

  return (
    <div>
      <div data-testid="loading">{loading ? 'Loading' : 'Not Loading'}</div>
      <div data-testid="error">{error || 'No Error'}</div>
      <div data-testid="count">{stories.length}</div>
      <button onClick={fetchStories}>Fetch</button>
    </div>
  )
}

describe('StoryContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('provides initial state', () => {
    render(
      <StoryProvider>
        <TestComponent />
      </StoryProvider>
    )

    expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading')
    expect(screen.getByTestId('error')).toHaveTextContent('No Error')
    expect(screen.getByTestId('count')).toHaveTextContent('0')
  })

  it('fetches stories successfully', async () => {
    const mockStories = {
      items: [
        { id: 1, title: 'Story 1' },
        { id: 2, title: 'Story 2' },
      ],
      total: 2,
      page: 1,
      page_size: 20,
      total_pages: 1,
    }

    vi.mocked(storyApi.getStories).mockResolvedValue(mockStories as StoryListResponse)

    render(
      <StoryProvider>
        <TestComponent />
      </StoryProvider>
    )

    fireEvent.click(screen.getByText('Fetch'))

    // Should show loading
    expect(screen.getByTestId('loading')).toHaveTextContent('Loading')

    // Wait for fetch to complete
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading')
    })

    expect(screen.getByTestId('count')).toHaveTextContent('2')
    expect(screen.getByTestId('error')).toHaveTextContent('No Error')
  })

  it('handles fetch errors', async () => {
    vi.mocked(storyApi.getStories).mockRejectedValue(new Error('API Error'))

    render(
      <StoryProvider>
        <TestComponent />
      </StoryProvider>
    )

    fireEvent.click(screen.getByText('Fetch'))

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('API Error')
    })

    expect(screen.getByTestId('count')).toHaveTextContent('0')
  })
})
