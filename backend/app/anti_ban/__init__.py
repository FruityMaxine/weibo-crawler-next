"""anti-ban 风控子系统 — Tick 5.

子模块:
  - cookie_pool: 多账号 cookie 轮换 + 健康度评分 + 失效检测
  - proxy_pool: HTTP/SOCKS5 代理池 + 探活 + 失败降权
  - ua_pool: UA 库 + 设备指纹随机
  - rate_limiter: Token Bucket + 自适应 + 退避 (替换 Tick 2 简版)
  - retry: 指数退避 + jitter
  - captcha_detector: 响应解析检测验证码 / 限频信号

设计原则:
  - 所有池都实现 acquire() / release(item, success) 统一接口
  - 健康度评分用 EMA 平滑, 失败超阈值自动屏蔽 N 分钟
  - 接入点是 crawler.client.AsyncWeiboClient (替换简易限频)
"""

from backend.app.anti_ban.cookie_pool import CookiePool
from backend.app.anti_ban.proxy_pool import ProxyPool
from backend.app.anti_ban.ua_pool import UAPool
from backend.app.anti_ban.rate_limiter import TokenBucketLimiter
from backend.app.anti_ban.retry import exponential_backoff_with_jitter
from backend.app.anti_ban.captcha_detector import detect_captcha, is_rate_limited

__all__ = [
    "CookiePool",
    "ProxyPool",
    "UAPool",
    "TokenBucketLimiter",
    "exponential_backoff_with_jitter",
    "detect_captcha",
    "is_rate_limited",
]
