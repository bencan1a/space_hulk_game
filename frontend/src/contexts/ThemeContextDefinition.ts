/**
 * Theme context definition.
 */
import { createContext } from 'react'
import type { Theme, ThemeMetadata } from '../types/theme'

export interface ThemeContextState {
  currentTheme: Theme | null
  availableThemes: ThemeMetadata[]
  loading: boolean
  error: string | null
  setTheme: (themeId: string) => Promise<void>
}

export const ThemeContext = createContext<ThemeContextState | undefined>(undefined)
