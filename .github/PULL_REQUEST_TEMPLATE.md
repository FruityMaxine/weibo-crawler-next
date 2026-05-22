# Pull Request

## 摘要 (Summary)

<!-- 1-2 句话说明这个 PR 做了什么 -->

## 动机 (Motivation)

<!-- 为什么需要这个改动? 解决什么问题? 关联 issue # -->

## 改动类型 (Type)

- [ ] feat: 新功能
- [ ] fix: bug 修复
- [ ] docs: 仅文档
- [ ] refactor: 不影响行为的代码重构
- [ ] perf: 性能优化
- [ ] test: 仅测试
- [ ] chore: 工程化 / 依赖升级
- [ ] ci: CI/CD 调整

## 影响范围 (Scope)

- [ ] 后端 (`backend/`)
- [ ] 抓取引擎 (`backend/app/crawler/`)
- [ ] 风控 (`backend/app/anti_ban/`)
- [ ] 导出器 (`backend/app/exporters/`)
- [ ] 通知 (`backend/app/notifications/`)
- [ ] CLI / TUI (`cli/`)
- [ ] 前端 (`frontend/`)
- [ ] 文档 (`docs/`)
- [ ] CI/CD (`.github/`)
- [ ] 部署 (`Dockerfile` / `deploy/`)

## 验证 (Verification)

<!-- 跑过的命令 + 结果 -->

```bash
# 例:
make test       # ✓ 27 passed
make lint       # ✓ no issues
make build-frontend  # ✓ 441KB JS
```

## 截图 (UI 改动时必须)

<!-- 拖图片到这里 -->

## 兼容性 (Breaking Changes?)

- [ ] 无 breaking change
- [ ] 含 breaking change (在下方详细描述迁移路径)

## Checklist

- [ ] 升级版本号 (`VERSION` + `pyproject.toml` + `backend/__init__.py`)
- [ ] 更新 `CHANGELOG.md` 或 `docs/progress/` (如适用)
- [ ] 新功能含对应测试
- [ ] 涉及 API 的改动已更新 `docs/API.md`
- [ ] commit 消息符合 Conventional Commits (`feat: ...` / `fix: ...`)
