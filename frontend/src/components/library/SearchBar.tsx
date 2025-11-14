import React, { useState, useEffect, useCallback, useRef } from 'react'
import styles from './SearchBar.module.css'

interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
  debounceMs?: number
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = 'Search stories...',
  debounceMs = 300,
}) => {
  const [value, setValue] = useState('')
  const onSearchRef = useRef(onSearch)

  // Keep ref updated with latest onSearch callback
  useEffect(() => {
    onSearchRef.current = onSearch
  }, [onSearch])

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearchRef.current(value)
    }, debounceMs)

    return () => clearTimeout(timer)
  }, [value, debounceMs])

  const handleClear = useCallback(() => {
    setValue('')
    onSearchRef.current('')
  }, [])

  return (
    <div className={styles.container}>
      <div className={styles.inputWrapper}>
        <span className={styles.icon} aria-hidden="true">
          🔍
        </span>
        <input
          type="text"
          className={styles.input}
          placeholder={placeholder}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          aria-label="Search stories"
        />
        {value && (
          <button
            className={styles.clearButton}
            onClick={handleClear}
            aria-label="Clear search"
            type="button"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  )
}
