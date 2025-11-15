import { renderHook, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useStory } from '../../hooks/useStory'
import { storyApi } from '../../services/storyApi'
import type { Story } from '../../types/story'

vi.mock('../../services/storyApi')

describe('useStory', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches story on mount', async () => {
    const mockStory = {
      id: 1,
      title: 'Test Story',
      description: 'Test description',
    }

    vi.mocked(storyApi.getStory).mockResolvedValue(mockStory as Story)

    const { result } = renderHook(() => useStory(1))

    expect(result.current.loading).toBe(true)
    expect(result.current.story).toBe(null)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.story).toEqual(mockStory)
    expect(result.current.error).toBe(null)
  })

  it('handles null storyId', () => {
    const { result } = renderHook(() => useStory(null))

    expect(result.current.story).toBe(null)
    expect(result.current.loading).toBe(false)
    expect(storyApi.getStory).not.toHaveBeenCalled()
  })

  it('handles fetch errors', async () => {
    vi.mocked(storyApi.getStory).mockRejectedValue(new Error('Story not found'))

    const { result } = renderHook(() => useStory(1))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.story).toBe(null)
    expect(result.current.error).toBe('Story not found')
  })
})
