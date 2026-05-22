"""响应检测 — 是否触发了验证码 / 限频 / 异地登录提示."""

from __future__ import annotations

from typing import Any

# 微博常见限频/验证码标志 (m.weibo.cn 实测)
CAPTCHA_KEYWORDS = (
    "验证码", "captcha", "需要验证", "请先登录",
    "异地登录", "操作过于频繁", "rate limit",
)

RATE_LIMIT_STATUS = {429, 418}


def detect_captcha(payload: dict[str, Any] | str | bytes | None) -> bool:
    """检查 payload 是否含验证码 / 异常提示词."""
    if payload is None:
        return False
    if isinstance(payload, (bytes, bytearray)):
        try:
            payload = payload.decode("utf-8", errors="ignore")
        except Exception:
            return False
    if isinstance(payload, str):
        lower = payload.lower()
        return any(k in payload or k.lower() in lower for k in CAPTCHA_KEYWORDS)
    if isinstance(payload, dict):
        # 微博 ok=0 + 含 msg 字段
        msg = (payload.get("msg") or payload.get("errmsg") or "") if isinstance(payload, dict) else ""
        if isinstance(msg, str) and any(k in msg or k.lower() in msg.lower() for k in CAPTCHA_KEYWORDS):
            return True
        # 递归扫描 data
        data = payload.get("data")
        if isinstance(data, dict):
            return detect_captcha(data)
    return False


def is_rate_limited(status_code: int, payload: dict | str | None = None) -> bool:
    """综合判断: HTTP status + payload."""
    if status_code in RATE_LIMIT_STATUS:
        return True
    return detect_captcha(payload)
