import { defineConfig } from 'vite';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  server: {
    allowedHosts: ['5173-iwuw5tvoest2kjowsk11q-14950869.sg1.manus.computer', 'localhost', '127.0.0.1'],
    proxy: { '/api': { target: 'http://127.0.0.1:5000', changeOrigin: true } },
  },
  resolve: {
    alias: {
      'three/addons': fileURLToPath(new URL('./node_modules/three/examples/jsm', import.meta.url)),
    },
  },
});
