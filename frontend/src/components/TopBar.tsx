import { useWebSocket } from "@/hooks/useWebSocket";
import { useHealth } from "@/api/hooks";

export function TopBar({ title }: { title: string }) {
  const { connected } = useWebSocket();
  const { data: health } = useHealth();

  return (
    <header className="sticky top-0 z-10 flex items-center justify-between border-b border-hairline bg-canvas/85 backdrop-blur px-6 py-3.5">
      <div className="flex items-baseline gap-3">
        <h1 className="text-ink text-lg font-semibold tracking-tightx">{title}</h1>
        <span className="text-ink-subtle text-xs font-mono">
          {health ? `· ${health.version}` : ""}
        </span>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs">
          <span
            className={`h-2 w-2 rounded-full ${connected ? "bg-success animate-pulse-glow" : "bg-danger"}`}
          />
          <span className="text-ink-muted">{connected ? "WS 已连接" : "WS 断开"}</span>
        </div>
        <div className="text-ink-subtle text-xs">
          {health?.status === "ok" ? "API ✓" : "API ✗"}
        </div>
      </div>
    </header>
  );
}
