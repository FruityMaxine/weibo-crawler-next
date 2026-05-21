export interface User {
  uid: number;
  screen_name: string;
  description?: string | null;
  verified: boolean;
  statuses_count: number;
  followers_count: number;
  follow_count: number;
  avatar_hd?: string | null;
  profile_url?: string | null;
}

export interface Weibo {
  weibo_id: string;
  uid: number;
  text: string;
  source?: string | null;
  pic_urls: string[];
  video_url?: string | null;
  is_retweet: boolean;
  attitudes_count: number;
  comments_count: number;
  reposts_count: number;
  created_at?: string | null;
}

export type TaskStatus = "pending" | "running" | "success" | "failed" | "paused";

export interface CrawlTask {
  id: number;
  name: string;
  uid: number | null;
  query: string | null;
  status: TaskStatus;
  progress: number;
  total_fetched: number;
  error: string | null;
  config_snapshot: Record<string, unknown> | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface SearchHit {
  weibo_id: string;
  uid: number;
  snippet: string;
  score: number;
  text: string;
  created_at: string | null;
}

export interface SearchResponse {
  query: string;
  count: number;
  hits: SearchHit[];
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  ts: string;
}

export interface DashboardTick {
  type: "dashboard_tick";
  ts: string;
  stats: { users: number; weibos: number; tasks: number };
  recent_tasks: Array<{
    id: number;
    name: string;
    status: TaskStatus;
    progress: number;
    total_fetched: number;
  }>;
}
