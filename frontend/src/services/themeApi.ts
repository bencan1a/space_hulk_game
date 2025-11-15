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
    const response = await apiClient.getThemes()
    return response.map((theme) => ({
      id: theme.id,
      name: theme.name,
      description: theme.description,
    }))
  },

  /**
   * Get complete theme configuration.
   */
  async getTheme(themeId: string): Promise<Theme> {
    const response = await apiClient.getTheme(themeId)
    // Map the API response to our full Theme type
    return {
      id: response.id,
      name: response.name,
      description: response.description,
      colors: response.colors as Theme['colors'],
      typography: {
        fontFamily: response.fonts?.primary || 'Georgia, serif',
        fontFamilyMono: response.fonts?.mono || 'Courier New, monospace',
        fontSize: {
          xs: '0.75rem',
          sm: '0.875rem',
          base: '1rem',
          lg: '1.125rem',
          xl: '1.25rem',
          xxl: '1.5rem',
        },
      },
      terminology: {
        story: 'Story',
        stories: 'Stories',
        character: 'Character',
        characters: 'Characters',
        enemy: 'Enemy',
        enemies: 'Enemies',
        item: 'Item',
        items: 'Items',
        location: 'Location',
        locations: 'Locations',
      },
      ui: {
        welcome: 'Welcome',
        createStory: 'Create Story',
        libraryTitle: 'Story Library',
        playButton: 'Play',
      },
      assets: {
        logo: '',
        background: '',
        icon: '',
      },
    }
  },

  /**
   * Get theme asset URL.
   */
  getAssetUrl(themeId: string, assetPath: string): string {
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    return `${baseURL}/api/v1/themes/${themeId}/assets/${assetPath}`
  },
}
