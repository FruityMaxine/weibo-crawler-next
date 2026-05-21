"""JSON 导出器 — 嵌套结构, 含用户摘要."""

from __future__ import annotations

import json
import time
from collections.abc import Iterable

from backend.app.exporters.base import BaseExporter, ExportContext, ExportResult
from backend.app.exporters.registry import register_exporter
from backend.app.db.models import Weibo


@register_exporter("json")
class JSONExporter(BaseExporter):
    DESCRIPTION = "JSON — 嵌套结构, ensure_ascii=False, indent=2"

    async def export(self, items: Iterable[Weibo], ctx: ExportContext) -> ExportResult:
        t0 = time.monotonic()
        ctx.output_dir.mkdir(parents=True, exist_ok=True)
        fname = ctx.filename or f"weibo-{ctx.uid or 'all'}.json"
        path = ctx.output_dir / fname

        rows = [self.weibo_to_dict(w) for w in items]
        payload = {
            "meta": {"uid": ctx.uid, "count": len(rows), "format": "json"},
            "weibos": rows,
        }
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except OSError as e:
            return ExportResult(
                format="json", success=False, item_count=0,
                error=str(e),
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        return ExportResult(
            format="json", success=True, item_count=len(rows),
            output_path=str(path),
            duration_ms=int((time.monotonic() - t0) * 1000),
        )
