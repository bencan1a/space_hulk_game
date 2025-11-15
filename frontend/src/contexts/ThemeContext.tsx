/**
 * Theme context for managing visual theme across the application.
 */
import React, { useState, useEffect, useCallback } from 'react'
import { themeApi } from '../services/themeApi'
import type { Theme, ThemeMetadata } from '../types/theme'
import { ThemeContext } from './ThemeContextDefinition'

const THEME_STORAGE_KEY = 'selectedThemeId'
const DEFAULT_THEME_ID = 'warhammer40k'

interface ThemeProviderProps {
  children: React.ReactNode
}

/**
 * ThemeProvider component that manages theme state and provides theme context to child components.
 *
 * Automatically loads available themes on mount and applies the saved theme from localStorage,
 * or defaults to 'warhammer40k' if no preference is saved.
 *
 * @param props.children - Child components that will have access to the theme context
 */
export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState<Theme | null>(null)
  const [availableThemes, setAvailableThemes] = useState<ThemeMetadata[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  /**
   * Apply theme CSS variables to document root.
   */
  const applyCSSVariables = useCallback((theme: Theme) => {
    const root = document.documentElement

    // Apply color variables
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value)
    })

    // Apply typography variables
    root.style.setProperty('--font-family', theme.typography.fontFamily)
    root.style.setProperty('--font-family-mono', theme.typography.fontFamilyMono)

    Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
      root.style.setProperty(`--font-size-${key}`, value)
    })

    // Update document title terminology
    document.title = `Space Hulk Game - ${theme.name}`
  }, [])

  /**
   * Load and apply a theme.
   */
  const loadTheme = useCallback(
    async (themeId: string) => {
      try {
        const theme = await themeApi.getTheme(themeId)
        setCurrentTheme(theme)
        applyCSSVariables(theme)
        localStorage.setItem(THEME_STORAGE_KEY, themeId)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load theme'
        setError(errorMessage)
        console.error('Error loading theme:', err)
      }
    },
    [applyCSSVariables]
  )

  /**
   * Change the current theme.
   */
  const setTheme = useCallback(
    async (themeId: string) => {
      if (loading) return // Prevent concurrent changes
      setLoading(true)
      setError(null)
      await loadTheme(themeId)
      setLoading(false)
    },
    [loadTheme, loading]
  )

  /**
   * Initialize theme system on mount.
   */
  useEffect(() => {
    const initializeThemes = async () => {
      setLoading(true)
      setError(null)

      try {
        // Load available themes list
        const themes = await themeApi.getThemes()
        setAvailableThemes(themes)

        // Determine which theme to load
        const savedThemeId = localStorage.getItem(THEME_STORAGE_KEY)
        const themeToLoad = savedThemeId || DEFAULT_THEME_ID

        // Verify theme exists
        const themeExists = themes.some((t) => t.id === themeToLoad)
        const finalThemeId = themeExists ? themeToLoad : DEFAULT_THEME_ID

        // Load the theme
        await loadTheme(finalThemeId)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to initialize themes'
        setError(errorMessage)
        console.error('Error initializing themes:', err)
      } finally {
        setLoading(false)
      }
    }

    initializeThemes()
  }, [loadTheme])

  const value = {
    currentTheme,
    availableThemes,
    loading,
    error,
    setTheme,
  }

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
