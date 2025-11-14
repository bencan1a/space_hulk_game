import React, { useState, useCallback } from 'react'
import { SearchBar, FilterPanel, StoryGrid } from '../components/library'
import type { Story, StoryFilters } from '../types/story'
import styles from './LibraryPage.module.css'

export const LibraryPage: React.FC = () => {
  const [filters, setFilters] = useState<StoryFilters>({})

  // TODO: Connect to real data in Task 2.6
  const stories: Story[] = []
  const loading = false
  const error = null

  const handleSearch = useCallback((query: string) => {
    // TODO: Implement search in Task 2.6
    console.log('Search query:', query)
  }, [])

  const handleStoryClick = useCallback((story: Story) => {
    // TODO: Navigate to play page in Task 2.6
    console.log('Navigate to story:', story.id)
  }, [])

  const handleRetry = useCallback(() => {
    // TODO: Implement retry logic in Task 2.6
    window.location.reload()
  }, [])

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Story Library</h1>
        <button
          className={styles.createButton}
          onClick={() => {
            // TODO: Navigate to create page
          }}
          aria-label="Create a new story"
        >
          + Create New Story
        </button>
      </header>

      <div className={styles.content}>
        <aside className={styles.sidebar}>
          <FilterPanel filters={filters} onFilterChange={setFilters} />
        </aside>

        <main className={styles.main}>
          <SearchBar onSearch={handleSearch} />
          <StoryGrid
            stories={stories}
            loading={loading}
            error={error}
            onStoryClick={handleStoryClick}
            onRetry={handleRetry}
          />
        </main>
      </div>
    </div>
  )
}

export default LibraryPage
