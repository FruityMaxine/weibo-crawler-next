"""集成测试: 翻页守卫 (v0.6.0.0 max_page + empty_page_threshold).

验证连续广告卡页时不会无限循环.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_continuous_ad_pages_stop_at_threshold(
    integration_db,
    respx_mock,
    weibo_responses,
    sample_user_response,
):
    """连续 N 页全广告卡 → empty_page_threshold 守卫强终, 不死循环."""
    respx_mock.get(
        "/api/container/getIndex",
        params={"type": "uid", "value": "555666777"},
    ).respond(json=sample_user_response)

    # 返回全广告卡页 100 次 (假设守卫不工作就会死循环)
    respx_mock.get("/api/container/getIndex").respond(
        json=weibo_responses["weibo_page_ad_only"],
    )

    from backend.app.crawler import AsyncWeiboClient
    from backend.app.db.base import get_sessionmaker
    from backend.app.services import UserService, WeiboService

    sm = get_sessionmaker()
    async with sm() as session:
        us = UserService(session)
        ws = WeiboService(session)
        async with AsyncWeiboClient(rate_per_sec=100.0) as client:
            await us.fetch_and_upsert(555666777, client=client)

            collected = []
            # 关键: 连续广告卡, 应在 empty_threshold 内强终
            async for w in ws.crawl_user(
                555666777, client=client,
                max_count=100,
                max_page=20,
                empty_page_threshold=3,
            ):
                collected.append(w)

            # 守卫应当让 collected 为空 (全广告) 并且翻页次数受限
            assert collected == []
            # 通过 respx_mock.calls 计数验证翻页确实被限制
            assert len(respx_mock.calls) < 10  # 不到 max_page=20


@pytest.mark.asyncio
async def test_max_page_hard_limit(
    integration_db,
    respx_mock,
    weibo_responses,
    sample_user_response,
):
    """每页都有微博 + 广告 (page_yielded>0 不触 empty), max_page=5 应在 5 页强终."""
    respx_mock.get(
        "/api/container/getIndex",
        params={"type": "uid", "value": "555666777"},
    ).respond(json=sample_user_response)

    # 每页 1 条微博 + 1 广告, 翻页可永远继续
    respx_mock.get("/api/container/getIndex").respond(json={
        "ok": 1,
        "data": {
            "cards": [
                {
                    "card_type": 9,
                    "mblog": {
                        "id": "PAGE_SAFETY_W",
                        "text": "test",
                        "user": {"id": 555666777},
                        "attitudes_count": 0, "comments_count": 0, "reposts_count": 0,
                    },
                },
            ],
        },
    })

    from backend.app.crawler import AsyncWeiboClient
    from backend.app.db.base import get_sessionmaker
    from backend.app.services import UserService, WeiboService

    sm = get_sessionmaker()
    async with sm() as session:
        us = UserService(session)
        ws = WeiboService(session)
        async with AsyncWeiboClient(rate_per_sec=100.0) as client:
            await us.fetch_and_upsert(555666777, client=client)
            collected = [
                w async for w in ws.crawl_user(
                    555666777, client=client,
                    max_count=1000,   # 大上限不限制
                    max_page=5,        # 但页数最多 5
                )
            ]
            # 同 weibo_id, 每次 upsert 不增, 所以 collected 顺序数量 ≤ 5
            # 关键看 respx.calls 数量不超过 max_page+小余
            user_index_calls = [c for c in respx_mock.calls if "containerid" in str(c.request.url)]
            assert len(user_index_calls) <= 6  # max_page=5 + 1 容差
