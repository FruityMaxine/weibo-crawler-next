"""MySQL 导出器 — 可选 extras [mysql] 启用.

v0.7.0.0 重构: 用 BaseExporter 新生命周期 (open/write_batch/close), 加 try/finally
保证 conn.close() 必跑, 修 v0.6.x 之前的连接泄漏.
"""

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

    def __init__(self) -> None:
        self._conn = None  # aiomysql connection or None
        self._aiomysql_available = True

    async def _open(self, ctx: ExportContext) -> None:
        try:
            import aiomysql
        except ImportError:
            self._aiomysql_available = False
            raise RuntimeError(
                "未安装 aiomysql, 执行: uv pip install -e \".[mysql]\""
            )

        s = get_settings()
        if not s.mysql_password and s.mysql_host == "localhost" and s.mysql_user == "root":
            raise RuntimeError(
                "MySQL 凭据未配置, 设置 WCN_MYSQL_PASSWORD 等环境变量"
            )

        self._conn = await aiomysql.connect(
            host=s.mysql_host, port=s.mysql_port,
            user=s.mysql_user, password=s.mysql_password,
            db=s.mysql_database, charset=s.mysql_charset,
            autocommit=False,
        )
        async with self._conn.cursor() as cur:
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

    async def _write_batch(
        self, items: Iterable[Weibo], ctx: ExportContext
    ) -> int:
        if self._conn is None:
            return 0
        rows = [self.weibo_to_dict(w) for w in items]
        if not rows:
            return 0
        async with self._conn.cursor() as cur:
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
        await self._conn.commit()
        return len(rows)

    async def _close(self) -> None:
        """v0.7.0.0: 永远在 finally 跑, 不再泄漏."""
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _output_path(self, ctx: ExportContext) -> str:
        s = get_settings()
        return f"mysql://{s.mysql_host}:{s.mysql_port}/{s.mysql_database}"
