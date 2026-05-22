# weibo-crawler-next

> 现代化微博数据采集与分析平台 — 完全重写自 [dataabc/weibo-crawler](https://github.com/dataabc/weibo-crawler).
> 新架构 · 双交互 (CLI + TUI + WebUI) · 高阶风控 · 5 种部署 · 插件化扩展.

[![CI](https://img.shields.io/badge/CI-passing-success)](.github/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-51%20passed-success)](tests/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 项目状态

**v0.4.0.0 · 已发版 (2026-05-22)** — 5 tick betterloop 全部闭环, 可投入生产.

| 里程碑 | 版本 | 内容 |
|---|---|---|
| Tick 1 | v0.0.1.0 | 立项 + loop 规划 + 风格选型 |
| Tick 2 | v0.1.0.0 | 后端骨架 + 抓取引擎 + 6 ORM + CLI |
| Tick 3 | v0.2.0.0 | Textual TUI 上下键菜单 + 6 导出器 + 配置中心 |
| Tick 4 | v0.3.0.0 | React WebUI (React Bits + Linear) + WS + FTS5 |
| Tick 5 | **v0.4.0.0** | anti-ban 5 子系统 + 4 通知 + 5 部署 + CI/CD + 完整文档 |

---

## 核心特性

### 三种交互方式

```bash
wcn run -u 1669879400      # CLI 一行抓取, Rich 富终端
wcn tui                    # TUI 上下键菜单, 6 子屏
wcn serve                  # WebUI 端口 28800, 7 路由 + WS 实时进度
```

### 高阶风控 (`anti_ban/`)

- **CookiePool**: 多账号轮换, 健康度 EMA + 加权随机, 连续失败指数冷却
- **ProxyPool**: HTTP/SOCKS5 + 异步探活 + 健康度+延迟双权
- **UAPool**: 8 条 2026 真实 UA + 设备指纹随机 (Sec-CH-UA + Device-Memory)
- **TokenBucketLimiter**: 自适应延时 + 429 指数退避 + 永久降速
- **CaptchaDetector**: 7 关键词 + HTTP 状态综合判断

详见 [docs/ANTI_BAN.md](docs/ANTI_BAN.md).

### 插件化导出 (6 种格式)

| 格式 | 适用 |
|---|---|
| `csv` | Excel 友好, utf-8-sig BOM |
| `json` | 嵌套结构, ensure_ascii=False |
| `sqlite` | 单文件可移植 |
| `mysql` | 需 `.[mysql]` extras |
| `mongodb` | 需 `.[mongo]` extras |
| `webhook` | POST 到外部 URL + Bearer |

加新格式: 一行 `@register_exporter("xxx")`. 详见 [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

### 4 通道通知

`NotificationEvent` 一次广播到所有配置的通道:

- Telegram Bot (Markdown)
- Discord Webhook (Embeds + 颜色)
- SMTP Email (TLS)
- 通用 Webhook (Bearer Token)

### 5 种部署 (详见 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md))

1. **pip / uv** — `make install && wcn serve`
2. **Docker** — `make docker && docker run ...`
3. **Docker Compose** — `make docker-up` 含可选 Postgres/Redis profiles
4. **systemd** — `deploy/systemd/wcn-api.service` 沙箱完备
5. **PyInstaller** — `make build-binary` → 跨平台单文件

CI 自动构建 Ubuntu/macOS/Windows 三平台 binary 上传 GitHub Release.

---

## 技术栈

| 层 | 选型 |
|---|---|
| 语言 | Python 3.12 |
| 包管理 | uv |
| Web 框架 | FastAPI + async (lifespan) |
| ORM | SQLAlchemy 2.0 async + alembic |
| 调度 | APScheduler |
| HTTP | httpx async + tenacity 重试 |
| TUI | Textual ≥ 0.86 + Rich |
| 前端 | Vite 5 + React 18 + TypeScript strict |
| 样式 | Tailwind + Linear DESIGN.md 暗色 |
| 组件 | React Bits 风格 (Aurora / SpotlightCard / AnimatedNumber / MagneticButton / TypingText) |
| 数据 | TanStack Query + WebSocket |
| DB | SQLite (含 FTS5) 默认 / MySQL / Postgres / MongoDB 可选 |
| 容器 | Docker multi-stage (uv backend + node frontend + slim runtime) |
| CI | GitHub Actions, 3 OS matrix |

---

## UI 风格

参考 [linear.app DESIGN.md](https://github.com/voltagent/awesome-design-md/tree/main/design-md/linear.app) (服务器本地 `/srv/agent-workspace/resources/voltagent-design/design-md/linear.app/`).

| 色 | 值 | 用途 |
|---|---|---|
| canvas | `#010102` | 最深底色 |
| surface | `#0f1011` | 卡片背景 |
| hairline | `#23252a` | 边框 |
| ink | `#f7f8f8` | 主文字 |
| **primary** | `#5e6ad2` | 雪青蓝 (唯一品牌色, 仅 focus ring 和 CTA) |

---

## 快速上手

```bash
# 1. 克隆
git clone https://github.com/FruityMaxine/weibo-crawler-next.git
cd weibo-crawler-next

# 2. 装依赖 (uv + Python 3.12)
make dev-install

# 3. 配置
cp env.example .env
# 编辑 .env, 填 WCN_WEIBO_COOKIE (可选)

# 4. 跑测试 + lint
make test          # 51 passed
make lint

# 5. 启动
make serve         # 后端 127.0.0.1:28800

# 6. 另一个终端 — 前端 dev (可选, 静态资源已内嵌进 dist)
cd frontend && npm install && npm run dev   # :5173

# 7. 用 CLI 抓
make run UID=1669879400
```

---

## CLI 命令速查

```
wcn version          打印版本
wcn info             显示当前配置 (Rich 表格)
wcn run -u <uid>     前台抓取单用户
wcn user <uid>       查本地用户
wcn weibo --uid <id> 列本地微博
wcn tasks            列采集任务
wcn export -f <fmt>  导出 (csv/json/sqlite/mysql/mongodb/webhook)
wcn exporters        列出所有可用导出器
wcn serve            启 FastAPI 后端
wcn tui              启 Textual TUI (上下键菜单)
```

完整 API 见 [docs/API.md](docs/API.md).

---

## 项目结构

```
weibo-crawler-next/
├── backend/app/
│   ├── crawler/          # m.weibo.cn API client + parser
│   ├── anti_ban/         # Cookie 池 / Proxy 池 / UA / 限频 / 验证码探测
│   ├── notifications/    # Telegram / Discord / Email / Webhook
│   ├── exporters/        # 6 种导出器 + 插件 registry
│   ├── db/               # SQLAlchemy 2.0 async + FTS5 + alembic
│   ├── routers/          # FastAPI: users/weibo/tasks/search/ws/health
│   ├── services/         # 业务逻辑
│   └── tasks/            # APScheduler + executor
├── cli/
│   └── tui/              # Textual App + 5 screens + 3 widgets
├── frontend/
│   └── src/
│       ├── pages/        # 7 路由
│       ├── components/   # Layout / Sidebar / TopBar / StatCard
│       └── components/reactbits/   # 5 动效组件
├── deploy/
│   ├── systemd/wcn-api.service
│   └── pyinstaller/wcn.spec
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CONTRIBUTING.md
│   ├── DEPLOYMENT.md
│   ├── ANTI_BAN.md
│   └── API.md
├── .github/
│   ├── workflows/        # ci.yml + release.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
├── tests/                # 51 passed
├── Dockerfile            # multi-stage
├── docker-compose.yml    # + postgres/redis profiles
├── Makefile              # 16 个 target
├── pyproject.toml        # uv + 5 extras (dev/tui/mysql/postgres/mongo)
└── CHANGELOG.md          # Keep a Changelog
```

---

## 测试

```bash
make test                    # 51 passed in 2.5s
# - 24 anti_ban (CookiePool/ProxyPool/UAPool/TokenBucket/captcha/notify)
# - 12 exporters (registry + 6 round-trip + 3 fail-path + config)
# - 5 TUI smoke (app start + 4 screen 切换)
# - 7 parser (HTML/topic/at/user/weibo card)
# - 3 config/models (settings + init_db + upsert)
```

---

## 贡献

欢迎 PR! 走 Conventional Commits + SemVer 4 段制. 详见 [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](LICENSE).
