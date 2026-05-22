"""Telegram bot 通知."""

from __future__ import annotations

import os
import time

import httpx

from backend.app.notifications.base import (
    BaseNotifier, NotificationEvent, NotificationResult,
)

LEVEL_EMOJI = {
    "info": "ℹ️", "warning": "⚠️", "error": "🚨", "success": "✅",
}


class TelegramNotifier(BaseNotifier):
    CHANNEL = "telegram"

    def __init__(self, bot_token: str | None = None, chat_id: str | None = None) -> None:
        self._bot_token = bot_token or os.getenv("WCN_TELEGRAM_BOT_TOKEN", "")
        self._chat_id = chat_id or os.getenv("WCN_TELEGRAM_CHAT_ID", "")

    @property
    def configured(self) -> bool:
        return bool(self._bot_token and self._chat_id)

    async def send(self, event: NotificationEvent) -> NotificationResult:
        t0 = time.monotonic()
        if not self.configured:
            return NotificationResult(self.CHANNEL, False, "TELEGRAM_BOT_TOKEN/CHAT_ID 未配置")
        emoji = LEVEL_EMOJI.get(event.level, "")
        text = f"{emoji} *{event.title}*\n\n{event.body}".strip()
        try:
            async with httpx.AsyncClient(timeout=15.0) as c:
                r = await c.post(
                    f"https://api.telegram.org/bot{self._bot_token}/sendMessage",
                    json={
                        "chat_id": self._chat_id,
                        "text": text,
                        "parse_mode": "Markdown",
                        "disable_web_page_preview": True,
                    },
                )
                r.raise_for_status()
        except httpx.HTTPError as e:
            return NotificationResult(
                self.CHANNEL, False, f"{type(e).__name__}: {e}",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )
        return NotificationResult(
            self.CHANNEL, True, duration_ms=int((time.monotonic() - t0) * 1000)
        )
