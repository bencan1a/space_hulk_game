/**
 * Story-related TypeScript interfaces.
 */

export interface Story {
  id: number
  title: string
  description: string | null
  theme_id: string
  tags: string[]
  game_file_path: string
  created_at: string
  updated_at: string
  play_count: number
  last_played: string | null
  prompt: string
  template_id: string | null
  iteration_count: number
  scene_count: number | null
  item_count: number | null
  npc_count: number | null
  puzzle_count: number | null
}

export interface StoryListResponse {
  items: Story[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface StoryFilters {
  search?: string
  theme_id?: string
  tags?: string[]
}
