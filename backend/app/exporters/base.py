"""导出器抽象接口 — 所有 exporter 实现此 ABC."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from backend.app.db.models import Weibo


@dataclass
class ExportContext:
    """单次导出的上下文 — 传给 exporter 用."""

    uid: int | None = None
    output_dir: Path = field(default_factory=lambda: Path("./weibo_output"))
    filename: str | None = None  # 由 exporter 自决, 也可显式覆盖
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

    子类要做的事:
        1) 定义 class FORMAT_NAME: str (registry 用)
        2) 定义 class DESCRIPTION: str (TUI/CLI 展示)
        3) 实现 async def export(items, ctx) -> ExportResult
    """

    FORMAT_NAME: str = "<override>"
    DESCRIPTION: str = "<override>"

    @abstractmethod
    async def export(
        self, items: Iterable[Weibo], ctx: ExportContext
    ) -> ExportResult:  # pragma: no cover - abstract
        raise NotImplementedError

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
