# Space Hulk Game - Frontend

Browser-based game creation and play interface built with React, TypeScript, and Vite.

## Features

- **React 18**: Modern React with TypeScript support
- **Vite**: Lightning-fast build tool with HMR
- **React Router v6**: Client-side routing for SPA
- **TypeScript**: Full type safety with strict mode
- **ESLint**: Code quality enforcement
- **Prettier**: Consistent code formatting

## Project Structure

```
frontend/
├── public/
│   └── favicon.svg          # Application icon
├── src/
│   ├── main.tsx            # Application entry point
│   ├── App.tsx             # Root component with routing
│   ├── components/
│   │   ├── Layout.tsx      # Main layout wrapper
│   │   └── common/
│   │       ├── Header.tsx  # Navigation header
│   │       └── Footer.tsx  # Footer component
│   ├── pages/
│   │   ├── HomePage.tsx    # Landing page
│   │   ├── LibraryPage.tsx # Game library browser
│   │   ├── CreatePage.tsx  # Game creation interface
│   │   └── PlayPage.tsx    # Game play interface
│   ├── contexts/           # React contexts (future)
│   ├── services/           # API services (future)
│   ├── styles/
│   │   └── index.css       # Global styles
│   └── types/
│       └── index.ts        # TypeScript type definitions
├── index.html              # HTML entry point
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
├── tsconfig.node.json      # TypeScript config for Vite
├── vite.config.ts          # Vite configuration
├── .eslintrc.cjs           # ESLint configuration
├── .prettierrc             # Prettier configuration
└── README.md               # This file
```

## Prerequisites

- Node.js 18+ or compatible runtime
- npm, yarn, or pnpm

## Installation

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

## Development

### Start Development Server

```bash
npm run dev
```

The application will be available at <http://localhost:3000>

Features:

- Hot Module Replacement (HMR)
- Fast refresh for React components
- API proxy to backend at <http://localhost:8000>
- WebSocket proxy for real-time updates

### Available Routes

- `/` - Home page
- `/library` - Browse game library
- `/create` - Create new game
- `/play/:id` - Play game by ID

## Code Quality

### Linting

Run ESLint to check for code issues:

```bash
npm run lint
```

ESLint is configured with:

- TypeScript support
- React hooks rules
- React Refresh plugin

### Formatting

Format code with Prettier:

```bash
npm run format
```

Check formatting:

```bash
npx prettier --check "src/**/*.{ts,tsx,css}"
```

### Type Checking

Check TypeScript types without emitting files:

```bash
npx tsc --noEmit
```

## Building for Production

Build optimized production bundle:

```bash
npm run build
```

Output will be in the `dist/` directory.

Preview production build:

```bash
npm run preview
```

## Configuration

### Vite Configuration

The `vite.config.ts` file includes:

- React plugin with Fast Refresh
- Development server on port 3000
- Proxy configuration for backend API
- WebSocket proxy for real-time features

### TypeScript Configuration

Strict mode enabled with:

- No unused locals
- No unused parameters
- No fallthrough cases in switch statements
- Full type checking

### API Proxy

All requests to `/api/*` are proxied to `http://localhost:8000` in development.

WebSocket connections to `/ws` are proxied to `ws://localhost:8000`.

## Component Guidelines

### Component Structure

```typescript
import { ReactNode } from 'react'

interface MyComponentProps {
  children?: ReactNode
  title: string
}

function MyComponent({ children, title }: MyComponentProps) {
  return (
    <div>
      <h2>{title}</h2>
      {children}
    </div>
  )
}

export default MyComponent
```

### Styling

- Use CSS classes defined in `src/styles/index.css`
- Follow BEM naming convention for new styles
- Keep styles modular and component-focused

## Next Steps

This is the foundation frontend setup (Task 1.3). Future tasks will add:

- State management (Context API or Redux)
- API integration with backend
- WebSocket connection for real-time game updates
- Game creation wizard
- Interactive game play interface
- User authentication
- Theming system (grimdark Warhammer 40K aesthetic)

## Troubleshooting

### Port Already in Use

If port 3000 is already in use, you can specify a different port:

```bash
npm run dev -- --port 3001
```

### Build Errors

Clear the build cache:

```bash
rm -rf dist node_modules/.vite
npm install
npm run build
```

### Type Errors

Ensure all dependencies are installed:

```bash
npm install
```

Run type checking to see specific errors:

```bash
npx tsc --noEmit
```

## Support

For issues or questions, refer to the main project documentation or create an issue in the repository.
