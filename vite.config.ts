import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: [
      "617d6955-e336-447e-9336-782340268964.preview.emergentagent.com",
      "14cd1f93-550c-4800-ac60-39195504d5ec.preview.emergentagent.com"
    ]
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
});
