/**
 * Theme API service methods.
 */
import apiClient from './api'
import type { Theme, ThemeMetadata } from '../types/theme'

export const themeApi = {
  /**
   * Get list of available themes.
   */
  async getThemes(): Promise<ThemeMetadata[]> {
    return await apiClient.getThemes()
  },

  /**
   * Get complete theme configuration.
   */
  async getTheme(themeId: string): Promise<Theme> {
    // The backend returns data with this structure directly
    const response = await apiClient.getTheme(themeId)
    return response as unknown as Theme
  },

  /**
   * Get theme asset URL.
   */
  getAssetUrl(themeId: string, assetPath: string): string {
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    return `${baseURL}/api/v1/themes/${themeId}/assets/${assetPath}`
  },
}
