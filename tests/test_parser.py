"""parser 单元测试 — 不打微博真接口, 用本地 fixture."""

from __future__ import annotations

from backend.app.crawler.parser import (
    extract_at_users,
    extract_topics,
    parse_user_info,
    parse_weibo_card,
    strip_html,
)


def test_strip_html_basic():
    assert strip_html("<a href='x'>hi</a> world") == "hi world"
    assert strip_html("") == ""
    assert strip_html(None) == ""  # type: ignore[arg-type]


def test_extract_topics():
    assert extract_topics("今天聊聊 #编程# 和 #Python# 真有趣") == ["编程", "Python"]
    assert extract_topics("no topics") == []


def test_extract_at_users():
    assert extract_at_users("感谢 @张三 和 @LiSi_2024 的支持") == ["张三", "LiSi_2024"]


def test_parse_user_info_minimal():
    payload = {
        "data": {
            "userInfo": {
                "id": 12345,
                "screen_name": "测试用户",
                "verified": True,
                "verified_type": 0,
                "statuses_count": 100,
                "followers_count": 200,
                "follow_count": 50,
                "description": "hello",
            }
        }
    }
    info = parse_user_info(payload)
    assert info["uid"] == 12345
    assert info["screen_name"] == "测试用户"
    assert info["verified"] is True
    assert info["statuses_count"] == 100


def test_parse_weibo_card_basic():
    card = {
        "card_type": 9,
        "mblog": {
            "id": "ABC123",
            "bid": "ABC123",
            "text": "今天 #天气# 真好 @张三",
            "attitudes_count": 10,
            "comments_count": 3,
            "reposts_count": 1,
            "user": {"id": 555},
            "pics": [{"large": {"url": "https://example.com/pic.jpg"}}],
        },
    }
    parsed = parse_weibo_card(card)
    assert parsed is not None
    assert parsed["weibo_id"] == "ABC123"
    assert parsed["uid"] == 555
    assert parsed["topics"] == ["天气"]
    assert parsed["at_users"] == ["张三"]
    assert parsed["pic_urls"] == ["https://example.com/pic.jpg"]
    assert parsed["is_retweet"] is False
    assert parsed["attitudes_count"] == 10


def test_parse_weibo_card_skip_non_weibo():
    assert parse_weibo_card({"card_type": 11, "card_group": []}) is None


def test_parse_weibo_card_retweet():
    card = {
        "card_type": 9,
        "mblog": {
            "id": "X1",
            "text": "转发: 看看这个",
            "user": {"id": 1},
            "retweeted_status": {"id": "Y2", "text": "原文"},
        },
    }
    parsed = parse_weibo_card(card)
    assert parsed is not None
    assert parsed["is_retweet"] is True
    assert parsed["retweet_id"] == "Y2"
