/**
 * Vite Configuration
 *
 * Configures the Vite build tool for our React application:
 * - React plugin for JSX transformation and Fast Refresh
 * - Path alias (@/) for cleaner imports instead of relative paths
 * - API proxy to forward /api requests to the Django backend during development,
 *   avoiding CORS issues in local development
 *
 * Vite docs: https://vitejs.dev/config/
 */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Allows importing from '@/components/...' instead of '../../components/...'
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    // Proxy API requests to Django backend during development
    // This avoids CORS issues since both frontend and API appear on same origin
    proxy: {
      '/api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
      },
    },
  },
});
