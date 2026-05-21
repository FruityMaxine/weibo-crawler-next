"""MenuList — 上下键 / Enter 选择的菜单 widget.

基于 Textual OptionList, 调一下样式给 sidebar 用.
"""

from __future__ import annotations

from textual.widgets import OptionList
from textual.widgets.option_list import Option


class MenuList(OptionList):
    """sidebar 菜单 — k/j/上下键导航, Enter 触发."""

    DEFAULT_CSS = """
    MenuList {
        height: auto;
    }
    """

    BINDINGS = [
        ("k", "cursor_up", "上"),
        ("j", "cursor_down", "下"),
    ]

    def __init__(self, items: list[tuple[str, str]], *, id: str | None = None) -> None:
        # items: list of (key, label)
        options = [Option(label, id=key) for key, label in items]
        super().__init__(*options, id=id)
