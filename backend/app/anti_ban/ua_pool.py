"""UA 池 — 真实浏览器 User-Agent 库 + 设备指纹随机."""

from __future__ import annotations

import random
import secrets

# 真实近期 (2026) UA 池, 优先移动端 (m.weibo.cn API 对移动端 UA 友好)
IPHONE_UAS = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
)

ANDROID_UAS = (
    "Mozilla/5.0 (Linux; Android 14; SM-S928U) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Mi 13) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/129.0.0.0 Mobile Safari/537.36",
)

DESKTOP_UAS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.5 Safari/605.1.15",
)


class UAPool:
    """UA 池 + 设备指纹生成器."""

    def __init__(self, *, mobile_weight: float = 0.7) -> None:
        self._mobile_weight = max(0.0, min(1.0, mobile_weight))
        self._mobile_uas = IPHONE_UAS + ANDROID_UAS
        self._desktop_uas = DESKTOP_UAS

    def random_ua(self) -> str:
        if random.random() < self._mobile_weight:
            return random.choice(self._mobile_uas)
        return random.choice(self._desktop_uas)

    def random_device_fingerprint(self) -> dict[str, str]:
        """生成一组随机设备指纹 headers (X-XSS / Sec-CH-UA 等).

        m.weibo.cn 实测对 sec-ch-ua* + device-memory 较友好.
        """
        return {
            "Sec-CH-UA-Mobile": "?1",
            "Sec-CH-UA-Platform": random.choice(['"iOS"', '"Android"', '"macOS"']),
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Device-Memory": random.choice(["2", "4", "8"]),
            # 简单随机化 etag-like 字段, 让指纹不完全静态
            "X-Request-Id": secrets.token_hex(8),
        }
