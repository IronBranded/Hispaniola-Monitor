import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/hispaniola-monitor/',
  build: {
    outDir: 'dist',
    rollupOptions: {
      output: {
        manualChunks: {
          'deck': ['deck.gl', '@deck.gl/core', '@deck.gl/layers'],
          'globe': ['globe.gl'],
          'react': ['react', 'react-dom'],
        }
      }
    }
  }
})
