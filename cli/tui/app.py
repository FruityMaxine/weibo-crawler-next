"""Textual TUI 主入口 — `wcn` 无参数 / `wcn tui` 启动."""

from __future__ import annotations

from textual.app import App

from backend.app.db.base import init_db
from cli.tui.screens.config import ConfigScreen
from cli.tui.screens.crawl import CrawlScreen
from cli.tui.screens.export import ExportScreen
from cli.tui.screens.help import HelpScreen
from cli.tui.screens.logs import LogsScreen
from cli.tui.screens.main import MainScreen
from cli.tui.screens.search import SearchScreen
from cli.tui.screens.tasks import TasksScreen
from cli.tui.screens.user_lists import UserListsScreen
from cli.tui.screens.users import UsersScreen
from cli.tui.screens.weibo_view import WeiboScreen
from cli.tui.theme import TUI_CSS


class WCNApp(App):
    """weibo-crawler-next Textual TUI."""

    CSS = TUI_CSS
    TITLE = "weibo-crawler-next"
    SUB_TITLE = "微博数据采集 · 交互式菜单"

    SCREENS = {
        "crawl":       CrawlScreen,
        "user_lists":  UserListsScreen,
        "tasks":       TasksScreen,
        "users":       UsersScreen,
        "weibo":       WeiboScreen,
        "search":      SearchScreen,
        "export":      ExportScreen,
        "config":      ConfigScreen,
        "logs":        LogsScreen,
        "help":        HelpScreen,
    }

    BINDINGS = [
        ("ctrl+c", "exit", "退出"),
    ]

    async def on_mount(self) -> None:
        await init_db()
        await self.push_screen(MainScreen())
