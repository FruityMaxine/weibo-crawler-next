"""UserListEditorScreen — 编辑单个用户列表的专用屏.

v0.8.0.0: 替代原 user_lists.py 的"平铺添加" 模式, 提供:
  - 列表内 UID 完整 CRUD (UIDInput widget 每行)
  - 批量粘贴: 一次贴多行 UID (一行一个或逗号分隔), 解析后批量加
  - 重命名当前列表
  - 列表统计

进入方式: user_lists.py 主管理屏点 [📝 编辑] → push 本屏 (含 list_name 参数).
"""

from __future__ import annotations

import re

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button, Footer, Header, Input, Label, Static, TextArea,
)

from cli.tui.user_list_store import UserListStore
from cli.tui.widgets.uid_input import UIDInput


class UserListEditorScreen(Screen):
    """单列表编辑屏: 列表名 + UID 列表 + 批量粘贴区."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "返回"),
        Binding("q", "app.exit", "退出"),
        Binding("ctrl+s", "save_all", "保存"),
    ]

    def __init__(self, list_name: str) -> None:
        super().__init__()
        self._store = UserListStore()
        self._list_name = list_name
        self._original_name = list_name

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with VerticalScroll(id="editor-form"):
            yield Static(
                f"[bold #5e6ad2]📝 编辑列表[/]   [#8a8f98]('{self._list_name}')[/]",
                classes="card-title",
            )

            yield Label("列表名 (可重命名):")
            yield Input(value=self._list_name, id="edit-list-name")

            yield Static(
                "[bold #5e6ad2]── 当前列表 UID ──[/]",
                classes="muted",
            )
            yield Vertical(id="uid-list-container")

            yield Static(
                "[bold #5e6ad2]── 批量粘贴 ──[/]",
                classes="muted",
            )
            yield Label("一次粘贴多行 UID (一行一个, 或逗号分隔, 后跟备注):")
            yield TextArea(
                "",
                id="bulk-paste",
                language="python",
            )
            with Horizontal():
                yield Button("➕ 批量添加", id="btn-bulk-add", classes="-primary")
                yield Button("🗑 清空 UID 列表", id="btn-clear", classes="-danger")

            yield Static("", id="editor-status", classes="card")

            with Horizontal():
                yield Button("💾 保存 (Ctrl+S)", id="btn-save", classes="-primary")
                yield Button("← 返回", id="btn-back")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_uid_list()

    def _refresh_uid_list(self) -> None:
        container = self.query_one("#uid-list-container", Vertical)
        # 清空再填
        for child in list(container.children):
            child.remove()
        data = self._store.load_full(self._list_name)
        uids = data.get("uids") or []
        labels = data.get("labels") or {}
        if not uids:
            container.mount(Static(
                "[#8a8f98](空, 用下面批量粘贴或回上一屏单个添加)[/]",
                classes="muted",
            ))
            return
        for u in uids:
            container.mount(UIDInput(uid=u, label=labels.get(str(u), "")))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "btn-back":
            self.app.pop_screen()
            return
        if bid == "btn-save":
            self.action_save_all()
            return
        if bid == "btn-bulk-add":
            self._bulk_add()
            return
        if bid == "btn-clear":
            self._store.save(self._list_name, [], {})
            self._refresh_uid_list()
            self._notify("已清空当前列表", "warning")
            return

    def _bulk_add(self) -> None:
        text = self.query_one("#bulk-paste", TextArea).text
        if not text.strip():
            self._notify("粘贴区为空", "warning")
            return
        # 解析: 每行第 1 个数字串作 UID, 剩余作 label
        added = 0
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # 支持 ',' / 'TAB' / 空格 分隔
            parts = re.split(r"[,\t\s]+", line, maxsplit=1)
            uid_str = parts[0].strip()
            if not uid_str.isdigit():
                continue
            label = parts[1].strip() if len(parts) > 1 else ""
            self._store.add_uid(self._list_name, int(uid_str), label)
            added += 1

        if added > 0:
            self.query_one("#bulk-paste", TextArea).text = ""
            self._refresh_uid_list()
            self._notify(f"批量添加 {added} 个 UID 成功", "success")
        else:
            self._notify("没解析到有效 UID (每行第 1 项须是数字)", "warning")

    def on_uid_input_deleted(self, event: UIDInput.Deleted) -> None:
        """UIDInput 子 widget 发删除消息时, 真删 + 刷新."""
        self._store.remove_uid(self._list_name, event.uid)
        self._refresh_uid_list()
        self._notify(f"已删除 uid={event.uid}", "warning")

    def action_save_all(self) -> None:
        """保存当前列表名 (重命名) + 当前 UIDInput 的 label."""
        new_name = self.query_one("#edit-list-name", Input).value.strip()
        if not new_name:
            self._notify("列表名不能为空", "danger")
            return

        # 1. 收集 UIDInput 的实时 label
        data = self._store.load_full(self._list_name)
        labels = data.get("labels") or {}
        for w in self.query(UIDInput):
            labels[str(w.uid)] = w.label
        uids = data.get("uids") or []
        self._store.save(self._list_name, uids, labels)

        # 2. 如果重命名了, 把文件换名
        if new_name != self._original_name:
            old_data = self._store.load_full(self._list_name)
            self._store.save(new_name, old_data.get("uids") or [], old_data.get("labels") or {})
            if new_name != self._list_name:
                self._store.delete(self._list_name)
            self._list_name = new_name
            self._original_name = new_name

        self._notify(
            f"✓ 已保存列表 '{self._list_name}' ({len(uids)} 个 UID)",
            "success",
        )

    def _notify(self, msg: str, level: str = "info") -> None:
        if not self.is_attached:
            return
        try:
            status = self.query_one("#editor-status", Static)
        except Exception:
            return
        cls = {"success": "success", "warning": "warning",
               "danger": "danger", "info": "info"}.get(level, "info")
        status.set_classes(f"card {cls}")
        status.update(msg)
