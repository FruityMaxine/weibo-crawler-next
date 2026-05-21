import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { NavLink } from "react-router-dom";
import { LayoutDashboard, ListChecks, Users, MessageSquare, Search, Settings as SettingsIcon, ScrollText } from "lucide-react";
import { cn } from "@/lib/cn";
const NAV = [
    { to: "/", label: "Dashboard", icon: LayoutDashboard },
    { to: "/tasks", label: "Tasks", icon: ListChecks },
    { to: "/users", label: "Users", icon: Users },
    { to: "/weibo", label: "Weibo", icon: MessageSquare },
    { to: "/search", label: "Search", icon: Search },
    { to: "/settings", label: "Settings", icon: SettingsIcon },
    { to: "/logs", label: "Logs", icon: ScrollText },
];
export function Sidebar() {
    return (_jsxs("aside", { className: "hidden md:flex h-screen w-60 flex-col border-r border-hairline bg-surface px-4 py-5", children: [_jsxs("div", { className: "mb-6 flex items-center gap-2", children: [_jsx("div", { className: "h-8 w-8 rounded-md bg-primary/20 grid place-items-center", children: _jsx("span", { className: "text-primary font-bold text-sm", children: "w" }) }), _jsxs("div", { className: "flex flex-col leading-tight", children: [_jsx("span", { className: "text-ink text-sm font-semibold", children: "weibo-crawler-next" }), _jsx("span", { className: "text-ink-subtle text-[10px] font-mono", children: "v0.3.0.0" })] })] }), _jsx("nav", { className: "flex flex-col gap-0.5 flex-1", children: NAV.map(({ to, label, icon: Icon }) => (_jsxs(NavLink, { to: to, end: to === "/", className: ({ isActive }) => cn("flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors", "text-ink-muted hover:text-ink hover:bg-surface-2", isActive && "bg-primary/15 text-primary font-medium"), children: [_jsx(Icon, { size: 16, strokeWidth: 1.75 }), _jsx("span", { children: label })] }, to))) }), _jsxs("div", { className: "mt-4 pt-4 border-t border-hairline text-[10px] text-ink-tertiary leading-relaxed", children: ["Linear design \u00D7 React Bits", _jsx("br", {}), _jsx("span", { className: "text-ink-subtle", children: "FastAPI 28800" })] })] }));
}
