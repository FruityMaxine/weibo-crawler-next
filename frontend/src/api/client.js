const BASE = ""; // 通过 Vite proxy 走 /api/*
async function req(path, init) {
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
    health: () => req("/healthz"),
    listUsers: (limit = 50) => req(`/api/users?limit=${limit}`),
    getUser: (uid) => req(`/api/users/${uid}`),
    refreshUser: (uid) => req(`/api/users/${uid}/refresh`, { method: "POST" }),
    listWeibo: (uid, limit = 50) => req(`/api/weibo?${uid ? `uid=${uid}&` : ""}limit=${limit}`),
    listTasks: () => req("/api/tasks"),
    createTask: (payload) => req("/api/tasks", {
        method: "POST",
        body: JSON.stringify(payload),
    }),
    getTask: (id) => req(`/api/tasks/${id}`),
    search: (q, limit = 50) => req(`/api/search?q=${encodeURIComponent(q)}&limit=${limit}`),
};
