import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// Production build: hashed assets under dist/assets (FRONTEND.md §12).
export default defineConfig({
  plugins: [vue()],
})
