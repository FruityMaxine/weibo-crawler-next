"""限频中间件 — 简易版.

⚠️ NOTE: 本模块为 Tick 2 初版 (固定 req/sec + 简单 sleep).
   将在 Tick 5 被 backend/app/anti_ban/rate_limiter.py 替换为:
   - Token Bucket 算法
   - 自适应延时 (按响应时间动态调整)
   - 429 / 验证码探测 + 指数退避
   - 多账号轮询
   Tick 5 实施时记得删除本文件以避免双版本共存.
"""

from __future__ import annotations

import asyncio
import time


class SimpleRateLimiter:
    """每秒最多 rate 次请求 (单进程内同步, 跨 asyncio 任务安全)."""

    def __init__(self, rate_per_sec: float = 1.0) -> None:
        self.rate = max(0.01, rate_per_sec)
        self._min_interval = 1.0 / self.rate
        self._last_call: float = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            wait = self._min_interval - (now - self._last_call)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_call = time.monotonic()
