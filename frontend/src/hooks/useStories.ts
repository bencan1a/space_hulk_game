/**
 * Hook for fetching and managing stories list.
 */
import { useEffect } from 'react'
import { useStoryContext } from '../contexts/StoryContext'

export const useStories = () => {
  const context = useStoryContext()
  const { fetchStories } = context

  // Auto-fetch on mount and when filters/page change
  useEffect(() => {
    fetchStories()
  }, [fetchStories])

  return context
}
