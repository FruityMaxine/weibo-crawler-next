"""pytest fixtures — 隔离数据库, 不污染开发 SQLite."""

from __future__ import annotations

import asyncio
import os
import tempfile
from collections.abc import AsyncIterator

import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def temp_db() -> AsyncIterator[str]:
    """每个测试一份临时 SQLite, 用完即删."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    url = f"sqlite+aiosqlite:///{path}"
    old = os.environ.get("WCN_DATABASE_URL")
    os.environ["WCN_DATABASE_URL"] = url
    try:
        # 清缓存以重新读 settings + engine
        from backend.app.config import get_settings
        from backend.app.db.base import reset_engine
        get_settings.cache_clear()  # type: ignore[attr-defined]
        await reset_engine()
        yield url
    finally:
        if old is not None:
            os.environ["WCN_DATABASE_URL"] = old
        else:
            os.environ.pop("WCN_DATABASE_URL", None)
        get_settings.cache_clear()  # type: ignore[attr-defined]
        await reset_engine()
        os.unlink(path)
