import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { TemplateGallery } from '../components/generation/TemplateGallery'
import { GenerationProgress } from '../components/generation/GenerationProgress'
import { apiClient } from '../services/api'
import type { TemplateMetadata } from '../services/types'

type ViewState = 'select' | 'generating'

function CreatePage() {
  const navigate = useNavigate()
  const [viewState, setViewState] = useState<ViewState>('select')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const startGeneration = async (prompt: string, templateId?: string) => {
    setIsSubmitting(true)
    setError(null)

    try {
      const response = await apiClient.createStory({
        prompt,
        template_id: templateId,
      })

      setSessionId(response.session_id)
      setViewState('generating')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start generation'
      setError(errorMessage)
      console.error('Generation failed:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleTemplateSelect = async (template: TemplateMetadata) => {
    // For now, use the template description as the prompt
    // In a full implementation, we'd collect variable values from the user
    const prompt = `Create a ${template.title} story: ${template.description}`
    await startGeneration(prompt, template.name)
  }

  const handleCustomPrompt = async (prompt: string) => {
    await startGeneration(prompt)
  }

  const handleGenerationComplete = () => {
    // Navigate to library to see the new story
    // In a full implementation, we'd navigate to /review/:storyId
    navigate('/library')
  }

  const handleGenerationError = (errorMessage: string) => {
    setError(errorMessage)
    // Stay on the generation view to show the error
  }

  const handleBackToSelection = () => {
    setViewState('select')
    setSessionId(null)
    setError(null)
  }

  if (viewState === 'generating' && sessionId) {
    return (
      <div className="page">
        <GenerationProgress
          sessionId={sessionId}
          onComplete={handleGenerationComplete}
          onError={handleGenerationError}
        />
        {error && (
          <div style={{ marginTop: '1rem', textAlign: 'center' }}>
            <button
              onClick={handleBackToSelection}
              style={{
                padding: '0.5rem 1rem',
                cursor: 'pointer',
              }}
            >
              Back to Template Selection
            </button>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="page">
      {error && (
        <div
          style={{
            padding: '1rem',
            marginBottom: '1rem',
            backgroundColor: '#fee',
            border: '1px solid #f00',
            borderRadius: '4px',
            color: '#c00',
          }}
        >
          {error}
        </div>
      )}
      {isSubmitting && (
        <div
          style={{
            padding: '1rem',
            marginBottom: '1rem',
            backgroundColor: '#eef',
            border: '1px solid #00f',
            borderRadius: '4px',
            textAlign: 'center',
          }}
        >
          Starting generation...
        </div>
      )}
      <TemplateGallery
        onTemplateSelect={handleTemplateSelect}
        onCustomPrompt={handleCustomPrompt}
      />
    </div>
  )
}

export default CreatePage
