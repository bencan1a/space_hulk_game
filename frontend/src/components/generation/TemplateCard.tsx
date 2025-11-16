import React from 'react'
import styles from './TemplateCard.module.css'
import type { TemplateMetadata } from '../../services/types'

interface TemplateCardProps {
  template: TemplateMetadata
  selected?: boolean
  onClick?: (template: TemplateMetadata) => void
}

export const TemplateCard: React.FC<TemplateCardProps> = ({
  template,
  selected = false,
  onClick,
}) => {
  const handleClick = () => {
    if (onClick) {
      onClick(template)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClick()
    }
  }

  return (
    <div
      className={`${styles.card} ${selected ? styles.selected : ''}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-label={`Template: ${template.title}`}
      aria-pressed={selected}
    >
      <div className={styles.header}>
        <h3 className={styles.title}>{template.title}</h3>
        <span className={styles.category} aria-label={`Category: ${template.category}`}>
          {template.category}
        </span>
      </div>

      <p className={styles.description}>{template.description}</p>

      <div className={styles.variables} aria-label="Required variables">
        {template.variables
          .filter((v) => v.required)
          .map((variable) => (
            <span key={variable.name} className={styles.variable}>
              {variable.name}
            </span>
          ))}
      </div>

      {selected && (
        <div className={styles.selectedIndicator} aria-label="Selected">
          ✓
        </div>
      )}
    </div>
  )
}
