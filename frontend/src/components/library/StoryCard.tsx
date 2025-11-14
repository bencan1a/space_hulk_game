import React from 'react';
import styles from './StoryCard.module.css';
import type { Story } from '../../types/story';

interface StoryCardProps {
  story: Story;
  onClick?: (story: Story) => void;
}

export const StoryCard: React.FC<StoryCardProps> = ({ story, onClick }) => {
  const handleClick = () => {
    if (onClick) {
      onClick(story);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  return (
    <div
      className={styles.card}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-label={`Story: ${story.title}`}
    >
      <div className={styles.header}>
        <h3 className={styles.title}>{story.title}</h3>
        <span className={styles.theme} aria-label={`Theme: ${story.theme_id}`}>
          {story.theme_id}
        </span>
      </div>

      {story.description && (
        <p className={styles.description}>{story.description}</p>
      )}

      <div className={styles.tags} aria-label="Tags">
        {story.tags.map((tag) => (
          <span key={tag} className={styles.tag}>
            {tag}
          </span>
        ))}
      </div>

      <div className={styles.footer}>
        <div className={styles.stats}>
          <span className={styles.stat} aria-label={`Played ${story.play_count} times`}>
            ▶ {story.play_count}
          </span>
          {story.scene_count && (
            <span className={styles.stat} aria-label={`${story.scene_count} scenes`}>
              📍 {story.scene_count}
            </span>
          )}
        </div>
        <time className={styles.date} dateTime={story.created_at}>
          {new Date(story.created_at).toLocaleDateString()}
        </time>
      </div>
    </div>
  );
};
