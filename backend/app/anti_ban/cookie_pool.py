"""Cookie 池 — 多账号轮换 + 健康度评分 + 自动屏蔽."""

from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field

logger = logging.getLogger("wcn.anti_ban.cookie")


@dataclass
class CookieEntry:
    """单条 cookie + 健康度状态."""

    value: str
    label: str = ""
    health: float = 1.0          # 0..1, EMA 平滑
    fail_streak: int = 0         # 连续失败次数
    cooldown_until: float = 0.0  # epoch sec, 此时间前不可用
    last_used_at: float = 0.0
    total_uses: int = 0

    @property
    def usable(self) -> bool:
        return time.time() >= self.cooldown_until and bool(self.value)


class CookiePool:
    """多账号 cookie 池, acquire/release 加权随机.

    用法:
        pool = CookiePool(["cookie1", "cookie2"])
        async with pool.acquire() as entry:
            try:
                ... use entry.value ...
                pool.release(entry, success=True)
            except Exception:
                pool.release(entry, success=False)
    """

    EMA_ALPHA = 0.3
    FAIL_THRESHOLD = 3            # 连续失败 3 次屏蔽
    COOLDOWN_BASE_SEC = 60        # 屏蔽冷却基数 (指数增长)
    COOLDOWN_MAX_SEC = 1800       # 最长屏蔽 30 min

    def __init__(self, cookies: list[str] | list[tuple[str, str]] | None = None) -> None:
        self._entries: list[CookieEntry] = []
        self._lock = asyncio.Lock()
        if cookies:
            for c in cookies:
                if isinstance(c, tuple):
                    self.add(c[0], label=c[1])
                else:
                    self.add(c)

    def add(self, value: str, *, label: str = "") -> None:
        if not value:
            return
        self._entries.append(CookieEntry(value=value, label=label or f"#{len(self._entries)}"))

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def healthy_count(self) -> int:
        return sum(1 for e in self._entries if e.usable)

    async def acquire(self) -> CookieEntry | None:
        """加权随机选 1 个可用 cookie (健康度 ** 2 加权)."""
        async with self._lock:
            usable = [e for e in self._entries if e.usable]
            if not usable:
                return None
            weights = [max(0.01, e.health) ** 2 for e in usable]
            entry = random.choices(usable, weights=weights, k=1)[0]
            entry.last_used_at = time.time()
            entry.total_uses += 1
            return entry

    def release(self, entry: CookieEntry, *, success: bool) -> None:
        """更新健康度, 失败超阈值进冷却."""
        if entry is None:
            return
        target = 1.0 if success else 0.0
        entry.health = (1 - self.EMA_ALPHA) * entry.health + self.EMA_ALPHA * target
        if success:
            entry.fail_streak = 0
        else:
            entry.fail_streak += 1
            if entry.fail_streak >= self.FAIL_THRESHOLD:
                cooldown = min(
                    self.COOLDOWN_MAX_SEC,
                    self.COOLDOWN_BASE_SEC * (2 ** (entry.fail_streak - self.FAIL_THRESHOLD)),
                )
                entry.cooldown_until = time.time() + cooldown
                logger.warning(
                    "Cookie %s 进冷却 %s 秒 (连续失败 %s 次, 健康度=%.2f)",
                    entry.label, cooldown, entry.fail_streak, entry.health,
                )

    def stats(self) -> dict:
        return {
            "total": len(self._entries),
            "healthy": self.healthy_count,
            "entries": [
                {
                    "label": e.label,
                    "usable": e.usable,
                    "health": round(e.health, 3),
                    "fail_streak": e.fail_streak,
                    "total_uses": e.total_uses,
                    "cooldown_remaining": max(0, e.cooldown_until - time.time()),
                }
                for e in self._entries
            ],
        }
