"""MySQL 导出器 — 可选 extras [mysql] 启用."""

from __future__ import annotations

import json
import time
from collections.abc import Iterable

from backend.app.config import get_settings
from backend.app.exporters.base import BaseExporter, ExportContext, ExportResult
from backend.app.exporters.registry import register_exporter
from backend.app.db.models import Weibo


@register_exporter("mysql")
class MySQLExporter(BaseExporter):
    DESCRIPTION = "MySQL — 需 extras [mysql] (aiomysql), 连接参数从 .env 读"

    async def export(self, items: Iterable[Weibo], ctx: ExportContext) -> ExportResult:
        t0 = time.monotonic()
        try:
            import aiomysql  # type: ignore
        except ImportError:
            return ExportResult(
                format="mysql", success=False, item_count=0,
                error="未安装 aiomysql, 执行: uv pip install -e \".[mysql]\"",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        s = get_settings()
        if not s.mysql_password and s.mysql_host == "localhost" and s.mysql_user == "root":
            return ExportResult(
                format="mysql", success=False, item_count=0,
                error="MySQL 凭据未配置, 设置 WCN_MYSQL_PASSWORD 等环境变量",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        rows = [self.weibo_to_dict(w) for w in items]
        try:
            conn = await aiomysql.connect(
                host=s.mysql_host, port=s.mysql_port,
                user=s.mysql_user, password=s.mysql_password,
                db=s.mysql_database, charset=s.mysql_charset,
                autocommit=False,
            )
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS weibos_exported (
                        weibo_id VARCHAR(64) PRIMARY KEY,
                        uid BIGINT NOT NULL,
                        text TEXT,
                        topics TEXT,
                        pic_urls TEXT,
                        is_retweet TINYINT(1) DEFAULT 0,
                        attitudes_count INT DEFAULT 0,
                        comments_count INT DEFAULT 0,
                        reposts_count INT DEFAULT 0,
                        created_at VARCHAR(32),
                        crawled_at VARCHAR(32),
                        INDEX ix_uid (uid)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
                for r in rows:
                    await cur.execute(
                        """
                        REPLACE INTO weibos_exported
                        (weibo_id, uid, text, topics, pic_urls, is_retweet,
                         attitudes_count, comments_count, reposts_count,
                         created_at, crawled_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            r["weibo_id"], r["uid"], r["text"],
                            json.dumps(r["topics"], ensure_ascii=False),
                            json.dumps(r["pic_urls"], ensure_ascii=False),
                            1 if r["is_retweet"] else 0,
                            r["attitudes_count"], r["comments_count"], r["reposts_count"],
                            r["created_at"], r["crawled_at"],
                        ),
                    )
            await conn.commit()
            conn.close()
        except Exception as e:  # pragma: no cover - 真连接才能测
            return ExportResult(
                format="mysql", success=False, item_count=0,
                error=f"{type(e).__name__}: {e}",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        return ExportResult(
            format="mysql", success=True, item_count=len(rows),
            output_path=f"mysql://{s.mysql_host}:{s.mysql_port}/{s.mysql_database}",
            duration_ms=int((time.monotonic() - t0) * 1000),
        )
