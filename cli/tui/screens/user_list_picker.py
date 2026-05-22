"""UserListPickerScreen — ModalScreen 弹窗式列表选择器.

v0.8.0.0: 修 crawl.py._load_list_dialog "始终加载第一个列表" 的设计缺陷.
用户在采集屏点 [📋 加载列表] → 弹本屏 → 选定列表 → dismiss 返回
(name, uids) 给 caller.

ModalScreen 与普通 Screen 区别: 半透明覆盖背景 + 焦点锁定 + dismiss 返结果.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Static

from cli.tui.user_list_store import UserListStore


class UserListPickerScreen(ModalScreen[tuple[str, list[int]] | None]):
    """弹窗选列表. dismiss 返 (name, uids) 或 None (取消)."""

    DEFAULT_CSS = """
    UserListPickerScreen {
        align: center middle;
    }

    UserListPickerScreen > Vertical {
        width: 70;
        max-height: 80%;
        border: heavy #5e6ad2;
        background: #0f1011;
        padding: 1 2;
    }

    UserListPickerScreen Button {
        width: 100%;
        margin: 0 0 1 0;
    }

    UserListPickerScreen #picker-cancel {
        background: transparent;
        border: solid #23252a;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "取消", priority=True),
        Binding("q", "cancel", "取消"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._store = UserListStore()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Static(
                "[bold #5e6ad2]📋 选择用户列表[/]",
                classes="card-title",
            )
            yield Static(
                "[#8a8f98]上下键移动 → Enter 或点击 → 自动 dismiss 返主屏批量抓取[/]",
                classes="muted",
            )
            yield VerticalScroll(id="picker-options")
            yield Button("× 取消 (Esc)", id="picker-cancel")
        yield Footer()

    async def on_mount(self) -> None:
        container = self.query_one("#picker-options", VerticalScroll)
        names = self._store.list_all()
        if not names:
            await container.mount(Static(
                "[#d9a300]还没保存任何用户列表.[/]\n"
                "[#8a8f98]先 Esc 返回主菜单, 选 [用户列表] 创建一个.[/]",
                classes="card",
            ))
            return
        for name in names:
            data = self._store.load_full(name)
            uids = data.get("uids") or []
            await container.mount(Button(
                f"📁 {name}  [#8a8f98]({len(uids)} 个 UID)[/]",
                id=f"pick-{name}",
                classes="-primary",
            ))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "picker-cancel":
            self.dismiss(None)
            return
        if bid.startswith("pick-"):
            name = bid[len("pick-"):]
            uids = self._store.load(name)
            self.dismiss((name, uids))

    def action_cancel(self) -> None:
        self.dismiss(None)
