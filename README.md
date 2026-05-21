# weibo-crawler-next

> 现代化微博数据采集与分析平台 — 完全重写自 [dataabc/weibo-crawler](https://github.com/dataabc/weibo-crawler), 新架构, 新交互, 新风控.

---

## 项目状态

**🚧 v0.0.x.x · 立项中（loop tick 持续推进）**

正在 4 阶段 betterloop 构建：

| 阶段 | 目标 | 状态 |
|---|---|---|
| Tick 2 → v0.1 | 后端骨架 + 抓取引擎 core + 数据模型 + 简易 CLI | ✓ 完成 |
| Tick 3 → v0.2 | Textual TUI（上下键菜单）+ 6 种导出器 + 配置中心 | ✓ 完成 |
| Tick 4 → v0.3 | React WebUI（React Bits + Linear 风）+ WS + FTS5 全文搜索 | ✓ 完成 |
| Tick 5 → v0.4 | 高阶风控（Cookie/Proxy/UA 池）+ 多部署 + Webhook + 文档 | 待启动 |

---

## 设计哲学

1. **不抄原项目代码**, 只吸纳功能与 API 知识, 全新架构
2. **CLI 与 WebUI 双模式**, 同一后端复用
3. **插件化** — Exporter / Notifier / Anti-Ban Strategy 均可插拔
4. **风控优先** — Cookie 池 + Proxy 池 + 自适应限频 + 退避重试
5. **跨系统** — Linux / macOS / Windows / ARM / x86 全支持
6. **社区友好** — PR / Issue 模板 + CI/CD + ARCHITECTURE.md

---

## 技术栈

| 层 | 选型 |
|---|---|
| 语言 | Python 3.12 |
| 包管理 | uv |
| Web 框架 | FastAPI + async |
| ORM | SQLAlchemy 2.0 async + alembic |
| 调度 | APScheduler |
| HTTP | httpx async |
| TUI | Textual + Rich |
| 前端 | Vite 5 + React 18 + TypeScript |
| 样式 | Tailwind + Linear DESIGN.md |
| 组件 | React Bits（动效组件库） |
| 数据 | TanStack Query + WebSocket |
| DB | SQLite (含 FTS5) 默认 / MySQL / Postgres / MongoDB 可选 |

---

## UI 风格参考

**Linear.app 暗色** — 来源 `/srv/agent-workspace/resources/voltagent-design/design-md/linear.app/DESIGN.md`

- canvas: `#010102` (deepest near-black)
- accent: `#5e6ad2` (Linear 雪青蓝, 仅 focus ring 和 CTA 用)
- ink: `#f7f8f8`
- surface: `#0f1011` / `#141516` / `#18191a`
- hairline: `#23252a`

---

## 项目结构（最终态预览）

```
weibo-crawler-next/
├── backend/                  # Python 后端
│   ├── app/
│   │   ├── crawler/          # 抓取引擎
│   │   ├── db/               # SQLAlchemy models + migrations
│   │   ├── exporters/        # 插件化导出器
│   │   ├── notifications/    # Webhook / Telegram / Discord
│   │   ├── anti_ban/         # 风控子系统（Cookie/Proxy/UA 池）
│   │   ├── routers/          # FastAPI routes + WebSocket
│   │   ├── services/         # 业务逻辑
│   │   └── tasks/            # APScheduler 任务
│   └── alembic/              # DB migrations
├── cli/                      # CLI 入口 + Textual TUI
│   └── tui/
├── frontend/                 # React WebUI
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── api/
├── deploy/                   # Docker / Compose / systemd / PyInstaller
├── docs/                     # ARCHITECTURE / CONTRIBUTING / DEPLOYMENT
└── .github/                  # PR/Issue 模板 + workflows
```

---

## 使用方式（预期, 待 Tick 完成后填具体命令）

```bash
# CLI 直跑
wcn run --user 1669879400

# TUI 模式（上下键菜单）
wcn tui

# WebUI 模式
wcn web   # 启动 FastAPI + 静态前端, 浏览器访问

# Docker 一键
docker compose up -d
```

---

## License

MIT
