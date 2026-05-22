"""MongoDB 导出器 — 可选 extras [mongo] 启用.

v0.7.0.0 重构: BaseExporter 生命周期 + bulk_write 替代 N 次 RTT.
"""

from __future__ import annotations

from collections.abc import Iterable

from backend.app.config import get_settings
from backend.app.exporters.base import BaseExporter, ExportContext, ExportResult
from backend.app.exporters.registry import register_exporter
from backend.app.db.models import Weibo


@register_exporter("mongodb")
class MongoDBExporter(BaseExporter):
    DESCRIPTION = "MongoDB — 需 extras [mongo] (motor), URI 从 .env 读"

    def __init__(self) -> None:
        self._client = None
        self._coll = None

    async def _open(self, ctx: ExportContext) -> None:
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ImportError:
            raise RuntimeError(
                "未安装 motor, 执行: uv pip install -e \".[mongo]\""
            )

        s = get_settings()
        if not s.mongodb_uri:
            raise RuntimeError("MongoDB URI 未配置, 设置 WCN_MONGODB_URI")
        self._client = AsyncIOMotorClient(s.mongodb_uri)
        self._coll = self._client[s.mongodb_database]["weibos"]

    async def _write_batch(
        self, items: Iterable[Weibo], ctx: ExportContext
    ) -> int:
        if self._coll is None:
            return 0
        try:
            from pymongo import ReplaceOne
        except ImportError:
            return 0
        rows = [self.weibo_to_dict(w) for w in items]
        if not rows:
            return 0
        # v0.7.0.0: bulk_write 一次 RTT 替代 N 次 replace_one
        ops = [
            ReplaceOne({"weibo_id": r["weibo_id"]}, r, upsert=True)
            for r in rows
        ]
        await self._coll.bulk_write(ops)
        return len(rows)

    async def _close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
            self._coll = None

    def _output_path(self, ctx: ExportContext) -> str:
        s = get_settings()
        return f"mongodb://{s.mongodb_database}/weibos"
