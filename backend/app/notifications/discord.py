"""Discord webhook 通知."""

from __future__ import annotations

import os
import time

import httpx

from backend.app.notifications.base import (
    BaseNotifier, NotificationEvent, NotificationResult,
)

LEVEL_COLOR = {
    "info": 0x5e6ad2, "warning": 0xd9a300,
    "error": 0xd65555, "success": 0x27a644,
}


class DiscordNotifier(BaseNotifier):
    CHANNEL = "discord"

    def __init__(self, webhook_url: str | None = None) -> None:
        self._url = webhook_url or os.getenv("WCN_DISCORD_WEBHOOK_URL", "")

    @property
    def configured(self) -> bool:
        return bool(self._url)

    async def send(self, event: NotificationEvent) -> NotificationResult:
        t0 = time.monotonic()
        if not self.configured:
            return NotificationResult(self.CHANNEL, False, "DISCORD_WEBHOOK_URL 未配置")
        embed = {
            "title": event.title,
            "description": event.body[:4000],
            "color": LEVEL_COLOR.get(event.level, 0x5e6ad2),
            "timestamp": event.ts.isoformat(),
            "footer": {"text": "weibo-crawler-next"},
        }
        if event.metadata:
            embed["fields"] = [
                {"name": k, "value": str(v)[:1000], "inline": True}
                for k, v in event.metadata.items()
            ][:10]
        try:
            async with httpx.AsyncClient(timeout=15.0) as c:
                r = await c.post(self._url, json={"embeds": [embed]})
                r.raise_for_status()
        except httpx.HTTPError as e:
            return NotificationResult(
                self.CHANNEL, False, f"{type(e).__name__}: {e}",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )
        return NotificationResult(
            self.CHANNEL, True, duration_ms=int((time.monotonic() - t0) * 1000)
        )
