"""anti_ban 池工厂 — 从 settings 读 cookie/proxy/ua 配置构建全局单例池.

修 v0.5.x 之前的死代码问题: executor / CLI / TUI 调 AsyncWeiboClient 时
未注入池, 整个 anti_ban 系统从未在生产路径触发. 本模块提供 `get_pools()`
返回全局单例三池供所有 caller 注入.

用法:
    from backend.app.anti_ban.factory import get_pools

    cookie_pool, proxy_pool, ua_pool = get_pools()
    async with AsyncWeiboClient(
        cookie_pool=cookie_pool,
        proxy_pool=proxy_pool,
        ua_pool=ua_pool,
    ) as client:
        ...
"""

from __future__ import annotations

import logging
from functools import lru_cache

from backend.app.anti_ban.cookie_pool import CookiePool
from backend.app.anti_ban.proxy_pool import ProxyPool
from backend.app.anti_ban.ua_pool import UAPool
from backend.app.config import get_settings

logger = logging.getLogger("wcn.anti_ban.factory")


def _parse_pool_str(s: str) -> list[str]:
    """; 分号分隔的池字符串 → list, 去空串."""
    if not s:
        return []
    return [x.strip() for x in s.split(";") if x.strip()]


@lru_cache(maxsize=1)
def get_pools() -> tuple[CookiePool, ProxyPool, UAPool]:
    """全局单例池. 第一次调时从 settings 构建, 之后复用.

    settings.cookie_pool 优先级 > settings.weibo_cookie (单 cookie fallback).
    """
    s = get_settings()

    # Cookie 池: 优先用 cookie_pool 多 cookie, fallback 单 cookie
    cookies = _parse_pool_str(s.cookie_pool)
    if not cookies and s.weibo_cookie:
        cookies = [s.weibo_cookie]
    cookie_entries = [(c, f"cookie#{i}") for i, c in enumerate(cookies)]
    cookie_pool = CookiePool(cookie_entries)

    # Proxy 池: 从 proxy_pool 解析
    proxies = _parse_pool_str(s.proxy_pool)
    proxy_pool = ProxyPool(proxies)

    # UA 池: 从 settings 读移动端权重
    ua_pool = UAPool(mobile_weight=s.ua_pool_mobile_weight)

    logger.info(
        "anti_ban 池初始化: cookie=%d proxy=%d ua_mobile_weight=%.2f",
        len(cookies), len(proxies), s.ua_pool_mobile_weight,
    )
    return cookie_pool, proxy_pool, ua_pool


def reset_pools() -> None:
    """测试用: 清缓存重建池."""
    get_pools.cache_clear()
