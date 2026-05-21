"""任务进度面板 — 标题 + ProgressBar + 实时状态."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import ProgressBar, Static


class ProgressPanel(Vertical):
    """显示一个任务的实时进度卡片."""

    DEFAULT_CSS = """
    ProgressPanel {
        height: auto;
        background: #0f1011;
        border: solid #23252a;
        padding: 1 2;
        margin-bottom: 1;
    }
    """

    def __init__(self, title: str, total: int = 100, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self._title = title
        self._total = total

    def compose(self) -> ComposeResult:
        yield Static(f"[bold #5e6ad2]{self._title}[/]")
        yield ProgressBar(total=self._total, id="progress-bar")
        yield Static("[#8a8f98]等待开始...[/]", id="progress-status")

    def update_progress(self, completed: int, status: str | None = None) -> None:
        bar = self.query_one("#progress-bar", ProgressBar)
        bar.update(progress=completed)
        if status:
            self.query_one("#progress-status", Static).update(f"[#8a8f98]{status}[/]")
