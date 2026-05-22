"""v0.7.0.0 安全 + Exporter 重构测试.

覆盖:
- SecurityHeadersMiddleware: 所有响应都有 CSP/X-Frame-Options/X-Content-Type
- sanitize_fts_query: AND/OR/NOT/NEAR 剥离
- BaseExporter 资源生命周期: open/write_batch/close, 异常路径仍 close
"""

from __future__ import annotations

import asyncio

import pytest


# ============ SecurityHeadersMiddleware ============

@pytest.mark.asyncio
async def test_security_headers_present(temp_db: str):
    """所有响应应当含 CSP / X-Frame-Options / X-Content-Type-Options."""
    from httpx import ASGITransport, AsyncClient
    from backend.app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/healthz")
        assert r.status_code == 200
        # 安全 headers 全部存在
        assert "content-security-policy" in {k.lower() for k in r.headers}
        assert r.headers.get("x-content-type-options") == "nosniff"
        assert r.headers.get("x-frame-options") == "DENY"
        assert "referrer-policy" in {k.lower() for k in r.headers}


@pytest.mark.asyncio
async def test_security_headers_hsts_when_enabled(monkeypatch, temp_db: str):
    """WCN_HSTS_ENABLED=true 时加 HSTS header."""
    monkeypatch.setenv("WCN_HSTS_ENABLED", "true")
    from httpx import ASGITransport, AsyncClient
    from backend.app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/healthz")
        assert "strict-transport-security" in {k.lower() for k in r.headers}


@pytest.mark.asyncio
async def test_csp_env_override(monkeypatch, temp_db: str):
    """WCN_CSP_POLICY 覆盖默认 CSP."""
    monkeypatch.setenv("WCN_CSP_POLICY", "default-src 'none'")
    from httpx import ASGITransport, AsyncClient
    from backend.app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/healthz")
        assert r.headers.get("content-security-policy") == "default-src 'none'"


# ============ sanitize_fts_query ============

def test_sanitize_strips_fts5_meta():
    from backend.app.db.fts import sanitize_fts_query
    assert sanitize_fts_query('"hello"') == "hello"
    assert sanitize_fts_query("a*b") == "a b"
    assert sanitize_fts_query("col:value") == "col value"
    assert sanitize_fts_query("a + b - c") == "a b c"


def test_sanitize_strips_boolean_keywords():
    from backend.app.db.fts import sanitize_fts_query
    assert sanitize_fts_query("hello AND world") == "hello world"
    assert sanitize_fts_query("a OR b") == "a b"
    assert sanitize_fts_query("foo NOT bar") == "foo bar"
    assert sanitize_fts_query("x NEAR y") == "x y"


def test_sanitize_case_insensitive():
    from backend.app.db.fts import sanitize_fts_query
    assert sanitize_fts_query("hello and world") == "hello world"
    assert sanitize_fts_query("a Or b") == "a b"


def test_sanitize_preserves_chinese():
    from backend.app.db.fts import sanitize_fts_query
    assert sanitize_fts_query("编程 Python 学习") == "编程 Python 学习"


# ============ BaseExporter 资源生命周期 ============

@pytest.mark.asyncio
async def test_base_exporter_lifecycle_calls_close_on_success():
    """成功路径: open → write_batch → close 全跑."""
    from backend.app.exporters.base import BaseExporter, ExportContext

    called: list[str] = []

    class _TestExporter(BaseExporter):
        FORMAT_NAME = "test"
        DESCRIPTION = "test"

        async def _open(self, ctx):
            called.append("open")

        async def _write_batch(self, items, ctx):
            called.append("write")
            return len(list(items))

        async def _close(self):
            called.append("close")

    result = await _TestExporter().export([], ExportContext())
    assert called == ["open", "write", "close"]
    assert result.success is True


@pytest.mark.asyncio
async def test_base_exporter_close_runs_on_exception():
    """异常路径: open 抛后 close 仍跑 (避免资源泄漏)."""
    from backend.app.exporters.base import BaseExporter, ExportContext

    called: list[str] = []

    class _BrokenExporter(BaseExporter):
        FORMAT_NAME = "broken"
        DESCRIPTION = "broken"

        async def _open(self, ctx):
            called.append("open")
            raise RuntimeError("can not connect")

        async def _write_batch(self, items, ctx):
            called.append("write")  # 不该被调
            return 0

        async def _close(self):
            called.append("close")

    result = await _BrokenExporter().export([], ExportContext())
    assert "open" in called
    assert "write" not in called
    assert "close" in called  # 关键: 异常路径必跑
    assert result.success is False
    assert "can not connect" in (result.error or "")


@pytest.mark.asyncio
async def test_base_exporter_write_batch_exception_still_close():
    """_write_batch 异常也必 close."""
    from backend.app.exporters.base import BaseExporter, ExportContext

    called: list[str] = []

    class _WriteFailExporter(BaseExporter):
        FORMAT_NAME = "write_fail"
        DESCRIPTION = "write_fail"

        async def _open(self, ctx):
            called.append("open")

        async def _write_batch(self, items, ctx):
            called.append("write")
            raise OSError("disk full")

        async def _close(self):
            called.append("close")

    result = await _WriteFailExporter().export([{"x": 1}], ExportContext())  # type: ignore
    assert called == ["open", "write", "close"]
    assert result.success is False
