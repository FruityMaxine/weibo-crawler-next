import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, ListChecks, Users, MessageSquare,
  Search, Settings as SettingsIcon, ScrollText
} from "lucide-react";
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
  return (
    <aside className="hidden md:flex h-screen w-60 flex-col border-r border-hairline bg-surface px-4 py-5">
      <div className="mb-6 flex items-center gap-2">
        <div className="h-8 w-8 rounded-md bg-primary/20 grid place-items-center">
          <span className="text-primary font-bold text-sm">w</span>
        </div>
        <div className="flex flex-col leading-tight">
          <span className="text-ink text-sm font-semibold">weibo-crawler-next</span>
          <span className="text-ink-subtle text-[10px] font-mono">v0.8.0.0</span>
        </div>
      </div>
      <nav className="flex flex-col gap-0.5 flex-1">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                "text-ink-muted hover:text-ink hover:bg-surface-2",
                isActive && "bg-primary/15 text-primary font-medium"
              )
            }
          >
            <Icon size={16} strokeWidth={1.75} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="mt-4 pt-4 border-t border-hairline text-[10px] text-ink-tertiary leading-relaxed">
        Linear design × React Bits<br />
        <span className="text-ink-subtle">FastAPI 28800</span>
      </div>
    </aside>
  );
}
