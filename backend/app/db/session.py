"""FastAPI 依赖注入 — 每请求一个 AsyncSession."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.base import get_sessionmaker


async def get_session() -> AsyncIterator[AsyncSession]:
    sm = get_sessionmaker()
    async with sm() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
