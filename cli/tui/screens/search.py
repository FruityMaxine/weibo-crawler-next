"""全文搜索屏 — SQLite FTS5 驱动."""

from __future__ import annotations

import re

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from backend.app.db.fts import fts_search, init_fts


class SearchScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "返回"),
        ("q", "app.exit", "退出"),
        ("ctrl+s", "submit", "搜索"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "[bold #b88aff]● 全文搜索[/]   "
            "[#8a8f98]输入关键词, Ctrl+S 或点 [搜索] 即可. 自动剥离 FTS5 元字符.[/]",
            classes="card-title",
        )
        with Horizontal(id="search-bar"):
            yield Label("关键词:")
            yield Input(placeholder="例: Python 编程", id="search-input")
            yield Button("🔍 搜索", id="btn-search", classes="-primary")
            yield Button("← 返回", id="btn-back")
        yield Static("", id="search-status", classes="muted")
        yield VerticalScroll(id="search-result")
        yield Footer()

    async def on_mount(self) -> None:
        await init_fts()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
            return
        if event.button.id == "btn-search":
            await self.action_submit()

    async def action_submit(self) -> None:
        q = self.query_one("#search-input", Input).value.strip()
        result_box = self.query_one("#search-result", VerticalScroll)
        status = self.query_one("#search-status", Static)
        await result_box.remove_children()

        if not q:
            status.update("[#d9a300]请输入关键词[/]")
            return

        status.update(f"[#8a8f98]搜索 '{q}'...[/]")
        hits = await fts_search(q, limit=50)
        status.update(
            f"[#5e6ad2]query: {q}[/]   "
            f"[bold #27a644]{len(hits)} 命中[/]"
        )
        if not hits:
            await result_box.mount(Static(
                "[#8a8f98]没找到匹配. 试试更简短或更具体的关键词.[/]"
            ))
            return
        for h in hits:
            snippet = h.get("snippet") or ""
            # 把 <mark>xxx</mark> 转 Rich 高亮
            snippet = re.sub(
                r"<mark>(.*?)</mark>",
                r"[reverse #b88aff]\1[/]",
                snippet,
            )
            await result_box.mount(Static(
                f"[#5e6ad2]{h['weibo_id']}[/]  "
                f"[#8a8f98]uid={h['uid']}  score={h['score']:.2f}[/]\n"
                f"  {snippet}",
                classes="card",
            ))
