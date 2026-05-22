"""anti_ban 5 子模块 + notify 4 通道 单元测试."""

from __future__ import annotations

import asyncio
import time

import pytest

from backend.app.anti_ban import (
    CookiePool, ProxyPool, UAPool, TokenBucketLimiter,
    exponential_backoff_with_jitter,
    detect_captcha, is_rate_limited,
)


# ============ CookiePool ============

@pytest.mark.asyncio
async def test_cookie_pool_acquire_release_cycle():
    pool = CookiePool(["cookieA", "cookieB"])
    assert len(pool) == 2
    assert pool.healthy_count == 2

    e = await pool.acquire()
    assert e is not None
    assert e.value in ("cookieA", "cookieB")
    pool.release(e, success=True)
    assert e.health == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_cookie_pool_fail_streak_triggers_cooldown():
    pool = CookiePool(["only_one"])
    # 连续 3 次失败 → 进冷却
    for _ in range(3):
        e = await pool.acquire()
        if e is None:
            break
        pool.release(e, success=False)
    # 第 4 次应当拿不到 (在冷却)
    e = await pool.acquire()
    assert e is None
    stats = pool.stats()
    assert stats["healthy"] == 0
    assert stats["entries"][0]["fail_streak"] >= 3


@pytest.mark.asyncio
async def test_cookie_pool_health_weighted_random():
    pool = CookiePool(["good", "bad"])
    # 把 bad 调到很低
    bad_entry = pool._entries[1]
    bad_entry.health = 0.05
    good_entry = pool._entries[0]
    good_entry.health = 1.0
    # 100 次抽样应该绝大多数选 good
    counts = {"good": 0, "bad": 0}
    for _ in range(100):
        e = await pool.acquire()
        counts[e.value] += 1
    assert counts["good"] > 80


def test_cookie_pool_empty_input():
    pool = CookiePool(None)
    assert len(pool) == 0
    pool.add("")
    assert len(pool) == 0  # 空字符串拒绝


def test_cookie_pool_labeled_input():
    pool = CookiePool([("cookieX", "main"), ("cookieY", "backup")])
    assert pool._entries[0].label == "main"
    assert pool._entries[1].label == "backup"


# ============ ProxyPool ============

@pytest.mark.asyncio
async def test_proxy_pool_basic():
    pool = ProxyPool(["http://127.0.0.1:9999", "socks5://127.0.0.1:8888"])
    assert len(pool) == 2
    e = await pool.acquire()
    assert e is not None
    pool.release(e, success=True, latency_ms=50.0)
    assert e.health > 0.9


@pytest.mark.asyncio
async def test_proxy_pool_failure_cooldown():
    pool = ProxyPool(["http://broken.invalid:80"])
    for _ in range(3):
        e = await pool.acquire()
        if e is None:
            break
        pool.release(e, success=False)
    e_after = await pool.acquire()
    assert e_after is None


def test_proxy_scheme_parse():
    pool = ProxyPool(["http://x:80", "socks5://y:1080"])
    assert pool._entries[0].scheme == "http"
    assert pool._entries[1].scheme == "socks5"


# ============ UAPool ============

def test_ua_pool_random_ua_returns_string():
    pool = UAPool()
    ua = pool.random_ua()
    assert isinstance(ua, str)
    assert "Mozilla" in ua or "Chrome" in ua or "Safari" in ua


def test_ua_pool_device_fingerprint():
    pool = UAPool()
    fp = pool.random_device_fingerprint()
    assert "Sec-CH-UA-Mobile" in fp
    assert "X-Request-Id" in fp
    assert len(fp["X-Request-Id"]) >= 8


def test_ua_pool_mobile_weight():
    pool = UAPool(mobile_weight=1.0)
    # 100 次都应当是移动端
    mobiles = [pool.random_ua() for _ in range(100)]
    assert all("Mobile" in u or "iPhone" in u or "iPad" in u for u in mobiles)


# ============ TokenBucketLimiter ============

@pytest.mark.asyncio
async def test_token_bucket_burst_drains():
    limiter = TokenBucketLimiter(rate=100.0, burst=5)
    t0 = time.monotonic()
    # 拿 burst+1 次, 第 6 次必须等
    for _ in range(5):
        await limiter.acquire()
    elapsed = time.monotonic() - t0
    assert elapsed < 0.1  # 前 5 次几乎无阻


