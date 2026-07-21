import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const websiteApiBaseUrl = process.env.VITE_WEBSITE_API_BASE_URL ?? "http://localhost:8001";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: websiteApiBaseUrl,
        changeOrigin: true,
      },
    },
  },
});