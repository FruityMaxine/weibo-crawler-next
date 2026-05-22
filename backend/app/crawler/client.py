"""异步微博 HTTP client — httpx + 限频 + 重试.

接入点:
- Tick 2: 简易 SimpleRateLimiter (这里)
- Tick 5: 替换为 anti_ban.rate_limiter Token Bucket + cookie 池 + proxy 池
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.app.config import get_settings
from backend.app.anti_ban import (
    CookiePool, ProxyPool, TokenBucketLimiter,
    is_rate_limited,
)
from backend.app.anti_ban.ua_pool import UAPool
from backend.app.crawler.api_endpoints import (
    USER_INFO,
    USER_WEIBO_LIST,
    WEIBO_COMMENTS_HOTFLOW,
    WEIBO_REPOST_TIMELINE,
    user_container_id,
)
from backend.app.crawler.headers import build_headers

logger = logging.getLogger("wcn.crawler")


class WeiboAPIError(Exception):
    """微博 API 返回 ok!=1 或 HTTP 非 2xx."""


class AsyncWeiboClient:
    """异步微博 API 客户端 — 上下文管理器使用."""

    def __init__(
        self,
        cookie: str | None = None,
        rate_per_sec: float | None = None,
        timeout: float | None = None,
        *,
        cookie_pool: CookiePool | None = None,
        proxy_pool: ProxyPool | None = None,
        ua_pool: UAPool | None = None,
    ) -> None:
        s = get_settings()
        self._cookie = cookie if cookie is not None else s.weibo_cookie
        self._limiter = TokenBucketLimiter(rate_per_sec or s.crawler_rate_limit, burst=3)
        self._timeout = timeout or s.crawler_timeout
        self._max_retry = s.crawler_retry_max
        self._client: httpx.AsyncClient | None = None
        self._cookie_pool = cookie_pool
        self._proxy_pool = proxy_pool
        self._ua_pool = ua_pool or UAPool()

    async def __aenter__(self) -> AsyncWeiboClient:
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self._timeout, connect=10.0),
            follow_redirects=True,
            http2=False,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _get(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        assert self._client is not None, "AsyncWeiboClient 须在 async with 上下文内使用"
        import time as _time

        await self._limiter.acquire()

        # 从池中拿 cookie / proxy (若池非空)
        cookie_entry = await self._cookie_pool.acquire() if self._cookie_pool else None
        proxy_entry = await self._proxy_pool.acquire() if self._proxy_pool else None
        effective_cookie = cookie_entry.value if cookie_entry else self._cookie

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self._max_retry),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.HTTPError, WeiboAPIError)),
            reraise=True,
        ):
            with attempt:
                headers = build_headers(effective_cookie)
                # 加 UA 池随机 + 设备指纹
                headers["User-Agent"] = self._ua_pool.random_ua()
                headers.update(self._ua_pool.random_device_fingerprint())

                t0 = _time.monotonic()
                resp = await self._client.get(url, params=params, headers=headers)
                latency_ms = (_time.monotonic() - t0) * 1000

                # 自适应限频反馈
                self._limiter.report_response_time(latency_ms)
                if self._proxy_pool and proxy_entry:
                    # 仅记录, success 在 outer 决定
                    proxy_entry.latency_ms = (
                        0.7 * proxy_entry.latency_ms + 0.3 * latency_ms
                    )

                try:
                    resp.raise_for_status()
                    data = resp.json()
                except (httpx.HTTPStatusError, ValueError) as e:
                    if is_rate_limited(resp.status_code, resp.text):
                        self._limiter.report_rate_limited()
                        if self._cookie_pool and cookie_entry:
                            self._cookie_pool.release(cookie_entry, success=False)
                        if self._proxy_pool and proxy_entry:
                            self._proxy_pool.release(proxy_entry, success=False)
                    raise

                ok = data.get("ok")
                if ok == 0 or ok is False:
                    msg = data.get("msg") or data.get("errmsg") or "ok=0"
                    logger.warning("微博 API 返回 ok=0: %s url=%s", msg, url)
                    if is_rate_limited(resp.status_code, data):
                        self._limiter.report_rate_limited()
                    if self._cookie_pool and cookie_entry:
                        self._cookie_pool.release(cookie_entry, success=False)
                    raise WeiboAPIError(msg)

                # 成功路径
                self._limiter.report_success()
                if self._cookie_pool and cookie_entry:
                    self._cookie_pool.release(cookie_entry, success=True)
                if self._proxy_pool and proxy_entry:
                    self._proxy_pool.release(proxy_entry, success=True, latency_ms=latency_ms)
                return data

        raise RuntimeError("unreachable")

    # ---------- 高层 API ----------

    async def get_user_info(self, uid: int | str) -> dict[str, Any]:
        return await self._get(USER_INFO, {"type": "uid", "value": str(uid)})

    async def get_user_weibo_page(
        self, uid: int | str, *, page: int = 1, since_id: str | None = None
    ) -> dict[str, Any]:
        params = {
            "type": "uid",
            "value": str(uid),
            "containerid": user_container_id(uid),
            "page": page,
        }
        if since_id:
            params["since_id"] = since_id
        return await self._get(USER_WEIBO_LIST, params)

    async def get_weibo_comments(
        self, weibo_id: str, *, max_id: int = 0, max_id_type: int = 0
    ) -> dict[str, Any]:
        return await self._get(
            WEIBO_COMMENTS_HOTFLOW,
            {"id": weibo_id, "mid": weibo_id, "max_id": max_id, "max_id_type": max_id_type},
        )

    async def get_weibo_reposts(self, weibo_id: str, *, page: int = 1) -> dict[str, Any]:
        return await self._get(
            WEIBO_REPOST_TIMELINE, {"id": weibo_id, "page": page}
        )
