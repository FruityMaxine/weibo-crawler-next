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
from backend.app.crawler.api_endpoints import (
    USER_INFO,
    USER_WEIBO_LIST,
    WEIBO_COMMENTS_HOTFLOW,
    WEIBO_REPOST_TIMELINE,
    user_container_id,
)
from backend.app.crawler.headers import build_headers
from backend.app.crawler.rate_limiter import SimpleRateLimiter

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
    ) -> None:
        s = get_settings()
        self._cookie = cookie if cookie is not None else s.weibo_cookie
        self._limiter = SimpleRateLimiter(rate_per_sec or s.crawler_rate_limit)
        self._timeout = timeout or s.crawler_timeout
        self._max_retry = s.crawler_retry_max
        self._client: httpx.AsyncClient | None = None

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
        await self._limiter.acquire()

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self._max_retry),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.HTTPError, WeiboAPIError)),
            reraise=True,
        ):
            with attempt:
                resp = await self._client.get(
                    url, params=params, headers=build_headers(self._cookie)
                )
                resp.raise_for_status()
                data = resp.json()
                ok = data.get("ok")
                if ok == 0 or ok is False:
                    msg = data.get("msg") or data.get("errmsg") or "ok=0"
                    logger.warning("微博 API 返回 ok=0: %s url=%s", msg, url)
                    raise WeiboAPIError(msg)
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
