// Common types
export interface ApiResponse<T> {
  data: T
  meta?: {
    timestamp: string
    version: string
  }
}

export interface ApiError {
  code: string
  message: string
  user_message: string
  retry_possible: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_next: boolean
}

// Story types
export interface Story {
  id: number
  title: string
  description: string | null
  theme_id: string
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
  tags: string[]
}

export interface CreateStoryRequest {
  prompt: string
  template_id?: string
  theme_id?: string
}

export interface IterationRequest {
  story_id: number
  feedback: string
  changes_requested?: Record<string, unknown>
}

// Generation types
export interface GenerationSession {
  id: string
  story_id: number | null
  status: 'creating' | 'iterating' | 'complete' | 'error'
  current_step: string | null
  progress_percent: number
  created_at: string
  completed_at: string | null
  error_message: string | null
}

// Game types
export interface GameSession {
  session_id: string
  story_id: number
  current_scene: string
  inventory: string[]
  game_over: boolean
}

export interface GameCommand {
  command: string
}

export interface GameResponse {
  output: string
  state: Record<string, unknown>
  valid: boolean
  game_over: boolean
}

// Theme types
export interface Theme {
  id: string
  name: string
  description: string
  colors: Record<string, string>
  fonts: Record<string, string>
}
