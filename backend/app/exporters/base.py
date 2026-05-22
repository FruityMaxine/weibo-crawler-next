"""导出器抽象接口 — v0.7.0.0 重构: 加资源生命周期 contract.

新方法 (子类可覆盖, 默认 no-op):
  - open():  导出前打开资源 (DB 连接 / 文件 handle)
  - write_batch(batch): 批量写入
  - close():  导出后关闭资源 (含 except 路径)

旧方法 export() 保留为高层 entry, 默认调 open → write_batch → close 模板.
子类可仅实现新方法, 或继续实现 export() 自管理.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from backend.app.db.models import Weibo

logger = logging.getLogger("wcn.exporters")


@dataclass
class ExportContext:
    """单次导出的上下文 — 传给 exporter 用."""

    uid: int | None = None
    output_dir: Path = field(default_factory=lambda: Path("./weibo_output"))
    filename: str | None = None
    include_media: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExportResult:
    """导出结果统一返回 — 给 CLI/TUI/API 上层用."""

    format: str
    success: bool
    item_count: int
    output_path: str | None = None
    error: str | None = None
    duration_ms: int = 0


class BaseExporter(ABC):
    """导出器接口.

    两种实现方式 (二选一):

    A) **生命周期方式 (推荐)**: 重写 `_open(ctx)` / `_write_batch(items, ctx)` / `_close()`,
       export() 默认会按顺序调用 + try/finally 保证 close() 必跑, 防资源泄漏.

    B) **整包方式 (旧)**: 直接重写 `export(items, ctx)` 全权控制.

    所有子类必须定义:
        FORMAT_NAME (str) — registry 用
        DESCRIPTION (str) — TUI/CLI 展示
    """

    FORMAT_NAME: str = "<override>"
    DESCRIPTION: str = "<override>"

    # 子类二选一: 重写 _open + _write_batch + _close, 或重写 export
    async def _open(self, ctx: ExportContext) -> None:
        """打开资源 (DB 连接 / 文件). 默认 no-op."""

    async def _write_batch(
        self, items: Iterable[Weibo], ctx: ExportContext
    ) -> int:
        """写入一批, 返回写入条数. 默认 no-op (返 0)."""
        return 0

    async def _close(self) -> None:
        """关闭资源. 必在 finally 跑. 默认 no-op."""

    async def export(
        self, items: Iterable[Weibo], ctx: ExportContext
    ) -> ExportResult:
        """默认实现: open → write_batch → close (含 try/finally).

        若子类需更精细控制, 可重写本方法 (不影响其他子类).
        """
        t0 = time.monotonic()
        items_list = list(items)
        try:
            await self._open(ctx)
            count = await self._write_batch(items_list, ctx)
        except Exception as e:
            try:
                await self._close()
            except Exception:
                logger.exception("[%s] close 失败 (在 except 路径中)", self.FORMAT_NAME)
            return ExportResult(
                format=self.FORMAT_NAME,
                success=False, item_count=0,
                error=f"{type(e).__name__}: {e}",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )
        # 成功路径: 也走 close
        try:
            await self._close()
        except Exception:
            logger.exception("[%s] close 失败 (成功路径)", self.FORMAT_NAME)
        return ExportResult(
            format=self.FORMAT_NAME,
            success=True, item_count=count,
            output_path=self._output_path(ctx),
            duration_ms=int((time.monotonic() - t0) * 1000),
        )

    def _output_path(self, ctx: ExportContext) -> str | None:
        """子类可覆盖, 默认 None."""
        return None

    def weibo_to_dict(self, w: Weibo) -> dict[str, Any]:
        """统一序列化, 子类按需调."""
        return {
            "weibo_id": w.weibo_id,
            "uid": w.uid,
            "text": w.text,
            "source": w.source,
            "location": w.location,
            "topics": w.topics or [],
            "at_users": w.at_users or [],
            "pic_urls": w.pic_urls or [],
            "video_url": w.video_url,
            "is_retweet": w.is_retweet,
            "retweet_id": w.retweet_id,
            "attitudes_count": w.attitudes_count,
            "comments_count": w.comments_count,
            "reposts_count": w.reposts_count,
            "created_at": w.created_at.isoformat() if w.created_at else None,
            "crawled_at": w.crawled_at.isoformat() if w.crawled_at else None,
        }
