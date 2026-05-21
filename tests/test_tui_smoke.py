"""Textual TUI smoke test — headless 启动 + 切屏 + 退出.

不模拟真用户场景, 仅证明 app 可启动且各 screen 可挂载.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_app_starts_and_shows_main_screen():
    from cli.tui import WCNApp

    app = WCNApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        # MainScreen 已 push, sidebar/main-content 都挂载了
        assert "MainScreen" in type(pilot.app.screen).__name__
        screen = pilot.app.screen
        assert screen.query("#sidebar")
        assert screen.query("#main-content")
        assert screen.query("#main-menu")


@pytest.mark.asyncio
async def test_navigate_to_export_screen():
    """从 main 推 export screen, 验证切屏正常."""
    from cli.tui import WCNApp

    app = WCNApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen("export")
        await pilot.pause()
        assert "ExportScreen" in type(pilot.app.screen).__name__


@pytest.mark.asyncio
async def test_navigate_to_config_screen():
    from cli.tui import WCNApp

    app = WCNApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen("config")
        await pilot.pause()
        assert "ConfigScreen" in type(pilot.app.screen).__name__


@pytest.mark.asyncio
async def test_navigate_to_tasks_screen():
    from cli.tui import WCNApp

    app = WCNApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen("tasks")
        await pilot.pause()
        assert "TasksScreen" in type(pilot.app.screen).__name__


@pytest.mark.asyncio
async def test_navigate_to_help_screen():
    from cli.tui import WCNApp

    app = WCNApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen("help")
        await pilot.pause()
        assert "HelpScreen" in type(pilot.app.screen).__name__
