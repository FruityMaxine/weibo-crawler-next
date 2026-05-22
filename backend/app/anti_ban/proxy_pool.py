"""Proxy 池 — HTTP/SOCKS5 代理轮换 + 探活 + 失败降权."""

from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

logger = logging.getLogger("wcn.anti_ban.proxy")


@dataclass
class ProxyEntry:
    url: str                      # http://host:port or socks5://host:port
    health: float = 1.0
    latency_ms: float = 0.0
    fail_streak: int = 0
    cooldown_until: float = 0.0
    last_check_at: float = 0.0
    total_uses: int = 0

    @property
    def usable(self) -> bool:
        return time.time() >= self.cooldown_until

    @property
    def scheme(self) -> str:
        return urlparse(self.url).scheme


class ProxyPool:
    """代理池, 自动周期探活 + 失败降权."""

    EMA_ALPHA = 0.3
    FAIL_THRESHOLD = 2
    COOLDOWN_BASE_SEC = 90
    COOLDOWN_MAX_SEC = 3600

    def __init__(
        self,
        proxies: list[str] | None = None,
        *,
        probe_url: str = "https://m.weibo.cn/",
        probe_timeout: float = 8.0,
    ) -> None:
        self._entries: list[ProxyEntry] = [ProxyEntry(url=u) for u in (proxies or []) if u]
        self._lock = asyncio.Lock()
        self._probe_url = probe_url
        self._probe_timeout = probe_timeout

    def add(self, url: str) -> None:
        if url:
            self._entries.append(ProxyEntry(url=url))

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def healthy_count(self) -> int:
        return sum(1 for e in self._entries if e.usable and e.health > 0.2)

    async def acquire(self) -> ProxyEntry | None:
        async with self._lock:
            usable = [e for e in self._entries if e.usable]
            if not usable:
                return None
            # 健康度 ** 2 / (1 + latency_ms/1000) 加权
            weights = [
                max(0.01, e.health) ** 2 / (1 + e.latency_ms / 1000)
                for e in usable
            ]
            entry = random.choices(usable, weights=weights, k=1)[0]
            entry.total_uses += 1
            return entry

    def release(self, entry: ProxyEntry | None, *, success: bool, latency_ms: float = 0.0) -> None:
        if entry is None:
            return
        target = 1.0 if success else 0.0
        entry.health = (1 - self.EMA_ALPHA) * entry.health + self.EMA_ALPHA * target
        if latency_ms > 0:
            entry.latency_ms = (
                (1 - self.EMA_ALPHA) * entry.latency_ms + self.EMA_ALPHA * latency_ms
            )
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
                    "Proxy %s 进冷却 %ss (失败 %s 次, 健康度=%.2f)",
                    entry.url, cooldown, entry.fail_streak, entry.health,
                )

    async def probe_all(self) -> None:
        """对所有代理跑一次探活 — 启动时 / cron 周期调."""
        if not self._entries:
            return
        async with httpx.AsyncClient(timeout=self._probe_timeout, follow_redirects=False) as client:
            await asyncio.gather(
                *(self._probe_one(client, e) for e in self._entries),
                return_exceptions=True,
            )

    async def _probe_one(self, client: httpx.AsyncClient, entry: ProxyEntry) -> None:
        t0 = time.monotonic()
        try:
            kwargs = {"proxy": entry.url} if entry.scheme in ("http", "https", "socks5") else {}
            async with httpx.AsyncClient(timeout=self._probe_timeout, **kwargs) as c:
                resp = await c.get(self._probe_url)
            ok = resp.status_code < 500
            latency = (time.monotonic() - t0) * 1000
            self.release(entry, success=ok, latency_ms=latency)
            entry.last_check_at = time.time()
            logger.debug("探活 %s → %s in %.0fms", entry.url, resp.status_code, latency)
        except Exception as e:
            self.release(entry, success=False)
            entry.last_check_at = time.time()
            logger.debug("探活 %s 失败: %s", entry.url, e)

    def stats(self) -> dict:
        return {
            "total": len(self._entries),
            "healthy": self.healthy_count,
            "entries": [
                {
                    "url": e.url,
                    "scheme": e.scheme,
                    "usable": e.usable,
                    "health": round(e.health, 3),
                    "latency_ms": round(e.latency_ms, 1),
                    "fail_streak": e.fail_streak,
                    "total_uses": e.total_uses,
                }
                for e in self._entries
            ],
        }
