import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeSelector } from '../../../components/theme/ThemeSelector'
import { ThemeProvider } from '../../../contexts/ThemeContext'
import { themeApi } from '../../../services/themeApi'
import type { Theme } from '../../../types/theme'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../../../services/themeApi')

describe('ThemeSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()

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

    vi.mocked(themeApi.getThemes).mockResolvedValue(mockThemes)
    vi.mocked(themeApi.getTheme).mockResolvedValue(mockTheme)
  })

  it('displays current theme name', async () => {
    render(
      <ThemeProvider>
        <ThemeSelector />
      </ThemeProvider>
    )

    await screen.findByText('Warhammer 40,000')

    expect(screen.getByText('Warhammer 40,000')).toBeInTheDocument()
  })

  it('opens dropdown when clicked', async () => {
    render(
      <ThemeProvider>
        <ThemeSelector />
      </ThemeProvider>
    )

    const trigger = await screen.findByLabelText('Select theme')

    fireEvent.click(trigger)

    expect(screen.getByText('Grimdark')).toBeInTheDocument()
    expect(screen.getByText('High-tech')).toBeInTheDocument()
  })

  it('shows checkmark on current theme', async () => {
    render(
      <ThemeProvider>
        <ThemeSelector />
      </ThemeProvider>
    )

    const trigger = await screen.findByLabelText('Select theme')
    fireEvent.click(trigger)

    // Find all options and check the one with aria-selected="true"
    const options = screen.getAllByRole('option')
    const selectedOption = options.find((option) => option.getAttribute('aria-selected') === 'true')

    expect(selectedOption).toBeDefined()
    expect(selectedOption).toHaveTextContent('Warhammer 40K') // This is from availableThemes metadata
    expect(selectedOption).toHaveTextContent('✓')
  })
})
