/**
 * Hook for fetching a single story by ID.
 */
import { useState, useEffect, useCallback } from 'react'
import { storyApi } from '../services/storyApi'
import type { Story } from '../types/story'

interface UseStoryResult {
  story: Story | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export const useStory = (storyId: number | null): UseStoryResult => {
  const [story, setStory] = useState<Story | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStory = useCallback(async () => {
    if (!storyId) {
      setStory(null)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const data = await storyApi.getStory(storyId)
      setStory(data)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch story'
      setError(errorMessage)
      if (import.meta.env.DEV) {
        console.error('Error fetching story:', err)
      }
    } finally {
      setLoading(false)
    }
  }, [storyId])

  useEffect(() => {
    fetchStory()
  }, [fetchStory])

  return {
    story,
    loading,
    error,
    refetch: fetchStory,
  }
}
