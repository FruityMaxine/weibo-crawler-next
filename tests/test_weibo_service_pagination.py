"""weibo_service.crawl_user v0.6.0.0 翻页守卫测试."""

from __future__ import annotations

import pytest


class _FakeClient:
    """模拟 AsyncWeiboClient.get_user_weibo_page 返回固定响应."""

    def __init__(self, pages: list[dict]) -> None:
        # pages: 每页返回的 payload (dict with 'data': {'cards': [...]})
        self._pages = pages
        self.page_calls: list[int] = []

    async def get_user_weibo_page(self, uid, *, page: int = 1, since_id=None):
        self.page_calls.append(page)
        idx = page - 1
        if idx >= len(self._pages):
            return {"data": {"cards": []}}
        return self._pages[idx]


def _ad_card() -> dict:
    """广告卡: card_type != 9, parse_weibo_card 返回 None."""
    return {"card_type": 11, "card_group": []}


def _weibo_card(weibo_id: str, uid: int = 555) -> dict:
    return {
        "card_type": 9,
        "mblog": {
            "id": weibo_id, "bid": weibo_id, "text": "test",
            "user": {"id": uid}, "attitudes_count": 0,
            "comments_count": 0, "reposts_count": 0,
        },
    }


@pytest.mark.asyncio
async def test_pagination_max_page_guard(temp_db: str):
    """连续多页全广告卡 → 翻页应在 max_page 上限强终."""
    from backend.app.db.base import get_sessionmaker, init_db
    from backend.app.services import WeiboService

    await init_db()
    # 50 页全广告卡, 每页 5 张广告
    ad_pages = [{"data": {"cards": [_ad_card() for _ in range(5)]}} for _ in range(100)]
    client = _FakeClient(ad_pages)

    sm = get_sessionmaker()
    async with sm() as session:
        ws = WeiboService(session)
        out = []
        # 关键: 单连续空页阈值 1 → 第 1 页空就终, 验证守卫
        async for w in ws.crawl_user(
            uid=999, client=client, max_count=None,
            max_page=10, empty_page_threshold=1,
        ):
            out.append(w)
        assert out == []
        # 不能翻 100 页, 受 empty_page_threshold=1 限制
        assert len(client.page_calls) <= 2


@pytest.mark.asyncio
async def test_pagination_empty_threshold(temp_db: str):
    """连续 3 空页强终 (默认行为)."""
    from backend.app.db.base import get_sessionmaker, init_db
    from backend.app.services import WeiboService

    await init_db()
    pages = [
        {"data": {"cards": [_ad_card(), _ad_card()]}},  # 页 1 空
        {"data": {"cards": [_ad_card()]}},               # 页 2 空
        {"data": {"cards": [_ad_card(), _ad_card()]}},  # 页 3 空
        {"data": {"cards": [_weibo_card("X1")]}},        # 页 4 不该到
    ]
    client = _FakeClient(pages)

    sm = get_sessionmaker()
    async with sm() as session:
        ws = WeiboService(session)
        out = []
        async for w in ws.crawl_user(
            uid=888, client=client, max_count=None,
            empty_page_threshold=3,
        ):
            out.append(w)
        # 连续 3 空页强终, 没翻到第 4 页
        assert out == []
        assert 3 not in client.page_calls or 4 not in client.page_calls


@pytest.mark.asyncio
async def test_pagination_normal_exit_on_no_cards(temp_db: str):
    """空 cards 数组正常退出 (原有行为)."""
    from backend.app.db.base import get_sessionmaker, init_db
    from backend.app.services import WeiboService

    await init_db()
    pages = [
        {"data": {"cards": [_weibo_card("A1")]}},
        {"data": {"cards": []}},  # 真正空 → 立即终止
    ]
    client = _FakeClient(pages)

    sm = get_sessionmaker()
    async with sm() as session:
        ws = WeiboService(session)
        out = [w async for w in ws.crawl_user(uid=777, client=client)]
        assert len(out) == 1
        assert out[0].weibo_id == "A1"


@pytest.mark.asyncio
async def test_pagination_max_count(temp_db: str):
    """max_count 限制 (Tick 2 之前已有的行为)."""
    from backend.app.db.base import get_sessionmaker, init_db
    from backend.app.services import WeiboService

    await init_db()
    pages = [
        {"data": {"cards": [_weibo_card(f"W{i}") for i in range(10)]}},
        {"data": {"cards": [_weibo_card(f"X{i}") for i in range(10)]}},
    ]
    client = _FakeClient(pages)

    sm = get_sessionmaker()
    async with sm() as session:
        ws = WeiboService(session)
        out = [
            w async for w in ws.crawl_user(uid=666, client=client, max_count=5)
        ]
        assert len(out) == 5
