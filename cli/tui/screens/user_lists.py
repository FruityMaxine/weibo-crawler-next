"""用户列表管理屏 — 创建/添加/删除/查看已保存的微博 UID 批次.

用户场景: 固定批次的微博用户, 第一次添加, 后续 [开始采集] → [📋 加载列表]
直接批量抓取, 不用每次重输.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button, Footer, Header, Input, Label, Select, Static,
)

from cli.tui.user_list_store import UserListStore


class UserListsScreen(Screen):
    """用户列表管理: 选列表 / 新建列表 / 加 UID / 删 UID."""

    BINDINGS = [
        ("escape", "app.pop_screen", "返回"),
        ("q", "app.exit", "退出"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._store = UserListStore()
        self._current: str = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "[bold #b88aff]● 用户列表管理[/]   "
            "[#8a8f98]批次保存 UID, 采集屏点 [加载列表] 一键拉取[/]",
            classes="card-title",
        )
        with Vertical(id="user-lists-form"):
            yield Label("选择已有列表:")
            yield Select(
                [("(无, 请新建)", "")],
                id="select-list",
                allow_blank=False,
            )

            yield Label("新建列表 (输入名称, 点 [新建]):")
            with Horizontal():
                yield Input(placeholder="例: 娱乐圈大V", id="new-list-name")
                yield Button("➕ 新建列表", id="btn-new-list", classes="-primary")

            yield Static(
                "[bold #5e6ad2]── 当前列表 UID 操作 ──[/]",
                classes="muted",
            )
            yield Label("UID:")
            with Horizontal():
                yield Input(placeholder="例: 1669879400", id="add-uid-input")
                yield Input(placeholder="备注 (可空, 如 '迪丽热巴')", id="add-uid-label")
                yield Button("➕ 添加", id="btn-add-uid", classes="-primary")

            yield Static("当前列表为空", id="current-list-display", classes="card")

            with Horizontal():
                yield Button("📝 编辑当前列表 (高级)", id="btn-edit-list", classes="-primary")
                yield Button("🗑 删除当前列表", id="btn-del-list", classes="-danger")
                yield Button("← 返回", id="btn-back")

            yield Static("", id="user-list-status", classes="card")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_list_options()

    def on_screen_resume(self) -> None:
        self._refresh_list_options()

    def _refresh_list_options(self) -> None:
        """更新 Select 中的列表选项."""
        sel = self.query_one("#select-list", Select)
        names = self._store.list_all()
        options = [(name, name) for name in names] or [("(无, 请新建)", "")]
        sel.set_options(options)
        if names and not self._current:
            self._current = names[0]
            sel.value = self._current
            self._refresh_display()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "select-list":
            val = str(event.value or "")
            if val:
                self._current = val
                self._refresh_display()

    def _refresh_display(self) -> None:
        display = self.query_one("#current-list-display", Static)
        if not self._current:
            display.update("[#8a8f98]未选列表[/]")
            return
        data = self._store.load_full(self._current)
        uids = data.get("uids", [])
        labels = data.get("labels", {})
        if not uids:
            display.update(f"[#5e6ad2]列表 '{self._current}'[/]  [#8a8f98](空, 加 UID 开始)[/]")
            return
        lines = [
            f"[bold #5e6ad2]列表 '{self._current}'[/]  "
            f"[#8a8f98]共 {len(uids)} 个 UID[/]\n"
        ]
        for u in uids:
            lbl = labels.get(str(u), "")
            tag = f"  [#27a644]●[/] [#f7f8f8]{u}[/]"
            if lbl:
                tag += f"  [#d0d6e0]{lbl}[/]"
            lines.append(tag)
        display.update("\n".join(lines))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            self.app.pop_screen()
            return

        if bid == "btn-new-list":
            name = self.query_one("#new-list-name", Input).value.strip()
            if not name:
                self._notify("请输入列表名称", "warning")
                return
            self._store.save(name, [])
            self._current = name
            self.query_one("#new-list-name", Input).value = ""
            self._refresh_list_options()
            self.query_one("#select-list", Select).value = name
            self._refresh_display()
            self._notify(f"已创建列表 '{name}'", "success")
            return

        if bid == "btn-add-uid":
            if not self._current:
                self._notify("先选/建一个列表再加 UID", "warning")
                return
            uid_text = self.query_one("#add-uid-input", Input).value.strip()
            label_text = self.query_one("#add-uid-label", Input).value.strip()
            if not uid_text.isdigit():
                self._notify("UID 必须是纯数字", "danger")
                return
            self._store.add_uid(self._current, int(uid_text), label_text)
            self.query_one("#add-uid-input", Input).value = ""
            self.query_one("#add-uid-label", Input).value = ""
            self._refresh_display()
            self._notify(f"已添加 uid={uid_text} 到列表 '{self._current}'", "success")
            return

        if bid == "btn-del-list":
            if not self._current:
                self._notify("无列表可删", "warning")
                return
            if self._store.delete(self._current):
                self._notify(f"已删除列表 '{self._current}'", "warning")
                self._current = ""
                self._refresh_list_options()
                self._refresh_display()
            return

        if bid == "btn-edit-list":
            # v0.8.0.0: push UserListEditorScreen 高级编辑
            if not self._current:
                self._notify("先选/建一个列表才能编辑", "warning")
                return
            from cli.tui.screens.user_list_editor import UserListEditorScreen
            await self.app.push_screen(UserListEditorScreen(self._current))
            return

    def _notify(self, msg: str, level: str = "info") -> None:
        if not self.is_attached:
            return
        try:
            status = self.query_one("#user-list-status", Static)
        except Exception:
            return
        cls = {"success": "success", "warning": "warning",
               "danger": "danger", "info": "info"}.get(level, "info")
        status.set_classes(f"card {cls}")
        status.update(msg)
