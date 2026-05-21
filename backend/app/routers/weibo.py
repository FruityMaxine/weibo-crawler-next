"""Weibo 路由."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_session
from backend.app.services import WeiboService

router = APIRouter()


class WeiboOut(BaseModel):
    weibo_id: str
    uid: int
    text: str
    source: str | None = None
    pic_urls: list[str] = []
    video_url: str | None = None
    is_retweet: bool = False
    attitudes_count: int = 0
    comments_count: int = 0
    reposts_count: int = 0
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[WeiboOut])
async def list_weibo(
    session: Annotated[AsyncSession, Depends(get_session)],
    uid: int | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
) -> list[WeiboOut]:
    service = WeiboService(session)
    items = await service.list_recent(limit=limit, uid=uid)
    return [WeiboOut.model_validate(w) for w in items]
