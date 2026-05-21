"""CrawlTask 路由."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_session
from backend.app.db.models import TaskStatus
from backend.app.services import TaskService
from backend.app.tasks.executor import run_user_crawl

router = APIRouter()


class TaskCreate(BaseModel):
    name: str
    uid: int | None = None
    query: str | None = None
    max_count: int = 50
    only_original: bool = False
    cookie_override: str | None = None


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


@router.get("", response_model=list[TaskOut])
async def list_tasks(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[TaskOut]:
    items = await TaskService(session).list_all()
    return [TaskOut.model_validate(t) for t in items]


@router.post("", response_model=TaskOut, status_code=201)
async def create_task(
    payload: TaskCreate,
    background: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TaskOut:
    if not payload.uid and not payload.query:
        raise HTTPException(400, "必须提供 uid 或 query 其一")

    service = TaskService(session)
    task = await service.create(
        name=payload.name,
        uid=payload.uid,
        query=payload.query,
        config=payload.model_dump(exclude={"name", "uid", "query"}),
    )
    await session.commit()  # 让 background 看得到
    background.add_task(run_user_crawl, task.id)
    return TaskOut.model_validate(task)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> TaskOut:
    task = await TaskService(session).get(task_id)
    if task is None:
        raise HTTPException(404)
    return TaskOut.model_validate(task)
