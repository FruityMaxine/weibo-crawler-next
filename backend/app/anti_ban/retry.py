"""指数退避 + jitter — 与 tenacity 配合或独立用."""

from __future__ import annotations

import random


def exponential_backoff_with_jitter(
    attempt: int,
    *,
    base: float = 1.0,
    max_delay: float = 60.0,
    jitter_ratio: float = 0.3,
) -> float:
    """
    Args:
        attempt: 第几次重试 (从 0 起)
        base: 第 0 次的基础等待秒
        max_delay: 上限
        jitter_ratio: 随机抖动比例 (0..1)
    Returns:
        本次等待秒数
    """
    delay = min(max_delay, base * (2 ** attempt))
    jitter = delay * jitter_ratio * (random.random() * 2 - 1)
    return max(0.1, delay + jitter)
