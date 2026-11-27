import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        // Port 8000 by default. Overridable because it is a popular port and
        // another local service holding it otherwise 404s every /api call --
        // including the e2e suite, whose in-page fetches all go through here.
        target: process.env.ATLASCODE_API_ORIGIN || 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
