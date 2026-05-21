"""导出屏 — 选格式 / 输入 uid / 一键导出."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

from backend.app.db.base import get_sessionmaker
from backend.app.exporters import available_exporters, get_exporter
from backend.app.exporters.base import ExportContext
from backend.app.services import WeiboService


class ExportScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "返回"),
        ("q", "app.exit", "退出"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("[bold #5e6ad2]数据导出[/]", classes="card-title")
        with Vertical():
            yield Static("选择格式:", classes="muted")
            yield Select(
                options=[(label, key) for key, label in available_exporters()],
                value="csv",
                id="format-select",
            )
            yield Label("UID (留空导出全部):")
            yield Input(placeholder="例: 1669879400", id="uid-input")
            yield Label("最多条数:")
            yield Input(value="50", id="limit-input")
            with Horizontal():
                yield Button("导出", variant="primary", id="export-btn")
                yield Button("返回", id="back-btn")
            yield Static("", id="export-status", classes="card")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-btn":
            self.app.pop_screen()
            return
        if event.button.id != "export-btn":
            return

        fmt = self.query_one("#format-select", Select).value
        uid_str = self.query_one("#uid-input", Input).value.strip()
        limit_str = self.query_one("#limit-input", Input).value.strip()
        status = self.query_one("#export-status", Static)

        uid = int(uid_str) if uid_str else None
        try:
            limit = int(limit_str) if limit_str else 50
        except ValueError:
            limit = 50

        if not isinstance(fmt, str):
            status.update("[#d65555]请选择格式[/]")
            return

        status.update("[#8a8f98]导出中...[/]")

        sm = get_sessionmaker()
        async with sm() as session:
            items = await WeiboService(session).list_recent(limit=limit, uid=uid)
        if not items:
            status.update(
                "[#d65555]本地无数据可导出, 先用 `wcn run -u <uid>` 抓取一些微博.[/]"
            )
            return

        exporter = get_exporter(fmt)
        result = await exporter.export(items, ExportContext(uid=uid))
        if result.success:
            status.update(
                f"[#27a644]✓ 成功导出 {result.item_count} 条到 [bold]{result.output_path}[/] "
                f"({result.duration_ms} ms)[/]"
            )
        else:
            status.update(f"[#d65555]✗ 导出失败: {result.error}[/]")
