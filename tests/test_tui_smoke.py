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


# v0.5.0.0: 新增 4 个屏 smoke test
@pytest.mark.asyncio
async def test_navigate_to_crawl_screen():
    from cli.tui import WCNApp
    app = WCNApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen("crawl")
        await pilot.pause()
        assert "CrawlScreen" in type(pilot.app.screen).__name__
        # 验证输入框 + 进度条 + 日志都挂载
        assert pilot.app.screen.query("#input-uid")
        assert pilot.app.screen.query("#crawl-progress")
        assert pilot.app.screen.query("#crawl-log")


@pytest.mark.asyncio
async def test_navigate_to_users_screen():
    from cli.tui import WCNApp
    app = WCNApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen("users")
        await pilot.pause()
        assert "UsersScreen" in type(pilot.app.screen).__name__


@pytest.mark.asyncio
async def test_navigate_to_weibo_screen():
    from cli.tui import WCNApp
    app = WCNApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen("weibo")
        await pilot.pause()
        assert "WeiboScreen" in type(pilot.app.screen).__name__


@pytest.mark.asyncio
async def test_navigate_to_search_screen():
    from cli.tui import WCNApp
    app = WCNApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.app.push_screen("search")
        await pilot.pause()
        assert "SearchScreen" in type(pilot.app.screen).__name__
        assert pilot.app.screen.query("#search-input")
