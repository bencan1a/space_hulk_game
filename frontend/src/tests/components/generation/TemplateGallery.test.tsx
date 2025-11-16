import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { TemplateGallery } from '../../../components/generation/TemplateGallery'
import { apiClient } from '../../../services/api'
import type { TemplateListResponse, TemplateMetadata } from '../../../services/types'
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock the API client
vi.mock('../../../services/api', () => ({
  apiClient: {
    getTemplates: vi.fn(),
  },
}))

const mockTemplates: TemplateMetadata[] = [
  {
    name: 'horror',
    title: 'Gothic Horror',
    description: 'Generate a horror-themed story',
    category: 'horror',
    variables: [
      {
        name: 'setting',
        type: 'string',
        required: true,
        description: 'The primary location',
      },
    ],
  },
  {
    name: 'rescue',
    title: 'Rescue Mission',
    description: 'Generate a rescue mission story',
    category: 'action',
    variables: [
      {
        name: 'objective',
        type: 'string',
        required: true,
        description: 'The rescue objective',
      },
    ],
  },
]

describe('TemplateGallery', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    vi.mocked(apiClient.getTemplates).mockImplementation(
      () =>
        new Promise(() => {
          /* never resolves */
        })
    )

    render(<TemplateGallery />)

    expect(screen.getByText('Loading templates...')).toBeInTheDocument()
  })

  it('fetches and displays templates', async () => {
    const mockResponse: TemplateListResponse = {
      templates: mockTemplates,
      total: 2,
    }
    vi.mocked(apiClient.getTemplates).mockResolvedValue(mockResponse)

    render(<TemplateGallery />)

    await waitFor(() => {
      expect(screen.getByText('Gothic Horror')).toBeInTheDocument()
      expect(screen.getByText('Rescue Mission')).toBeInTheDocument()
    })
  })

  it('handles API errors', async () => {
    vi.mocked(apiClient.getTemplates).mockRejectedValue(new Error('API Error'))

    render(<TemplateGallery />)

    await waitFor(() => {
      expect(screen.getByText(/Failed to load templates/i)).toBeInTheDocument()
    })
  })

  it('calls onTemplateSelect when template is clicked', async () => {
    const mockResponse: TemplateListResponse = {
      templates: mockTemplates,
      total: 2,
    }
    vi.mocked(apiClient.getTemplates).mockResolvedValue(mockResponse)

    const handleTemplateSelect = vi.fn()
    render(<TemplateGallery onTemplateSelect={handleTemplateSelect} />)

    await waitFor(() => {
      expect(screen.getByText('Gothic Horror')).toBeInTheDocument()
    })

    const horrorCard = screen.getByLabelText('Template: Gothic Horror')
    fireEvent.click(horrorCard)

    expect(handleTemplateSelect).toHaveBeenCalledWith(mockTemplates[0])
  })

  it('switches to custom prompt mode', async () => {
    const mockResponse: TemplateListResponse = {
      templates: mockTemplates,
      total: 2,
    }
    vi.mocked(apiClient.getTemplates).mockResolvedValue(mockResponse)

    render(<TemplateGallery />)

    await waitFor(() => {
      expect(screen.getByText('Gothic Horror')).toBeInTheDocument()
    })

    const customButton = screen.getByRole('button', { name: /Custom Prompt/i })
    fireEvent.click(customButton)

    expect(screen.getByLabelText(/Custom Prompt/i)).toBeInTheDocument()
    expect(screen.queryByText('Gothic Horror')).not.toBeInTheDocument()
  })

  it('switches back to templates from custom prompt', async () => {
    const mockResponse: TemplateListResponse = {
      templates: mockTemplates,
      total: 2,
    }
    vi.mocked(apiClient.getTemplates).mockResolvedValue(mockResponse)

    render(<TemplateGallery />)

    await waitFor(() => {
      expect(screen.getByText('Gothic Horror')).toBeInTheDocument()
    })

    const customButton = screen.getByRole('button', { name: /Custom Prompt/i })
    fireEvent.click(customButton)

    expect(screen.getByLabelText(/Custom Prompt/i)).toBeInTheDocument()

    const templatesButton = screen.getByRole('button', { name: /Templates/i })
    fireEvent.click(templatesButton)

    await waitFor(() => {
      expect(screen.getByText('Gothic Horror')).toBeInTheDocument()
    })
  })

  it('displays empty state when no templates', async () => {
    const mockResponse: TemplateListResponse = {
      templates: [],
      total: 0,
    }
    vi.mocked(apiClient.getTemplates).mockResolvedValue(mockResponse)

    render(<TemplateGallery />)

    await waitFor(() => {
      expect(screen.getByText('No templates available')).toBeInTheDocument()
    })
  })
})
