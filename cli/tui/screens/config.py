"""配置屏 — 按 FIELD_GROUPS 渲染分组, 显示当前值 + 敏感字段脱敏."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from backend.app.config import get_settings
from backend.app.config.schema import FIELD_GROUPS, SECRET_FIELDS, field_label


class ConfigScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "返回"),
        ("q", "app.exit", "退出"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("[bold #5e6ad2]配置中心[/]", classes="card-title")
        yield VerticalScroll(id="config-list")
        yield Footer()

    def on_mount(self) -> None:
        container = self.query_one("#config-list", VerticalScroll)
        s = get_settings()
        d = s.model_dump()
        for group, fields in FIELD_GROUPS.items():
            container.mount(
                Static(f"[bold #5e6ad2]── {group} ──[/]", classes="muted")
            )
            for k in fields:
                if k not in d:
                    continue
                raw = d[k]
                if k in SECRET_FIELDS and raw:
                    val = "******"
                else:
                    val = str(raw)
                container.mount(
                    Static(
                        f"  [#d0d6e0]{field_label(k):<28}[/] "
                        f"[#f7f8f8]{val}[/]"
                    )
                )
        container.mount(
            Static(
                "\n[#8a8f98]当前为只读视图. 编辑请修改 .env 或 config.yaml 后重启.\n"
                "Tick 4 WebUI 将提供可视化编辑界面.[/]",
                classes="muted",
            )
        )
