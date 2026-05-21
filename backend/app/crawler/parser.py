"""微博响应解析 — JSON → 标准化 dict.

m.weibo.cn 接口返回结构复杂, 这里把它压平成 ORM 友好的 dict.
"""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any

from dateutil import parser as dateparser

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_AT_RE = re.compile(r"@([\u4e00-\u9fa5A-Za-z0-9_\-]+)")
_TOPIC_RE = re.compile(r"#([^#]+)#")


def strip_html(text: str) -> str:
    return _HTML_TAG_RE.sub("", text or "").strip()


def extract_topics(text: str) -> list[str]:
    return _TOPIC_RE.findall(text or "")


def extract_at_users(text: str) -> list[str]:
    return _AT_RE.findall(text or "")


def parse_weibo_time(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return dateparser.parse(s)
    except (ValueError, TypeError):
        return None


def parse_user_info(data: dict[str, Any]) -> dict[str, Any]:
    """解析 m.weibo.cn /api/container/getIndex (用户主页) 的 userInfo 字段."""
    info = (data or {}).get("data", {}).get("userInfo") or {}
    return {
        "uid": int(info.get("id", 0) or 0),
        "screen_name": info.get("screen_name", ""),
        "gender": info.get("gender"),
        "description": info.get("description"),
        "verified": bool(info.get("verified", False)),
        "verified_type": info.get("verified_type"),
        "verified_reason": info.get("verified_reason"),
        "statuses_count": int(info.get("statuses_count", 0) or 0),
        "followers_count": int(info.get("followers_count", 0) or 0),
        "follow_count": int(info.get("follow_count", 0) or 0),
        "urank": info.get("urank"),
        "mbrank": info.get("mbrank"),
        "avatar_hd": info.get("avatar_hd"),
        "profile_url": info.get("profile_url"),
    }


def parse_weibo_card(card: dict[str, Any], *, strip_tags: bool = True) -> dict[str, Any] | None:
    """单条微博 card 解析. 返回 None 表示非微博卡片 (如广告/分割块)."""
    if card.get("card_type") != 9:
        return None
    mblog = card.get("mblog") or {}
    if not mblog:
        return None

    text_raw = mblog.get("text", "")
    text = strip_html(text_raw) if strip_tags else text_raw

    pic_urls: list[str] = []
    for p in mblog.get("pics", []) or []:
        large = (p.get("large") or {}).get("url") or p.get("url")
        if large:
            pic_urls.append(large)

    video_url = None
    page_info = mblog.get("page_info") or {}
    if page_info.get("type") == "video":
        media_info = page_info.get("media_info") or {}
        video_url = (
            media_info.get("mp4_hd_url")
            or media_info.get("mp4_sd_url")
            or media_info.get("stream_url")
        )

    retweet = mblog.get("retweeted_status") or {}
    is_retweet = bool(retweet)
    retweet_id = str(retweet.get("id")) if is_retweet and retweet.get("id") else None

    return {
        "weibo_id": str(mblog.get("id", "")),
        "bid": mblog.get("bid"),
        "uid": int((mblog.get("user") or {}).get("id", 0) or 0),
        "text": text,
        "text_raw": text_raw,
        "source": mblog.get("source"),
        "location": _extract_location(text_raw),
        "topics": extract_topics(text),
        "at_users": extract_at_users(text),
        "pic_urls": pic_urls,
        "video_url": video_url,
        "article_url": page_info.get("page_url") if page_info.get("type") == "article" else None,
        "is_retweet": is_retweet,
        "retweet_id": retweet_id,
        "attitudes_count": int(mblog.get("attitudes_count", 0) or 0),
        "comments_count": int(mblog.get("comments_count", 0) or 0),
        "reposts_count": int(mblog.get("reposts_count", 0) or 0),
        "created_at": parse_weibo_time(mblog.get("created_at")),
    }


def _extract_location(html: str) -> str | None:
    if not html:
        return None
    m = re.search(r'<a [^>]*href="https://weibo\.cn/sinaurl[^"]*"[^>]*>([^<]+)</a>', html)
    return m.group(1) if m else None


def iter_weibo_cards(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """从 getIndex 响应中提取 cards 列表."""
    return (payload or {}).get("data", {}).get("cards", []) or []
