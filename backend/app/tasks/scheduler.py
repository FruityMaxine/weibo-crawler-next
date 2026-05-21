"""APScheduler 集成 — 与 FastAPI lifespan 共存."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.app.config import get_settings

logger = logging.getLogger("wcn.tasks.scheduler")

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="UTC")
    return _scheduler


@asynccontextmanager
async def lifespan_scheduler():
    settings = get_settings()
    if not settings.scheduler_enabled:
        logger.info("APScheduler 已禁用 (WCN_SCHEDULER_ENABLED=false)")
        yield
        return

    sched = get_scheduler()
    sched.start()
    logger.info("APScheduler 启动 (timezone=UTC)")
    try:
        yield
    finally:
        sched.shutdown(wait=False)
        logger.info("APScheduler 已关闭")
