import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import ReviewPage from '../../pages/ReviewPage'
import { storyApi } from '../../services/storyApi'
import { Story } from '../../types/story'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import userEvent from '@testing-library/user-event'

// Mock the storyApi
vi.mock('../../services/storyApi', () => ({
  storyApi: {
    getStory: vi.fn(),
  },
}))

const mockStory: Story = {
  id: 1,
  title: 'Test Story',
  description: 'A test story description',
  theme_id: 'warhammer40k',
  tags: ['test', 'horror'],
  game_file_path: '/data/stories/001/game.json',
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:30:00Z',
  play_count: 0,
  last_played: null,
  prompt: 'Test prompt',
  template_id: 'horror',
  iteration_count: 0,
  scene_count: 10,
  item_count: 15,
  npc_count: 5,
  puzzle_count: 3,
}

describe('ReviewPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays loading state initially', () => {
    vi.mocked(storyApi.getStory).mockImplementation(() => new Promise(() => {})) // Never resolves

    render(
      <MemoryRouter initialEntries={['/review/1']}>
        <Routes>
          <Route path="/review/:storyId" element={<ReviewPage />} />
        </Routes>
      </MemoryRouter>
    )

    expect(screen.getByText('Loading your story...')).toBeInTheDocument()
    expect(screen.getByRole('status', { name: /loading story/i })).toBeInTheDocument()
  })

  it('fetches and displays story data', async () => {
    vi.mocked(storyApi.getStory).mockResolvedValue(mockStory)

    render(
      <MemoryRouter initialEntries={['/review/1']}>
        <Routes>
          <Route path="/review/:storyId" element={<ReviewPage />} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Your Story is Ready!')).toBeInTheDocument()
    })

    expect(screen.getByText('Test Story')).toBeInTheDocument()
    expect(screen.getByText('A test story description')).toBeInTheDocument()
  })

  it('displays error when story fetch fails', async () => {
    vi.mocked(storyApi.getStory).mockRejectedValue(new Error('Network error'))

    render(
      <MemoryRouter initialEntries={['/review/1']}>
        <Routes>
          <Route path="/review/:storyId" element={<ReviewPage />} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument()
    })

    expect(screen.getByText('Failed to load story. Please try again.')).toBeInTheDocument()
  })

  it('displays error when no storyId is provided', async () => {
    render(
      <MemoryRouter initialEntries={['/review/']}>
        <Routes>
          <Route path="/review/:storyId?" element={<ReviewPage />} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument()
    })

    expect(screen.getByText('No story ID provided')).toBeInTheDocument()
  })

  it('navigates to play page when Play Now is clicked', async () => {
    vi.mocked(storyApi.getStory).mockResolvedValue(mockStory)

    const user = userEvent.setup()

    render(
      <MemoryRouter initialEntries={['/review/1']}>
        <Routes>
          <Route path="/review/:storyId" element={<ReviewPage />} />
          <Route path="/play/:id" element={<div>Play Page</div>} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Story')).toBeInTheDocument()
    })

    const playButton = screen.getByRole('button', { name: /play this story now/i })
    await user.click(playButton)

    await waitFor(() => {
      expect(screen.getByText('Play Page')).toBeInTheDocument()
    })
  })

  it('navigates to feedback page when Give Feedback is clicked', async () => {
    vi.mocked(storyApi.getStory).mockResolvedValue(mockStory)

    const user = userEvent.setup()

    render(
      <MemoryRouter initialEntries={['/review/1']}>
        <Routes>
          <Route path="/review/:storyId" element={<ReviewPage />} />
          <Route path="/feedback/:id" element={<div>Feedback Page</div>} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Story')).toBeInTheDocument()
    })

    const feedbackButton = screen.getByRole('button', { name: /give feedback on this story/i })
    await user.click(feedbackButton)

    await waitFor(() => {
      expect(screen.getByText('Feedback Page')).toBeInTheDocument()
    })
  })

  it('navigates to library on error button click', async () => {
    vi.mocked(storyApi.getStory).mockRejectedValue(new Error('Network error'))

    const user = userEvent.setup()

    render(
      <MemoryRouter initialEntries={['/review/1']}>
        <Routes>
          <Route path="/review/:storyId" element={<ReviewPage />} />
          <Route path="/library" element={<div>Library Page</div>} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument()
    })

    const returnButton = screen.getByRole('button', { name: /return to library/i })
    await user.click(returnButton)

    await waitFor(() => {
      expect(screen.getByText('Library Page')).toBeInTheDocument()
    })
  })

  it('calls storyApi.getStory with correct ID', async () => {
    vi.mocked(storyApi.getStory).mockResolvedValue(mockStory)

    render(
      <MemoryRouter initialEntries={['/review/42']}>
        <Routes>
          <Route path="/review/:storyId" element={<ReviewPage />} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(storyApi.getStory).toHaveBeenCalledWith(42)
    })
  })

  it('displays page header and subtitle', async () => {
    vi.mocked(storyApi.getStory).mockResolvedValue(mockStory)

    render(
      <MemoryRouter initialEntries={['/review/1']}>
        <Routes>
          <Route path="/review/:storyId" element={<ReviewPage />} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Your Story is Ready!')).toBeInTheDocument()
    })

    expect(
      screen.getByText('Review your generated story and decide what to do next')
    ).toBeInTheDocument()
  })
})
