"""全文搜索路由 — SQLite FTS5 驱动."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.fts import fts_search
from backend.app.db.models import Weibo
from backend.app.db.session import get_session

router = APIRouter()


class SearchHit(BaseModel):
    weibo_id: str
    uid: int
    snippet: str
    score: float
    text: str = ""
    created_at: str | None = None


class SearchResponse(BaseModel):
    query: str
    count: int
    hits: list[SearchHit]


@router.get("", response_model=SearchResponse)
async def search(
    session: Annotated[AsyncSession, Depends(get_session)],
    q: str = Query(..., min_length=1, max_length=100, description="FTS5 MATCH 查询表达式"),
    limit: int = Query(50, ge=1, le=200),
) -> SearchResponse:
    raw_hits = await fts_search(q, limit=limit)
    if not raw_hits:
        return SearchResponse(query=q, count=0, hits=[])

    ids = [h["weibo_id"] for h in raw_hits]
    result = await session.execute(select(Weibo).where(Weibo.weibo_id.in_(ids)))
    weibos = {w.weibo_id: w for w in result.scalars().all()}

    hits = []
    for h in raw_hits:
        w = weibos.get(h["weibo_id"])
        hits.append(
            SearchHit(
                weibo_id=h["weibo_id"],
                uid=h["uid"],
                snippet=h["snippet"],
                score=h["score"],
                text=(w.text if w else "")[:300],
                created_at=w.created_at.isoformat() if w and w.created_at else None,
            )
        )
    return SearchResponse(query=q, count=len(hits), hits=hits)
