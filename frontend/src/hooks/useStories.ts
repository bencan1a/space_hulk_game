/**
 * Hook for fetching and managing stories list.
 */
import { useEffect } from 'react'
import { useStoryContext } from '../contexts/StoryContext'

export const useStories = () => {
  const context = useStoryContext()

  // Auto-fetch on mount and when filters/page change
  useEffect(() => {
    context.fetchStories()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [context.filters, context.pagination.page])

  return context
}
