import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

const TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/tasks": "采集任务",
  "/users": "已抓用户",
  "/weibo": "微博列表",
  "/search": "全文搜索",
  "/settings": "配置",
  "/logs": "日志",
};

export function Layout() {
  const loc = useLocation();
  const title = TITLES[loc.pathname] || "weibo-crawler-next";
  return (
    <div className="flex min-h-screen bg-canvas">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        <TopBar title={title} />
        <div className="flex-1 px-6 py-6 max-w-[1400px] w-full mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
