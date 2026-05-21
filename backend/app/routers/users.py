"""User 路由."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crawler import AsyncWeiboClient
from backend.app.db.session import get_session
from backend.app.services import UserService

router = APIRouter()


class UserOut(BaseModel):
    uid: int
    screen_name: str
    description: str | None = None
    verified: bool = False
    statuses_count: int = 0
    followers_count: int = 0
    follow_count: int = 0
    avatar_hd: str | None = None
    profile_url: str | None = None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[UserOut])
async def list_users(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[UserOut]:
    service = UserService(session)
    users = await service.list_all(limit=limit, offset=offset)
    return [UserOut.model_validate(u) for u in users]


@router.get("/{uid}", response_model=UserOut)
async def get_user(
    uid: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> UserOut:
    service = UserService(session)
    user = await service.get(uid)
    if user is None:
        raise HTTPException(404, f"user {uid} not found, 先抓取")
    return UserOut.model_validate(user)


@router.post("/{uid}/refresh", response_model=UserOut)
async def refresh_user(
    uid: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> UserOut:
    """触发一次用户信息刷新 (同步小请求, 不创建后台任务)."""
    service = UserService(session)
    async with AsyncWeiboClient() as client:
        user = await service.fetch_and_upsert(uid, client=client)
    return UserOut.model_validate(user)
