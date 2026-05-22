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

# 触发器: 与 weibos 表同步 (insert / update / delete).
# 用 INSERT OR REPLACE 让 upsert 的 update 分支也能正确同步 (auditor W2 修复).
TRIGGER_INSERT = """
CREATE TRIGGER IF NOT EXISTS weibos_fts_insert AFTER INSERT ON weibos
BEGIN
    DELETE FROM weibos_fts WHERE weibo_id = new.weibo_id;
    INSERT INTO weibos_fts(weibo_id, uid, text, topics)
    VALUES (new.weibo_id, new.uid, new.text,
            COALESCE(json_extract(new.topics, '$'), ''));
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
    VALUES (new.weibo_id, new.uid, new.text,
            COALESCE(json_extract(new.topics, '$'), ''));
END;
"""

# 显式 reindex API — Tick 4 旧数据/批量补索引用
REINDEX_FTS5 = """
INSERT INTO weibos_fts(weibo_id, uid, text, topics)
SELECT weibo_id, uid, text, COALESCE(json_extract(topics, '$'), '')
FROM weibos
WHERE weibo_id NOT IN (SELECT weibo_id FROM weibos_fts);
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
            # 用新版 trigger 替换老版 (Tick 4 → Tick 5)
            await conn.execute(sql_text("DROP TRIGGER IF EXISTS weibos_fts_insert"))
            await conn.execute(sql_text("DROP TRIGGER IF EXISTS weibos_fts_delete"))
            await conn.execute(sql_text("DROP TRIGGER IF EXISTS weibos_fts_update"))
            await conn.execute(sql_text(TRIGGER_INSERT))
            await conn.execute(sql_text(TRIGGER_DELETE))
            await conn.execute(sql_text(TRIGGER_UPDATE))
            # 启动时把 weibos 表里有但 FTS 没有的记录 backfill 进去
            await conn.execute(sql_text(REINDEX_FTS5))
            logger.info("FTS5 虚拟表 + triggers 已就绪 (含 backfill)")
        except Exception as e:
            logger.warning("FTS5 初始化失败 (可能未启用 fts5 模块): %s", e)


def sanitize_fts_query(q: str) -> str:
    """净化用户输入: 剥离 FTS5 元字符 + AND/OR/NOT/NEAR 关键字.

    v0.7.0.0: 修 reviewer 报告 — 注释说"防 AND/OR/NOT/NEAR 关键字" 但实际没剥.
    现真正剥离这些 FTS5 boolean 关键字, 防用户输入 "hello AND OR NOT" 类查询
    引发 sqlite FTS5 语法错误(被外层 except 吞掉 → 静默失败).

    保留: 普通文字 / 中文 / 数字 / 单空格.
    剥离: " * : ^ - + ( ) 以及独立的 AND OR NOT NEAR 关键字.
    """
    import re
    # 移除 FTS5 特殊操作符
    q = re.sub(r'[":*^()+\-]', " ", q)
    # 剥 boolean 关键字 (FTS5 内部识别大写, 不区分位置只看完整 word)
    q = re.sub(r"\b(AND|OR|NOT|NEAR)\b", " ", q, flags=re.IGNORECASE)
    # 多空格压缩为单空格
    q = re.sub(r"\s+", " ", q).strip()
    return q


async def fts_search(q: str, *, limit: int = 50) -> list[dict]:
    """执行 FTS5 MATCH 查询, 返回 weibo_id 列表 + 排名分数."""
    engine = get_engine()
    q = sanitize_fts_query(q or "")
    if not q:
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
