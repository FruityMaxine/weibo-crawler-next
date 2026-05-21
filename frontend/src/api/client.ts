import type {
  CrawlTask,
  HealthResponse,
  SearchResponse,
  User,
  Weibo,
} from "./types";

const BASE = "";  // 通过 Vite proxy 走 /api/*

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  if (!r.ok) {
    throw new Error(`${r.status} ${r.statusText}: ${await r.text()}`);
  }
  return r.json();
}

export const api = {
  health: () => req<HealthResponse>("/healthz"),
  listUsers: (limit = 50) => req<User[]>(`/api/users?limit=${limit}`),
  getUser: (uid: number) => req<User>(`/api/users/${uid}`),
  refreshUser: (uid: number) =>
    req<User>(`/api/users/${uid}/refresh`, { method: "POST" }),

  listWeibo: (uid?: number, limit = 50) =>
    req<Weibo[]>(`/api/weibo?${uid ? `uid=${uid}&` : ""}limit=${limit}`),

  listTasks: () => req<CrawlTask[]>("/api/tasks"),
  createTask: (payload: {
    name: string;
    uid?: number;
    query?: string;
    max_count?: number;
    only_original?: boolean;
  }) =>
    req<CrawlTask>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getTask: (id: number) => req<CrawlTask>(`/api/tasks/${id}`),

  search: (q: string, limit = 50) =>
    req<SearchResponse>(`/api/search?q=${encodeURIComponent(q)}&limit=${limit}`),
};
