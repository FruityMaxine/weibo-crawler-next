"""HTTP headers / User-Agent 管理.

Tick 2 简版: 静态 UA 池 + cookie 注入.
Tick 5 升级: 接入 anti_ban.ua_pool 做设备指纹随机.
"""

from __future__ import annotations

import random

DEFAULT_UA_POOL: tuple[str, ...] = (
    # iPhone Safari (移动端最稳)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    # Android Chrome
    "Mozilla/5.0 (Linux; Android 14; SM-S928U) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Mobile Safari/537.36",
    # Desktop Chrome (适用于 weibo.com)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36",
)


def random_ua() -> str:
    return random.choice(DEFAULT_UA_POOL)


def build_headers(cookie: str = "", *, referer: str = "https://m.weibo.cn/") -> dict[str, str]:
    headers = {
        "User-Agent": random_ua(),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": referer,
        "X-Requested-With": "XMLHttpRequest",
        "MWeibo-Pwa": "1",
    }
    if cookie:
        headers["Cookie"] = cookie
    return headers
