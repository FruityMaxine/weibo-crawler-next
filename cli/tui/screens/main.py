"""主屏 — sidebar 菜单 + 主区欢迎卡片."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from backend import __version__
from cli.tui.widgets.menu_list import MenuList


class MainScreen(Screen):
    BINDINGS = [
        ("q", "quit_app", "退出"),
        ("escape", "quit_app", "退出"),
        ("?", "push_screen('help')", "帮助"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("[bold]wcn[/]", id="sidebar-title")
                yield MenuList(
                    items=[
                        ("tasks", "📋  任务"),
                        ("export", "📤  导出"),
                        ("config", "⚙   配置"),
                        ("logs", "📜  日志"),
                        ("help", "?   帮助"),
                        ("quit", "✕   退出"),
                    ],
                    id="main-menu",
                )
            with Vertical(id="main-content"):
                yield Static(
                    "[bold #5e6ad2]weibo-crawler-next[/]  "
                    f"[#8a8f98]v{__version__}[/]",
                    classes="card-title",
                )
                yield Static(
                    "现代化微博数据采集与分析平台.\n\n"
                    "[#d0d6e0]左侧菜单上下键导航, Enter 进入.[/]\n"
                    "[#8a8f98]快捷键: q 退出 · ? 帮助 · Tab 切焦点[/]",
                    classes="card",
                )
                yield Static(
                    "[bold]当前模式[/]: TUI 交互模式\n"
                    "[bold]后端[/]: 已连接本地 SQLite + APScheduler\n"
                    "[bold]导出器[/]: 6 种 (CSV / JSON / SQLite / MySQL / MongoDB / Webhook)",
                    classes="card",
                )
        yield Footer()

    def on_option_list_option_selected(self, event) -> None:
        target = event.option.id
        if target == "quit":
            self.app.exit()
            return
        if target in {"tasks", "export", "config", "logs", "help"}:
            self.app.push_screen(target)

    def action_quit_app(self) -> None:
        self.app.exit()
