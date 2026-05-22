"""通知抽象接口 — 4 通道实现此 ABC."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class NotificationEvent:
    """通知事件 — 由各通道适配为各自格式."""

    title: str
    body: str = ""
    level: str = "info"          # info / warning / error / success
    metadata: dict[str, Any] = field(default_factory=dict)
    ts: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class NotificationResult:
    channel: str
    success: bool
    error: str | None = None
    duration_ms: int = 0


class BaseNotifier(ABC):
    CHANNEL: str = "<override>"

    @abstractmethod
    async def send(self, event: NotificationEvent) -> NotificationResult:  # pragma: no cover
        raise NotImplementedError

    @property
    def configured(self) -> bool:
        """子类返回 True 表示有有效配置, 不打 endpoint."""
        return False
