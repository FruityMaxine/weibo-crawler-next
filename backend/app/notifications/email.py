"""SMTP email 通知 (异步包装同步 smtplib)."""

from __future__ import annotations

import asyncio
import os
import smtplib
import time
from email.message import EmailMessage

from backend.app.notifications.base import (
    BaseNotifier, NotificationEvent, NotificationResult,
)


class EmailNotifier(BaseNotifier):
    CHANNEL = "email"

    def __init__(
        self,
        *,
        host: str | None = None, port: int | None = None,
        user: str | None = None, password: str | None = None,
        sender: str | None = None, recipients: list[str] | None = None,
        use_tls: bool = True,
    ) -> None:
        self._host = host or os.getenv("WCN_SMTP_HOST", "")
        self._port = port or int(os.getenv("WCN_SMTP_PORT", "587"))
        self._user = user or os.getenv("WCN_SMTP_USER", "")
        self._password = password or os.getenv("WCN_SMTP_PASSWORD", "")
        self._sender = sender or os.getenv("WCN_SMTP_SENDER", self._user)
        recipients_env = os.getenv("WCN_SMTP_RECIPIENTS", "")
        self._recipients = recipients or [r.strip() for r in recipients_env.split(",") if r.strip()]
        self._use_tls = use_tls

    @property
    def configured(self) -> bool:
        return bool(self._host and self._user and self._password and self._recipients)

    async def send(self, event: NotificationEvent) -> NotificationResult:
        t0 = time.monotonic()
        if not self.configured:
            return NotificationResult(
                self.CHANNEL, False, "SMTP_HOST/USER/PASSWORD/RECIPIENTS 未完整配置"
            )

        def _send_sync() -> None:
            msg = EmailMessage()
            msg["Subject"] = f"[wcn:{event.level}] {event.title}"
            msg["From"] = self._sender
            msg["To"] = ", ".join(self._recipients)
            body = event.body
            if event.metadata:
                body += "\n\n" + "\n".join(f"{k}: {v}" for k, v in event.metadata.items())
            msg.set_content(body)
            with smtplib.SMTP(self._host, self._port, timeout=15) as smtp:
                if self._use_tls:
                    smtp.starttls()
                smtp.login(self._user, self._password)
                smtp.send_message(msg)

        try:
            await asyncio.get_event_loop().run_in_executor(None, _send_sync)
        except Exception as e:
            return NotificationResult(
                self.CHANNEL, False, f"{type(e).__name__}: {e}",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )
        return NotificationResult(
            self.CHANNEL, True, duration_ms=int((time.monotonic() - t0) * 1000)
        )
