import React from 'react'
import styles from './FilterPanel.module.css'
import type { StoryFilters } from '../../types/story'

interface FilterPanelProps {
  filters: StoryFilters
  onFilterChange: (filters: StoryFilters) => void
  availableThemes?: string[]
  availableTags?: string[]
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onFilterChange,
  availableThemes = ['warhammer40k', 'cyberpunk'],
  availableTags = ['horror', 'action', 'exploration', 'mystery'],
}) => {
  const handleThemeChange = (themeId: string) => {
    onFilterChange({
      ...filters,
      theme_id: themeId === '' ? undefined : themeId,
    })
  }

  const handleTagToggle = (tag: string) => {
    const currentTags = filters.tags || []
    const newTags = currentTags.includes(tag)
      ? currentTags.filter((t) => t !== tag)
      : [...currentTags, tag]

    onFilterChange({
      ...filters,
      tags: newTags.length > 0 ? newTags : undefined,
    })
  }

  const handleClearFilters = () => {
    onFilterChange({})
  }

  const hasActiveFilters = filters.theme_id || (filters.tags && filters.tags.length > 0)

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h3 className={styles.title}>Filters</h3>
        {hasActiveFilters && (
          <button
            className={styles.clearButton}
            onClick={handleClearFilters}
            aria-label="Clear all filters"
          >
            Clear All
          </button>
        )}
      </div>

      <div className={styles.section}>
        <label htmlFor="theme-select" className={styles.label}>
          Theme
        </label>
        <select
          id="theme-select"
          className={styles.select}
          value={filters.theme_id || ''}
          onChange={(e) => handleThemeChange(e.target.value)}
        >
          <option value="">All Themes</option>
          {availableThemes.map((theme) => (
            <option key={theme} value={theme}>
              {theme}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.section}>
        <span className={styles.label}>Tags</span>
        <div className={styles.tagGrid} role="group" aria-label="Filter by tags">
          {availableTags.map((tag) => (
            <label key={tag} className={styles.tagLabel}>
              <input
                type="checkbox"
                className={styles.checkbox}
                checked={filters.tags?.includes(tag) || false}
                onChange={() => handleTagToggle(tag)}
                aria-label={`Filter by ${tag}`}
              />
              <span className={styles.tagText}>{tag}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}
