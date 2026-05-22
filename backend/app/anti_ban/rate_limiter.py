"""Token Bucket 限流器 + 自适应延时 + 429 退避.

替换 Tick 2 的 crawler/rate_limiter.py 简易版 (本 tick 同 commit 删除).
"""

from __future__ import annotations

import asyncio
import logging
import time

logger = logging.getLogger("wcn.anti_ban.rate")


class TokenBucketLimiter:
    """Token bucket — 每秒补 `rate` 个 token, 容量 `burst`.

    特点:
      - acquire() 阻塞直到拿到 1 token
      - report_response_time(ms) → 自适应延时 (响应慢→降速, 响应快→可加速)
      - report_rate_limited() → 触发指数退避, 暂停 N 秒
    """

    def __init__(
        self,
        rate: float = 1.0,
        burst: int = 3,
        *,
        adaptive: bool = True,
    ) -> None:
        self._initial_rate = max(0.01, rate)
        self._current_rate = self._initial_rate
        self._burst = max(1, burst)
        self._tokens = float(self._burst)
        self._last_refill = time.monotonic()
        self._adaptive = adaptive
        self._lock = asyncio.Lock()
        self._backoff_until: float = 0.0
        self._consecutive_429 = 0
        # 自适应平均响应时间 (EMA), 用于动态调速
        self._ema_response_ms: float = 0.0

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                # 处于退避期 → 等
                if now < self._backoff_until:
                    wait = self._backoff_until - now
                else:
                    # 补 token
                    elapsed = now - self._last_refill
                    self._tokens = min(self._burst, self._tokens + elapsed * self._current_rate)
                    self._last_refill = now
                    if self._tokens >= 1.0:
                        self._tokens -= 1.0
                        return
                    wait = (1.0 - self._tokens) / self._current_rate
            await asyncio.sleep(max(0.05, wait))

    def report_response_time(self, ms: float) -> None:
        """同步 fast-path. 调用方应在 acquire() 之后, 单 coroutine 上下文内调.

        注: 修改的字段是 float, Python GIL 保证赋值原子, 高并发下偶发的
        ±0.1 速率漂移是可接受的 (EMA 自我矫正). 严格强一致用 lock 版本.
        """
        if not self._adaptive or ms <= 0:
            return
        alpha = 0.2
        new_ema = (1 - alpha) * self._ema_response_ms + alpha * ms
        self._ema_response_ms = new_ema
        cur = self._current_rate
        if new_ema < 500 and cur < self._initial_rate * 2:
            self._current_rate = min(self._initial_rate * 2, cur * 1.1)
        elif new_ema > 2000:
            self._current_rate = max(self._initial_rate * 0.2, cur * 0.8)

    def report_rate_limited(self) -> None:
        """收到 429 / 验证码信号时调 — 指数退避. 字段原子赋值."""
        self._consecutive_429 += 1
        backoff = min(300.0, 5.0 * (2 ** (self._consecutive_429 - 1)))
        self._backoff_until = time.monotonic() + backoff
        self._current_rate = max(self._initial_rate * 0.1, self._current_rate * 0.5)
        logger.warning(
            "限频检测, 退避 %.1fs, 速率降至 %.2f req/sec (连续 %d 次)",
            backoff, self._current_rate, self._consecutive_429,
        )

    def report_success(self) -> None:
        """成功响应 → 重置 429 计数."""
        if self._consecutive_429 > 0:
            self._consecutive_429 = 0

    def stats(self) -> dict:
        return {
            "initial_rate": self._initial_rate,
            "current_rate": round(self._current_rate, 3),
            "burst": self._burst,
            "tokens": round(self._tokens, 2),
            "ema_response_ms": round(self._ema_response_ms, 1),
            "consecutive_429": self._consecutive_429,
            "backoff_remaining": max(0, self._backoff_until - time.monotonic()),
        }
