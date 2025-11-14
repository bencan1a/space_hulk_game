import { render, screen, fireEvent } from '@testing-library/react'
import { FilterPanel } from '../../../components/library/FilterPanel'
import type { StoryFilters } from '../../../types/story'
import { describe, it, expect, vi } from 'vitest'

describe('FilterPanel', () => {
  it('renders filters correctly', () => {
    const filters: StoryFilters = {}
    render(<FilterPanel filters={filters} onFilterChange={vi.fn()} />)

    expect(screen.getByText('Filters')).toBeInTheDocument()
    expect(screen.getByLabelText('Theme')).toBeInTheDocument()
    expect(screen.getByText('Tags')).toBeInTheDocument()
  })

  it('updates theme filter when theme is selected', () => {
    const handleFilterChange = vi.fn()
    const filters: StoryFilters = {}
    render(<FilterPanel filters={filters} onFilterChange={handleFilterChange} />)

    const themeSelect = screen.getByLabelText('Theme')
    fireEvent.change(themeSelect, { target: { value: 'warhammer40k' } })

    expect(handleFilterChange).toHaveBeenCalledWith({
      theme_id: 'warhammer40k',
    })
  })

  it('updates tag filters when tags are toggled', () => {
    const handleFilterChange = vi.fn()
    const filters: StoryFilters = {}
    render(<FilterPanel filters={filters} onFilterChange={handleFilterChange} />)

    const horrorCheckbox = screen.getByLabelText('Filter by horror')
    fireEvent.click(horrorCheckbox)

    expect(handleFilterChange).toHaveBeenCalledWith({
      tags: ['horror'],
    })
  })

  it('removes tag from filters when unchecked', () => {
    const handleFilterChange = vi.fn()
    const filters: StoryFilters = { tags: ['horror', 'action'] }
    render(<FilterPanel filters={filters} onFilterChange={handleFilterChange} />)

    const horrorCheckbox = screen.getByLabelText('Filter by horror')
    fireEvent.click(horrorCheckbox)

    expect(handleFilterChange).toHaveBeenCalledWith({
      tags: ['action'],
    })
  })

  it('shows clear button when filters are active', () => {
    const filters: StoryFilters = { theme_id: 'warhammer40k' }
    render(<FilterPanel filters={filters} onFilterChange={vi.fn()} />)

    expect(screen.getByLabelText('Clear all filters')).toBeInTheDocument()
  })

  it('hides clear button when no filters are active', () => {
    const filters: StoryFilters = {}
    render(<FilterPanel filters={filters} onFilterChange={vi.fn()} />)

    expect(screen.queryByLabelText('Clear all filters')).not.toBeInTheDocument()
  })

  it('clears all filters when clear button is clicked', () => {
    const handleFilterChange = vi.fn()
    const filters: StoryFilters = { theme_id: 'warhammer40k', tags: ['horror'] }
    render(<FilterPanel filters={filters} onFilterChange={handleFilterChange} />)

    const clearButton = screen.getByLabelText('Clear all filters')
    fireEvent.click(clearButton)

    expect(handleFilterChange).toHaveBeenCalledWith({})
  })
})
