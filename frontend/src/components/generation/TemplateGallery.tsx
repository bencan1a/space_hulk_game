import React, { useEffect, useState } from 'react'
import styles from './TemplateGallery.module.css'
import { TemplateCard } from './TemplateCard'
import { CustomPromptForm } from './CustomPromptForm'
import type { TemplateMetadata } from '../../services/types'
import { apiClient } from '../../services/api'

interface TemplateGalleryProps {
  onTemplateSelect?: (template: TemplateMetadata) => void
  onCustomPrompt?: (prompt: string) => void
}

export const TemplateGallery: React.FC<TemplateGalleryProps> = ({
  onTemplateSelect,
  onCustomPrompt,
}) => {
  const [templates, setTemplates] = useState<TemplateMetadata[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateMetadata | null>(null)
  const [showCustom, setShowCustom] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await apiClient.getTemplates()
        setTemplates(response.templates)
      } catch (err) {
        console.error('Error fetching templates:', err)
        setError('Failed to load templates. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    fetchTemplates()
  }, [])

  const handleTemplateClick = (template: TemplateMetadata) => {
    setSelectedTemplate(template)
    setShowCustom(false)
  }

  const handleGenerateClick = () => {
    if (selectedTemplate && onTemplateSelect) {
      onTemplateSelect(selectedTemplate)
    }
  }

  const handleCustomClick = () => {
    setShowCustom(true)
    setSelectedTemplate(null)
  }

  const handleCustomPromptSubmit = (prompt: string) => {
    if (onCustomPrompt) {
      onCustomPrompt(prompt)
    }
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading} role="status" aria-live="polite">
          Loading templates...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error} role="alert">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Choose Your Story Template</h2>
        <p className={styles.subtitle}>
          Select a predefined template or create your own custom prompt
        </p>
      </div>

      <div className={styles.options}>
        <button
          className={`${styles.optionButton} ${!showCustom ? styles.optionButtonActive : ''}`}
          onClick={() => setShowCustom(false)}
          aria-pressed={!showCustom}
        >
          Templates
        </button>
        <button
          className={`${styles.optionButton} ${showCustom ? styles.optionButtonActive : ''}`}
          onClick={handleCustomClick}
          aria-pressed={showCustom}
        >
          Custom Prompt
        </button>
      </div>

      {!showCustom ? (
        <>
          <div className={styles.gallery} role="list" aria-label="Template gallery">
            {templates.map((template) => (
              <div key={template.name} role="listitem">
                <TemplateCard
                  template={template}
                  selected={selectedTemplate?.name === template.name}
                  onClick={handleTemplateClick}
                />
              </div>
            ))}

            {templates.length === 0 && (
              <div className={styles.emptyState}>
                <p>No templates available</p>
              </div>
            )}
          </div>

          {selectedTemplate && (
            <div className={styles.actionSection}>
              <button
                className={styles.generateButton}
                onClick={handleGenerateClick}
                aria-label={`Generate story using ${selectedTemplate.title} template`}
              >
                Generate Story
              </button>
            </div>
          )}
        </>
      ) : (
        <div className={styles.customSection}>
          <CustomPromptForm onSubmit={handleCustomPromptSubmit} />
        </div>
      )}
    </div>
  )
}
