import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
import { Terminal } from "lucide-react";
export default function Logs() {
    return (_jsxs(SpotlightCard, { className: "p-5", children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx(Terminal, { size: 16, className: "text-primary" }), _jsx("h3", { className: "text-ink font-semibold", children: "\u65E5\u5FD7\u67E5\u770B" })] }), _jsx("div", { className: "text-ink-muted text-sm mb-3", children: "\u9ED8\u8BA4\u65E5\u5FD7\u8F93\u51FA stderr (uvicorn / APScheduler / wcn). \u542F\u7528\u6587\u4EF6\u65E5\u5FD7:" }), _jsx("pre", { className: "bg-surface-2 border border-hairline rounded-md p-3 text-xs font-mono text-ink-muted overflow-x-auto", children: `# .env 中加入
WCN_LOG_FILE=./data/wcn.log

# 然后查看
tail -f ./data/wcn.log

# 或 systemd
journalctl -u wcn-api -f` }), _jsx("div", { className: "mt-4 text-ink-subtle text-xs", children: "Tick 5 \u5C06\u63D0\u4F9B WebSocket \u5B9E\u65F6\u65E5\u5FD7\u6D41 + level \u8FC7\u6EE4 + \u865A\u62DF\u5217\u8868." })] }));
}
