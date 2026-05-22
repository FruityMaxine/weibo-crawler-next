"""UIDInput — 复合 widget: UID 数字输入 + 备注 + 删除按钮一行.

v0.8.0.0: 替代 user_lists.py 中"Input + Input + Button" 三个分离 widget 的
扁平布局, 让每行成为一个可复用的列表项.

事件:
  on(UIDInput.Deleted): 用户点了删除按钮
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Input, Static


class UIDInput(Horizontal):
    """单行 UID 编辑控件: [UID] [备注] [X 删除]."""

    DEFAULT_CSS = """
    UIDInput {
        height: 3;
        margin-bottom: 0;
        padding: 0;
    }
    UIDInput Input {
        width: 1fr;
        margin-right: 1;
    }
    UIDInput .uid-input-uid {
        width: 18;
    }
    UIDInput Button {
        width: 5;
        min-width: 5;
    }
    """

    class Deleted(Message):
        """删除按钮按下时发出, 父屏负责从数据源真删."""

        def __init__(self, sender: "UIDInput", uid: int) -> None:
            super().__init__()
            self.uid_widget = sender
            self.uid = uid

    def __init__(self, uid: int, label: str = "", *, widget_id: str | None = None) -> None:
        super().__init__(id=widget_id)
        self._uid = uid
        self._label = label

    def compose(self) -> ComposeResult:
        yield Static(
            f"[#5e6ad2]●[/] [bold]{self._uid}[/]",
            classes="uid-input-uid",
        )
        yield Input(
            value=self._label,
            placeholder="备注 (可空)",
            id=f"label-{self._uid}",
        )
        yield Button("✕", id=f"del-{self._uid}", variant="error", classes="-danger")

    @property
    def uid(self) -> int:
        return self._uid

    @property
    def label(self) -> str:
        """返回当前备注 (用户编辑后实时读取)."""
        try:
            return self.query_one(f"#label-{self._uid}", Input).value
        except Exception:
            return self._label

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == f"del-{self._uid}":
            event.stop()
            self.post_message(self.Deleted(self, self._uid))
