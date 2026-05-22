"""anti_ban 工厂 v0.6.0.0 测试 — 防 死代码 / 配置解析."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _reset_pools_and_settings():
    """每测试隔离: 清池缓存 + settings 缓存."""
    from backend.app.anti_ban import reset_pools
    from backend.app.config import get_settings
    reset_pools()
    get_settings.cache_clear()
    yield
    reset_pools()
    get_settings.cache_clear()


def test_get_pools_returns_three(monkeypatch):
    """工厂返回 (cookie_pool, proxy_pool, ua_pool) 三元组."""
    monkeypatch.delenv("WCN_COOKIE_POOL", raising=False)
    monkeypatch.delenv("WCN_PROXY_POOL", raising=False)
    monkeypatch.delenv("WCN_WEIBO_COOKIE", raising=False)

    from backend.app.anti_ban import get_pools, CookiePool, ProxyPool, UAPool
    cp, pp, up = get_pools()
    assert isinstance(cp, CookiePool)
    assert isinstance(pp, ProxyPool)
    assert isinstance(up, UAPool)


def test_empty_config_gives_empty_pools(monkeypatch):
    monkeypatch.delenv("WCN_COOKIE_POOL", raising=False)
    monkeypatch.delenv("WCN_PROXY_POOL", raising=False)
    monkeypatch.delenv("WCN_WEIBO_COOKIE", raising=False)
    from backend.app.anti_ban import get_pools
    cp, pp, _ = get_pools()
    assert len(cp) == 0
    assert len(pp) == 0


def test_single_cookie_fallback(monkeypatch):
    """无 cookie_pool 但有 weibo_cookie 时, fallback 单 cookie."""
    monkeypatch.delenv("WCN_COOKIE_POOL", raising=False)
    monkeypatch.setenv("WCN_WEIBO_COOKIE", "SUB=test123")
    from backend.app.anti_ban import get_pools
    cp, _, _ = get_pools()
    assert len(cp) == 1


def test_cookie_pool_multi(monkeypatch):
    """cookie_pool 优先于单 cookie, ; 分隔."""
    monkeypatch.setenv("WCN_COOKIE_POOL", "cookieA; cookieB; cookieC")
    monkeypatch.setenv("WCN_WEIBO_COOKIE", "ignored")
    from backend.app.anti_ban import get_pools
    cp, _, _ = get_pools()
    assert len(cp) == 3


def test_proxy_pool_parsing(monkeypatch):
    monkeypatch.setenv(
        "WCN_PROXY_POOL",
        "http://10.0.0.1:8080;socks5://10.0.0.2:1080;http://10.0.0.3:80",
    )
    from backend.app.anti_ban import get_pools
    _, pp, _ = get_pools()
    assert len(pp) == 3


def test_singleton_pattern(monkeypatch):
    """同进程内多次调用返回同一对象."""
    monkeypatch.setenv("WCN_COOKIE_POOL", "x")
    from backend.app.anti_ban import get_pools
    a = get_pools()
    b = get_pools()
    assert a is b  # 同元组对象
    assert a[0] is b[0]  # 同 CookiePool 实例


def test_reset_pools_clears_cache(monkeypatch):
    monkeypatch.setenv("WCN_COOKIE_POOL", "x")
    from backend.app.anti_ban import get_pools, reset_pools
    a = get_pools()
    reset_pools()
    monkeypatch.setenv("WCN_COOKIE_POOL", "x;y")
    # 还需清 settings cache 才能重读 env
    from backend.app.config import get_settings
    get_settings.cache_clear()
    b = get_pools()
    assert a is not b
    assert len(b[0]) == 2


def test_parse_pool_str_strips_whitespace():
    from backend.app.anti_ban.factory import _parse_pool_str
    assert _parse_pool_str("a; b ;c") == ["a", "b", "c"]
    assert _parse_pool_str("") == []
    assert _parse_pool_str(";;") == []
