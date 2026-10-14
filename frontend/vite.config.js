import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// The FastAPI app serves the build under /static and answers /api itself;
// in development the Vite server proxies /api to a locally running backend.
export default defineConfig({
  base: '/static/',
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:47835',
    },
  },
  test: {
    environment: 'jsdom',
  },
});
