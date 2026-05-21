"""日志屏 — 显示最近 lines, tail -f 风格."""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, RichLog


class LogsScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "返回"),
        ("q", "app.exit", "退出"),
        ("c", "clear", "清空"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield RichLog(highlight=True, markup=True, id="log-view", wrap=False)
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#log-view", RichLog)
        log.write("[bold #5e6ad2]wcn 日志流 (静态读取最近 200 行)[/]")
        log.write("")
        # 尝试读 data/wcn.log; 不存在则提示
        p = Path("./data/wcn.log")
        if not p.exists():
            log.write("[#8a8f98]当前未配置文件日志. 默认日志输出 stderr.[/]")
            log.write(
                "[#8a8f98]启用文件日志: 设置 WCN_LOG_FILE=./data/wcn.log 后重启 wcn serve.[/]"
            )
            return
        try:
            lines = p.read_text(encoding="utf-8").splitlines()[-200:]
            for line in lines:
                log.write(line)
        except OSError as e:
            log.write(f"[#d65555]读日志失败: {e}[/]")

    def action_clear(self) -> None:
        self.query_one("#log-view", RichLog).clear()
