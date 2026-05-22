"""主屏 — 七彩 sidebar 菜单 + 主区欢迎卡片."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from backend import __version__
from cli.tui.widgets.menu_list import MenuList


# (key, label, color_class) — color_class 仅用于装饰高亮, 不破坏 OptionList 选项
MENU_ITEMS = [
    ("crawl",      "[#27a644]●[/] [bold]开始采集[/]              [#8a8f98](核心功能)[/]"),
    ("user_lists", "[#b88aff]●[/] [bold]用户列表[/]              [#8a8f98](批次管理)[/]"),
    ("tasks",      "[#5e6ad2]●[/] [bold]任务列表[/]              [#8a8f98](后台进度)[/]"),
    ("users",      "[#4ec3ff]●[/] [bold]已抓用户[/]              [#8a8f98](浏览)[/]"),
    ("weibo",      "[#ff7eb6]●[/] [bold]已抓微博[/]              [#8a8f98](浏览)[/]"),
    ("search",     "[#b88aff]●[/] [bold]全文搜索[/]              [#8a8f98](FTS5)[/]"),
    ("export",     "[#ffaa3e]●[/] [bold]导出数据[/]              [#8a8f98](6 格式)[/]"),
    ("config",     "[#d9a300]●[/] [bold]配置[/]                  [#8a8f98](可编辑)[/]"),
    ("logs",       "[#8a8f98]●[/] [bold]日志[/]"),
    ("help",       "[#5e6ad2]?[/] [bold]帮助[/]"),
    ("quit",       "[#d65555]✕[/] [bold]退出[/]"),
]


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
                yield Static("[bold #5e6ad2]weibo-crawler-next[/]", id="sidebar-title")
                yield Static(f"v{__version__}", id="sidebar-version")
                yield MenuList(items=MENU_ITEMS, id="main-menu")
            with Vertical(id="main-content"):
                yield Static(
                    "[bold #5e6ad2]欢迎使用 weibo-crawler-next[/]",
                    classes="card-title",
                )
                yield Static(
                    "[#d0d6e0]这是一个微博数据采集工具的交互式菜单 (TUI).[/]\n"
                    "[#d0d6e0]左侧菜单上下键移动, [bold]Enter[/] 进入子界面.[/]\n\n"
                    "[#8a8f98]快捷键:  ↑↓ / j k 移动  ·  Enter 选择  ·  Esc/q 退出  ·  ? 帮助[/]",
                    classes="card",
                )
                yield Static(
                    "[bold #27a644]► 开始采集[/]  抓取微博\n"
                    "[#d0d6e0]    输入微博 UID 和抓取数量, 实时进度条 + 滚动日志[/]",
                    classes="card",
                )
                yield Static(
                    "[bold #5e6ad2]► 任务列表[/]  查看已建任务\n"
                    "[bold #4ec3ff]► 已抓用户/微博[/]  浏览数据\n"
                    "[bold #b88aff]► 全文搜索[/]  SQLite FTS5\n"
                    "[bold #ffaa3e]► 导出数据[/]  CSV / JSON / SQLite / MySQL / MongoDB / Webhook",
                    classes="card",
                )
                yield Static(
                    "[#8a8f98]如需后端 API + WebUI, 另开终端: [bold]wcn serve[/][/]",
                    classes="card",
                )
        yield Footer()

    def on_option_list_option_selected(self, event) -> None:
        target = event.option.id
        if target == "quit":
            self.app.exit()
            return
        if target in {"crawl", "user_lists", "tasks", "users", "weibo",
                      "search", "export", "config", "logs", "help"}:
            self.app.push_screen(target)

    def action_quit_app(self) -> None:
        self.app.exit()
