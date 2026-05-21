# Loop Plan — 组 1

**项目**: weibo-crawler-next
**启动时间**: 2026-05-21 23:00 UTC (北京时间 2026-05-22 07:00)
**触发命令**: `/betterloop ... weibo-crawler-next ...`
**主 Opus**: 4.7 (1M context)
**停止意图识别**: ARGUMENTS 含 "完成上面需求后停止 loop 汇报项目全貌" → **有明示停止条件**, 4 个执行 tick 全闭环 + 全部需求达成后触发 §10.4 自主停。

---

## 上组总结

无（组 1 为首组）。

---

## 项目大局观（主 Opus 自调研）

### 参照源
- GitHub `dataabc/weibo-crawler` (原项目, 屎山代码) — 仅参照 API 用法、cookie 获取、功能清单
- 本项目 = **完全重写**, 不抄一行代码

### 原项目功能清单（必须全部覆盖）
1. **数据采集**: 用户信息（19 项 metadata）/ 微博正文 / 转发 / 评论 / 图片 / 视频 / Live Photo / 话题 / @ 提及
2. **导出**: CSV / JSON / SQLite / MySQL / MongoDB / POST API（6 种）
3. **Cookie**: 非必需但推荐, 2000+ 微博及关键词搜索需 cookie
4. **配置**: 26+ 字段 config.json（覆盖采集范围/媒体下载/导出格式/数据库/EXIF/文件时间）
5. **部署**: 直跑 python / Docker / Docker Compose, 含 schedule_interval 循环
6. **定时**: since_date 整数模式 + user_id_list.txt 追加模式 + const.py append 模式
7. **CLI**: argparse 简单参数

### 新增功能（原项目无, 必须超过）
1. **TUI 交互菜单**（Textual 框架, 上下键导航/子菜单）— 用户明示
2. **WebUI 仪表盘**（React + Vite + TS + React Bits + Linear 暗色风）— 用户明示
3. **高阶风控**（Cookie 池/Proxy 池/UA 池/自适应限频/指数退避/验证码探测）— 用户明示
4. **多部署**（Docker/Compose/systemd/PyInstaller standalone/pip）— 用户明示"原项目所有部署模式"+ 扩展
5. **插件化导出器**（BaseExporter ABC + registry, 易扩展）
6. **WebSocket 实时进度**（前端实时显示任务）
7. **SQLite FTS5 全文搜索**（爬完即可查）
8. **Webhook 通知**（Telegram / Discord / Email / 通用 webhook）
9. **OpenAPI 自动生成 + Python/TS SDK**
10. **CI/CD GitHub Actions + Release 自动打包**
11. **完整文档体系**（ARCHITECTURE / CONTRIBUTING / DEPLOYMENT / ANTI_BAN / API）

### 架构定型
| 层 | 选型 |
|---|---|
| 后端语言 | Python 3.12 + uv 包管理 |
| Web 框架 | FastAPI + async/await |
| ORM | SQLAlchemy 2.0 async + alembic |
| 调度 | APScheduler |
| HTTP client | httpx (async) |
| TUI | Textual >= 0.50 + Rich |
| 前端 | Vite 5 + React 18 + TS strict |
| 前端样式 | Tailwind + Linear DESIGN.md 暗色（canvas #010102 / 雪青蓝 #5e6ad2） |
| 前端组件 | React Bits（Aurora bg / Spotlight card / Animated number / Magnetic button 等动效组件） |
| 前端数据 | TanStack Query + WebSocket |
| 默认 DB | SQLite（含 FTS5）|
| 可选 DB | MySQL / Postgres / MongoDB |
| 部署 | Docker multi-stage / Compose / systemd / PyInstaller / pip install |

### UI 风格参考（DESIGN.md）
**linear.app**
- canvas #010102（near-black, deepest dark）
- 雪青蓝 #5e6ad2（唯一品牌色, 仅 focus ring 与 CTA）
- ink #f7f8f8 / ink-muted #d0d6e0
- 卡片 #0f1011 hairline #23252a
- Linear Display 字体 (SF Pro fallback) 500-700 weight, 负 letter-spacing
- 工具型仪表盘最佳匹配

---

## 本组 4 个执行 tick 规划

