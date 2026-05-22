# weibo-crawler-next

> 微博数据采集与分析平台. CLI + TUI + WebUI 三种交互, 内置 anti-ban 风控池,
> 支持 5 种部署方式 (pip / Docker / Compose / systemd / PyInstaller binary).

[![CI](https://github.com/FruityMaxine/weibo-crawler-next/actions/workflows/ci.yml/badge.svg)](https://github.com/FruityMaxine/weibo-crawler-next/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/FruityMaxine/weibo-crawler-next?include_prereleases)](https://github.com/FruityMaxine/weibo-crawler-next/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org)

---

## 关于本项目

本项目基于 [dataabc/weibo-crawler](https://github.com/dataabc/weibo-crawler) 的功能边界, 完全重写并扩展, 不复用原项目任何源代码.

**与原项目的关系**: 仅吸收 `m.weibo.cn` 公开接口的 URL 规则 / cookie 获取流程 / 26 项配置字段语义, 在此基础上重新设计为现代化 Python 项目.

**致谢**: 感谢 `dataabc` 长期维护原项目, 让后来者得以理解微博 API 的边界与限制. 本项目以新架构延续其工作.

---

## 核心特性

| 维度 | 实现 |
|---|---|
| 采集范围 | 用户 19 项 metadata · 原创/转发微博 · 评论 · 图片/视频/Live Photo |
| 交互方式 | CLI (`wcn run`) · TUI (`wcn tui`, 键盘上下键菜单) · WebUI (`wcn serve`, 7 路由) |
| 数据导出 | CSV · JSON · SQLite · MySQL · MongoDB · Webhook (POST) |
| 反封策略 | Cookie 池 (健康度 EMA + 失败冷却) · 代理池 · UA 随机 · Token Bucket 自适应 · 429 退避 · 验证码探测 |
| 数据存储 | SQLite (含 FTS5 全文索引) · 可选 MySQL / Postgres / MongoDB |
| 通知 | Telegram bot · Discord webhook · SMTP email · 通用 webhook |
| 实时推送 | WebSocket 心跳 (dashboard 统计 + 任务进度) |
| 部署 | pip / Docker (multi-stage) / Docker Compose / systemd / PyInstaller 单文件 binary |
| CI/CD | GitHub Actions 3 OS 矩阵 (Ubuntu / macOS / Windows) · Release 自动构建 binary + GHCR Docker push |

---

## 技术栈

| 层 | 选型 | 版本 |
|---|---|---|
| 语言 | Python | 3.12+ |
| 包管理 | uv | ≥ 0.5 |
| Web 框架 | FastAPI | ≥ 0.115 |
| ORM | SQLAlchemy 2.0 (async) + alembic | ≥ 2.0.36 |
| HTTP | httpx + tenacity | ≥ 0.27 |
| 调度 | APScheduler (async) | ≥ 3.10 |
| TUI | Textual + Rich | ≥ 0.86 |
| 前端 | Vite + React + TypeScript (strict) | Vite 6 / React 18 |
| 样式 | Tailwind CSS + Linear design system | 3.4 |
| 前端数据 | TanStack Query + WebSocket | 5.67 |

---

## 前置依赖

- **Python 3.12+**
- **uv** (Python 包管理器): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Node.js 20+** (仅前端开发需要)
- **Docker** (仅容器化部署需要)
- **Make** (Linux/macOS, 用于 `make` 命令; Windows 用户直接执行底层命令)

---

## 快速开始

### Linux / macOS

```bash
git clone https://github.com/FruityMaxine/weibo-crawler-next.git
cd weibo-crawler-next

# 安装依赖 (uv 会自动建 .venv)
make dev-install

# 配置 (可选 - 默认匿名模式可抓 2000 条公开微博)
cp env.example .env
# 编辑 .env, 填 WCN_WEIBO_COOKIE 等

# 验证: 跑测试
make test                  # 应输出 "65 passed"

# 启动后端 (默认 127.0.0.1:28800)
make serve

# 另开终端: CLI 抓取
make run UID=1669879400

# 或启动 TUI (键盘上下键菜单)
make tui
```

### Windows

`Makefile` 仅支持 Linux/macOS. Windows 用户请直接调底层命令:

```powershell
git clone https://github.com/FruityMaxine/weibo-crawler-next.git
cd weibo-crawler-next

uv venv .venv --python 3.12
uv pip install -e ".[dev,tui]" --python .venv

# 跑测试
.venv\Scripts\pytest tests/

# 启动后端
.venv\Scripts\wcn serve

# CLI 抓取
.venv\Scripts\wcn run -u 1669879400
```

---

## CLI 用法

```
wcn version                         打印版本
wcn info                            显示当前配置 (Rich 表格)
wcn run -u <uid> [-n MAX] [--since N|YYYY-MM-DD] [--only-original]
wcn run -f <user-id-list.txt>       批量抓取 (兼容原项目格式)
wcn user <uid>                      查本地已抓用户
wcn weibo --uid <uid>               列本地已抓微博
wcn tasks                           列采集任务
wcn export -f <fmt> [--uid UID] [-n LIMIT]
wcn exporters                       列出所有可用导出格式
wcn serve [--port PORT]             启动后端 API + WebUI
wcn tui                             启动 Textual TUI (上下键菜单, 需 TTY)
```

`--since` 支持两种格式:
- `--since 2026-01-01` 绝对日期
- `--since 7` 整数: 最近 N 天 (兼容原项目)

完整 API 参考: [docs/API.md](docs/API.md).

---

## WebUI

```bash
# 启动后端 (内嵌前端 dist, 无需 dev server)
wcn serve

# 浏览器访问
open http://127.0.0.1:28800/
```

前端开发模式 (HMR):
```bash
cd frontend
npm install
npm run dev          # http://127.0.0.1:5173/
```

7 个路由: `Dashboard` / `Tasks` / `Users` / `Weibo` / `Search` / `Settings` / `Logs`.

---

## 端口冲突处理

默认后端 `28800`, 前端 dev `5173`.

- **前端 5173 被占用**: Vite 自动递增到 5174 / 5175... (无需手动)
- **后端 28800 被占用**: 用 `WCN_PORT` 环境变量统一改, vite proxy 会自动跟随:
  ```bash
  WCN_PORT=28801 wcn serve            # 后端
  WCN_PORT=28801 npm run dev          # 前端 (proxy 自动指向 28801)
  ```
- **Vite dev 端口**: 可用 `WCN_DEV_PORT` 单独设

---

## 部署

完整文档: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

### Docker (推荐生产)

从 Release 拉镜像:
```bash
docker run -d \
  --name wcn-api \
  -p 127.0.0.1:28800:28800 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/weibo_output:/app/weibo_output \
  ghcr.io/fruitymaxine/weibo-crawler-next:latest
```

容器内进程自动监听 `::` (IPv6 双栈通配) 让宿主端口映射生效.
宿主端口已限制 `127.0.0.1:28800`, 公网由 Caddy/Nginx 反代终端 TLS.

### Docker Compose

```bash
git clone https://github.com/FruityMaxine/weibo-crawler-next.git
cd weibo-crawler-next
cp env.example .env             # 编辑后
docker compose up -d            # 默认 SQLite
docker compose --profile postgres up -d    # 加 Postgres
docker compose --profile redis up -d       # 加 Redis
```

### systemd (Linux 服务器)

```bash
sudo cp deploy/systemd/wcn-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now wcn-api
journalctl -u wcn-api -f
```

unit 文件已配 `ProtectSystem=full` + `ReadWritePaths` 沙箱.

### PyInstaller 单文件 binary

从 [Releases](https://github.com/FruityMaxine/weibo-crawler-next/releases) 下载对应平台 binary, 直接运行:

```bash
chmod +x wcn-v0.4.2.0-linux-x64
./wcn-v0.4.2.0-linux-x64 serve
```

binary 内嵌前端 dist, 无需额外依赖. 跨平台支持 Linux / macOS / Windows.

---

## 反封策略 (anti-ban)

5 子系统, 详见 [docs/ANTI_BAN.md](docs/ANTI_BAN.md):

| 子系统 | 算法 |
|---|---|
| CookiePool | 加权随机 (健康度 ²) + EMA 平滑 + 连续失败指数冷却 (60s → 30min) |
| ProxyPool | HTTP/SOCKS5 + 异步探活 + 延迟+健康度双权 + 失败降权 |
| UAPool | 8 条 2026 真实 UA + Sec-CH-UA / Device-Memory / X-Request-Id 随机 |
| TokenBucketLimiter | 自适应速率 (响应快加速 / 慢降速) + 429 指数退避 (5s → 5min) |
| CaptchaDetector | 7 关键词 + HTTP 状态码综合判断 |

接入示例:

```python
from backend.app.anti_ban import CookiePool, ProxyPool, UAPool
from backend.app.crawler import AsyncWeiboClient

cookie_pool = CookiePool([("SUB=...", "main"), ("SUB=...", "backup")])
proxy_pool = ProxyPool(["http://10.0.0.1:8080", "socks5://10.0.0.2:1080"])
await proxy_pool.probe_all()

async with AsyncWeiboClient(
    cookie_pool=cookie_pool,
    proxy_pool=proxy_pool,
    ua_pool=UAPool(mobile_weight=0.85),
) as client:
    user = await client.get_user_info(1669879400)
```

---

## 数据存储

默认 SQLite 含 FTS5 全文索引, 零配置. 可切其他后端:

```bash
# Postgres (需 .[postgres] extras)
WCN_DATABASE_URL=postgresql+asyncpg://...
alembic upgrade head

# MySQL (需 .[mysql] extras)
WCN_DATABASE_URL=mysql+aiomysql://...
```

---

## 项目结构

```
weibo-crawler-next/
├── backend/app/
│   ├── crawler/          m.weibo.cn API client + parser
│   ├── anti_ban/         Cookie 池 / Proxy 池 / UA / 限频 / 验证码探测
│   ├── notifications/    Telegram / Discord / Email / Webhook
│   ├── exporters/        6 种导出器 (插件 registry)
│   ├── db/               SQLAlchemy 2.0 async + FTS5 + alembic
│   ├── routers/          users / weibo / tasks / search / ws / health
│   ├── services/         业务逻辑
│   └── tasks/            APScheduler + executor
├── cli/
│   └── tui/              Textual App + 5 screens + 3 widgets
├── frontend/
│   └── src/              Vite + React + Tailwind
├── deploy/
│   ├── systemd/          wcn-api.service
│   └── pyinstaller/      wcn.spec
├── docs/                 ARCHITECTURE · CONTRIBUTING · DEPLOYMENT · ANTI_BAN · API
├── .github/workflows/    ci.yml · release.yml
├── tests/                65 passed
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── pyproject.toml
```

---

## 测试与质量

```bash
make test     # 全测 65 passed
make lint     # ruff check
```

CI 在 Ubuntu / macOS / Windows × Python 3.12 上跑所有测试 + Docker buildx + 前端 type-check.

---

## 贡献

详见 [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md). 走 Conventional Commits + SemVer 4 段制.

---

## 文档索引

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 模块边界与数据流
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — 5 种部署方式详解
- [docs/ANTI_BAN.md](docs/ANTI_BAN.md) — 反封策略原理
- [docs/API.md](docs/API.md) — REST + WebSocket + CLI 参考
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) — 贡献指南
- [CHANGELOG.md](CHANGELOG.md) — 版本历史

---

## 致谢

- [dataabc/weibo-crawler](https://github.com/dataabc/weibo-crawler) — 原项目, 提供 API 知识与功能边界参考
- [Linear](https://linear.app) — UI 设计语言参考
- [React Bits](https://github.com/DavidHDev/react-bits) — 动效组件设计灵感
- [Astral / uv](https://docs.astral.sh/uv/) — 现代 Python 包管理
- [Textual](https://textual.textualize.io/) — 现代 TUI 框架

---

## License

[MIT](LICENSE)
