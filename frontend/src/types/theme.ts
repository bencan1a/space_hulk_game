/**
 * Theme-related TypeScript interfaces.
 */

export interface ThemeColors {
  primary: string
  secondary: string
  background: string
  surface: string
  text: string
  textSecondary: string
  accent: string
  error: string
  success: string
  warning: string
  [key: string]: string
}

export interface ThemeTypography {
  fontFamily: string
  fontFamilyMono: string
  fontSize: {
    xs: string
    sm: string
    base: string
    lg: string
    xl: string
    xxl: string
  }
}

export interface ThemeTerminology {
  story: string
  stories: string
  character: string
  characters: string
  enemy: string
  enemies: string
  item: string
  items: string
  location: string
  locations: string
  [key: string]: string
}

export interface ThemeUI {
  welcome: string
  createStory: string
  libraryTitle: string
  playButton: string
  [key: string]: string
}

export interface ThemeAssets {
  logo: string
  background: string
  icon: string
  [key: string]: string
}

export interface Theme {
  id: string
  name: string
  description: string
  colors: ThemeColors
  typography: ThemeTypography
  terminology: ThemeTerminology
  ui: ThemeUI
  assets: ThemeAssets
}

export interface ThemeMetadata {
  id: string
  name: string
  description: string
}