### Tick 2 — 后端骨架 + 抓取引擎 core + 数据模型（PASS）
- **模式**: A (新模块开发)
- **改动**: 30+ 新文件 / 1500-2000 行 / 5 layer (API/Service/Domain/Persistence/CLI入口) / 90-120 min
- **版本号**: v0.1.0.0
- **公告**: 初版 FastAPI 后端 + Weibo 抓取引擎 + 5 ORM 模型 + SQLite 默认存储 + 简易 CLI `wcn run --user <uid>`
- **关键约束**:
  - 后端只 bind 127.0.0.1:28800
  - `backend/app/crawler/rate_limiter.py` 顶部需注释 "本模块 Tick 5 anti_ban/rate_limiter 替换"

### Tick 3 — Textual TUI + 配置中心 + 导出器插件系统（PASS）
- **模式**: A + B (新模块 + 全新交互界面)
- **改动**: 20+ 新文件 / 1500-1800 行 / 3 layer / 90-110 min
- **版本号**: v0.2.0.0
- **公告**: TUI 交互界面（上下键 6 子屏）+ 6 种导出器（CSV/JSON/SQLite/MySQL/MongoDB/Webhook）+ 三层配置中心

### Tick 4 — WebUI (React Bits + Linear) + WS + 全文搜索（PASS）
- **模式**: B + C (全新界面 + 后端新交互逻辑)
- **改动**: 20+ frontend 新文件 + 2 backend / 2000-2500 行 / 4 layer / 110-130 min
- **版本号**: v0.3.0.0
- **公告**: React 18 WebUI 6 路由 + React Bits 动效 + Linear 暗色 + WebSocket 实时进度 + FTS5 全文搜索

### Tick 5 — 高阶风控 + 多部署 + Webhook + 完整文档（PASS）
- **模式**: A + C (新模块 + 后端新逻辑)
- **改动**: 31+ 新文件 / 1800-2200 行 / 4 layer / 110-130 min
- **版本号**: v0.4.0.0
- **公告**: anti-ban 5 子系统 + 4 路 Webhook + 5 种部署 + CI/CD + 完整文档体系
- **关键约束**:
  - 删除 Tick 2 遗留的 `crawler/rate_limiter.py` 初版, 合并入 anti_ban
  - 验证抓取流程回归不破

---

## Subagent 审查结论

`fruity-skills:betterloop-auditor` (Sonnet 4.6) 审查时间: 2026-05-21T23:05Z

**总判定**: 全 4 候选 PASS（按 §2.2 模式 + §2.3 量化护栏 + §2.4 反例 + §2.5 6 问决策流全过）

**Auditor 额外提示**:
- Tick 2 与 Tick 5 的 rate_limiter 模块设计为分阶段（先简后精）, Tick 5 实施时务必合并/删除 Tick 2 初版避免双版本共存
- Tick 4 行数预估偏保守, 实际可能 2500-3000 行（仍远超 150 行护栏）

**进入 Tick 2 状态**: 允许 ✅

---

## ScheduleWakeup 策略

| 阶段 | 间隔 | 理由 |
|---|---|---|
| Tick 1 → Tick 2 | 270s | 缓存热保持, Tick 2 即将开工写大量代码 |
| Tick 2 → Tick 3 | 270s | 同上 |
| Tick 3 → Tick 4 | 270s | 同上 |
| Tick 4 → Tick 5 | 270s | 同上 |
| Tick 5 → 自主停 | 不调用 ScheduleWakeup, 触发 §10.4 自主停 |

当前 quota: 5h 25% / 7d 13%, 健康, 全程 270s 缓存内推进无压力。

---

## 自主停止判定

ARGUMENTS 末尾 "完成上面需求后停止 loop 汇报项目全貌, 等待新指示" → 明示停止条件。

**触发条件**: Tick 2-5 全部完成且实测通过 + 原 prompt 全部需求达成
1. ✅ 微博 API 抓取（按 weibo-crawler 参照）
2. ✅ CLI 模式（Textual TUI + 上下键菜单）
3. ✅ WebUI 模式（React Bits + 统一风格）
4. ✅ 包含原项目所有功能（6 导出/26 配置/Cookie/Docker/Compose 等）
5. ✅ 高效架构 / GitHub PR 友好（CONTRIBUTING/PR 模板/CI）
6. ✅ 额外功能（TUI/WebUI/插件/FTS5/Webhook/AI 等多项）
7. ✅ 高阶风控（Cookie/Proxy/UA 池 + 自适应 + 退避）
8. ✅ 多系统部署（Docker/Compose/systemd/PyInstaller/pip）

Tick 5 闭环 commit 后, 主 Opus 生成结案报告 + 不调 ScheduleWakeup → loop 终止。
