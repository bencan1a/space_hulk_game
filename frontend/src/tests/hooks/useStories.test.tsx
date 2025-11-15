import React from 'react'
import { renderHook, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useStories } from '../../hooks/useStories'
import { StoryProvider } from '../../contexts/StoryContext'
import { storyApi } from '../../services/storyApi'
import type { StoryListResponse } from '../../types/story'

vi.mock('../../services/storyApi')

describe('useStories', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <StoryProvider>{children}</StoryProvider>
  )

  it('auto-fetches stories on mount', async () => {
    const mockStories = {
      items: [
        { id: 1, title: 'Story 1' },
        { id: 2, title: 'Story 2' },
      ],
      total: 2,
      page: 1,
      page_size: 20,
      total_pages: 1,
    }

    vi.mocked(storyApi.getStories).mockResolvedValue(mockStories as StoryListResponse)

    const { result } = renderHook(() => useStories(), { wrapper })

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.stories).toHaveLength(2)
    expect(result.current.error).toBe(null)
  })

  it('provides pagination state', async () => {
    const mockStories = {
      items: [],
      total: 100,
      page: 1,
      page_size: 20,
      total_pages: 5,
    }

    vi.mocked(storyApi.getStories).mockResolvedValue(mockStories as StoryListResponse)

    const { result } = renderHook(() => useStories(), { wrapper })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.pagination).toEqual({
      page: 1,
      pageSize: 20,
      total: 100,
      totalPages: 5,
    })
  })

  it('handles API errors', async () => {
    vi.mocked(storyApi.getStories).mockRejectedValue(new Error('Failed to fetch'))

    const { result } = renderHook(() => useStories(), { wrapper })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBe('Failed to fetch')
    expect(result.current.stories).toHaveLength(0)
  })
})
