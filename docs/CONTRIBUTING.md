# 贡献指南 (Contributing)

> 欢迎 PR! 本项目走 Conventional Commits + SemVer 4 段制.

---

## 快速上手

```bash
git clone https://github.com/FruityMaxine/weibo-crawler-next.git
cd weibo-crawler-next
make dev-install        # 装 dev/tui/mysql/postgres/mongo 全套 extras
make test               # 跑全测
make serve              # 启动 dev 后端 (127.0.0.1:28800)

# 另一个终端
cd frontend && npm install && npm run dev   # Vite dev :5173
```

---

## 分支策略

- `main` — 始终可发版. 不直接推, 所有改动走 PR.
- `feat/xxx` / `fix/xxx` / `docs/xxx` — 功能分支, 命名按 Conventional Commits 类型.

---

## Commit 规范 — Conventional Commits

```
<type>(<scope>): <emoji?> <短描述>

[可选 body]
```

**type**: `feat / fix / docs / refactor / perf / test / chore / ci`
**scope**: `backend / crawler / exporters / anti_ban / cli / tui / frontend / docs / ci` 等

例:
```
feat(exporters): 新增 Parquet 导出器
fix(crawler): 修 since_date 整数模式越界
docs(anti_ban): 补 Cookie 池健康度评分说明
```

**不允许**: `Co-Authored-By:` trailer / "Generated with Claude Code" footer (本项目 author 100% 是仓库 owner).

---

## 版本号规则 (SemVer 4 段)

`MAJOR.MINOR.PATCH.BUILD`

| 段 | 何时 +1 |
|---|---|
| MAJOR | 破坏性变更 (不兼容 API / DB 迁移破坏 / 核心流程重构) |
| MINOR | 新功能 (向后兼容): 新页面 / 新参数 / 新 endpoint / 新模块 |
| PATCH | bug 修复 (向后兼容) |
| BUILD | 微小修改: 文案 / 注释 / typo / UI 微调 |

**右零归零**: 升一段, 右侧全部归 0.
**混合改动**: 按最大段升.

每次 PR **必须** 同步:
- `VERSION`
- `pyproject.toml` 的 `version`
- `backend/__init__.py` 的 `__version__`
- `backend/app/main.py` 的 `app.version`
- `frontend/src/components/Sidebar.tsx` 中显示的版本号

---

## 测试

- 后端测试: `make test` (pytest-asyncio + httpx)
- 前端测试: 后续会加 Vitest
- TUI: `tests/test_tui_smoke.py` headless run_test 验证 screen 可挂载
- 覆盖率目标: 后端 ≥ 70%

```bash
.venv/bin/pytest tests/ -v --cov=backend --cov=cli --cov-report=html
open htmlcov/index.html
```

---

## Lint / 格式化

```bash
make lint               # ruff check + mypy
uv run ruff format backend cli tests   # auto format
```

ruff 配置在 `pyproject.toml [tool.ruff]`, 选了 `E/F/I/B/UP/ASYNC/S/SIM/ARG`.

---

## 加新导出器

参考 `docs/ARCHITECTURE.md#扩展点` 段.

最小例:
```python
# backend/app/exporters/myformat_exporter.py
from backend.app.exporters import BaseExporter, register_exporter
from backend.app.exporters.base import ExportContext, ExportResult

@register_exporter("myformat")
class MyExporter(BaseExporter):
    DESCRIPTION = "My custom format"

    async def export(self, items, ctx: ExportContext) -> ExportResult:
        ...
        return ExportResult(format="myformat", success=True, item_count=len(items))
```

记得在 `backend/app/exporters/__init__.py` 添加 import 触发自注册.

加测试 `tests/test_exporters.py` 含 round-trip 验证.

---

## 加新通知通道

`backend/app/notifications/<name>.py` 实现 `BaseNotifier`, 在 `dispatcher.configured_notifiers()` 注册.

---

## 安全

- **绝不**在代码 / docs / commit message 写真实 cookie / token / 密码.
- 敏感字段全部从 env 读 (`backend/app/config/settings.py` 中带 `WCN_` 前缀).
- 发现安全漏洞? 发邮件而非开公开 issue.

---

## Code Review 关注点

PR 评审时会问:
1. 版本号 bump 了吗?
2. 测试覆盖了新代码吗?
3. 含敏感字符串 / 真实 cookie 吗? (CI 会扫)
4. 破坏性变更标了 `BREAKING CHANGE:` 吗?
5. API 改了同步更新 `docs/API.md` 吗?
6. UI 改了附截图了吗?

---

感谢贡献!
