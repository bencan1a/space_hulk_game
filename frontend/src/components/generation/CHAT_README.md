# Chat Refinement UI Components

This directory contains the Chat Refinement UI components that provide a conversational interface for guiding users through story generation prompts.

## Components

### ChatMessage

Displays individual messages in the chat interface from either the user or the AI assistant.

**Props:**

- `role`: 'user' | 'assistant' - Determines message styling and layout
- `content`: string - The message text to display
- `timestamp?`: string - Optional timestamp to show when message was sent

**Features:**

- Distinct styling for user vs assistant messages
- Slide-in animation for new messages
- Responsive design with max-width constraints
- Supports multiline content

**Usage:**

```tsx
<ChatMessage
  role="assistant"
  content="What theme would you like for your game?"
  timestamp="12:34 PM"
/>
```

### ChatInput

Input component for capturing user responses with built-in validation.

**Props:**

- `onSubmit`: (message: string) => void - Callback when user submits a message
- `placeholder?`: string - Input placeholder text
- `disabled?`: boolean - Whether input is disabled
- `minLength?`: number - Minimum character length (default: 1)
- `maxLength?`: number - Maximum character length (default: 500)
- `validationMessage?`: string - Custom validation error message
- `autoFocus?`: boolean - Whether to auto-focus the input

**Features:**

- Real-time character count display
- Validation with error messages
- Submit on Enter (Shift+Enter for new line)
- Auto-clear after submission
- Trims whitespace from input
- Accessible with ARIA attributes

**Usage:**

```tsx
<ChatInput
  onSubmit={(message) => console.log(message)}
  placeholder="Type your answer..."
  minLength={10}
  maxLength={200}
  autoFocus
/>
```

### ChatInterface

Main component that orchestrates the conversational flow through a series of questions.

**Props:**

- `questions`: ChatQuestion[] - Array of questions to ask
- `onComplete?`: (answers: Record<string, string>) => void - Callback when all questions answered
- `onCancel?`: () => void - Callback when user cancels
- `initialMessages?`: ChatMessageProps[] - Optional initial messages

**ChatQuestion Type:**

```typescript
interface ChatQuestion {
  id: string              // Unique identifier for the question
  question: string        // The question text to display
  minLength?: number      // Minimum answer length
  maxLength?: number      // Maximum answer length
  validationMessage?: string  // Custom validation message
}
```

**Features:**

- Sequential question flow with progress indicator
- Stores all user answers with question IDs
- Generates final combined prompt from all answers
- Auto-scroll to latest messages
- Confirmation screen with final prompt preview
- "Start Over" and "Generate Story" actions

**Usage:**

```tsx
const questions: ChatQuestion[] = [
  {
    id: 'theme',
    question: 'What theme would you like?',
    minLength: 10,
    maxLength: 200,
  },
  {
    id: 'setting',
    question: 'Describe the setting.',
    minLength: 20,
    maxLength: 300,
  },
]

<ChatInterface
  questions={questions}
  onComplete={(answers) => {
    console.log('Answers:', answers)
    console.log('Final prompt:', answers.finalPrompt)
  }}
  onCancel={() => console.log('Cancelled')}
/>
```

## Styling

All components use CSS Modules for scoped styling with the following design tokens:

- `--color-text`: Primary text color
- `--color-text-secondary`: Secondary text color
- `--color-text-tertiary`: Tertiary text color
- `--color-surface`: Primary surface background
- `--color-surface-secondary`: Secondary surface background
- `--color-background`: Main background color
- `--color-border`: Border color
- `--color-primary`: Primary brand color (red)
- `--color-primary-dark`: Darker primary color
- `--color-accent`: Accent color (green)

## Accessibility

All components follow accessibility best practices:

- Semantic HTML with proper roles (`article`, `log`, `progressbar`)
- ARIA labels and descriptions
- Keyboard navigation support
- Live regions for dynamic content
- Clear focus indicators
- Screen reader friendly

## Testing

Each component has comprehensive test coverage:

- **ChatMessage**: 8 tests covering rendering, roles, timestamps, multiline content
- **ChatInput**: 17 tests covering validation, submission, keyboard events, character limits
- **ChatInterface**: 13 tests covering question flow, progress, completion, cancellation

Run tests with:

```bash
npm test
```

## Integration Example

See `ChatRefinementExample.tsx` for a complete integration example showing:

1. How to define questions for Space Hulk game generation
2. How to handle completion and cancellation
3. How to integrate with the broader application flow

## Animation

Components include smooth animations:

- Message slide-in effect (0.3s ease)
- Progress bar transitions (0.5s ease)
- Button hover effects (0.2s ease)
- Smooth auto-scroll behavior

## Responsive Design

All components are fully responsive with:

- Flexible layouts using flexbox
- Percentage-based widths
- Media queries for mobile devices (<768px)
- Touch-friendly button sizes
- Scrollable message containers

## Browser Support

Components are compatible with:

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Requires ES6+ support
