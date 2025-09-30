import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    sourcemap: 'inline', // Включает source maps для production
  },
  server: {
    sourcemap: 'inline', // Включает source maps для development
  }
})
