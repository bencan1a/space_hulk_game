import React, { useState, useCallback } from 'react'
import { SearchBar, FilterPanel, StoryGrid } from '../components/library'
import { useStories } from '../hooks'
import type { Story, StoryFilters } from '../types/story'
import styles from './LibraryPage.module.css'

export const LibraryPage: React.FC = () => {
  const { stories, loading, error, filters, setFilters } = useStories()
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = useCallback(
    (query: string) => {
      setSearchQuery(query)
      setFilters({ ...filters, search: query || undefined })
    },
    [filters, setFilters]
  )

  const handleFilterChange = useCallback(
    (newFilters: StoryFilters) => {
      setFilters({ ...newFilters, search: searchQuery || undefined })
    },
    [searchQuery, setFilters]
  )

  const handleStoryClick = (story: Story) => {
    console.log('Story clicked:', story.id)
    // TODO: Navigate to play page
    // navigate(`/play/${story.id}`);
  }

  const handleCreateStory = () => {
    console.log('Create new story')
    // TODO: Navigate to create page
    // navigate('/create');
  }

  const handleRetry = useCallback(() => {
    window.location.reload()
  }, [])

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Story Library</h1>
        <button className={styles.createButton} onClick={handleCreateStory}>
          + Create New Story
        </button>
      </header>

      <div className={styles.content}>
        <aside className={styles.sidebar}>
          <FilterPanel filters={filters} onFilterChange={handleFilterChange} />
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
