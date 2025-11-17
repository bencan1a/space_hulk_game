import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { StoryPreview } from '../components/generation/StoryPreview'
import { Story } from '../types/story'
import { storyApi } from '../services/storyApi'
import styles from './ReviewPage.module.css'

/**
 * ReviewPage displays the generated story preview and provides navigation
 * to either play the story or give feedback for iteration.
 *
 * URL params:
 * - storyId: The ID of the story to review
 *
 * Navigation:
 * - "Play Now" -> /play/:id
 * - "Give Feedback" -> /feedback/:id (placeholder until feedback page is implemented)
 */
function ReviewPage() {
  const { storyId } = useParams<{ storyId: string }>()
  const navigate = useNavigate()
  const [story, setStory] = useState<Story | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStory = async () => {
      if (!storyId) {
        setError('No story ID provided')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError(null)
        const fetchedStory = await storyApi.getStory(parseInt(storyId, 10))
        setStory(fetchedStory)
      } catch (err) {
        console.error('Error fetching story:', err)
        setError('Failed to load story. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    fetchStory()
  }, [storyId])

  const handlePlayNow = () => {
    if (story) {
      navigate(`/play/${story.id}`)
    }
  }

  const handleGiveFeedback = () => {
    if (story) {
      // Navigate to feedback page (to be implemented in Task 4.3)
      navigate(`/feedback/${story.id}`)
    }
  }

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.loading}>
          <div className={styles.spinner} role="status" aria-label="Loading story">
            <span className={styles.spinnerIcon}>⏳</span>
          </div>
          <p className={styles.loadingText}>Loading your story...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={styles.page}>
        <div className={styles.error}>
          <h2 className={styles.errorTitle}>Error</h2>
          <p className={styles.errorMessage}>{error}</p>
          <button className={styles.errorButton} onClick={() => navigate('/library')}>
            Return to Library
          </button>
        </div>
      </div>
    )
  }

  if (!story) {
    return (
      <div className={styles.page}>
        <div className={styles.error}>
          <h2 className={styles.errorTitle}>Story Not Found</h2>
          <p className={styles.errorMessage}>The requested story could not be found.</p>
          <button className={styles.errorButton} onClick={() => navigate('/library')}>
            Return to Library
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.pageTitle}>Your Story is Ready!</h1>
        <p className={styles.pageSubtitle}>Review your generated story and decide what to do next</p>
      </div>
      <StoryPreview story={story} onPlayNow={handlePlayNow} onGiveFeedback={handleGiveFeedback} />
    </div>
  )
}

export default ReviewPage
