# API 参考

> 后端 FastAPI 自动生成的 OpenAPI 在 `http://127.0.0.1:28800/docs` (Swagger UI) 和 `/redoc`.

---

## REST endpoints

### 健康检查

```
GET  /healthz
GET  /health      (别名)
```

返回:
```json
{
  "status": "ok",
  "service": "weibo-crawler-next",
  "version": "0.4.0.0",
  "ts": "2026-05-22T00:00:00+00:00"
}
```

---

### Users

```
GET  /api/users?limit=50&offset=0
GET  /api/users/{uid}
POST /api/users/{uid}/refresh        # 同步触发用户信息刷新
```

UserOut:
```json
{
  "uid": 1669879400,
  "screen_name": "迪丽热巴",
  "description": "...",
  "verified": true,
  "statuses_count": 1234,
  "followers_count": 56789012,
  "follow_count": 78,
  "avatar_hd": "https://...",
  "profile_url": "https://m.weibo.cn/u/1669879400"
}
```

---

### Weibo

```
GET  /api/weibo?uid=<uid>&limit=50
```

WeiboOut:
```json
{
  "weibo_id": "1234567890",
  "uid": 1669879400,
  "text": "...",
  "source": "iPhone 15 Pro",
  "pic_urls": ["https://...", "https://..."],
  "video_url": null,
  "is_retweet": false,
  "attitudes_count": 1234,
  "comments_count": 567,
  "reposts_count": 89,
  "created_at": "2026-05-21T12:34:56+00:00"
}
```

---

### Tasks (异步采集任务)

```
GET  /api/tasks
POST /api/tasks
GET  /api/tasks/{task_id}
```

POST body:
```json
{
  "name": "周末抓 X 用户",
  "uid": 1669879400,
  "max_count": 100,
  "only_original": false,
  "cookie_override": null
}
```

TaskOut:
```json
{
  "id": 1,
  "name": "...",
  "uid": 1669879400,
  "status": "running",
  "progress": 45,
  "total_fetched": 45,
  "error": null,
  "config_snapshot": {...},
  "created_at": "...",
  "started_at": "...",
  "finished_at": null
}
```

`status`: `pending | running | success | failed | paused`

---

### Search (SQLite FTS5)

```
GET  /api/search?q=<expr>&limit=50
```

`q` 支持 FTS5 表达式: `编程`, `编程 AND Python`, `Python OR Rust`, `"hello world"`.

返回:
```json
{
  "query": "Python",
  "count": 1,
  "hits": [
    {
      "weibo_id": "FTS_PY1",
      "uid": 88888,
      "snippet": "<mark>Python</mark> 与 React 全栈开发...",
      "score": -0.96,
      "text": "...",
      "created_at": "2026-05-21T16:00:00+00:00"
    }
  ]
}
```

---

## WebSocket

```
GET  /ws
```

接入后服务端立即推一次 dashboard snapshot, 之后每 3s 一次心跳:

```json
{
  "type": "dashboard_tick",
  "ts": "2026-05-22T00:00:00+00:00",
  "stats": {"users": 12, "weibos": 4567, "tasks": 8},
  "recent_tasks": [
    {"id": 1, "name": "...", "status": "running", "progress": 45, "total_fetched": 45},
    ...
  ]
}
```

客户端可发 `{"type": "ping"}` 测试连通, 服务端响 `{"type": "pong"}`.

---

## Python SDK (内嵌客户端)

```python
from backend.app.crawler import AsyncWeiboClient

async with AsyncWeiboClient() as client:
    user_payload = await client.get_user_info(1669879400)
    page1 = await client.get_user_weibo_page(1669879400, page=1)
    comments = await client.get_weibo_comments("1234567890")
    reposts = await client.get_weibo_reposts("1234567890", page=1)
```

参数:
- `cookie`: 覆盖默认 cookie (字符串)
- `cookie_pool`, `proxy_pool`, `ua_pool`: 注入 anti_ban 池
- `rate_per_sec`, `timeout`: 限频与超时

---

## CLI 速查

```
wcn version           打印版本
wcn info              显示当前配置摘要
wcn run -u <uid>      前台抓取单用户
wcn user <uid>        查本地用户
wcn weibo --uid <uid> 列本地微博
wcn tasks             列采集任务
wcn export -f <fmt>   导出 (csv/json/sqlite/mysql/mongodb/webhook)
wcn exporters         列出可用格式
wcn serve             启 FastAPI 后端
wcn tui               启 Textual TUI
```

---

## 错误码

| HTTP | 含义 |
|---|---|
| 200 | OK |
| 400 | 请求参数无效 (e.g. uid+query 同时为空) |
| 404 | 资源不存在 (用户未抓 / 任务 ID 不存在) |
| 422 | pydantic 校验失败 |
| 500 | 服务端内部错误 (含 anti_ban 触发的限频降级) |

错误响应:
```json
{ "detail": "<错误信息>" }
```
或 pydantic 详细:
```json
{ "detail": [{"type": "...", "loc": [...], "msg": "..."}] }
```
