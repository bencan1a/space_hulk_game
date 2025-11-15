// Type definitions for the Space Hulk Game frontend
// This file will be expanded as the application grows

export interface Game {
  id: string
  title: string
  description: string
  createdAt: string
  updatedAt: string
}

export interface GameSession {
  id: string
  gameId: string
  state: string
  createdAt: string
}

export * from './theme'
export * from './story'
