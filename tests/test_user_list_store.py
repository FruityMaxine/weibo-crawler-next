"""UserListStore + UserListsScreen 测试."""

from __future__ import annotations

import pytest

from cli.tui.user_list_store import UserListStore


def test_save_and_load_roundtrip(tmp_path):
    store = UserListStore(base_dir=tmp_path)
    store.save("default", [1, 2, 3])
    assert store.load("default") == [1, 2, 3]


def test_load_full_returns_labels(tmp_path):
    store = UserListStore(base_dir=tmp_path)
    store.save("x", [100, 200], {"100": "Alice"})
    data = store.load_full("x")
    assert data["uids"] == [100, 200]
    assert data["labels"] == {"100": "Alice"}


def test_add_uid_no_duplicate(tmp_path):
    store = UserListStore(base_dir=tmp_path)
    store.save("x", [1])
    store.add_uid("x", 1)  # 重复加
    store.add_uid("x", 2)
    assert store.load("x") == [1, 2]


def test_add_uid_with_label(tmp_path):
    store = UserListStore(base_dir=tmp_path)
    store.save("x", [])
    store.add_uid("x", 999, "测试")
    full = store.load_full("x")
    assert full["labels"]["999"] == "测试"


def test_remove_uid(tmp_path):
    store = UserListStore(base_dir=tmp_path)
    store.save("x", [1, 2, 3])
    assert store.remove_uid("x", 2)
    assert store.load("x") == [1, 3]
    assert not store.remove_uid("x", 999)


def test_list_all(tmp_path):
    store = UserListStore(base_dir=tmp_path)
    store.save("a", [1])
    store.save("b", [2])
    names = store.list_all()
    assert set(names) == {"a", "b"}


def test_delete(tmp_path):
    store = UserListStore(base_dir=tmp_path)
    store.save("x", [1])
    assert store.delete("x")
    assert not (tmp_path / "x.json").exists()
    assert not store.delete("x")


def test_safe_name_strips_dangerous_chars(tmp_path):
    store = UserListStore(base_dir=tmp_path)
    store.save("../../etc/passwd", [1])
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    assert ".." not in files[0].name


def test_empty_load(tmp_path):
    store = UserListStore(base_dir=tmp_path)
    assert store.load("nonexistent") == []
    full = store.load_full("nonexistent")
    assert full["uids"] == []


def test_load_uids_filter_non_digit(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text('{"uids": [1, "abc", 2, null], "labels": {}}', encoding="utf-8")
    store = UserListStore(base_dir=tmp_path)
    assert store.load("bad") == [1, 2]


@pytest.mark.asyncio
async def test_user_lists_screen_mounts():
    from cli.tui import WCNApp
    app = WCNApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen("user_lists")
        await pilot.pause()
        assert "UserListsScreen" in type(pilot.app.screen).__name__
        assert pilot.app.screen.query("#select-list")
        assert pilot.app.screen.query("#new-list-name")
