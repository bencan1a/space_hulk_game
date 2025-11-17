// Import jest-dom matchers for vitest
// This provides custom matchers like toBeInTheDocument(), toHaveTextContent(), etc.
import { expect } from 'vitest'
import * as matchers from '@testing-library/jest-dom/matchers'

// Extend vitest's expect with jest-dom matchers
expect.extend(matchers)
