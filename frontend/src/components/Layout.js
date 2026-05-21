import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
const TITLES = {
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
    return (_jsxs("div", { className: "flex min-h-screen bg-canvas", children: [_jsx(Sidebar, {}), _jsxs("main", { className: "flex-1 flex flex-col", children: [_jsx(TopBar, { title: title }), _jsx("div", { className: "flex-1 px-6 py-6 max-w-[1400px] w-full mx-auto", children: _jsx(Outlet, {}) })] })] }));
}
