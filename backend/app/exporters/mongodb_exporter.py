"""MongoDB 导出器 — 可选 extras [mongo] 启用."""

from __future__ import annotations

import time
from collections.abc import Iterable

from backend.app.config import get_settings
from backend.app.exporters.base import BaseExporter, ExportContext, ExportResult
from backend.app.exporters.registry import register_exporter
from backend.app.db.models import Weibo


@register_exporter("mongodb")
class MongoDBExporter(BaseExporter):
    DESCRIPTION = "MongoDB — 需 extras [mongo] (motor), URI 从 .env 读"

    async def export(self, items: Iterable[Weibo], ctx: ExportContext) -> ExportResult:
        t0 = time.monotonic()
        try:
            from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
        except ImportError:
            return ExportResult(
                format="mongodb", success=False, item_count=0,
                error="未安装 motor, 执行: uv pip install -e \".[mongo]\"",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        s = get_settings()
        if not s.mongodb_uri:
            return ExportResult(
                format="mongodb", success=False, item_count=0,
                error="MongoDB URI 未配置, 设置 WCN_MONGODB_URI",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        rows = [self.weibo_to_dict(w) for w in items]
        try:
            client = AsyncIOMotorClient(s.mongodb_uri)
            coll = client[s.mongodb_database]["weibos"]
            for r in rows:
                await coll.replace_one({"weibo_id": r["weibo_id"]}, r, upsert=True)
            client.close()
        except Exception as e:  # pragma: no cover
            return ExportResult(
                format="mongodb", success=False, item_count=0,
                error=f"{type(e).__name__}: {e}",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        return ExportResult(
            format="mongodb", success=True, item_count=len(rows),
            output_path=f"mongodb://{s.mongodb_database}/weibos",
            duration_ms=int((time.monotonic() - t0) * 1000),
        )
