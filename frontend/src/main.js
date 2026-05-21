import { jsx as _jsx } from "react/jsx-runtime";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./styles/theme.css";
import { router } from "./router";
const qc = new QueryClient({
    defaultOptions: {
        queries: { staleTime: 4000, retry: 1, refetchOnWindowFocus: false },
    },
});
createRoot(document.getElementById("root")).render(_jsx(StrictMode, { children: _jsx(QueryClientProvider, { client: qc, children: _jsx(RouterProvider, { router: router }) }) }));
