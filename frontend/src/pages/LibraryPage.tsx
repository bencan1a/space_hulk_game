import React, { useState, useCallback } from 'react'
import { SearchBar, FilterPanel, StoryGrid } from '../components/library'
import { useStories } from '../hooks'
import type { Story, StoryFilters } from '../types/story'
import styles from './LibraryPage.module.css'

export const LibraryPage: React.FC = () => {
  const { stories, loading, error, filters, setFilters, fetchStories } = useStories()
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = useCallback(
    (query: string) => {
      setSearchQuery(query)
      setFilters({ search: query || undefined })
    },
    [setFilters]
  )

  const handleFilterChange = useCallback(
    (newFilters: StoryFilters) => {
      const mergedFilters = { ...newFilters }
      if (searchQuery) {
        mergedFilters.search = searchQuery
      }
      setFilters(mergedFilters)
    },
    [searchQuery, setFilters]
  )

  const handleStoryClick = (story: Story) => {
    if (import.meta.env.DEV) {
      console.log('Story clicked:', story.id)
    }
    // TODO: Navigate to play page
    // navigate(`/play/${story.id}`);
  }

  const handleCreateStory = () => {
    if (import.meta.env.DEV) {
      console.log('Create new story')
    }
    // TODO: Navigate to create page
    // navigate('/create');
  }

  const handleRetry = useCallback(() => {
    fetchStories()
  }, [fetchStories])

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
