"""User 业务: 抓取 / upsert / 查询."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crawler import AsyncWeiboClient, parse_user_info
from backend.app.db.models import User

logger = logging.getLogger("wcn.services.user")


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def fetch_and_upsert(self, uid: int, *, client: AsyncWeiboClient) -> User:
        """从微博 API 拉用户主页 → upsert 到 users 表."""
        payload = await client.get_user_info(uid)
        parsed = parse_user_info(payload)
        if parsed["uid"] == 0:
            parsed["uid"] = int(uid)
        return await self.upsert(parsed)

    async def upsert(self, data: dict[str, Any]) -> User:
        """SQLite upsert (ON CONFLICT (uid) DO UPDATE)."""
        stmt = sqlite_insert(User).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=[User.uid],
            set_={
                k: stmt.excluded[k]
                for k in data
                if k not in ("uid", "crawled_at")
            },
        )
        await self.session.execute(stmt)
        result = await self.session.execute(select(User).where(User.uid == data["uid"]))
        user = result.scalar_one()
        logger.info("upsert user %s (%s)", user.uid, user.screen_name)
        return user

    async def get(self, uid: int) -> User | None:
        result = await self.session.execute(select(User).where(User.uid == uid))
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[User]:
        result = await self.session.execute(
            select(User).order_by(User.crawled_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
