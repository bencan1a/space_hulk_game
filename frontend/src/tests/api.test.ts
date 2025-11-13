import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios, { AxiosInstance } from 'axios'
import type { PaginatedResponse, Story, ApiResponse } from '../services/types'

// Mock axios before any imports
vi.mock('axios')

describe('API Client', () => {
  let mockAxiosInstance: {
    get: ReturnType<typeof vi.fn>
    post: ReturnType<typeof vi.fn>
    delete: ReturnType<typeof vi.fn>
    request: ReturnType<typeof vi.fn>
    interceptors: {
      request: { use: ReturnType<typeof vi.fn> }
      response: { use: ReturnType<typeof vi.fn> }
    }
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let ApiClient: any

  beforeEach(async () => {
    vi.clearAllMocks()

    // Create a mock axios instance
    mockAxiosInstance = {
      get: vi.fn(),
      post: vi.fn(),
      delete: vi.fn(),
      request: vi.fn(),
      interceptors: {
        request: {
          use: vi.fn(() => {
            // Store the interceptor for later use if needed
            return 0
          }),
        },
        response: {
          use: vi.fn(() => {
            // Store the interceptor for later use if needed
            return 0
          }),
        },
      },
    }

    // Mock axios.create to return our mock instance
    vi.mocked(axios.create).mockReturnValue(mockAxiosInstance as unknown as AxiosInstance)

    // Dynamically import the API client after setting up mocks
    const apiModule = await import('../services/api')
    // Create a new instance of the ApiClient class
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const ClientClass = (apiModule.default as any).constructor
    ApiClient = new ClientClass()
  })

  afterEach(() => {
    vi.resetModules()
  })

  it('should fetch stories successfully', async () => {
    const mockStories: PaginatedResponse<Story> = {
      items: [
        {
          id: 1,
          title: 'Test Story',
          description: 'Test',
          theme_id: 'warhammer40k',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          play_count: 0,
          last_played: null,
          prompt: 'Test prompt',
          template_id: null,
          iteration_count: 1,
          scene_count: 5,
          item_count: 3,
          npc_count: 2,
          puzzle_count: 1,
          tags: ['test'],
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
      has_next: false,
    }

    const mockResponse: ApiResponse<PaginatedResponse<Story>> = {
      data: mockStories,
    }

    mockAxiosInstance.get.mockResolvedValueOnce({
      data: mockResponse,
    })

    const stories = await ApiClient.getStories()
    expect(stories).toEqual(mockStories)
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/v1/stories', { params: undefined })
  })

  it('should handle network errors', async () => {
    const networkError = {
      request: {},
      message: 'Network Error',
      isAxiosError: true,
    }

    // Mock the response interceptor to throw the error
    mockAxiosInstance.get.mockRejectedValueOnce(networkError)

    await expect(ApiClient.getStories()).rejects.toThrow()
  })

  it('should handle 404 errors', async () => {
    const notFoundError = {
      response: {
        status: 404,
        data: {},
      },
      message: 'Not Found',
      isAxiosError: true,
    }

    mockAxiosInstance.get.mockRejectedValueOnce(notFoundError)

    await expect(ApiClient.getStory(999)).rejects.toThrow()
  })
})
