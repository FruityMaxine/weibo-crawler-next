# Changelog

格式参考 [Keep a Changelog](https://keepachangelog.com/), 版本号遵循 SemVer 4 段制.

## [0.5.0.0] - 2026-05-22

> 主交互改造 — TUI 升级为"上下键菜单 + 子界面 + 输入框 + 实时进度条 + 滚动日志"完整体验, 七彩主题.

### Added (核心 TUI 体验)

- **默认入口**: `wcn` 无参数自动启 TUI 菜单 (TTY 环境), 不用记任何命令
- **CrawlScreen 新增** (核心采集屏): 输入 UID + 数量 + 起始日期 + Cookie, 启动后**右侧实时进度条** + **滚动日志**, 中途可 Ctrl+X 停止
- **UsersScreen 新增**: 已抓用户卡片列表 (头像/认证/统计)
- **WeiboScreen 新增**: 已抓微博列表 + UID 过滤
- **SearchScreen 新增**: 全文搜索 + FTS5 元字符自动净化 + `<mark>` 高亮渲染
- **ConfigScreen 改成可编辑**: 9 分组配置全字段 Input, 敏感字段脱敏, Ctrl+S 写 .env
- **七彩主题**: 在 Linear 暗色基底上加 7 色状态 (success 绿 / warning 黄 / danger 红 / info 青 / accent 粉/紫/橙), TUI CSS 全套支持

### Changed

- 主菜单重排: `开始采集` 置顶 (核心), 其余按使用频率排
- 主菜单每项带颜色标记 + 中文功能描述
- `cli/__main__.py`: 无参数 + TTY 时自动启 TUI; 非 TTY 走原 click 命令
- TUI sidebar 宽度 28 → 32 (容纳更长中文菜单)
- 测试: 69 passed (+4 新屏 smoke)

---

## [0.4.2.0] - 2026-05-22

> 公开 release 前置审查 — security/typescript/code 三个 ECC reviewer 联审后修复.

### Fixed (3 新 Critical + 7 Warning)

- **C1 — cookie_override 通过 API 泄露**: `tasks` router 改用 `_sanitize_config()` 过滤敏感字段, `cookie_override` 仅在内存传给 background task, 不入 `config_snapshot`. `TaskOut.from_orm_sanitized()` 兜底脱敏
- **C2 — release.yml binary-build 缺前端 build**: 加 `setup-node@v4` + `npm ci && npm run build` 步骤, 否则 binary 内无 WebUI 静态资源
- **C3 — README 状态过时**: 完整重写, 反映 v0.4.x 真实测试数 + uv 前置依赖 + Makefile 仅 Linux/macOS + Windows 用法

### Added (用户特别提问的端口退避 + 安全增强)

- **端口自动对齐**: `vite.config.ts` 读 `WCN_PORT` env, 后端换端口时前端 proxy 自动跟随. `WCN_DEV_PORT` 单独配 Vite dev. Vite `strictPort: false` 让 5173 占用时自动递增
- **FTS5 输入净化**: `sanitize_fts_query()` 剥离 `" * : ^ - + ( )` 等 FTS5 元字符防注入
- **TaskCreate 字段长度限制**: `name max=200` / `query max=200` / `max_count [1, 10000]`
- **systemd ReadWritePaths**: 放行 `data/` 和 `weibo_output/`, 修复 `ProtectSystem=full` 下写文件失败
- **wcn tui TTY 检测**: 非交互式终端立即报友好错误, 不抛 Textual traceback
- **Webhook output_path 脱敏**: 不返回完整 URL (可能含 token), 只露 `scheme://host/path`
- **PyInstaller binary 命名**: 三平台分别生成 `wcn-vX.X.X.X-{linux,macos,windows}-x64` 上传 Release

### Changed

- pytest **65 passed** 保持
- frontend build 仍 441KB JS / 15KB CSS

---

## [0.4.1.0] - 2026-05-22

### Fixed (5 Critical + 6 Warning 由 python-reviewer subagent 审出)

- **C3 — Docker 部署无法访问前端**: `backend/app/main.py` 新增 `_frontend_dist_path()` 多源探测 + `StaticFiles` 自动挂载
- **C5 — docker-compose 零配启动**: `settings.adjust_for_container()` 检测 /.dockerenv 自动切到 IPv6 通配 `::`
- **C4 — 生产 CORS 拦截**: `WCN_CORS_ORIGINS` env 驱动 + 自动加 same-origin 兜底
- **C1+C2 — cookie/proxy 池泄漏**: 所有错误路径强制 release 池更新健康度
- **W1 — rate_limiter 字段竞态**: report_* 方法用临时变量隔离读-改-写
- **W2 — FTS5 upsert 同步**: trigger 改用 `DELETE + INSERT` + 启动 backfill
- **W5 — PyInstaller spec**: 改用 `SPECPATH` + `os.path.abspath`

### Added

- **since_date 整数模式**: 兼容原项目 `--since 7` 写法
- **批量 uid 文件**: `wcn run -f user_id_list.txt` 兼容原项目
- **14 audit-fixes 测试**

### Changed

- pytest **65 passed** (51 → 65), README 全面重写

---

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
