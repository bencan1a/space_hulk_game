/* eslint-disable react-refresh/only-export-components */
/**
 * API Client Usage Examples
 * 
 * This file demonstrates how to use the API client in your components.
 * DO NOT import this file - it's for documentation purposes only.
 */

import { apiClient } from './api'
import type { CreateStoryRequest, GameCommand } from './types'
import { getErrorMessage } from '../utils/errorHandler'

// Example 1: Fetch all stories
async function fetchStories() {
  try {
    const stories = await apiClient.getStories({
      page: 1,
      page_size: 20,
      theme_id: 'warhammer40k',
    })
    console.log(`Found ${stories.total} stories`)
    return stories.items
  } catch (error) {
    console.error('Failed to fetch stories:', getErrorMessage(error))
    throw error
  }
}

// Example 2: Create a new story
async function createNewStory() {
  try {
    const request: CreateStoryRequest = {
      prompt: 'A story about a Space Marine squad exploring a derelict ship',
      theme_id: 'warhammer40k',
    }
    const session = await apiClient.createStory(request)
    console.log(`Story generation started: ${session.id}`)
    return session
  } catch (error) {
    console.error('Failed to create story:', getErrorMessage(error))
    throw error
  }
}

// Example 3: Check generation status
async function checkGenerationStatus(sessionId: string) {
  try {
    const status = await apiClient.getGenerationStatus(sessionId)
    console.log(`Generation ${status.progress_percent}% complete`)
    return status
  } catch (error) {
    console.error('Failed to check status:', getErrorMessage(error))
    throw error
  }
}

// Example 4: Start a game
async function startNewGame(storyId: number) {
  try {
    const gameSession = await apiClient.startGame(storyId)
    console.log(`Game started: ${gameSession.session_id}`)
    return gameSession
  } catch (error) {
    console.error('Failed to start game:', getErrorMessage(error))
    throw error
  }
}

// Example 5: Send a game command
async function sendGameCommand(sessionId: string, commandText: string) {
  try {
    const command: GameCommand = { command: commandText }
    const response = await apiClient.sendCommand(sessionId, command)
    console.log('Game response:', response.output)
    return response
  } catch (error) {
    console.error('Failed to send command:', getErrorMessage(error))
    throw error
  }
}

// Example 6: Fetch themes
async function fetchThemes() {
  try {
    const themes = await apiClient.getThemes()
    console.log(`Found ${themes.length} themes`)
    return themes
  } catch (error) {
    console.error('Failed to fetch themes:', getErrorMessage(error))
    throw error
  }
}

// Example 7: React component usage
import { useState, useEffect } from 'react'
import type { Story } from './types'

function StoriesComponent() {
  const [stories, setStories] = useState<Story[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadStories() {
      try {
        setLoading(true)
        const data = await apiClient.getStories({ page: 1, page_size: 10 })
        setStories(data.items)
        setError(null)
      } catch (err) {
        setError(getErrorMessage(err))
      } finally {
        setLoading(false)
      }
    }

    loadStories()
  }, [])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  return (
    <div>
      {stories.map((story) => (
        <div key={story.id}>{story.title}</div>
      ))}
    </div>
  )
}

// Example 8: Error handling with retry
import { AppError } from '../utils/errorHandler'

async function fetchWithRetry() {
  try {
    const story = await apiClient.getStory(1)
    return story
  } catch (error) {
    if (error instanceof AppError) {
      console.log(`Error code: ${error.code}`)
      console.log(`User message: ${error.userMessage}`)
      console.log(`Can retry: ${error.retryPossible}`)
      console.log(`Status: ${error.status}`)
    }
    throw error
  }
}

export {
  fetchStories,
  createNewStory,
  checkGenerationStatus,
  startNewGame,
  sendGameCommand,
  fetchThemes,
  StoriesComponent,
  fetchWithRetry,
}
