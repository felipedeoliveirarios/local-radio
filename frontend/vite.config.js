import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/queue": "http://localhost:8000",
      "/now-playing": "http://localhost:8000",
      "/admin": "http://localhost:8000",
      "/qrcode": "http://localhost:8000",
    },
  },
});
