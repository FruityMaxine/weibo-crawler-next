"""UserListEditor / Picker / UIDInput widget v0.8.0.0 测试."""

from __future__ import annotations

import pytest

from cli.tui.user_list_store import UserListStore


@pytest.mark.asyncio
async def test_picker_mounts_with_lists(tmp_path, monkeypatch):
    """UserListPickerScreen 启动时列出已有列表."""
    monkeypatch.setenv("WCN_USER_LISTS_DIR", str(tmp_path))
    store = UserListStore(base_dir=tmp_path)
    store.save("test1", [1, 2])
    store.save("test2", [3])

    from cli.tui import WCNApp
    from cli.tui.screens.user_list_picker import UserListPickerScreen

    app = WCNApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen(UserListPickerScreen())
        await pilot.pause()
        assert "UserListPickerScreen" in type(pilot.app.screen).__name__
        # 应有 2 个 pick 按钮 + 1 取消
        buttons = pilot.app.screen.query("Button")
        assert len(buttons) >= 3


@pytest.mark.asyncio
async def test_picker_empty_state(tmp_path, monkeypatch):
    """无列表时 picker 显示提示."""
    monkeypatch.setenv("WCN_USER_LISTS_DIR", str(tmp_path))

    from cli.tui import WCNApp
    from cli.tui.screens.user_list_picker import UserListPickerScreen

    app = WCNApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen(UserListPickerScreen())
        await pilot.pause()
        assert "UserListPickerScreen" in type(pilot.app.screen).__name__


@pytest.mark.asyncio
async def test_editor_mounts_with_list(tmp_path, monkeypatch):
    """UserListEditorScreen 启动 + 显示 UIDInput 每行."""
    monkeypatch.setenv("WCN_USER_LISTS_DIR", str(tmp_path))
    store = UserListStore(base_dir=tmp_path)
    store.save("edit_test", [100, 200, 300], {"100": "user-a", "200": "user-b"})

    from cli.tui import WCNApp
    from cli.tui.screens.user_list_editor import UserListEditorScreen
    from cli.tui.widgets.uid_input import UIDInput

    app = WCNApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen(UserListEditorScreen("edit_test"))
        await pilot.pause()
        screen = pilot.app.screen
        assert "UserListEditorScreen" in type(screen).__name__
        # 应有 3 个 UIDInput (每个 UID 一个)
        uid_inputs = screen.query(UIDInput)
        assert len(uid_inputs) == 3


@pytest.mark.asyncio
async def test_editor_bulk_add(tmp_path, monkeypatch):
    """UserListEditor 批量粘贴解析."""
    monkeypatch.setenv("WCN_USER_LISTS_DIR", str(tmp_path))
    store = UserListStore(base_dir=tmp_path)
    store.save("bulk_test", [])

    from cli.tui import WCNApp
    from cli.tui.screens.user_list_editor import UserListEditorScreen
    from textual.widgets import TextArea

    app = WCNApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen(UserListEditorScreen("bulk_test"))
        await pilot.pause()
        # 模拟用户粘贴
        screen = pilot.app.screen
        ta = screen.query_one("#bulk-paste", TextArea)
        ta.text = "1000 Alice\n2000, Bob\n3000\n# 这行注释\nnotanumber\n"
        await pilot.pause()
        # 点批量添加
        await pilot.click("#btn-bulk-add")
        await pilot.pause()
        # 验证: 3 个合法 UID 被加 (跳过注释 + 非数字)
        uids = store.load("bulk_test")
        assert set(uids) == {1000, 2000, 3000}
        labels = store.load_full("bulk_test").get("labels", {})
        assert labels.get("1000") == "Alice"
        assert labels.get("2000") == "Bob"


@pytest.mark.asyncio
async def test_uid_input_widget(tmp_path, monkeypatch):
    """UIDInput widget 渲染 + 删除消息."""
    monkeypatch.setenv("WCN_USER_LISTS_DIR", str(tmp_path))
    store = UserListStore(base_dir=tmp_path)
    store.save("widget_test", [555], {"555": "tester"})

    from cli.tui import WCNApp
    from cli.tui.screens.user_list_editor import UserListEditorScreen
    from cli.tui.widgets.uid_input import UIDInput

    app = WCNApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen(UserListEditorScreen("widget_test"))
        await pilot.pause()
        screen = pilot.app.screen
        widgets = screen.query(UIDInput)
        assert len(widgets) == 1
        w = widgets[0]
        assert w.uid == 555
        assert w.label == "tester"  # Input 的初始值


@pytest.mark.asyncio
async def test_editor_rename_list(tmp_path, monkeypatch):
    """编辑时改 list-name 触发文件重命名."""
    monkeypatch.setenv("WCN_USER_LISTS_DIR", str(tmp_path))
    store = UserListStore(base_dir=tmp_path)
    store.save("old_name", [42])

    from cli.tui import WCNApp
    from cli.tui.screens.user_list_editor import UserListEditorScreen
    from textual.widgets import Input

    app = WCNApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen(UserListEditorScreen("old_name"))
        await pilot.pause()
        # 改名
        name_input = pilot.app.screen.query_one("#edit-list-name", Input)
        name_input.value = "new_name"
        await pilot.pause()
        # 触发保存
        pilot.app.screen.action_save_all()
        await pilot.pause()
        # 验证: 新名存在, 旧名不存在
        assert "new_name" in store.list_all()
        assert "old_name" not in store.list_all()
        assert store.load("new_name") == [42]
