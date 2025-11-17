import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.ts',
    passWithNoTests: true,
    watch: false,
    testTimeout: 5000,
    teardownTimeout: 5000,
    // Prevent hanging by forcing cleanup
    clearMocks: true,
    mockReset: true,
    restoreMocks: true,
  },
})
