"""配置 + 模型基础测试."""

from __future__ import annotations

import pytest

from backend.app.config import get_settings


def test_settings_defaults():
    s = get_settings()
    assert s.host == "127.0.0.1"
    assert s.port == 28800
    assert s.crawler_rate_limit > 0
    assert s.database_url.startswith("sqlite")


@pytest.mark.asyncio
async def test_init_db_creates_tables(temp_db: str):
    from backend.app.db.base import get_engine, init_db
    from sqlalchemy import inspect

    await init_db()
    engine = get_engine()
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda c: inspect(c).get_table_names())
    for t in ("users", "weibos", "media", "comments", "reposts", "crawl_tasks"):
        assert t in tables, f"表 {t} 未创建, 现有: {tables}"


@pytest.mark.asyncio
async def test_user_upsert_roundtrip(temp_db: str):
    from backend.app.db.base import get_sessionmaker, init_db
    from backend.app.services import UserService

    await init_db()
    sm = get_sessionmaker()
    async with sm() as session:
        us = UserService(session)
        u = await us.upsert({
            "uid": 999, "screen_name": "TestUser",
            "verified": False, "statuses_count": 5,
        })
        await session.commit()
        assert u.uid == 999

    async with sm() as session:
        us = UserService(session)
        fetched = await us.get(999)
        assert fetched is not None
        assert fetched.screen_name == "TestUser"
