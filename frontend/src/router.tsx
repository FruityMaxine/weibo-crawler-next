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
    element: <Layout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "tasks", element: <Tasks /> },
      { path: "users", element: <Users /> },
      { path: "weibo", element: <Weibo /> },
      { path: "search", element: <Search /> },
      { path: "settings", element: <Settings /> },
      { path: "logs", element: <Logs /> },
    ],
  },
]);
