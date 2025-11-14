import React, { useState } from 'react';
import { SearchBar, FilterPanel, StoryGrid } from '../components/library';
import type { Story, StoryFilters } from '../types/story';
import styles from './LibraryPage.module.css';

export const LibraryPage: React.FC = () => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_search, setSearch] = useState('');
  const [filters, setFilters] = useState<StoryFilters>({});

  // TODO: Connect to real data in Task 2.6
  const stories: Story[] = [];
  const loading = false;
  const error = null;

  const handleStoryClick = (story: Story) => {
    console.log('Story clicked:', story.id);
    // TODO: Navigate to play page
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Story Library</h1>
        <button className={styles.createButton}>
          + Create New Story
        </button>
      </header>

      <div className={styles.content}>
        <aside className={styles.sidebar}>
          <FilterPanel filters={filters} onFilterChange={setFilters} />
        </aside>

        <main className={styles.main}>
          <SearchBar onSearch={setSearch} />
          <StoryGrid
            stories={stories}
            loading={loading}
            error={error}
            onStoryClick={handleStoryClick}
          />
        </main>
      </div>
    </div>
  );
};

export default LibraryPage;
