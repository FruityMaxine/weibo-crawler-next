"""通知子系统 — Telegram / Discord / Email / 通用 Webhook 四通道.

接口:
    notifier = TelegramNotifier(bot_token, chat_id)
    await notifier.send(NotificationEvent(...))

或者用 dispatch_event 一次广播给所有配置好的通道.
"""

from backend.app.notifications.base import (
    BaseNotifier, NotificationEvent, NotificationResult,
)
from backend.app.notifications.telegram import TelegramNotifier
from backend.app.notifications.discord import DiscordNotifier
from backend.app.notifications.email import EmailNotifier
from backend.app.notifications.webhook import WebhookNotifier
from backend.app.notifications.dispatcher import dispatch_event, configured_notifiers

__all__ = [
    "BaseNotifier",
    "NotificationEvent",
    "NotificationResult",
    "TelegramNotifier",
    "DiscordNotifier",
    "EmailNotifier",
    "WebhookNotifier",
    "dispatch_event",
    "configured_notifiers",
]
