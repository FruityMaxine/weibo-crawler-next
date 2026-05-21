"""Weibo 业务: 翻页抓取 / upsert / 查询."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from datetime import date
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crawler import AsyncWeiboClient
from backend.app.crawler.parser import iter_weibo_cards, parse_weibo_card
from backend.app.db.models import Media, Weibo

logger = logging.getLogger("wcn.services.weibo")


class WeiboService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def crawl_user(
        self,
        uid: int,
        *,
        client: AsyncWeiboClient,
        max_count: int | None = None,
        since: date | None = None,
        only_original: bool = False,
    ) -> AsyncIterator[Weibo]:
        """翻页抓取用户微博. yield 每条入库后的 Weibo."""
        page = 1
        fetched = 0
        while True:
            payload = await client.get_user_weibo_page(uid, page=page)
            cards = iter_weibo_cards(payload)
            if not cards:
                logger.info("uid=%s page=%s 无更多卡片, 终止", uid, page)
                break

            page_yielded = 0
            for card in cards:
                parsed = parse_weibo_card(card)
                if parsed is None:
                    continue
                if only_original and parsed["is_retweet"]:
                    continue
                if since and parsed["created_at"] and parsed["created_at"].date() < since:
                    logger.info("达 since=%s, 终止", since)
                    return

                weibo = await self.upsert(parsed)
                yield weibo
                page_yielded += 1
                fetched += 1
                if max_count and fetched >= max_count:
                    logger.info("达 max_count=%s, 终止", max_count)
                    return

            if page_yielded == 0:
                logger.info("page=%s 全部为非微博卡片, 终止", page)
                break
            page += 1

    async def upsert(self, data: dict[str, Any]) -> Weibo:
        pic_urls = data.pop("pic_urls", []) or []
        video_url = data.get("video_url")
        weibo_id = data["weibo_id"]

        stmt = sqlite_insert(Weibo).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Weibo.weibo_id],
            set_={
                k: stmt.excluded[k]
                for k in data
                if k not in ("weibo_id", "crawled_at")
            },
        )
        await self.session.execute(stmt)
        result = await self.session.execute(select(Weibo).where(Weibo.weibo_id == weibo_id))
        weibo = result.scalar_one()

        # 媒体落库
        for url in pic_urls:
            await self._upsert_media(weibo.weibo_id, "pic", url)
        if video_url:
            await self._upsert_media(weibo.weibo_id, "video", video_url)
        await self.session.flush()
        return weibo

    async def _upsert_media(self, weibo_id: str, kind: str, url: str) -> None:
        exists = await self.session.execute(
            select(Media.id).where(Media.weibo_id == weibo_id, Media.url == url)
        )
        if exists.scalar_one_or_none() is not None:
            return
        self.session.add(Media(weibo_id=weibo_id, kind=kind, url=url))

    async def count_by_user(self, uid: int) -> int:
        result = await self.session.execute(
            select(func.count(Weibo.id)).where(Weibo.uid == uid)
        )
        return int(result.scalar_one())

    async def list_recent(self, limit: int = 50, uid: int | None = None) -> list[Weibo]:
        stmt = select(Weibo).order_by(Weibo.created_at.desc().nullslast()).limit(limit)
        if uid:
            stmt = stmt.where(Weibo.uid == uid)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
