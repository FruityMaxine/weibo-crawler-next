"""帮助屏 — 快捷键 + 使用流程 cheatsheet."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


HELP_TEXT = """
[bold #5e6ad2]wcn TUI 快捷键[/]

[bold]全局[/]
  q / Esc        退出 / 返回上一屏
  Tab            切换焦点
  ?              本帮助屏

[bold]菜单导航[/]
  ↑ / k          上一项
  ↓ / j          下一项
  Enter          进入选中项

[bold]任务屏[/]
  r              刷新任务列表

[bold]导出屏[/]
  Enter          触发导出按钮

[bold #5e6ad2]使用流程[/]

  1. CLI 抓取数据:
       wcn run -u 1669879400 -n 20

  2. TUI 查看任务 / 配置 / 导出:
       wcn tui

  3. WebUI 启动 (Tick 4):
       wcn serve  + 前端 dev server

[bold #5e6ad2]导出格式[/]
  csv / json / sqlite / mysql / mongodb / webhook

[bold #5e6ad2]更多文档[/]
  README.md · docs/ARCHITECTURE.md (Tick 5)
"""


class HelpScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "返回"),
        ("q", "app.exit", "退出"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(HELP_TEXT, classes="card")
        yield Footer()
