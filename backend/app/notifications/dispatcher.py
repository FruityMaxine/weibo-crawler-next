"""统一分发器 — 一次 send 广播到所有配置的通道."""

from __future__ import annotations

import asyncio
import logging

from backend.app.notifications.base import (
    BaseNotifier, NotificationEvent, NotificationResult,
)
from backend.app.notifications.discord import DiscordNotifier
from backend.app.notifications.email import EmailNotifier
from backend.app.notifications.telegram import TelegramNotifier
from backend.app.notifications.webhook import WebhookNotifier

logger = logging.getLogger("wcn.notify")


def configured_notifiers() -> list[BaseNotifier]:
    """根据 env 实例化并返回所有已配置的 notifier."""
    out: list[BaseNotifier] = []
    for cls in (TelegramNotifier, DiscordNotifier, EmailNotifier, WebhookNotifier):
        n = cls()  # type: ignore[call-arg]
        if n.configured:
            out.append(n)
    return out


async def dispatch_event(event: NotificationEvent) -> list[NotificationResult]:
    """并发发到所有 configured 通道, 返回每通道结果."""
    notifiers = configured_notifiers()
    if not notifiers:
        logger.debug("无配置的 notifier, 跳过 dispatch")
        return []
    results = await asyncio.gather(
        *(n.send(event) for n in notifiers), return_exceptions=False
    )
    for r in results:
        if not r.success:
            logger.warning("通知 %s 失败: %s", r.channel, r.error)
    return results
