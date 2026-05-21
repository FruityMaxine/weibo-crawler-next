"""健康检查 — 公网监控 / Docker healthcheck 用."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from backend import __version__

router = APIRouter()


@router.get("/health", tags=["health"])
@router.get("/healthz", tags=["health"])
async def healthcheck() -> dict[str, str | float]:
    return {
        "status": "ok",
        "service": "weibo-crawler-next",
        "version": __version__,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
