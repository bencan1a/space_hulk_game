import React from 'react'
import { StoryCard } from './StoryCard'
import styles from './StoryGrid.module.css'
import type { Story } from '../../types/story'

interface StoryGridProps {
  stories: Story[]
  loading?: boolean
  error?: string | null
  onStoryClick?: (story: Story) => void
  onRetry?: () => void
}

export const StoryGrid: React.FC<StoryGridProps> = ({
  stories,
  loading = false,
  error = null,
  onStoryClick,
  onRetry,
}) => {
  // Loading state
  if (loading) {
    return (
      <div className={styles.grid} aria-busy="true" aria-label="Loading stories">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className={styles.skeleton} aria-hidden="true">
            <div className={styles.skeletonHeader} />
            <div className={styles.skeletonText} />
            <div className={styles.skeletonText} />
            <div className={styles.skeletonFooter} />
          </div>
        ))}
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className={styles.error} role="alert">
        <p className={styles.errorIcon}>⚠️</p>
        <p className={styles.errorMessage}>{error}</p>
        <button
          className={styles.retryButton}
          onClick={onRetry || (() => window.location.reload())}
          aria-label="Retry loading stories"
        >
          Retry
        </button>
      </div>
    )
  }

  // Empty state
  if (stories.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyIcon}>📚</p>
        <p className={styles.emptyMessage}>No stories found</p>
        <p className={styles.emptyHint}>Try adjusting your filters or create a new story</p>
      </div>
    )
  }

  // Success state
  return (
    <div className={styles.grid} role="list" aria-label="Story library">
      {stories.map((story) => (
        <StoryCard key={story.id} story={story} onClick={onStoryClick} />
      ))}
    </div>
  )
}
