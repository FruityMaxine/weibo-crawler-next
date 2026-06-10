"""端到端集成测试 — mock HTTP → crawler → DB → 查询验证.

覆盖 v0.4-v0.8 主流程: HTTP 抓取 → 解析 → upsert → 入库 → 查询.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_full_crawl_flow_single_user(
    integration_db,
    respx_mock,
    weibo_responses,
):
    """完整 1 用户抓取流程: mock HTTP → service → DB → 验证."""
    # 1. 配 respx mock 路由
    respx_mock.get(
        "/api/container/getIndex",
        params={"type": "uid", "value": "1669879400"},
    ).respond(json=weibo_responses["user_index_dilireba"])
    respx_mock.get(
        "/api/container/getIndex",
        params={"containerid": "1076031669879400"},
    ).respond(json=weibo_responses["weibo_page_normal"])
    # 第 2 页空 → 终止
    respx_mock.get("/api/container/getIndex").respond(
        json=weibo_responses["weibo_page_empty"],
    )

    # 2. 跑 service
    from backend.app.crawler import AsyncWeiboClient
    from backend.app.db.base import get_sessionmaker
    from backend.app.services import UserService, WeiboService

    sm = get_sessionmaker()
    async with sm() as session:
        us = UserService(session)
        ws = WeiboService(session)
        async with AsyncWeiboClient() as client:
            user = await us.fetch_and_upsert(1669879400, client=client)
            await session.commit()
            assert user.screen_name == "迪丽热巴"
            assert user.verified is True

            count = 0
            async for w in ws.crawl_user(
                1669879400, client=client, max_count=10,
            ):
                count += 1
            await session.commit()
            # 至少抓到第 1 页的 2 条
            assert count >= 2

    # 3. 验证 DB 真落库
    async with sm() as session:
        from backend.app.db.models import User, Weibo
        from sqlalchemy import select
        u = (await session.execute(
            select(User).where(User.uid == 1669879400)
        )).scalar_one()
        assert u.screen_name == "迪丽热巴"
        assert u.statuses_count == 5000

        weibos = (await session.execute(
            select(Weibo).where(Weibo.uid == 1669879400)
        )).scalars().all()
        assert len(weibos) >= 2
        ids = {w.weibo_id for w in weibos}
        assert "FIX_W001" in ids


@pytest.mark.asyncio
async def test_full_crawl_with_retweet(
    integration_db,
    respx_mock,
    weibo_responses,
):
    """抓取含转发的页面, 验证 is_retweet 正确标记."""
    respx_mock.get(
        "/api/container/getIndex",
        params={"type": "uid", "value": "1669879400"},
    ).respond(json=weibo_responses["user_index_dilireba"])

    # 第 1 页含转发, 第 2 页空
    routes = [
        weibo_responses["weibo_page_with_retweet"],
        weibo_responses["weibo_page_empty"],
    ]
    call_count = [0]

    def respond(request):
        idx = call_count[0]
        call_count[0] += 1
        import httpx
        return httpx.Response(200, json=routes[min(idx, len(routes) - 1)])

    respx_mock.get("/api/container/getIndex").mock(side_effect=respond)

    from backend.app.crawler import AsyncWeiboClient
    from backend.app.db.base import get_sessionmaker
    from backend.app.services import UserService, WeiboService

    sm = get_sessionmaker()
    async with sm() as session:
        us = UserService(session)
        ws = WeiboService(session)
        async with AsyncWeiboClient() as client:
            await us.fetch_and_upsert(1669879400, client=client)
            await session.commit()
            collected = []
            async for w in ws.crawl_user(1669879400, client=client, max_count=10):
                collected.append(w)
            await session.commit()
            assert any(w.is_retweet for w in collected)


@pytest.mark.asyncio
async def test_full_crawl_only_original_filter(
    integration_db,
    respx_mock,
    weibo_responses,
):
    """only_original=True 过滤掉转发."""
    respx_mock.get(
        "/api/container/getIndex",
        params={"type": "uid", "value": "1669879400"},
    ).respond(json=weibo_responses["user_index_dilireba"])

    # 第 1 页全转发, 第 2 页空 → only_original 后应当 0 条
    routes = [
        weibo_responses["weibo_page_with_retweet"],
        weibo_responses["weibo_page_empty"],
    ]
    call_count = [0]

    def respond(request):
        idx = call_count[0]
        call_count[0] += 1
        import httpx
        return httpx.Response(200, json=routes[min(idx, len(routes) - 1)])

    respx_mock.get("/api/container/getIndex").mock(side_effect=respond)

    from backend.app.crawler import AsyncWeiboClient
    from backend.app.db.base import get_sessionmaker
    from backend.app.services import UserService, WeiboService

    sm = get_sessionmaker()
    async with sm() as session:
        us = UserService(session)
        ws = WeiboService(session)
        async with AsyncWeiboClient() as client:
            await us.fetch_and_upsert(1669879400, client=client)
            collected = [
                w async for w in ws.crawl_user(
                    1669879400, client=client, max_count=10,
                    only_original=True,
                )
            ]
            assert all(not w.is_retweet for w in collected)
