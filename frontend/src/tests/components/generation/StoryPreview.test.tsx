import { render, screen, fireEvent } from '@testing-library/react'
import { StoryPreview } from '../../../components/generation/StoryPreview'
import { Story } from '../../../types/story'
import { describe, it, expect, vi } from 'vitest'

const mockStory: Story = {
  id: 1,
  title: 'The Derelict Hulk',
  description: 'A tense exploration of an abandoned space hulk filled with danger',
  theme_id: 'warhammer40k',
  tags: ['horror', 'exploration', 'combat'],
  game_file_path: '/data/stories/001/game.json',
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:30:00Z',
  play_count: 0,
  last_played: null,
  prompt: 'Generate a horror story set in an abandoned space hulk',
  template_id: 'horror',
  iteration_count: 2,
  scene_count: 15,
  item_count: 23,
  npc_count: 8,
  puzzle_count: 5,
}

describe('StoryPreview', () => {
  it('renders story title and description', () => {
    render(<StoryPreview story={mockStory} />)

    expect(screen.getByText('The Derelict Hulk')).toBeInTheDocument()
    expect(
      screen.getByText('A tense exploration of an abandoned space hulk filled with danger')
    ).toBeInTheDocument()
  })

  it('displays theme metadata', () => {
    render(<StoryPreview story={mockStory} />)

    expect(screen.getByText('Theme:')).toBeInTheDocument()
    expect(screen.getByText('warhammer40k')).toBeInTheDocument()
  })

  it('displays all tags', () => {
    render(<StoryPreview story={mockStory} />)

    expect(screen.getByText('horror')).toBeInTheDocument()
    expect(screen.getByText('exploration')).toBeInTheDocument()
    expect(screen.getByText('combat')).toBeInTheDocument()
  })

  it('displays creation date formatted correctly', () => {
    render(<StoryPreview story={mockStory} />)

    expect(screen.getByText('Created:')).toBeInTheDocument()
    // Date formatting may vary by locale, so just check it's there
    expect(screen.getByText(/1\/15\/2024|15\/1\/2024/)).toBeInTheDocument()
  })

  it('displays iteration count when greater than 0', () => {
    render(<StoryPreview story={mockStory} />)

    expect(screen.getByText('Iterations:')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('does not display iteration count when 0', () => {
    const storyWithNoIterations = { ...mockStory, iteration_count: 0 }
    render(<StoryPreview story={storyWithNoIterations} />)

    expect(screen.queryByText('Iterations:')).not.toBeInTheDocument()
  })

  it('displays all statistics when available', () => {
    render(<StoryPreview story={mockStory} />)

    expect(screen.getByText('Scenes')).toBeInTheDocument()
    expect(screen.getByText('15')).toBeInTheDocument()

    expect(screen.getByText('Items')).toBeInTheDocument()
    expect(screen.getByText('23')).toBeInTheDocument()

    expect(screen.getByText('NPCs')).toBeInTheDocument()
    expect(screen.getByText('8')).toBeInTheDocument()

    expect(screen.getByText('Puzzles')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
  })

  it('does not display statistics when null', () => {
    const storyWithoutStats = {
      ...mockStory,
      scene_count: null,
      item_count: null,
      npc_count: null,
      puzzle_count: null,
    }
    render(<StoryPreview story={storyWithoutStats} />)

    expect(screen.queryByText('Scenes')).not.toBeInTheDocument()
    expect(screen.queryByText('Items')).not.toBeInTheDocument()
    expect(screen.queryByText('NPCs')).not.toBeInTheDocument()
    expect(screen.queryByText('Puzzles')).not.toBeInTheDocument()
  })

  it('displays statistic with value of 0', () => {
    const storyWithZeroStat = {
      ...mockStory,
      puzzle_count: 0,
    }
    render(<StoryPreview story={storyWithZeroStat} />)

    expect(screen.getByText('Puzzles')).toBeInTheDocument()
    expect(screen.getByText('0')).toBeInTheDocument()
  })

  it('renders Play Now button', () => {
    render(<StoryPreview story={mockStory} />)

    const playButton = screen.getByRole('button', { name: /play this story now/i })
    expect(playButton).toBeInTheDocument()
    expect(playButton).toHaveTextContent('Play Now')
  })

  it('renders Give Feedback button', () => {
    render(<StoryPreview story={mockStory} />)

    const feedbackButton = screen.getByRole('button', { name: /give feedback on this story/i })
    expect(feedbackButton).toBeInTheDocument()
    expect(feedbackButton).toHaveTextContent('Give Feedback')
  })

  it('calls onPlayNow when Play Now button is clicked', () => {
    const handlePlayNow = vi.fn()
    render(<StoryPreview story={mockStory} onPlayNow={handlePlayNow} />)

    const playButton = screen.getByRole('button', { name: /play this story now/i })
    fireEvent.click(playButton)

    expect(handlePlayNow).toHaveBeenCalledTimes(1)
  })

  it('calls onGiveFeedback when Give Feedback button is clicked', () => {
    const handleGiveFeedback = vi.fn()
    render(<StoryPreview story={mockStory} onGiveFeedback={handleGiveFeedback} />)

    const feedbackButton = screen.getByRole('button', { name: /give feedback on this story/i })
    fireEvent.click(feedbackButton)

    expect(handleGiveFeedback).toHaveBeenCalledTimes(1)
  })

  it('handles story without description', () => {
    const storyWithoutDescription = { ...mockStory, description: null }
    render(<StoryPreview story={storyWithoutDescription} />)

    expect(screen.getByText('The Derelict Hulk')).toBeInTheDocument()
    expect(
      screen.queryByText('A tense exploration of an abandoned space hulk filled with danger')
    ).not.toBeInTheDocument()
  })

  it('handles story without tags', () => {
    const storyWithoutTags = { ...mockStory, tags: [] }
    render(<StoryPreview story={storyWithoutTags} />)

    expect(screen.queryByText('Tags:')).not.toBeInTheDocument()
  })

  it('displays statistics icons', () => {
    render(<StoryPreview story={mockStory} />)

    // Check that emoji icons are rendered (they're part of the component)
    expect(screen.getByText('🎬')).toBeInTheDocument() // Scenes
    expect(screen.getByText('🎒')).toBeInTheDocument() // Items
    expect(screen.getByText('👤')).toBeInTheDocument() // NPCs
    expect(screen.getByText('🧩')).toBeInTheDocument() // Puzzles
  })

  it('renders with minimal story data', () => {
    const minimalStory: Story = {
      id: 2,
      title: 'Minimal Story',
      description: null,
      theme_id: 'generic',
      tags: [],
      game_file_path: '/data/stories/002/game.json',
      created_at: '2024-01-15T10:30:00Z',
      updated_at: '2024-01-15T10:30:00Z',
      play_count: 0,
      last_played: null,
      prompt: 'Test prompt',
      template_id: null,
      iteration_count: 0,
      scene_count: null,
      item_count: null,
      npc_count: null,
      puzzle_count: null,
    }
    render(<StoryPreview story={minimalStory} />)

    expect(screen.getByText('Minimal Story')).toBeInTheDocument()
    expect(screen.getByText('generic')).toBeInTheDocument()
  })
})
