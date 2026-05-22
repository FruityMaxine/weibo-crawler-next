"""Webhook 导出器 — POST 数据到外部 URL (兼容原项目 post_config)."""

from __future__ import annotations

import time
from collections.abc import Iterable

import httpx

from backend.app.config import get_settings
from backend.app.exporters.base import BaseExporter, ExportContext, ExportResult
from backend.app.exporters.registry import register_exporter
from backend.app.db.models import Weibo


@register_exporter("webhook")
class WebhookExporter(BaseExporter):
    DESCRIPTION = "Webhook — POST 到外部 URL, 含 Authorization Bearer"

    async def export(self, items: Iterable[Weibo], ctx: ExportContext) -> ExportResult:
        t0 = time.monotonic()
        s = get_settings()
        if not s.webhook_url:
            return ExportResult(
                format="webhook", success=False, item_count=0,
                error="WCN_WEBHOOK_URL 未配置",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        rows = [self.weibo_to_dict(w) for w in items]
        headers = {"Content-Type": "application/json"}
        if s.webhook_token:
            headers["Authorization"] = f"Bearer {s.webhook_token}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    s.webhook_url,
                    json={"uid": ctx.uid, "count": len(rows), "weibos": rows},
                    headers=headers,
                )
                resp.raise_for_status()
        except httpx.HTTPError as e:
            return ExportResult(
                format="webhook", success=False, item_count=0,
                error=f"{type(e).__name__}: {e}",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )

        # 不把完整 URL (可能含 query string token) 回传, 仅露 host
        from urllib.parse import urlparse
        parsed = urlparse(s.webhook_url)
        safe_endpoint = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return ExportResult(
            format="webhook", success=True, item_count=len(rows),
            output_path=safe_endpoint,
            duration_ms=int((time.monotonic() - t0) * 1000),
        )
