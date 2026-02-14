import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://194.150.220.138:8443',
        changeOrigin: true,
        secure: false, 
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  }
})
