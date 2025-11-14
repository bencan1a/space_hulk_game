import { render, screen } from '@testing-library/react'
import { StoryGrid } from '../../../components/library/StoryGrid'
import type { Story } from '../../../types/story'
import { describe, it, expect, vi } from 'vitest'

const mockStories: Story[] = [
  {
    id: 1,
    title: 'Story 1',
    description: 'Description 1',
    theme_id: 'warhammer40k',
    tags: ['horror'],
    game_file_path: 'data/test/game1.json',
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
    play_count: 5,
    last_played: null,
    prompt: 'Test prompt 1',
    template_id: null,
    iteration_count: 1,
    scene_count: 10,
    item_count: 5,
    npc_count: 3,
    puzzle_count: 2,
  },
  {
    id: 2,
    title: 'Story 2',
    description: 'Description 2',
    theme_id: 'cyberpunk',
    tags: ['action'],
    game_file_path: 'data/test/game2.json',
    created_at: '2024-01-16T10:00:00Z',
    updated_at: '2024-01-16T10:00:00Z',
    play_count: 3,
    last_played: null,
    prompt: 'Test prompt 2',
    template_id: null,
    iteration_count: 1,
    scene_count: 8,
    item_count: 4,
    npc_count: 2,
    puzzle_count: 1,
  },
]

describe('StoryGrid', () => {
  it('renders stories correctly', () => {
    render(<StoryGrid stories={mockStories} />)

    expect(screen.getByText('Story 1')).toBeInTheDocument()
    expect(screen.getByText('Story 2')).toBeInTheDocument()
  })

  it('displays loading state with skeleton cards', () => {
    render(<StoryGrid stories={[]} loading={true} />)

    expect(screen.getByLabelText('Loading stories')).toBeInTheDocument()
    expect(screen.getByLabelText('Loading stories')).toHaveAttribute('aria-busy', 'true')
  })

  it('displays error state', () => {
    const errorMessage = 'Failed to load stories'
    render(<StoryGrid stories={[]} error={errorMessage} />)

    expect(screen.getByText(errorMessage)).toBeInTheDocument()
    expect(screen.getByText('Retry')).toBeInTheDocument()
  })

  it('displays empty state when no stories', () => {
    render(<StoryGrid stories={[]} />)

    expect(screen.getByText('No stories found')).toBeInTheDocument()
    expect(screen.getByText(/Try adjusting your filters/i)).toBeInTheDocument()
  })

  it('calls onStoryClick when a story card is clicked', () => {
    const handleClick = vi.fn()
    render(<StoryGrid stories={mockStories} onStoryClick={handleClick} />)

    const cards = screen.getAllByRole('button')
    cards[0].click()

    expect(handleClick).toHaveBeenCalledWith(mockStories[0])
  })
})
