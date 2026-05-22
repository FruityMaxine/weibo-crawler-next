import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

// 与后端 wcn serve 端口对齐: 同一 WCN_PORT env 驱动两端.
// 后端 28800 被占? 一行命令换端口 (前后端同时):
//   WCN_PORT=28801 wcn serve
//   WCN_PORT=28801 npm run dev
const BACKEND_PORT = Number(process.env.WCN_PORT) || 28800;
const FRONTEND_PORT = Number(process.env.WCN_DEV_PORT) || 5173;

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  server: {
    host: "127.0.0.1",
    port: FRONTEND_PORT,
    strictPort: false,  // 占用时 vite 自动递增 (5174, 5175, ...)
    proxy: {
      "/api": {
        target: `http://127.0.0.1:${BACKEND_PORT}`,
        changeOrigin: true,
      },
      "/ws": {
        target: `ws://127.0.0.1:${BACKEND_PORT}`,
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
