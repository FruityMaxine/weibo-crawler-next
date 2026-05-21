"""SQLite FTS5 全文索引 — 为 Weibo.text 建虚拟表 + triggers 同步."""

from __future__ import annotations

import logging

from sqlalchemy import text as sql_text

from backend.app.db.base import get_engine

logger = logging.getLogger("wcn.db.fts")


CREATE_FTS5 = """
CREATE VIRTUAL TABLE IF NOT EXISTS weibos_fts USING fts5(
    weibo_id UNINDEXED,
    uid UNINDEXED,
    text,
    topics,
    tokenize='unicode61 remove_diacritics 2'
);
"""

# 触发器: 与 weibos 表同步 (insert / update / delete)
TRIGGER_INSERT = """
CREATE TRIGGER IF NOT EXISTS weibos_fts_insert AFTER INSERT ON weibos
BEGIN
    INSERT INTO weibos_fts(weibo_id, uid, text, topics)
    VALUES (new.weibo_id, new.uid, new.text, json_extract(new.topics, '$'));
END;
"""
TRIGGER_DELETE = """
CREATE TRIGGER IF NOT EXISTS weibos_fts_delete AFTER DELETE ON weibos
BEGIN
    DELETE FROM weibos_fts WHERE weibo_id = old.weibo_id;
END;
"""
TRIGGER_UPDATE = """
CREATE TRIGGER IF NOT EXISTS weibos_fts_update AFTER UPDATE ON weibos
BEGIN
    DELETE FROM weibos_fts WHERE weibo_id = old.weibo_id;
    INSERT INTO weibos_fts(weibo_id, uid, text, topics)
    VALUES (new.weibo_id, new.uid, new.text, json_extract(new.topics, '$'));
END;
"""


async def init_fts() -> None:
    """启动时建 FTS5 表 + 触发器. 仅对 SQLite 生效."""
    engine = get_engine()
    url = str(engine.url)
    if "sqlite" not in url:
        logger.info("非 SQLite 后端 (%s), 跳过 FTS5 初始化", url)
        return
    async with engine.begin() as conn:
        # 检测 FTS5 是否编译进 sqlite
        try:
            await conn.execute(sql_text(CREATE_FTS5))
            await conn.execute(sql_text(TRIGGER_INSERT))
            await conn.execute(sql_text(TRIGGER_DELETE))
            await conn.execute(sql_text(TRIGGER_UPDATE))
            logger.info("FTS5 虚拟表 + triggers 已就绪")
        except Exception as e:
            logger.warning("FTS5 初始化失败 (可能未启用 fts5 模块): %s", e)


async def fts_search(q: str, *, limit: int = 50) -> list[dict]:
    """执行 FTS5 MATCH 查询, 返回 weibo_id 列表 + 排名分数."""
    engine = get_engine()
    if not q.strip():
        return []
    async with engine.connect() as conn:
        try:
            stmt = sql_text(
                """
                SELECT weibo_id, uid, snippet(weibos_fts, 2, '<mark>', '</mark>', '…', 16) AS snip,
                       rank
                FROM weibos_fts
                WHERE weibos_fts MATCH :q
                ORDER BY rank
                LIMIT :limit
                """
            )
            result = await conn.execute(stmt, {"q": q, "limit": limit})
            return [
                {
                    "weibo_id": str(r[0]),
                    "uid": int(r[1]) if r[1] is not None else 0,
                    "snippet": r[2] or "",
                    "score": float(r[3]) if r[3] is not None else 0.0,
                }
                for r in result.fetchall()
            ]
        except Exception as e:
            logger.warning("FTS 查询失败: %s", e)
            return []
