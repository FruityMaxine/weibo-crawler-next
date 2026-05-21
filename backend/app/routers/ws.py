"""WebSocket 路由 — 实时任务进度推送 + dashboard 心跳.

事件协议 (JSON over text WS):
  client -> server: {"type": "subscribe", "channel": "tasks" | "dashboard"}
  server -> client: {"type": "task_update", "id": int, "progress": int, ...}
                    {"type": "dashboard_tick", "ts": str, "stats": {...}}
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import func, select

from backend.app.db.base import get_sessionmaker
from backend.app.db.models import CrawlTask, User, Weibo

logger = logging.getLogger("wcn.ws")
router = APIRouter()


class WSHub:
    """简易广播枢纽 — Tick 4 用, Tick 5 可扩 Redis pubsub."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._clients.add(ws)
        logger.info("WS 客户端接入 (总数=%s)", len(self._clients))

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(ws)
        logger.info("WS 客户端断开 (总数=%s)", len(self._clients))

    async def broadcast(self, payload: dict) -> None:
        dead: list[WebSocket] = []
        msg = json.dumps(payload, ensure_ascii=False, default=str)
        for ws in list(self._clients):
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws)


hub = WSHub()


async def dashboard_snapshot() -> dict:
    """收集仪表盘统计 — 用户数 / 微博数 / 任务数 / 最近活动."""
    sm = get_sessionmaker()
    async with sm() as s:
        user_count = (await s.execute(select(func.count(User.uid)))).scalar_one()
        weibo_count = (await s.execute(select(func.count(Weibo.id)))).scalar_one()
        task_count = (await s.execute(select(func.count(CrawlTask.id)))).scalar_one()
        recent = (
            await s.execute(
                select(CrawlTask)
                .order_by(CrawlTask.created_at.desc())
                .limit(5)
            )
        ).scalars().all()
        recent_tasks = [
            {
                "id": t.id, "name": t.name, "status": str(t.status.value),
                "progress": t.progress, "total_fetched": t.total_fetched,
            }
            for t in recent
        ]
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "users": int(user_count),
            "weibos": int(weibo_count),
            "tasks": int(task_count),
        },
        "recent_tasks": recent_tasks,
    }


@router.websocket("/ws")
async def ws_root(ws: WebSocket) -> None:
    """单一 WS endpoint, 用消息内 type 路由."""
    await hub.connect(ws)
    try:
        # 立即推一次 snapshot
        await ws.send_text(json.dumps(
            {"type": "dashboard_tick", **(await dashboard_snapshot())},
            ensure_ascii=False, default=str,
        ))
        # 心跳循环 — 每 3 秒推一次 (足够 dashboard 实时感)
        while True:
            try:
                # 等客户端消息 (subscribe/ping) 或超时
                msg = await asyncio.wait_for(ws.receive_text(), timeout=3.0)
                try:
                    data = json.loads(msg)
                except json.JSONDecodeError:
                    continue
                if data.get("type") == "ping":
                    await ws.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                # 周期推送 snapshot
                snap = await dashboard_snapshot()
                await ws.send_text(json.dumps(
                    {"type": "dashboard_tick", **snap},
                    ensure_ascii=False, default=str,
                ))
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WS 处理异常")
    finally:
        await hub.disconnect(ws)
