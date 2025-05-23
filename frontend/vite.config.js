import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // Changed port to 5000 to match your Flask app
        changeOrigin: true,
        secure: false
      },
      '/models': {
        target: 'http://localhost:5000', // Added proxy for /models path
        changeOrigin: true,
        secure: false
      }
    }
  }
});