@pytest.mark.asyncio
async def test_token_bucket_rate_limit_backoff():
    limiter = TokenBucketLimiter(rate=10.0, burst=3)
    initial_rate = limiter._current_rate
    limiter.report_rate_limited()
    # 速率应当降到一半以下
    assert limiter._current_rate < initial_rate
    # backoff_until 在未来
    assert limiter._backoff_until > time.monotonic()


def test_token_bucket_adaptive_speedup_on_fast_response():
    limiter = TokenBucketLimiter(rate=1.0, burst=3)
    initial = limiter._current_rate
    # 多次 fast response → 加速
    for _ in range(30):
        limiter.report_response_time(200.0)
    assert limiter._current_rate > initial


def test_token_bucket_adaptive_slowdown_on_slow_response():
    limiter = TokenBucketLimiter(rate=2.0, burst=3)
    initial = limiter._current_rate
    for _ in range(30):
        limiter.report_response_time(3500.0)
    assert limiter._current_rate < initial


def test_token_bucket_stats_fields():
    limiter = TokenBucketLimiter(rate=1.0)
    s = limiter.stats()
    assert "current_rate" in s
    assert "consecutive_429" in s
    assert "backoff_remaining" in s


# ============ retry / captcha ============

def test_exponential_backoff_monotonic_ceiling():
    delays = [exponential_backoff_with_jitter(i, base=1.0, max_delay=10.0) for i in range(8)]
    # 不严格单调因 jitter, 但 attempt 7 应 ≈ 10s ± jitter
    assert delays[7] <= 13.0 and delays[7] >= 7.0


def test_detect_captcha_keywords():
    assert detect_captcha("操作过于频繁, 请稍后再试") is True
    assert detect_captcha({"ok": 0, "msg": "需要验证码"}) is True
    assert detect_captcha("normal weibo text") is False
    assert detect_captcha(None) is False


def test_is_rate_limited_status_code():
    assert is_rate_limited(429) is True
    assert is_rate_limited(418) is True
    assert is_rate_limited(200, {"ok": 0, "msg": "异地登录"}) is True
    assert is_rate_limited(200, {"ok": 1, "msg": ""}) is False


# ============ Notifications ============

@pytest.mark.asyncio
async def test_notify_telegram_unconfigured(monkeypatch):
    monkeypatch.delenv("WCN_TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("WCN_TELEGRAM_CHAT_ID", raising=False)
    from backend.app.notifications import TelegramNotifier, NotificationEvent
    n = TelegramNotifier()
    assert n.configured is False
    r = await n.send(NotificationEvent(title="test"))
    assert r.success is False
    assert "TELEGRAM" in r.error


@pytest.mark.asyncio
async def test_notify_discord_unconfigured(monkeypatch):
    monkeypatch.delenv("WCN_DISCORD_WEBHOOK_URL", raising=False)
    from backend.app.notifications import DiscordNotifier, NotificationEvent
    n = DiscordNotifier()
    assert n.configured is False
    r = await n.send(NotificationEvent(title="test"))
    assert r.success is False


@pytest.mark.asyncio
async def test_notify_email_unconfigured(monkeypatch):
    for key in ("WCN_SMTP_HOST", "WCN_SMTP_USER", "WCN_SMTP_PASSWORD", "WCN_SMTP_RECIPIENTS"):
        monkeypatch.delenv(key, raising=False)
    from backend.app.notifications import EmailNotifier, NotificationEvent
    n = EmailNotifier()
    assert n.configured is False
    r = await n.send(NotificationEvent(title="test"))
    assert r.success is False


@pytest.mark.asyncio
async def test_notify_webhook_unconfigured(monkeypatch):
    monkeypatch.delenv("WCN_NOTIFY_WEBHOOK_URL", raising=False)
    from backend.app.notifications import WebhookNotifier, NotificationEvent
    n = WebhookNotifier()
    assert n.configured is False


@pytest.mark.asyncio
async def test_dispatch_with_no_configured_notifiers(monkeypatch):
    for key in (
        "WCN_TELEGRAM_BOT_TOKEN", "WCN_TELEGRAM_CHAT_ID",
        "WCN_DISCORD_WEBHOOK_URL",
        "WCN_SMTP_HOST", "WCN_SMTP_USER", "WCN_SMTP_PASSWORD", "WCN_SMTP_RECIPIENTS",
        "WCN_NOTIFY_WEBHOOK_URL",
    ):
        monkeypatch.delenv(key, raising=False)
    from backend.app.notifications import dispatch_event, NotificationEvent
    results = await dispatch_event(NotificationEvent(title="test", body="..."))
    assert results == []
