"""集成测试 fixtures — respx HTTP mock + in-memory SQLite + 共享 weibo 样本数据."""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
import respx


# 所有集成测试默认带 integration mark
def pytest_collection_modifyitems(config, items):
    for item in items:
        if "tests/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture
def fixtures_dir() -> Path:
    """fixtures/ 目录绝对路径."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def weibo_responses(fixtures_dir: Path) -> dict:
    """加载 m_weibo_responses.json — 真实 m.weibo.cn 响应样本."""
    p = fixtures_dir / "m_weibo_responses.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


@pytest_asyncio.fixture
async def integration_db() -> AsyncIterator[str]:
    """in-memory SQLite (或临时文件) 隔离的集成测试 DB.

    每个测试一份, 用完即删, 不污染开发库.
    """
    fd, path = tempfile.mkstemp(suffix="_integ.db")
    os.close(fd)
    url = f"sqlite+aiosqlite:///{path}"
    old = os.environ.get("WCN_DATABASE_URL")
    os.environ["WCN_DATABASE_URL"] = url

    # 清 settings cache + engine cache
    from backend.app.config import get_settings
    from backend.app.db.base import reset_engine
    get_settings.cache_clear()
    await reset_engine()

    # 初始化 schema
    from backend.app.db.base import init_db
    from backend.app.db.fts import init_fts
    await init_db()
    await init_fts()

    try:
        yield url
    finally:
        if old is not None:
            os.environ["WCN_DATABASE_URL"] = old
        else:
            os.environ.pop("WCN_DATABASE_URL", None)
        get_settings.cache_clear()
        await reset_engine()
        os.unlink(path)


@pytest_asyncio.fixture
async def respx_mock():
    """respx HTTP mock 上下文 — 自动启停."""
    with respx.mock(base_url="https://m.weibo.cn", assert_all_called=False) as mock:
        yield mock


@pytest.fixture
def sample_user_response() -> dict:
    """m.weibo.cn /api/container/getIndex?type=uid 用户信息样本."""
    return {
        "ok": 1,
        "data": {
            "userInfo": {
                "id": 555666777,
                "screen_name": "集成测试用户",
                "description": "integration test fixture",
                "verified": True,
                "verified_type": 0,
                "verified_reason": "测试认证",
                "statuses_count": 1234,
                "followers_count": 100000,
                "follow_count": 50,
                "gender": "f",
            },
        },
    }


@pytest.fixture
def sample_weibo_page_response() -> dict:
    """m.weibo.cn 用户微博列表样本 (含 1 原创 + 1 转发 + 1 广告卡)."""
    return {
        "ok": 1,
        "data": {
            "cards": [
                {
                    "card_type": 9,
                    "mblog": {
                        "id": "INT_W1",
                        "bid": "BID1",
                        "text": "集成测试 #编程# 真不错 @张三",
                        "source": "iPhone",
                        "attitudes_count": 100,
                        "comments_count": 30,
                        "reposts_count": 10,
                        "user": {"id": 555666777},
                        "pics": [{"large": {"url": "https://example.com/p1.jpg"}}],
                    },
                },
                {
                    "card_type": 9,
                    "mblog": {
                        "id": "INT_W2",
                        "bid": "BID2",
                        "text": "转发了一条消息",
                        "user": {"id": 555666777},
                        "attitudes_count": 5,
                        "comments_count": 1,
                        "reposts_count": 0,
                        "retweeted_status": {"id": "RT1", "text": "原文"},
                    },
                },
                # 广告卡 (card_type != 9)
                {"card_type": 11, "card_group": []},
            ],
        },
    }


@pytest.fixture
def sample_empty_page_response() -> dict:
    """空页响应 — 表示翻完."""
    return {"ok": 1, "data": {"cards": []}}


@pytest.fixture
def sample_ad_only_page_response() -> dict:
    """全广告卡页 — 测连续空页守卫触发."""
    return {
        "ok": 1,
        "data": {
            "cards": [
                {"card_type": 11, "card_group": []},
                {"card_type": 11, "card_group": []},
            ],
        },
    }


@pytest.fixture
def sample_rate_limited_response() -> dict:
    """微博 429 风格响应 — 测限频处理."""
    return {
        "ok": 0,
        "msg": "操作过于频繁, 请稍后再试",
    }
