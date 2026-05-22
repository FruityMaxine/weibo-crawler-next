"""配置屏 — 按分组渲染可编辑表单, 保存写 .env."""

from __future__ import annotations

import os
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from backend.app.config import get_settings
from backend.app.config.schema import FIELD_GROUPS, SECRET_FIELDS, field_label


class ConfigScreen(Screen):
    """配置编辑屏 — 按 group 渲染 Input, 点保存写 .env."""

    BINDINGS = [
        ("escape", "app.pop_screen", "返回"),
        ("q", "app.exit", "退出"),
        ("ctrl+s", "save", "保存"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "[bold #5e6ad2]● 配置编辑[/]   "
            "[#8a8f98]修改后按 Ctrl+S 或点 [保存] 写入 .env, 重启 wcn 生效.[/]",
            classes="card-title",
        )
        with VerticalScroll(id="config-form"):
            s = get_settings()
            d = s.model_dump()
            for group, fields in FIELD_GROUPS.items():
                yield Static(f"[bold #5e6ad2]── {group} ──[/]", classes="muted")
                for k in fields:
                    if k not in d:
                        continue
                    yield Label(f"{field_label(k)}  [#8a8f98]({k})[/]")
                    raw = d[k]
                    is_secret = k in SECRET_FIELDS
                    yield Input(
                        value="" if is_secret else str(raw or ""),
                        placeholder=("[已设置, 留空保持]" if is_secret and raw else f"默认: {raw}"),
                        id=f"cfg-{k}",
                        password=is_secret,
                    )
        with Horizontal(id="config-actions"):
            yield Button("💾 保存到 .env", id="btn-save", classes="-primary")
            yield Button("← 返回", id="btn-back")
        yield Static("", id="config-status", classes="card")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
            return
        if event.button.id == "btn-save":
            await self.action_save()

    async def action_save(self) -> None:
        # 收集所有 Input 值, 与默认对比, 只写入"非空且与默认不同"项
        s = get_settings()
        d = s.model_dump()
        changes: dict[str, str] = {}
        for k, v in d.items():
            inp = self.query_one(f"#cfg-{k}", Input)
            new_val = inp.value
            if k in SECRET_FIELDS and new_val == "":
                continue  # 留空保持原值
            if str(new_val) != str(v):
                changes[k] = new_val

        if not changes:
            self._notify("[#8a8f98]无变更, 未写入 .env.[/]", "info")
            return

        env_path = Path(".env")
        existing_lines: list[str] = []
        if env_path.exists():
            existing_lines = env_path.read_text(encoding="utf-8").splitlines()

        # 把 changes 转 KEY=VAL 行, 已存在则替换
        existing_keys = {}
        for i, line in enumerate(existing_lines):
            if "=" in line and not line.strip().startswith("#"):
                key = line.split("=", 1)[0].strip()
                existing_keys[key] = i

        for k, v in changes.items():
            env_key = f"WCN_{k.upper()}"
            line = f"{env_key}={v}"
            if env_key in existing_keys:
                existing_lines[existing_keys[env_key]] = line
            else:
                existing_lines.append(line)

        env_path.write_text("\n".join(existing_lines) + "\n", encoding="utf-8")

        # 同时更新当前进程 env (但 get_settings cache 不会重读)
        for k, v in changes.items():
            os.environ[f"WCN_{k.upper()}"] = str(v)

        self._notify(
            f"[#27a644]✓ 写入 {len(changes)} 项到 .env. 重启 wcn 生效.[/]",
            "success",
        )

    def _notify(self, msg: str, level: str = "info") -> None:
        status = self.query_one("#config-status", Static)
        cls = {"success": "success", "warning": "warning",
               "danger": "danger", "info": "info"}.get(level, "info")
        status.set_classes(f"card {cls}")
        status.update(msg)
