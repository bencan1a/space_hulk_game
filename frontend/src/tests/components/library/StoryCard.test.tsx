import { render, screen, fireEvent } from '@testing-library/react'
import { StoryCard } from '../../../components/library/StoryCard'
import type { Story } from '../../../types/story'
import { describe, it, expect, vi } from 'vitest'

const mockStory: Story = {
  id: 1,
  title: 'Test Horror Story',
  description: 'A spooky test story',
  theme_id: 'warhammer40k',
  tags: ['horror', 'atmospheric'],
  game_file_path: 'data/test/game.json',
  created_at: '2024-01-15T10:00:00Z',
  updated_at: '2024-01-15T10:00:00Z',
  play_count: 5,
  last_played: null,
  prompt: 'Test prompt',
  template_id: null,
  iteration_count: 1,
  scene_count: 10,
  item_count: 5,
  npc_count: 3,
  puzzle_count: 2,
}

describe('StoryCard', () => {
  it('renders story information correctly', () => {
    render(<StoryCard story={mockStory} />)

    expect(screen.getByText('Test Horror Story')).toBeInTheDocument()
    expect(screen.getByText('A spooky test story')).toBeInTheDocument()
    expect(screen.getByText('warhammer40k')).toBeInTheDocument()
    expect(screen.getByText('horror')).toBeInTheDocument()
    expect(screen.getByText('atmospheric')).toBeInTheDocument()
  })

  it('calls onClick when card is clicked', () => {
    const handleClick = vi.fn()
    render(<StoryCard story={mockStory} onClick={handleClick} />)

    fireEvent.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledWith(mockStory)
  })

  it('calls onClick when Enter key is pressed', () => {
    const handleClick = vi.fn()
    render(<StoryCard story={mockStory} onClick={handleClick} />)

    fireEvent.keyDown(screen.getByRole('button'), { key: 'Enter' })

    expect(handleClick).toHaveBeenCalledWith(mockStory)
  })

  it('displays play count', () => {
    render(<StoryCard story={mockStory} />)

    expect(screen.getByLabelText(/played 5 times/i)).toBeInTheDocument()
  })

  it('displays scene count when available', () => {
    render(<StoryCard story={mockStory} />)

    expect(screen.getByLabelText(/10 scenes/i)).toBeInTheDocument()
  })

  it('handles missing description gracefully', () => {
    const storyWithoutDescription = { ...mockStory, description: null }
    render(<StoryCard story={storyWithoutDescription} />)

    expect(screen.queryByText('A spooky test story')).not.toBeInTheDocument()
  })
})
