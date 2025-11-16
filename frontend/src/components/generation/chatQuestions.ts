import { ChatQuestion } from './ChatInterface'

/**
 * Example question sets for chat refinement
 */

// Example questions for space hulk game generation
export const spaceHulkQuestions: ChatQuestion[] = [
  {
    id: 'theme',
    question: 'What overall theme would you like for your Space Hulk game?',
    minLength: 10,
    maxLength: 200,
    validationMessage: 'Please provide at least 10 characters to describe the theme',
  },
  {
    id: 'setting',
    question: 'Describe the setting and location where the game takes place.',
    minLength: 20,
    maxLength: 300,
    validationMessage: 'Please provide more details about the setting (minimum 20 characters)',
  },
  {
    id: 'atmosphere',
    question: 'What kind of atmosphere and mood should the game have?',
    minLength: 15,
    maxLength: 250,
    validationMessage: 'Please describe the atmosphere in more detail (minimum 15 characters)',
  },
  {
    id: 'objective',
    question: 'What is the primary objective or mission for the player?',
    minLength: 15,
    maxLength: 250,
    validationMessage: 'Please describe the objective in more detail (minimum 15 characters)',
  },
  {
    id: 'difficulty',
    question: 'What difficulty level would you prefer? (e.g., easy, medium, hard, nightmare)',
    minLength: 4,
    maxLength: 100,
    validationMessage: 'Please specify a difficulty level',
  },
]

// Example with custom questions
export const customQuestionsExample: ChatQuestion[] = [
  {
    id: 'genre',
    question: 'What genre would you like? (horror, sci-fi, mystery, etc.)',
    minLength: 5,
    maxLength: 50,
  },
  {
    id: 'protagonist',
    question: 'Who is the main character?',
    minLength: 10,
    maxLength: 200,
  },
  {
    id: 'conflict',
    question: 'What is the main conflict or challenge?',
    minLength: 15,
    maxLength: 250,
  },
]
