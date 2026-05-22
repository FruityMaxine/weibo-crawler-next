"""已抓微博浏览屏 — 列表 + UID 过滤."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from backend.app.db.base import get_sessionmaker
from backend.app.services import WeiboService


class WeiboScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "返回"),
        ("q", "app.exit", "退出"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("[bold #ff7eb6]● 已抓微博[/]   [#8a8f98]输 UID 过滤, 留空看全部[/]", classes="card-title")
        with Horizontal(id="weibo-filter"):
            yield Label("UID 过滤:")
            yield Input(placeholder="留空 = 全部", id="filter-uid")
            yield Button("刷新", id="btn-refresh", classes="-primary")
            yield Button("← 返回", id="btn-back")
        yield VerticalScroll(id="weibo-list")
        yield Footer()

    async def on_mount(self) -> None:
        await self._refresh(None)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
            return
        if event.button.id == "btn-refresh":
            uid_str = self.query_one("#filter-uid", Input).value.strip()
            uid = int(uid_str) if uid_str.isdigit() else None
            await self._refresh(uid)

    async def _refresh(self, uid: int | None) -> None:
        container = self.query_one("#weibo-list", VerticalScroll)
        await container.remove_children()
        sm = get_sessionmaker()
        async with sm() as session:
            items = await WeiboService(session).list_recent(limit=100, uid=uid)
        if not items:
            await container.mount(Static(
                "[#8a8f98]暂无微博. 回主菜单选 [开始采集].[/]"
            ))
            return
        for w in items:
            tag = "[#b88aff]🔁 转发[/]" if w.is_retweet else "[#27a644]📝 原创[/]"
            ts = w.created_at.strftime("%Y-%m-%d %H:%M") if w.created_at else "-"
            preview = (w.text or "")[:120].replace("\n", " ")
            await container.mount(Static(
                f"{tag}  [#8a8f98]{ts}[/]  [#5e6ad2]{w.weibo_id}[/]  "
                f"[#8a8f98]uid={w.uid}[/]\n"
                f"  [#f7f8f8]{preview}[/]\n"
                f"  [#d65555]❤ {w.attitudes_count}[/]  "
                f"[#4ec3ff]💬 {w.comments_count}[/]  "
                f"[#ffaa3e]🔁 {w.reposts_count}[/]",
                classes="card",
            ))
