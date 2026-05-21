import { jsx as _jsx } from "react/jsx-runtime";
import { createBrowserRouter } from "react-router-dom";
import { Layout } from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import Tasks from "@/pages/Tasks";
import Users from "@/pages/Users";
import Weibo from "@/pages/Weibo";
import Search from "@/pages/Search";
import Settings from "@/pages/Settings";
import Logs from "@/pages/Logs";
export const router = createBrowserRouter([
    {
        path: "/",
        element: _jsx(Layout, {}),
        children: [
            { index: true, element: _jsx(Dashboard, {}) },
            { path: "tasks", element: _jsx(Tasks, {}) },
            { path: "users", element: _jsx(Users, {}) },
            { path: "weibo", element: _jsx(Weibo, {}) },
            { path: "search", element: _jsx(Search, {}) },
            { path: "settings", element: _jsx(Settings, {}) },
            { path: "logs", element: _jsx(Logs, {}) },
        ],
    },
]);
