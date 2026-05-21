"""CSV 导出器."""

from __future__ import annotations

import csv
import time
from collections.abc import Iterable

from backend.app.config import get_settings
from backend.app.exporters.base import BaseExporter, ExportContext, ExportResult
from backend.app.exporters.registry import register_exporter
from backend.app.db.models import Weibo


@register_exporter("csv")
class CSVExporter(BaseExporter):
    DESCRIPTION = "CSV — Excel 友好, 默认分隔符 ',' 可配"

    async def export(self, items: Iterable[Weibo], ctx: ExportContext) -> ExportResult:
        t0 = time.monotonic()
        s = get_settings()
        ctx.output_dir.mkdir(parents=True, exist_ok=True)
        fname = ctx.filename or f"weibo-{ctx.uid or 'all'}.csv"
        path = ctx.output_dir / fname

        rows = [self.weibo_to_dict(w) for w in items]
        if not rows:
            return ExportResult(
                format="csv", success=True, item_count=0,
                output_path=str(path),
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        keys = list(rows[0].keys())
        try:
            with path.open("w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=keys, delimiter=s.export_csv_delimiter
                )
                writer.writeheader()
                for r in rows:
                    # list / dict 转字符串
                    flat = {
                        k: (",".join(v) if isinstance(v, list) else v)
                        for k, v in r.items()
                    }
                    writer.writerow(flat)
        except OSError as e:
            return ExportResult(
                format="csv", success=False, item_count=0,
                error=str(e),
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        return ExportResult(
            format="csv", success=True, item_count=len(rows),
            output_path=str(path),
            duration_ms=int((time.monotonic() - t0) * 1000),
        )
