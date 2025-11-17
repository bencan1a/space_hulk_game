import type { Meta, StoryObj } from '@storybook/react'
import { StoryPreview } from './StoryPreview'
import { Story as StoryType } from '../../types/story'

const meta: Meta<typeof StoryPreview> = {
  title: 'Generation/StoryPreview',
  component: StoryPreview,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    onPlayNow: { action: 'play-now-clicked' },
    onGiveFeedback: { action: 'give-feedback-clicked' },
  },
}

export default meta
type Story = StoryObj<typeof StoryPreview>

// Mock story data
const mockStoryData: StoryType = {
  id: 1,
  title: 'The Derelict Hulk',
  description: 'A tense exploration of an abandoned space hulk filled with danger and mystery. Navigate through dark corridors, discover ancient technology, and survive encounters with hostile entities.',
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

// Story: Default
export const Default: Story = {
  args: {
    story: mockStoryData,
  },
}

// Story: With Minimal Data
export const MinimalData: Story = {
  args: {
    story: {
      id: 2,
      title: 'Simple Adventure',
      description: null,
      theme_id: 'generic',
      tags: [],
      game_file_path: '/data/stories/002/game.json',
      created_at: '2024-01-20T14:00:00Z',
      updated_at: '2024-01-20T14:00:00Z',
      play_count: 0,
      last_played: null,
      prompt: 'A simple adventure',
      template_id: null,
      iteration_count: 0,
      scene_count: null,
      item_count: null,
      npc_count: null,
      puzzle_count: null,
    },
  },
}

// Story: No Iterations
export const NoIterations: Story = {
  args: {
    story: {
      ...mockStoryData,
      iteration_count: 0,
    },
  },
}

// Story: With Many Tags
export const ManyTags: Story = {
  args: {
    story: {
      ...mockStoryData,
      tags: ['horror', 'exploration', 'combat', 'puzzle', 'stealth', 'strategy', 'survival'],
    },
  },
}

// Story: Large Numbers
export const LargeStatistics: Story = {
  args: {
    story: {
      ...mockStoryData,
      scene_count: 150,
      item_count: 234,
      npc_count: 89,
      puzzle_count: 52,
    },
  },
}

// Story: Zero Statistics
export const ZeroStatistics: Story = {
  args: {
    story: {
      ...mockStoryData,
      scene_count: 0,
      item_count: 0,
      npc_count: 0,
      puzzle_count: 0,
    },
  },
}

// Story: Cyberpunk Theme
export const CyberpunkTheme: Story = {
  args: {
    story: {
      id: 3,
      title: 'Neon Shadows',
      description: 'In a dystopian megacity, hack your way through corporate defenses and uncover a conspiracy that threatens the entire grid.',
      theme_id: 'cyberpunk',
      tags: ['hacking', 'stealth', 'investigation'],
      game_file_path: '/data/stories/003/game.json',
      created_at: '2024-02-01T09:00:00Z',
      updated_at: '2024-02-01T09:00:00Z',
      play_count: 5,
      last_played: '2024-02-10T18:30:00Z',
      prompt: 'Generate a cyberpunk hacking adventure',
      template_id: 'cyberpunk',
      iteration_count: 1,
      scene_count: 12,
      item_count: 18,
      npc_count: 15,
      puzzle_count: 8,
    },
  },
}

// Story: Long Title and Description
export const LongContent: Story = {
  args: {
    story: {
      ...mockStoryData,
      title: 'The Chronicles of the Forgotten Space Hulk: A Journey Through Darkness and Despair',
      description: 'A comprehensive and detailed exploration of an abandoned space hulk that has been drifting through the void for millennia. Navigate through countless dark corridors, discover ancient technology from a bygone era, uncover the mysteries of what happened to the original crew, and survive encounters with hostile entities that have made the hulk their home. This is a long and complex adventure that will test your skills, patience, and courage as you delve deeper into the unknown reaches of space.',
    },
  },
}
