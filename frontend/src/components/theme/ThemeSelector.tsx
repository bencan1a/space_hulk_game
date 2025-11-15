import React, { useState, useRef, useEffect } from 'react'
import { useTheme } from '../../contexts/useTheme'
import styles from './ThemeSelector.module.css'

export const ThemeSelector: React.FC = () => {
  const { currentTheme, availableThemes, setTheme } = useTheme()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleThemeSelect = async (themeId: string) => {
    await setTheme(themeId)
    setIsOpen(false)
  }

  const handleKeyDown = (event: React.KeyboardEvent, themeId: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      handleThemeSelect(themeId)
    }
  }

  if (!currentTheme) {
    return null
  }

  return (
    <div className={styles.container} ref={dropdownRef}>
      <button
        className={styles.trigger}
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label="Select theme"
      >
        <span className={styles.triggerIcon}>🎨</span>
        <span className={styles.triggerText}>{currentTheme.name}</span>
        <span className={styles.triggerArrow}>{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className={styles.dropdown} role="listbox">
          {availableThemes.map((theme) => (
            <div
              key={theme.id}
              className={`${styles.option} ${
                theme.id === currentTheme.id ? styles.optionSelected : ''
              }`}
              role="option"
              aria-selected={theme.id === currentTheme.id}
              onClick={() => handleThemeSelect(theme.id)}
              onKeyDown={(e) => handleKeyDown(e, theme.id)}
              tabIndex={0}
            >
              <div className={styles.optionContent}>
                <span className={styles.optionName}>{theme.name}</span>
                <span className={styles.optionDescription}>{theme.description}</span>
              </div>
              {theme.id === currentTheme.id && (
                <span className={styles.optionCheck} aria-hidden="true">
                  ✓
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
