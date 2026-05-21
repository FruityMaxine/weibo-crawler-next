"""导出器 + 配置中心测试."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from backend.app.exporters import available_exporters, get_exporter
from backend.app.exporters.base import ExportContext


@pytest.mark.asyncio
async def test_registry_has_six_exporters():
    names = [n for n, _ in available_exporters()]
    assert set(names) == {"csv", "json", "sqlite", "mysql", "mongodb", "webhook"}


@pytest.mark.asyncio
async def test_get_unknown_exporter():
    with pytest.raises(KeyError):
        get_exporter("doesnotexist")


def _make_weibo_stub(weibo_id: str = "X1", uid: int = 555):
    """Tick 3 lightweight stub — 不入 DB, 仅给 exporter 序列化."""

    class _Stub:
        pass

    w = _Stub()
    w.weibo_id = weibo_id
    w.uid = uid
    w.text = "测试微博 #test# @foo"
    w.source = "iPhone"
    w.location = None
    w.topics = ["test"]
    w.at_users = ["foo"]
    w.pic_urls = ["https://example.com/pic.jpg"]
    w.video_url = None
    w.is_retweet = False
    w.retweet_id = None
    w.attitudes_count = 10
    w.comments_count = 2
    w.reposts_count = 1
    w.created_at = datetime(2026, 5, 21, 10, 0, tzinfo=timezone.utc)
    w.crawled_at = datetime(2026, 5, 21, 10, 5, tzinfo=timezone.utc)
    return w


@pytest.mark.asyncio
async def test_csv_exporter_roundtrip(tmp_path: Path):
    exporter = get_exporter("csv")
    items = [_make_weibo_stub("A1"), _make_weibo_stub("A2", uid=999)]
    ctx = ExportContext(uid=555, output_dir=tmp_path, filename="test.csv")
    result = await exporter.export(items, ctx)
    assert result.success, result.error
    assert result.item_count == 2
    out = Path(result.output_path)
    assert out.exists()
    content = out.read_text(encoding="utf-8-sig")
    assert "A1" in content and "A2" in content
    assert "weibo_id" in content  # header


@pytest.mark.asyncio
async def test_json_exporter_roundtrip(tmp_path: Path):
    exporter = get_exporter("json")
    items = [_make_weibo_stub("J1")]
    ctx = ExportContext(uid=555, output_dir=tmp_path)
    result = await exporter.export(items, ctx)
    assert result.success
    payload = json.loads(Path(result.output_path).read_text(encoding="utf-8"))
    assert payload["meta"]["count"] == 1
    assert payload["weibos"][0]["weibo_id"] == "J1"
    assert payload["weibos"][0]["topics"] == ["test"]


@pytest.mark.asyncio
async def test_sqlite_exporter_roundtrip(tmp_path: Path):
    import sqlite3

    exporter = get_exporter("sqlite")
    items = [_make_weibo_stub("S1"), _make_weibo_stub("S2")]
    ctx = ExportContext(uid=555, output_dir=tmp_path)
    result = await exporter.export(items, ctx)
    assert result.success
    conn = sqlite3.connect(result.output_path)
    rows = conn.execute("SELECT weibo_id, uid FROM weibos ORDER BY weibo_id").fetchall()
    conn.close()
    assert [r[0] for r in rows] == ["S1", "S2"]


@pytest.mark.asyncio
async def test_mysql_exporter_missing_creds():
    """无 aiomysql/凭据时应返回 success=False 而非崩溃."""
    exporter = get_exporter("mysql")
    result = await exporter.export([_make_weibo_stub()], ExportContext())
    assert result.success is False
    assert result.error is not None


@pytest.mark.asyncio
async def test_mongodb_exporter_missing_creds():
    exporter = get_exporter("mongodb")
    result = await exporter.export([_make_weibo_stub()], ExportContext())
    assert result.success is False
    assert result.error is not None


@pytest.mark.asyncio
async def test_webhook_exporter_missing_url():
    exporter = get_exporter("webhook")
    result = await exporter.export([_make_weibo_stub()], ExportContext())
    assert result.success is False
    assert "WCN_WEBHOOK_URL" in (result.error or "")


def test_config_yaml_loader(tmp_path: Path):
    from backend.app.config import load_yaml, save_yaml

    p = tmp_path / "wcn.yaml"
    save_yaml(p, {"host": "127.0.0.1", "port": 28900, "scheduler_enabled": False})
    loaded = load_yaml(p)
    assert loaded["host"] == "127.0.0.1"
    assert loaded["port"] == 28900
    assert loaded["scheduler_enabled"] is False


def test_config_yaml_loader_missing_file_returns_empty(tmp_path: Path):
    from backend.app.config import load_yaml
    assert load_yaml(tmp_path / "nonexistent.yaml") == {}


def test_config_schema_includes_groups():
    from backend.app.config import config_json_schema

    schema = config_json_schema()
    assert "x-field-groups" in schema
    assert "x-secret-fields" in schema
    assert "weibo_cookie" in schema["x-secret-fields"]


def test_config_merge_into_env(monkeypatch):
    from backend.app.config import merge_into_env

    monkeypatch.delenv("WCN_PORT", raising=False)
    merge_into_env({"port": 28999, "scheduler_enabled": False, "weibo_cookie": "test"})
    import os
    assert os.environ.get("WCN_PORT") == "28999"
    assert os.environ.get("WCN_SCHEDULER_ENABLED") == "false"
    assert os.environ.get("WCN_WEIBO_COOKIE") == "test"
