import React from 'react'
import { Story } from '../../types/story'
import styles from './StoryPreview.module.css'

export interface StoryPreviewProps {
  /**
   * The generated story data to preview
   */
  story: Story

  /**
   * Callback when "Play Now" button is clicked
   */
  onPlayNow?: () => void

  /**
   * Callback when "Give Feedback" button is clicked
   */
  onGiveFeedback?: () => void
}

/**
 * Component that displays a preview of a generated story with metadata,
 * statistics, and action buttons.
 *
 * Shows:
 * - Story title and description
 * - Theme and tags
 * - Statistics (scenes, items, NPCs, puzzles)
 * - Creation date
 * - Action buttons (Play Now, Give Feedback)
 *
 * @example
 * ```tsx
 * <StoryPreview
 *   story={generatedStory}
 *   onPlayNow={() => navigate(`/play/${story.id}`)}
 *   onGiveFeedback={() => navigate(`/feedback/${story.id}`)}
 * />
 * ```
 */
export const StoryPreview: React.FC<StoryPreviewProps> = ({ story, onPlayNow, onGiveFeedback }) => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>{story.title}</h2>
        {story.description && <p className={styles.description}>{story.description}</p>}
      </div>

      <div className={styles.metadata}>
        <div className={styles.metadataItem}>
          <span className={styles.metadataLabel}>Theme:</span>
          <span className={styles.metadataValue}>{story.theme_id}</span>
        </div>
        {story.tags && story.tags.length > 0 && (
          <div className={styles.metadataItem}>
            <span className={styles.metadataLabel}>Tags:</span>
            <div className={styles.tags}>
              {story.tags.map((tag) => (
                <span key={tag} className={styles.tag}>
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
        <div className={styles.metadataItem}>
          <span className={styles.metadataLabel}>Created:</span>
          <span className={styles.metadataValue}>
            {new Date(story.created_at).toLocaleDateString()}
          </span>
        </div>
        {story.iteration_count > 0 && (
          <div className={styles.metadataItem}>
            <span className={styles.metadataLabel}>Iterations:</span>
            <span className={styles.metadataValue}>{story.iteration_count}</span>
          </div>
        )}
      </div>

      <div className={styles.statistics}>
        <h3 className={styles.statisticsTitle}>Story Statistics</h3>
        <div className={styles.statisticsGrid}>
          {story.scene_count !== null && story.scene_count !== undefined && (
            <StatisticItem label="Scenes" value={story.scene_count} icon="🎬" />
          )}
          {story.item_count !== null && story.item_count !== undefined && (
            <StatisticItem label="Items" value={story.item_count} icon="🎒" />
          )}
          {story.npc_count !== null && story.npc_count !== undefined && (
            <StatisticItem label="NPCs" value={story.npc_count} icon="👤" />
          )}
          {story.puzzle_count !== null && story.puzzle_count !== undefined && (
            <StatisticItem label="Puzzles" value={story.puzzle_count} icon="🧩" />
          )}
        </div>
      </div>

      <div className={styles.actions}>
        <button
          className={`${styles.button} ${styles.buttonPrimary}`}
          onClick={onPlayNow}
          aria-label="Play this story now"
        >
          Play Now
        </button>
        <button
          className={`${styles.button} ${styles.buttonSecondary}`}
          onClick={onGiveFeedback}
          aria-label="Give feedback on this story"
        >
          Give Feedback
        </button>
      </div>
    </div>
  )
}

interface StatisticItemProps {
  label: string
  value: number
  icon: string
}

const StatisticItem: React.FC<StatisticItemProps> = ({ label, value, icon }) => {
  return (
    <div className={styles.statItem}>
      <div className={styles.statIcon}>{icon}</div>
      <div className={styles.statContent}>
        <div className={styles.statValue}>{value}</div>
        <div className={styles.statLabel}>{label}</div>
      </div>
    </div>
  )
}
