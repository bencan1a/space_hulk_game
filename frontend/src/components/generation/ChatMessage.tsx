import React from 'react'
import styles from './ChatMessage.module.css'

export interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ role, content, timestamp }) => {
  return (
    <div
      className={`${styles.message} ${role === 'user' ? styles.messageUser : styles.messageAssistant}`}
      role="article"
      aria-label={`${role === 'user' ? 'User' : 'Assistant'} message`}
    >
      <div className={styles.messageHeader}>
        <span className={styles.role}>{role === 'user' ? 'You' : 'AI Guide'}</span>
        {timestamp && <span className={styles.timestamp}>{timestamp}</span>}
      </div>
      <div className={styles.content}>{content}</div>
    </div>
  )
}
