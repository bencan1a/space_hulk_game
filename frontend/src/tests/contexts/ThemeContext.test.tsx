import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { ThemeProvider } from '../../contexts/ThemeContext'
import { useTheme } from '../../contexts/useTheme'
import { themeApi } from '../../services/themeApi'
import type { Theme } from '../../types/theme'
import { vi } from 'vitest'

vi.mock('../../services/themeApi')

const TestComponent = () => {
  const { currentTheme, availableThemes, setTheme, loading } = useTheme()

  return (
    <div>
      <div data-testid="loading">{loading ? 'Loading' : 'Loaded'}</div>
      <div data-testid="current-theme">{currentTheme?.name || 'None'}</div>
      <div data-testid="theme-count">{availableThemes.length}</div>
      <button onClick={() => setTheme('cyberpunk')}>Change Theme</button>
    </div>
  )
}

describe('ThemeContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('loads default theme on mount', async () => {
    const mockThemes = [
      { id: 'warhammer40k', name: 'Warhammer 40K', description: 'Grimdark' },
      { id: 'cyberpunk', name: 'Cyberpunk', description: 'High-tech' },
    ]

    const mockTheme: Theme = {
      id: 'warhammer40k',
      name: 'Warhammer 40,000',
      description: 'Grimdark',
      colors: { 
        primary: '#8B0000',
        secondary: '#C0C0C0',
        background: '#1A1A1A',
        surface: '#2D2D2D',
        text: '#E0E0E0',
        textSecondary: '#A0A0A0',
        accent: '#FFD700',
        error: '#FF4444',
        success: '#44FF44',
        warning: '#FFAA00',
      },
      typography: { 
        fontFamily: 'Cinzel', 
        fontFamilyMono: 'Mono', 
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
        story: 'Mission',
        stories: 'Missions',
        character: 'Space Marine',
        characters: 'Space Marines',
        enemy: 'Xenos',
        enemies: 'Xenos',
        item: 'Wargear',
        items: 'Wargear',
        location: 'Deck',
        locations: 'Decks',
      },
      ui: {
        welcome: 'Welcome to the Space Hulk',
        createStory: 'Generate Mission',
        libraryTitle: 'Mission Archives',
        playButton: 'Deploy',
      },
      assets: {
        logo: '',
        background: '',
        icon: '',
      },
    }

    vi.mocked(themeApi.getThemes).mockResolvedValue(mockThemes)
    vi.mocked(themeApi.getTheme).mockResolvedValue(mockTheme)

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Loaded')
    })

    expect(screen.getByTestId('current-theme')).toHaveTextContent('Warhammer 40,000')
    expect(screen.getByTestId('theme-count')).toHaveTextContent('2')
  })

  it('persists theme selection to localStorage', async () => {
    const mockThemes = [
      { id: 'warhammer40k', name: 'Warhammer 40K', description: 'Grimdark' },
      { id: 'cyberpunk', name: 'Cyberpunk', description: 'High-tech' },
    ]

    const mockWarhammerTheme: Theme = {
      id: 'warhammer40k',
      name: 'Warhammer 40,000',
      description: 'Grimdark',
      colors: {
        primary: '#8B0000',
        secondary: '#C0C0C0',
        background: '#1A1A1A',
        surface: '#2D2D2D',
        text: '#E0E0E0',
        textSecondary: '#A0A0A0',
        accent: '#FFD700',
        error: '#FF4444',
        success: '#44FF44',
        warning: '#FFAA00',
      },
      typography: { 
        fontFamily: 'Cinzel', 
        fontFamilyMono: 'Mono', 
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
        story: 'Mission',
        stories: 'Missions',
        character: 'Space Marine',
        characters: 'Space Marines',
        enemy: 'Xenos',
        enemies: 'Xenos',
        item: 'Wargear',
        items: 'Wargear',
        location: 'Deck',
        locations: 'Decks',
      },
      ui: {
        welcome: 'Welcome',
        createStory: 'Create',
        libraryTitle: 'Library',
        playButton: 'Play',
      },
      assets: {
        logo: '',
        background: '',
        icon: '',
      },
    }

    const mockCyberpunkTheme: Theme = {
      id: 'cyberpunk',
      name: 'Cyberpunk',
      description: 'High-tech',
      colors: {
        primary: '#FF00FF',
        secondary: '#00FFFF',
        background: '#0A0A0A',
        surface: '#1A1A1A',
        text: '#00FF00',
        textSecondary: '#00AA00',
        accent: '#FFFF00',
        error: '#FF0000',
        success: '#00FF00',
        warning: '#FFA500',
      },
      typography: { 
        fontFamily: 'Orbitron', 
        fontFamilyMono: 'Mono', 
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
        story: 'Run',
        stories: 'Runs',
        character: 'Runner',
        characters: 'Runners',
        enemy: 'Corp',
        enemies: 'Corps',
        item: 'Gear',
        items: 'Gear',
        location: 'Node',
        locations: 'Nodes',
      },
      ui: {
        welcome: 'Jack In',
        createStory: 'New Run',
        libraryTitle: 'Archives',
        playButton: 'Execute',
      },
      assets: {
        logo: '',
        background: '',
        icon: '',
      },
    }

    vi.mocked(themeApi.getThemes).mockResolvedValue(mockThemes)
    vi.mocked(themeApi.getTheme)
      .mockResolvedValueOnce(mockWarhammerTheme)
      .mockResolvedValueOnce(mockCyberpunkTheme)

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Loaded')
    })

    fireEvent.click(screen.getByText('Change Theme'))

    await waitFor(() => {
      expect(localStorage.getItem('selectedThemeId')).toBe('cyberpunk')
    })
  })

  it('applies CSS variables when theme changes', async () => {
    const mockThemes = [
      { id: 'warhammer40k', name: 'Warhammer 40K', description: 'Grimdark' },
      { id: 'cyberpunk', name: 'Cyberpunk', description: 'High-tech' },
    ]

    const mockWarhammerTheme: Theme = {
      id: 'warhammer40k',
      name: 'Warhammer 40,000',
      description: 'Grimdark',
      colors: { 
        primary: '#8B0000',
        secondary: '#C0C0C0',
        background: '#1A1A1A',
        surface: '#2D2D2D',
        text: '#E0E0E0',
        textSecondary: '#A0A0A0',
        accent: '#FFD700',
        error: '#FF4444',
        success: '#44FF44',
        warning: '#FFAA00',
      },
      typography: { 
        fontFamily: 'Cinzel', 
        fontFamilyMono: 'Mono', 
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
        story: 'Mission',
        stories: 'Missions',
        character: 'Space Marine',
        characters: 'Space Marines',
        enemy: 'Xenos',
        enemies: 'Xenos',
        item: 'Wargear',
        items: 'Wargear',
        location: 'Deck',
        locations: 'Decks',
      },
      ui: {
        welcome: 'Welcome',
        createStory: 'Create',
        libraryTitle: 'Library',
        playButton: 'Play',
      },
      assets: {
        logo: '',
        background: '',
        icon: '',
      },
    }

    const mockCyberpunkTheme: Theme = {
      id: 'cyberpunk',
      name: 'Cyberpunk',
      description: 'High-tech',
      colors: { 
        primary: '#FF00FF', 
        background: '#0A0A0A',
        secondary: '#00FFFF',
        surface: '#1A1A1A',
        text: '#00FF00',
        textSecondary: '#00AA00',
        accent: '#FFFF00',
        error: '#FF0000',
        success: '#00FF00',
        warning: '#FFA500',
      },
      typography: { 
        fontFamily: 'Orbitron', 
        fontFamilyMono: 'Mono', 
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
        story: 'Run',
        stories: 'Runs',
        character: 'Runner',
        characters: 'Runners',
        enemy: 'Corp',
        enemies: 'Corps',
        item: 'Gear',
        items: 'Gear',
        location: 'Node',
        locations: 'Nodes',
      },
      ui: {
        welcome: 'Jack In',
        createStory: 'New Run',
        libraryTitle: 'Archives',
        playButton: 'Execute',
      },
      assets: {
        logo: '',
        background: '',
        icon: '',
      },
    }

    vi.mocked(themeApi.getThemes).mockResolvedValue(mockThemes)
    vi.mocked(themeApi.getTheme)
      .mockResolvedValueOnce(mockWarhammerTheme)
      .mockResolvedValueOnce(mockCyberpunkTheme)

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Loaded')
    })

    fireEvent.click(screen.getByText('Change Theme'))

    await waitFor(() => {
      const root = document.documentElement
      expect(root.style.getPropertyValue('--color-primary')).toBe('#FF00FF')
      expect(root.style.getPropertyValue('--font-family')).toBe('Orbitron')
    })
  })
})
