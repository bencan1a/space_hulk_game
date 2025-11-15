/**
 * Story context for managing story state across the application.
 */
import React, { createContext, useContext, useState, useCallback } from 'react'
import { storyApi } from '../services/storyApi'
import type { Story, StoryListResponse, StoryFilters } from '../types/story'

interface StoryContextState {
  // State
  stories: Story[]
  loading: boolean
  error: string | null
  filters: StoryFilters
  pagination: {
    page: number
    pageSize: number
    total: number
    totalPages: number
  }

  // Actions
  fetchStories: () => Promise<void>
  setFilters: (filters: StoryFilters) => void
  setPage: (page: number) => void
  refreshStories: () => Promise<void>
}

const StoryContext = createContext<StoryContextState | undefined>(undefined)

interface StoryProviderProps {
  children: React.ReactNode
}

export const StoryProvider: React.FC<StoryProviderProps> = ({ children }) => {
  const [stories, setStories] = useState<Story[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFiltersState] = useState<StoryFilters>({})
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0,
  })

  const fetchStories = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const response: StoryListResponse = await storyApi.getStories(
        pagination.page,
        pagination.pageSize,
        filters
      )

      setStories(response.items)
      setPagination({
        page: response.page,
        pageSize: response.page_size,
        total: response.total,
        totalPages: response.total_pages,
      })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch stories'
      setError(errorMessage)
      console.error('Error fetching stories:', err)
    } finally {
      setLoading(false)
    }
  }, [pagination.page, pagination.pageSize, filters])

  const setFilters = useCallback((newFilters: StoryFilters) => {
    setFiltersState(newFilters)
    setPagination((prev) => ({ ...prev, page: 1 })) // Reset to page 1 on filter change
  }, [])

  const setPage = useCallback((page: number) => {
    setPagination((prev) => ({ ...prev, page }))
  }, [])

  const refreshStories = useCallback(async () => {
    await fetchStories()
  }, [fetchStories])

  const value: StoryContextState = {
    stories,
    loading,
    error,
    filters,
    pagination,
    fetchStories,
    setFilters,
    setPage,
    refreshStories,
  }

  return <StoryContext.Provider value={value}>{children}</StoryContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export const useStoryContext = (): StoryContextState => {
  const context = useContext(StoryContext)
  if (!context) {
    throw new Error('useStoryContext must be used within StoryProvider')
  }
  return context
}
