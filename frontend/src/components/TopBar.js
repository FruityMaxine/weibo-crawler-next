import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useHealth } from "@/api/hooks";
export function TopBar({ title }) {
    const { connected } = useWebSocket();
    const { data: health } = useHealth();
    return (_jsxs("header", { className: "sticky top-0 z-10 flex items-center justify-between border-b border-hairline bg-canvas/85 backdrop-blur px-6 py-3.5", children: [_jsxs("div", { className: "flex items-baseline gap-3", children: [_jsx("h1", { className: "text-ink text-lg font-semibold tracking-tightx", children: title }), _jsx("span", { className: "text-ink-subtle text-xs font-mono", children: health ? `· ${health.version}` : "" })] }), _jsxs("div", { className: "flex items-center gap-4", children: [_jsxs("div", { className: "flex items-center gap-2 text-xs", children: [_jsx("span", { className: `h-2 w-2 rounded-full ${connected ? "bg-success animate-pulse-glow" : "bg-danger"}` }), _jsx("span", { className: "text-ink-muted", children: connected ? "WS 已连接" : "WS 断开" })] }), _jsx("div", { className: "text-ink-subtle text-xs", children: health?.status === "ok" ? "API ✓" : "API ✗" })] })] }));
}
