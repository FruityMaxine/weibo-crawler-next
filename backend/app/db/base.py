"""SQLAlchemy 2.0 async — engine + Base + init."""

from collections.abc import AsyncIterator
import logging

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from backend.app.config import get_settings

logger = logging.getLogger("wcn.db")


class Base(DeclarativeBase):
    """所有 ORM model 的基类."""


_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        connect_args: dict = {}
        if settings.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        _engine = create_async_engine(
            settings.database_url,
            echo=False,
            future=True,
            connect_args=connect_args,
            pool_pre_ping=True,
        )
        logger.debug("AsyncEngine 已创建: %s", settings.database_url)
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=False,
        )
    return _sessionmaker


async def init_db() -> None:
    """启动时建表 (开发期使用, 生产用 alembic upgrade head)."""
    # 注意: 这里 import models 触发 SQLAlchemy 注册
    from backend.app.db import models  # noqa: F401

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("初始 schema 已建 (create_all)")


async def session_scope() -> AsyncIterator[AsyncSession]:
    """提供独立的 session 上下文 (CLI / 任务执行用)."""
    sm = get_sessionmaker()
    async with sm() as session:
        yield session


async def reset_engine() -> None:
    """测试 / 重连场景: 清掉缓存的 engine + sessionmaker."""
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _sessionmaker = None
