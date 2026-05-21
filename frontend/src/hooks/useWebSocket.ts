import { useEffect, useRef, useState } from "react";
import type { DashboardTick } from "@/api/types";

type WSMessage = DashboardTick | { type: string; [k: string]: unknown };

/**
 * useWebSocket — 自动重连的 /ws 客户端.
 * 默认每 3 秒后端会推一次 dashboard_tick.
 */
export function useWebSocket(url = "/ws") {
  const [tick, setTick] = useState<DashboardTick | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let stopped = false;
    let reconnectTimer: number | undefined;

    function connect() {
      if (stopped) return;
      const proto = window.location.protocol === "https:" ? "wss" : "ws";
      const ws = new WebSocket(`${proto}://${window.location.host}${url}`);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        if (!stopped) reconnectTimer = window.setTimeout(connect, 3000);
      };
      ws.onerror = () => ws.close();
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data) as WSMessage;
          if (msg.type === "dashboard_tick") setTick(msg as DashboardTick);
        } catch {
          /* ignore */
        }
      };
    }

    connect();
    return () => {
      stopped = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      wsRef.current?.close();
    };
  }, [url]);

  return { tick, connected };
}
