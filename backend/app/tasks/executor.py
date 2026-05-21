"""任务执行器 — 从 CrawlTask 读配置, 调 crawler + services 落库."""

from __future__ import annotations

import logging
import traceback
from datetime import date

from backend.app.crawler import AsyncWeiboClient
from backend.app.db.base import get_sessionmaker
from backend.app.services import TaskService, UserService, WeiboService

logger = logging.getLogger("wcn.tasks.executor")


async def run_user_crawl(task_id: int) -> None:
    """异步执行 CrawlTask: 抓用户 + 抓微博 + 更新进度."""
    sm = get_sessionmaker()
    async with sm() as session:
        try:
            ts = TaskService(session)
            task = await ts.get(task_id)
            if task is None:
                logger.error("CrawlTask id=%s 不存在, 跳过", task_id)
                return
            cfg = task.config_snapshot or {}
            max_count: int = cfg.get("max_count", 50)
            only_original: bool = cfg.get("only_original", False)
            cookie_override: str | None = cfg.get("cookie_override")

            await ts.start(task_id)
            await session.commit()

            if task.uid is None:
                await ts.finish(task_id, success=False, error="未实现 query 关键词搜索 (Tick 3+)")
                await session.commit()
                return

            us = UserService(session)
            ws = WeiboService(session)
            total = 0
            async with AsyncWeiboClient(cookie=cookie_override) as client:
                await us.fetch_and_upsert(task.uid, client=client)
                async for _ in ws.crawl_user(
                    task.uid, client=client, max_count=max_count, only_original=only_original
                ):
                    total += 1
                    if total % 5 == 0:
                        progress = min(99, int(total / max(1, max_count) * 100))
                        await ts.update_progress(task_id, progress=progress, total_fetched=total)
                        await session.commit()

            await ts.update_progress(task_id, progress=100, total_fetched=total)
            await ts.finish(task_id, success=True)
            await session.commit()
            logger.info("CrawlTask id=%s 完成, 共抓取 %s 条", task_id, total)
        except Exception as e:
            logger.exception("CrawlTask id=%s 失败", task_id)
            try:
                await session.rollback()
                async with sm() as s2:
                    await TaskService(s2).finish(
                        task_id, success=False, error=f"{e}\n{traceback.format_exc()[:1000]}"
                    )
                    await s2.commit()
            except Exception:
                logger.exception("失败状态写回也出错")
