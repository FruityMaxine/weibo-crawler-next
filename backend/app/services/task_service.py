"""CrawlTask 业务: 创建任务 / 执行 / 状态更新."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import CrawlTask, TaskStatus

logger = logging.getLogger("wcn.services.task")


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        name: str,
        *,
        uid: int | None = None,
        query: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> CrawlTask:
        task = CrawlTask(
            name=name,
            uid=uid,
            query=query,
            status=TaskStatus.PENDING,
            config_snapshot=config or {},
        )
        self.session.add(task)
        await self.session.flush()
        logger.info("创建 CrawlTask id=%s name=%s", task.id, task.name)
        return task

    async def start(self, task_id: int) -> CrawlTask:
        task = await self._get_or_raise(task_id)
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc)
        await self.session.flush()
        return task

    async def update_progress(
        self, task_id: int, *, progress: int, total_fetched: int
    ) -> None:
        task = await self._get_or_raise(task_id)
        task.progress = max(0, min(100, progress))
        task.total_fetched = total_fetched
        await self.session.flush()

    async def finish(self, task_id: int, *, success: bool, error: str | None = None) -> CrawlTask:
        task = await self._get_or_raise(task_id)
        task.status = TaskStatus.SUCCESS if success else TaskStatus.FAILED
        task.error = error
        task.progress = 100 if success else task.progress
        task.finished_at = datetime.now(timezone.utc)
        await self.session.flush()
        return task

    async def get(self, task_id: int) -> CrawlTask | None:
        result = await self.session.execute(select(CrawlTask).where(CrawlTask.id == task_id))
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 50) -> list[CrawlTask]:
        result = await self.session.execute(
            select(CrawlTask).order_by(CrawlTask.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def _get_or_raise(self, task_id: int) -> CrawlTask:
        task = await self.get(task_id)
        if task is None:
            raise ValueError(f"CrawlTask id={task_id} 不存在")
        return task
