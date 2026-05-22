"""通用 webhook POST 通知 — 含 Authorization Bearer."""

from __future__ import annotations

import os
import time

import httpx

from backend.app.notifications.base import (
    BaseNotifier, NotificationEvent, NotificationResult,
)


class WebhookNotifier(BaseNotifier):
    CHANNEL = "webhook"

    def __init__(self, url: str | None = None, token: str | None = None) -> None:
        self._url = url or os.getenv("WCN_NOTIFY_WEBHOOK_URL", "")
        self._token = token or os.getenv("WCN_NOTIFY_WEBHOOK_TOKEN", "")

    @property
    def configured(self) -> bool:
        return bool(self._url)

    async def send(self, event: NotificationEvent) -> NotificationResult:
        t0 = time.monotonic()
        if not self.configured:
            return NotificationResult(self.CHANNEL, False, "NOTIFY_WEBHOOK_URL 未配置")
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        payload = {
            "service": "weibo-crawler-next",
            "level": event.level,
            "title": event.title,
            "body": event.body,
            "metadata": event.metadata,
            "ts": event.ts.isoformat(),
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as c:
                r = await c.post(self._url, json=payload, headers=headers)
                r.raise_for_status()
        except httpx.HTTPError as e:
            return NotificationResult(
                self.CHANNEL, False, f"{type(e).__name__}: {e}",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )
        return NotificationResult(
            self.CHANNEL, True, duration_ms=int((time.monotonic() - t0) * 1000)
        )
