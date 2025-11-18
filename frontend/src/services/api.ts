import axios, { AxiosInstance, AxiosError } from 'axios'
import { retryRequest } from '../utils/retryLogic'
import { handleApiError } from '../utils/errorHandler'
import type {
  ApiResponse,
  PaginatedResponse,
  Story,
  CreateStoryRequest,
  GenerationSession,
  GenerationStatus,
  GameSession,
  GameCommand,
  GameResponse,
} from './types'
import type { Theme, ThemeMetadata } from '../types/theme'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add timestamp to requests
        config.headers['X-Request-Time'] = new Date().toISOString()

        // Add any auth tokens here in future
        // const token = localStorage.getItem('auth_token')
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`
        // }

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Log successful responses in dev mode
        if (import.meta.env.DEV) {
          console.log(
            `API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`,
            response.data
          )
        }
        return response
      },
      async (error: AxiosError) => {
        // Handle errors
        if (error.response) {
          // Server responded with error status
          if (import.meta.env.DEV) {
            console.error('API Error Response:', error.response.status, error.response.data)
          }
        } else if (error.request) {
          // Request made but no response received
          if (import.meta.env.DEV) {
            console.error('API No Response:', error.request)
          }
        } else {
          // Error in request setup
          if (import.meta.env.DEV) {
            console.error('API Request Error:', error.message)
          }
        }

        // Retry logic for specific errors
        if (this.shouldRetry(error)) {
          if (!error.config) return Promise.reject(handleApiError(error))
          return retryRequest(this.client, error.config, 3)
        }

        throw handleApiError(error)
      }
    )
  }

  private shouldRetry(error: AxiosError): boolean {
    // Retry on network errors or 503 Service Unavailable
    if (!error.response) return true
    if (error.response.status === 503) return true
    return false
  }

  // Story endpoints
  async getStories(params?: {
    page?: number
    page_size?: number
    search?: string
    theme_id?: string
    tags?: string[]
  }): Promise<PaginatedResponse<Story>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<Story>>>(
      '/api/v1/stories',
      { params }
    )
    return response.data.data
  }

  async getStory(id: number): Promise<Story> {
    const response = await this.client.get<ApiResponse<Story>>(`/api/v1/stories/${id}`)
    return response.data.data
  }

  async createStory(data: CreateStoryRequest): Promise<GenerationSession> {
    const response = await this.client.post<GenerationSession>('/api/v1/generate', data)
    return response.data
  }

  async deleteStory(id: number): Promise<void> {
    await this.client.delete(`/api/v1/stories/${id}`)
  }

  // Generation endpoints
  async getGenerationStatus(sessionId: string): Promise<GenerationStatus> {
    const response = await this.client.get<GenerationStatus>(`/api/v1/generate/${sessionId}`)
    return response.data
  }

  // Game endpoints
  async startGame(storyId: number): Promise<GameSession> {
    const response = await this.client.post<ApiResponse<GameSession>>(
      `/api/v1/game/${storyId}/start`
    )
    return response.data.data
  }

  async sendCommand(sessionId: string, command: GameCommand): Promise<GameResponse> {
    const response = await this.client.post<ApiResponse<GameResponse>>(
      `/api/v1/game/${sessionId}/command`,
      command
    )
    return response.data.data
  }

  async saveGame(sessionId: string, saveName: string): Promise<{ save_id: string }> {
    const response = await this.client.post<ApiResponse<{ save_id: string }>>(
      `/api/v1/game/${sessionId}/save`,
      { name: saveName }
    )
    return response.data.data
  }

  // Theme endpoints
  async getThemes(): Promise<ThemeMetadata[]> {
    const response = await this.client.get<ApiResponse<ThemeMetadata[]>>('/api/v1/themes')
    return response.data.data
  }

  async getTheme(themeId: string): Promise<Theme> {
    const response = await this.client.get<ApiResponse<Theme>>(`/api/v1/themes/${themeId}`)
    return response.data.data
  }

  // Template endpoints
  async getTemplates(): Promise<import('./types').TemplateListResponse> {
    const response =
      await this.client.get<import('./types').TemplateListResponse>('/api/v1/templates')
    return response.data
  }

  async getTemplate(name: string): Promise<import('./types').TemplateDetail> {
    const response = await this.client.get<import('./types').TemplateDetail>(
      `/api/v1/templates/${name}`
    )
    return response.data
  }
}

export const apiClient = new ApiClient()
export default apiClient
