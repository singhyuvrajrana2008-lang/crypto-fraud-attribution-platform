import { defineConfig } from 'vite';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  server: {
    allowedHosts: true,
    proxy: { '/api': { target: 'http://127.0.0.1:5000', changeOrigin: true } },
  },
  resolve: {
    alias: {
      'three/addons': fileURLToPath(new URL('./node_modules/three/examples/jsm', import.meta.url)),
    },
  },
});
