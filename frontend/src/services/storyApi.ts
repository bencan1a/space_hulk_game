/**
 * Story API service methods.
 */
import { apiClient } from './apiClient'
import type { Story, StoryListResponse, StoryFilters } from '../types/story'

export const storyApi = {
  /**
   * Get paginated list of stories with optional filters.
   */
  async getStories(
    page: number = 1,
    pageSize: number = 20,
    filters?: StoryFilters
  ): Promise<StoryListResponse> {
    const params: Record<string, string | number> = {
      page,
      page_size: pageSize,
    }

    if (filters?.search) {
      params.search = filters.search
    }

    if (filters?.theme_id) {
      params.theme_id = filters.theme_id
    }

    if (filters?.tags && filters.tags.length > 0) {
      params.tags = filters.tags.join(',')
    }

    return apiClient.get<StoryListResponse>('/api/v1/stories', params)
  },

  /**
   * Get single story by ID.
   */
  async getStory(storyId: number): Promise<Story> {
    return apiClient.get<Story>(`/api/v1/stories/${storyId}`)
  },

  /**
   * Get story game content (game.json).
   */
  async getStoryContent(storyId: number): Promise<Record<string, unknown>> {
    return apiClient.get<Record<string, unknown>>(`/api/v1/stories/${storyId}/content`)
  },

  /**
   * Delete story by ID.
   */
  async deleteStory(storyId: number): Promise<void> {
    return apiClient.delete<void>(`/api/v1/stories/${storyId}`)
  },
}
