import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    cors: true,
    proxy : {
      '/api' : {
        target : 'https://api.bull-bear.app',
        changeOrigin : true,
        secure : true
      }
    }

  }

})
