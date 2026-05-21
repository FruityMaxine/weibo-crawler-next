"""Textual TUI 主入口 — `wcn tui` 调用 WCNApp().run()."""

from __future__ import annotations

from textual.app import App

from backend.app.db.base import init_db
from cli.tui.screens.config import ConfigScreen
from cli.tui.screens.export import ExportScreen
from cli.tui.screens.help import HelpScreen
from cli.tui.screens.logs import LogsScreen
from cli.tui.screens.main import MainScreen
from cli.tui.screens.tasks import TasksScreen
from cli.tui.theme import TUI_CSS


class WCNApp(App):
    """weibo-crawler-next Textual TUI."""

    CSS = TUI_CSS
    TITLE = "weibo-crawler-next"
    SUB_TITLE = "现代化微博数据采集 — TUI"

    SCREENS = {
        "tasks": TasksScreen,
        "config": ConfigScreen,
        "logs": LogsScreen,
        "export": ExportScreen,
        "help": HelpScreen,
    }

    BINDINGS = [
        ("ctrl+c", "exit", "退出"),
    ]

    async def on_mount(self) -> None:
        await init_db()
        await self.push_screen(MainScreen())
