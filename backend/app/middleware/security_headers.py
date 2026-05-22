"""安全 HTTP headers 中间件 — CSP / X-Content-Type-Options / X-Frame-Options / Referrer-Policy.

v0.7.0.0 修 reviewer 报告的"无安全 headers"问题. 默认策略:
  - Content-Security-Policy: 默认严格 self-only, 但允许内联样式 (Tailwind 需要)
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY (防 clickjacking)
  - Referrer-Policy: strict-origin-when-cross-origin
  - Strict-Transport-Security: 仅 HTTPS 部署时生效 (env 启用)

可通过 env 自定义:
  WCN_CSP_POLICY     覆盖默认 CSP
  WCN_HSTS_ENABLED   启 HSTS (反代终端 TLS 后开)
"""

from __future__ import annotations

import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# Tailwind 内联样式需 'unsafe-inline', React Bits 动效用 framer-motion 也需要
DEFAULT_CSP = (
    "default-src 'self'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data: https:; "
    "script-src 'self'; "
    "connect-src 'self' ws: wss:; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """注入所有响应的安全 headers."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        headers = response.headers

        # 仅在 headers 未由路由显式设置时填默认值
        headers.setdefault(
            "Content-Security-Policy",
            os.getenv("WCN_CSP_POLICY", DEFAULT_CSP),
        )
        headers.setdefault("X-Content-Type-Options", "nosniff")
        headers.setdefault("X-Frame-Options", "DENY")
        headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )

        # HSTS 仅在 env 启用 (反代终端 TLS 时)
        if os.getenv("WCN_HSTS_ENABLED", "").lower() in ("1", "true", "yes"):
            headers.setdefault(
                "Strict-Transport-Security",
                "max-age=63072000; includeSubDomains; preload",
            )
        return response
