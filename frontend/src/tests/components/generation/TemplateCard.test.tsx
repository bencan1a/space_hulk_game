import { render, screen, fireEvent } from '@testing-library/react'
import { TemplateCard } from '../../../components/generation/TemplateCard'
import type { TemplateMetadata } from '../../../services/types'
import { describe, it, expect, vi } from 'vitest'

const mockTemplate: TemplateMetadata = {
  name: 'horror',
  title: 'Gothic Horror',
  description: 'Generate a horror-themed story with atmospheric dread and suspense',
  category: 'horror',
  variables: [
    {
      name: 'setting',
      type: 'string',
      required: true,
      description: 'The primary location or environment for the horror story',
      example: 'abandoned space hulk',
    },
    {
      name: 'threat',
      type: 'string',
      required: true,
      description: 'The primary threat or horror element',
      example: 'genestealers',
    },
    {
      name: 'atmosphere',
      type: 'string',
      required: false,
      description: 'The mood and atmosphere to establish',
      default: 'claustrophobic and oppressive',
    },
  ],
}

describe('TemplateCard', () => {
  it('renders template information correctly', () => {
    render(<TemplateCard template={mockTemplate} />)

    expect(screen.getByText('Gothic Horror')).toBeInTheDocument()
    expect(
      screen.getByText('Generate a horror-themed story with atmospheric dread and suspense')
    ).toBeInTheDocument()
    expect(screen.getByText('horror')).toBeInTheDocument()
  })

  it('displays required variables', () => {
    render(<TemplateCard template={mockTemplate} />)

    expect(screen.getByText('setting')).toBeInTheDocument()
    expect(screen.getByText('threat')).toBeInTheDocument()
  })

  it('does not display optional variables', () => {
    render(<TemplateCard template={mockTemplate} />)

    expect(screen.queryByText('atmosphere')).not.toBeInTheDocument()
  })

  it('calls onClick when card is clicked', () => {
    const handleClick = vi.fn()
    render(<TemplateCard template={mockTemplate} onClick={handleClick} />)

    fireEvent.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledWith(mockTemplate)
  })

  it('calls onClick when Enter key is pressed', () => {
    const handleClick = vi.fn()
    render(<TemplateCard template={mockTemplate} onClick={handleClick} />)

    fireEvent.keyDown(screen.getByRole('button'), { key: 'Enter' })

    expect(handleClick).toHaveBeenCalledWith(mockTemplate)
  })

  it('calls onClick when Space key is pressed', () => {
    const handleClick = vi.fn()
    render(<TemplateCard template={mockTemplate} onClick={handleClick} />)

    fireEvent.keyDown(screen.getByRole('button'), { key: ' ' })

    expect(handleClick).toHaveBeenCalledWith(mockTemplate)
  })

  it('applies selected styles when selected', () => {
    render(<TemplateCard template={mockTemplate} selected={true} />)

    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByLabelText('Selected')).toBeInTheDocument()
  })

  it('does not show selected indicator when not selected', () => {
    render(<TemplateCard template={mockTemplate} selected={false} />)

    expect(screen.queryByLabelText('Selected')).not.toBeInTheDocument()
  })
})
