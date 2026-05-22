# 架构 (Architecture)

> weibo-crawler-next 的设计取舍, 模块边界与数据流图.

---

## 顶层视图

```
┌──────────────────────────────────────────────────────────────────┐
│                          Interface Layer                          │
│   CLI (click)   ·   TUI (Textual)   ·   WebUI (React + Vite)     │
└────────────┬──────────────────┬─────────────────────┬────────────┘
             │                  │                     │
             ▼                  ▼                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                        │
│   /api/users  /api/weibo  /api/tasks  /api/search  /ws  /healthz │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Service Layer                              │
│   UserService  ·  WeiboService  ·  TaskService                    │
└──────────────┬──────────────────────────┬────────────────────────┘
               │                          │
       ┌───────▼────────┐         ┌───────▼────────┐
       │  Crawler Core  │         │   Persistence  │
       │  AsyncWeibo    │         │  SQLAlchemy    │
       │  Client + Parser│        │  + alembic     │
       └───────┬────────┘         │  + FTS5        │
               │                  └────────────────┘
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Anti-Ban Layer                              │
│   CookiePool · ProxyPool · UAPool · TokenBucketLimiter            │
│   + retry (exp+jitter) + captcha detector                         │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                       m.weibo.cn API
```

---

## 模块边界

### `backend/app/crawler/`
- **职责**: HTTP 抓取 + 微博 API 端点封装 + 响应解析
- **不做**: 业务规则 (留给 service) / DB 落库 (留给 service)
- **依赖**: `anti_ban/` (限频/池) · `httpx` · `tenacity`

### `backend/app/services/`
- **职责**: 业务流程 (抓取-解析-去重-入库)
- **不做**: HTTP / 配置读取 (注入)
- **依赖**: `crawler/` · `db/`

### `backend/app/db/`
- **职责**: ORM model + session 工厂 + alembic + FTS5
- **不做**: 业务逻辑
- **依赖**: SQLAlchemy 2.0 async

### `backend/app/exporters/`
- **职责**: 把 Weibo 实体写到外部 (CSV/JSON/SQLite/MySQL/MongoDB/Webhook)
- **接口**: `BaseExporter` ABC + `@register_exporter("xxx")` 装饰器自注册
- **扩展**: 第三方一行 register 即可加新格式

### `backend/app/anti_ban/`
- **职责**: 多账号 cookie / proxy / UA 池 + 自适应限频 + 退避 + 验证码检测
- **接入点**: `AsyncWeiboClient` 构造函数接受 `cookie_pool` / `proxy_pool` / `ua_pool` 参数

### `backend/app/notifications/`
- **职责**: 任务成功/失败/系统事件外推 (Telegram/Discord/Email/Webhook)
- **接口**: `BaseNotifier` ABC + `dispatch_event()` 并发广播

### `cli/`
- **CLI 直跑**: `wcn run / serve / export / user / weibo / tasks / info / version`
- **TUI**: `wcn tui` → Textual App, 5 个 SCREEN, 上下键菜单

### `frontend/`
- **技术**: Vite 5 + React 18 + TS strict + Tailwind + TanStack Query
- **风格**: Linear DESIGN.md 暗色 + React Bits 动效组件
- **路由**: Dashboard / Tasks / Users / Weibo / Search / Settings / Logs

---

## 数据流: 一次"抓取用户微博"任务

```
1. WebUI POST /api/tasks (uid, max_count)
       │
2. tasks router → TaskService.create() → DB INSERT crawl_tasks
       │
3. FastAPI BackgroundTasks → executor.run_user_crawl(task_id)
       │
4. AsyncWeiboClient (含 cookie_pool/proxy_pool/ua_pool 注入)
       │
5. for each page:
     - rate_limiter.acquire()  ← Token Bucket 自适应限频
     - cookie_pool.acquire()    ← 选最健康 cookie
     - proxy_pool.acquire()     ← 选最快代理 (健康度+延迟加权)
     - httpx GET m.weibo.cn/api/container/getIndex
     - parse_weibo_card() → 标准化 dict
     - WeiboService.upsert() → DB ON CONFLICT DO UPDATE
     - FTS5 trigger 自动同步 weibos_fts 表
     - TaskService.update_progress() (每 5 条一次)
       │
6. 完成 → TaskService.finish() → WS hub.broadcast(task_update)
       │
7. (可选) dispatch_event(NotificationEvent("任务完成", ...))
       → Telegram / Discord / Email / Webhook 广播
```

---

## 关键设计取舍

| 决策 | 理由 |
|---|---|
| **不抄原 dataabc/weibo-crawler 代码** | 原项目同步 requests + 全局变量+ 巨型 weibo.py, 不可维护. 仅复用 API URL 知识. |
| **async 而非同步** | 抓取 IO 密集, asyncio 单进程跑 100 并发不破汗 |
| **SQLAlchemy 2.0 async + SQLite 默认** | 零依赖默认 + FTS5 全文搜索, 同时给 MySQL/Postgres 留 extras |
| **插件化 exporter / notifier** | 用 ABC + 装饰器 registry, 让社区零摩擦扩展 |
| **127.0.0.1 默认绑定** | 安全默认, 公网由反代 (Caddy/Nginx) 处理 TLS + 鉴权 |
| **anti_ban 5 子模块分离** | Cookie/Proxy/UA 池独立可拆, 单测友好, 可换实现 |
| **React Bits + Linear 暗色** | 工具型仪表盘最佳调性, 不引入重组件库, 5 个核心动效组件足够 |
| **WebSocket 心跳 vs 轮询** | 3s 一次 dashboard_tick 推送, 比轮询省 90% 请求 |

---

## 扩展点

### 加一个新的导出格式
```python
# backend/app/exporters/parquet_exporter.py
from backend.app.exporters import BaseExporter, register_exporter

@register_exporter("parquet")
class ParquetExporter(BaseExporter):
    DESCRIPTION = "Apache Parquet for big data"
    async def export(self, items, ctx):
        ...
```

启动时 `from backend.app.exporters import parquet_exporter` 自注册. `wcn export -f parquet` 即可用.

### 加一个新的通知通道
同模式, 实现 `BaseNotifier` + 注入到 `dispatcher.configured_notifiers()`.

### 用 Postgres 替代 SQLite
```bash
uv pip install -e ".[postgres]"
export WCN_DATABASE_URL="postgresql+asyncpg://wcn:pwd@host:5432/weibo"
alembic upgrade head
wcn serve
```

### 接入多账号 cookie 池
```python
from backend.app.anti_ban import CookiePool
from backend.app.crawler import AsyncWeiboClient

pool = CookiePool([
    ("SUB=xxx;...", "account1"),
    ("SUB=yyy;...", "account2"),
])
async with AsyncWeiboClient(cookie_pool=pool) as client:
    ...
```
