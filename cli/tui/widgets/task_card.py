"""任务卡片 — 用于 TasksScreen 列表渲染."""

from __future__ import annotations

from textual.containers import Vertical
from textual.widgets import Static


class TaskCard(Vertical):
    """单任务卡片 — 显示状态/进度/已抓条数."""

    DEFAULT_CSS = """
    TaskCard {
        height: auto;
        background: #0f1011;
        border: solid #23252a;
        padding: 1 2;
        margin-bottom: 1;
    }
    TaskCard:focus {
        border: solid #5e6ad2;
    }
    """

    def __init__(
        self,
        task_id: int,
        name: str,
        status: str,
        progress: int,
        fetched: int,
        *,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self.task_id = task_id
        self._name = name
        self._status = status
        self._progress = progress
        self._fetched = fetched

    def compose(self):
        color = {
            "success": "#27a644",
            "failed": "#d65555",
            "running": "#5e6ad2",
            "pending": "#8a8f98",
            "paused": "#d0d6e0",
        }.get(self._status, "#8a8f98")
        yield Static(
            f"[bold]#{self.task_id}[/] [bold #f7f8f8]{self._name}[/]  "
            f"[{color}]{self._status}[/]"
        )
        yield Static(
            f"[#8a8f98]进度 {self._progress}% · 已抓 {self._fetched} 条[/]"
        )
