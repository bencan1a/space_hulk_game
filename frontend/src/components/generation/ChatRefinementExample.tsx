import React from 'react'
import { ChatInterface } from './ChatInterface'
import { spaceHulkQuestions } from './chatQuestions'

/**
 * Example usage of the ChatInterface component for story generation
 * 
 * This demonstrates the chat refinement flow where users answer a series
 * of questions to build a detailed prompt for story generation.
 */

// Example component demonstrating ChatInterface usage
export const ChatRefinementExample: React.FC = () => {
  const handleComplete = (answers: Record<string, string>): void => {
    console.log('Chat refinement complete!')
    console.log('User answers:', answers)
    console.log('Final prompt:', answers.finalPrompt)
    
    // In a real application, you would:
    // 1. Send the finalPrompt to the generation API
    // 2. Navigate to the generation progress page
    // 3. Show the WebSocket-based progress updates
  }

  const handleCancel = () => {
    console.log('User cancelled chat refinement')
    // In a real application, you would navigate back to template selection
  }

  return (
    <div style={{ height: '100vh', padding: '2rem' }}>
      <ChatInterface
        questions={spaceHulkQuestions}
        onComplete={handleComplete}
        onCancel={handleCancel}
      />
    </div>
  )
}

/**
 * Integration notes:
 * 
 * 1. The ChatInterface component can be integrated into the story creation flow
 *    as an alternative to the CustomPromptForm component.
 * 
 * 2. It should be displayed after the user selects a template or chooses
 *    "Chat Refinement" option from the TemplateGallery.
 * 
 * 3. The onComplete callback receives all answers including a generated
 *    finalPrompt that combines all user responses.
 * 
 * 4. Questions can be customized based on the selected template, allowing
 *    template-specific refinement flows.
 * 
 * 5. The component manages its own state and provides progress indication
 *    to the user as they answer questions.
 */

