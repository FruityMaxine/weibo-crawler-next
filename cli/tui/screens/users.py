"""已抓用户浏览屏 — 列表 + 详情."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from backend.app.db.base import get_sessionmaker
from backend.app.services import UserService


class UsersScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "返回"),
        ("r", "refresh", "刷新"),
        ("q", "app.exit", "退出"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("[bold #4ec3ff]● 已抓用户[/]   [#8a8f98]r 刷新 · Esc 返回[/]", classes="card-title")
        yield VerticalScroll(id="users-list")
        yield Footer()

    async def on_mount(self) -> None:
        await self._refresh()

    async def action_refresh(self) -> None:
        await self._refresh()

    async def _refresh(self) -> None:
        container = self.query_one("#users-list", VerticalScroll)
        await container.remove_children()
        sm = get_sessionmaker()
        async with sm() as session:
            items = await UserService(session).list_all(limit=100)
        if not items:
            await container.mount(Static(
                "[#8a8f98]暂无用户. 回主菜单选 [开始采集] 抓一个看看.[/]"
            ))
            return
        for u in items:
            verified = "[#5e6ad2]✓ 认证[/]" if u.verified else ""
            await container.mount(Static(
                f"[bold #f7f8f8]{u.screen_name}[/]  "
                f"[#8a8f98]uid={u.uid}[/]  {verified}\n"
                f"  [#d0d6e0]{u.description or '无简介'}[/]\n"
                f"  [#27a644]微博 {u.statuses_count}[/]  "
                f"[#4ec3ff]粉丝 {u.followers_count}[/]  "
                f"[#b88aff]关注 {u.follow_count}[/]",
                classes="card",
            ))
