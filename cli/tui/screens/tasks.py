"""任务列表屏 — 显示最近 CrawlTask + 实时刷新."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from backend.app.db.base import get_sessionmaker
from backend.app.services import TaskService
from cli.tui.widgets.task_card import TaskCard


class TasksScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "返回"),
        ("r", "refresh", "刷新"),
        ("q", "app.exit", "退出"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("[bold #5e6ad2]任务列表[/]", classes="card-title")
        yield VerticalScroll(id="tasks-list")
        yield Footer()

    async def on_mount(self) -> None:
        await self._refresh_tasks()

    async def action_refresh(self) -> None:
        await self._refresh_tasks()

    async def _refresh_tasks(self) -> None:
        container = self.query_one("#tasks-list", VerticalScroll)
        await container.remove_children()
        sm = get_sessionmaker()
        async with sm() as session:
            items = await TaskService(session).list_all(limit=50)
        if not items:
            await container.mount(
                Static("[#8a8f98]暂无任务. 通过 API /api/tasks 或下次 CLI 命令创建.[/]")
            )
            return
        for t in items:
            await container.mount(
                TaskCard(
                    task_id=t.id, name=t.name,
                    status=str(t.status.value),
                    progress=t.progress, fetched=t.total_fetched,
                )
            )
