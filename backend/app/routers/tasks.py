"""CrawlTask 路由."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_session
from backend.app.db.models import TaskStatus
from backend.app.services import TaskService
from backend.app.tasks.executor import run_user_crawl

router = APIRouter()

# 敏感字段集合 — 创建任务时从 config_snapshot 过滤掉, GET 时也不返回
_SECRET_KEYS = {"cookie_override", "cookie", "password", "token"}


class TaskCreate(BaseModel):
    name: str = Field(..., max_length=200, description="任务名")
    uid: int | None = None
    query: str | None = Field(default=None, max_length=200)
    max_count: int = Field(default=50, ge=1, le=10000)
    only_original: bool = False
    cookie_override: str | None = None


def _sanitize_config(cfg: dict[str, Any]) -> dict[str, Any]:
    """去掉敏感字段, 保留可公开展示的配置."""
    return {k: v for k, v in cfg.items() if k not in _SECRET_KEYS}


class TaskOut(BaseModel):
    id: int
    name: str
    uid: int | None
    query: str | None
    status: TaskStatus
    progress: int
    total_fetched: int
    error: str | None
    config_snapshot: dict[str, Any] | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_sanitized(cls, task) -> "TaskOut":
        """从 ORM 构造响应, 强制脱敏 config_snapshot."""
        raw = cls.model_validate(task)
        if raw.config_snapshot:
            raw.config_snapshot = _sanitize_config(raw.config_snapshot)
        return raw


@router.get("", response_model=list[TaskOut])
async def list_tasks(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[TaskOut]:
    items = await TaskService(session).list_all()
    return [TaskOut.from_orm_sanitized(t) for t in items]


@router.post("", response_model=TaskOut, status_code=201)
async def create_task(
    payload: TaskCreate,
    background: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TaskOut:
    if not payload.uid and not payload.query:
        raise HTTPException(400, "必须提供 uid 或 query 其一")

    # 把 cookie_override 单独取出, 不入 config_snapshot 持久化
    cookie_override = payload.cookie_override
    full_config = payload.model_dump(exclude={"name", "uid", "query"})
    safe_config = _sanitize_config(full_config)

    service = TaskService(session)
    task = await service.create(
        name=payload.name,
        uid=payload.uid,
        query=payload.query,
        config=safe_config,
    )
    await session.commit()  # 让 background 看得到

    # cookie_override 仅在内存中传给 background task, 不持久化
    background.add_task(run_user_crawl, task.id, cookie_override)

    return TaskOut.from_orm_sanitized(task)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> TaskOut:
    task = await TaskService(session).get(task_id)
    if task is None:
        raise HTTPException(404)
    return TaskOut.from_orm_sanitized(task)
