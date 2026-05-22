# Changelog

格式参考 [Keep a Changelog](https://keepachangelog.com/), 版本号遵循 SemVer 4 段制.

## [0.4.0.0] - 2026-05-22

### Added
- **anti-ban 5 子系统**: `CookiePool` (健康度 EMA + 失败屏蔽) / `ProxyPool` (探活 + 加权) / `UAPool` (8 真实 UA + 设备指纹随机) / `TokenBucketLimiter` (自适应 + 429 退避) / `captcha_detector` (响应分析)
- **通知 4 通道**: Telegram bot / Discord webhook / SMTP email / 通用 webhook + `dispatch_event()` 并发广播
- **5 种部署**: Dockerfile multi-stage / docker-compose + Postgres/Redis profiles / systemd unit (含沙箱) / PyInstaller binary spec / pip install
- **CI/CD**: `.github/workflows/ci.yml` (Ubuntu/macOS/Windows × Python 3.12) + `release.yml` (GitHub Release + GHCR Docker + 3 平台 binary)
- **完整文档**: docs/ARCHITECTURE.md (架构图 + 模块边界 + 扩展点) / CONTRIBUTING.md / DEPLOYMENT.md (5 部署方式逐一) / ANTI_BAN.md (5 子系统详解) / API.md (REST + WS + CLI)
- **社区**: PR/Issue 模板 + CONTRIBUTING + Conventional Commits + SemVer 4 段制约束
- `Makefile` 统一 build / test / run / docker / release 命令

### Changed
- `AsyncWeiboClient` 接受 `cookie_pool` / `proxy_pool` / `ua_pool` 注入, 自动反馈成功/失败到池健康度
- 替换 `crawler/rate_limiter.py` 简易版 → `anti_ban/rate_limiter.py` Token Bucket
- env.example 新增 11 个通知 + 任务相关字段

### Removed
- `backend/app/crawler/rate_limiter.py` (Tick 2 简易版, 被 anti_ban 替换)

---

## [0.3.1.0] - 2026-05-22

### Fixed
- 清理 tsc -b 误生成的 24 个 .js 产物 + tsconfig.tsbuildinfo
- `frontend/package.json` build script: `tsc -b` → `tsc --noEmit` (vite 自己编译)
- .gitignore 加 `frontend/src/**/*.js` 防御复发

---

## [0.3.0.0] - 2026-05-22

### Added
- **WebUI**: Vite 5 + React 18 + TS strict + Tailwind + Linear DESIGN.md 暗色 + Inter 字体
- 5 React Bits 组件: Aurora / SpotlightCard / AnimatedNumber / MagneticButton / TypingText
- 7 路由页面: Dashboard / Tasks / Users / Weibo / Search / Settings / Logs
- TanStack Query 数据层 + WebSocket 自动重连 hook
- SQLite FTS5 全文索引 + 3 trigger 同步 weibos 表
- `/api/search` endpoint (snippet `<mark>` 高亮 + rank 排序)
- `/ws` WebSocket endpoint + dashboard_tick 心跳 (每 3s)

### Fixed
- FTS5 contentless 模式改回普通 (能 SELECT 列)
- search router 加 int/str 类型容错

---

## [0.2.0.0] - 2026-05-21

### Added
- **TUI**: Textual + Rich, 5 SCREEN (main/tasks/config/logs/export/help) + 3 widgets, 上下键 / k-j 双绑导航
- **6 导出器**: BaseExporter ABC + 装饰器 registry + csv/json/sqlite/mysql/mongodb/webhook
- **配置中心**: `backend/app/config/` 包 (settings/loader/schema), 27 字段 / 9 分组 / 3 secret + YAML 加载 + JSON Schema
- `wcn tui` / `wcn export -f <格式>` / `wcn exporters` 子命令

---

## [0.1.0.0] - 2026-05-21

### Added
- FastAPI 后端骨架 (4 路由 + 8 endpoint), bind 127.0.0.1:28800
- SQLAlchemy 2.0 async + alembic, 6 ORM (User/Weibo/Media/Comment/Repost/CrawlTask)
- 抓取引擎: httpx + tenacity 重试 + 简易限频 + m.weibo.cn API 端点封装
- 3 service 层 + APScheduler lifespan + BackgroundTasks 执行器
- CLI click + Rich: 8 子命令 (run/serve/user/weibo/tasks/info/version/tui)
- pytest 10 测试 (parser + config + upsert)

---

## [0.0.1.0] - 2026-05-21

### Added
- 项目立项 · loop 组1 规划
- 选 Linear DESIGN.md 暗色 + React Bits 组件库
- README + LICENSE (MIT) + .gitignore
- docs/progress/loop-plan-组1.md
