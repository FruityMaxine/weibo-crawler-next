"""SQLite 导出器 — 用独立目标 SQLite 文件 (不是主数据库)."""

from __future__ import annotations

import json
import sqlite3
import time
from collections.abc import Iterable

from backend.app.exporters.base import BaseExporter, ExportContext, ExportResult
from backend.app.exporters.registry import register_exporter
from backend.app.db.models import Weibo


@register_exporter("sqlite")
class SQLiteExporter(BaseExporter):
    DESCRIPTION = "SQLite — 单文件可移植, 用独立 db 不污染主库"

    async def export(self, items: Iterable[Weibo], ctx: ExportContext) -> ExportResult:
        t0 = time.monotonic()
        ctx.output_dir.mkdir(parents=True, exist_ok=True)
        fname = ctx.filename or f"weibo-{ctx.uid or 'all'}.db"
        path = ctx.output_dir / fname

        # 同步 sqlite3 写, 容量小不必 aiosqlite
        rows = list(items)
        try:
            conn = sqlite3.connect(str(path))
            try:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS weibos (
                        weibo_id   TEXT PRIMARY KEY,
                        uid        INTEGER NOT NULL,
                        text       TEXT,
                        source     TEXT,
                        location   TEXT,
                        topics     TEXT,
                        at_users   TEXT,
                        pic_urls   TEXT,
                        video_url  TEXT,
                        is_retweet INTEGER NOT NULL DEFAULT 0,
                        attitudes_count INTEGER DEFAULT 0,
                        comments_count  INTEGER DEFAULT 0,
                        reposts_count   INTEGER DEFAULT 0,
                        created_at TEXT,
                        crawled_at TEXT
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS ix_uid ON weibos(uid)")
                count = 0
                for w in rows:
                    d = self.weibo_to_dict(w)
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO weibos VALUES
                        (:weibo_id, :uid, :text, :source, :location,
                         :topics, :at_users, :pic_urls, :video_url,
                         :is_retweet, :attitudes_count, :comments_count,
                         :reposts_count, :created_at, :crawled_at)
                        """,
                        {
                            **d,
                            "topics": json.dumps(d["topics"], ensure_ascii=False),
                            "at_users": json.dumps(d["at_users"], ensure_ascii=False),
                            "pic_urls": json.dumps(d["pic_urls"], ensure_ascii=False),
                            "is_retweet": 1 if d["is_retweet"] else 0,
                        },
                    )
                    count += 1
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error as e:
            return ExportResult(
                format="sqlite", success=False, item_count=0,
                error=str(e),
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        return ExportResult(
            format="sqlite", success=True, item_count=count,
            output_path=str(path),
            duration_ms=int((time.monotonic() - t0) * 1000),
        )
