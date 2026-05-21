"""5 ORM model: User / Weibo / Media / Comment / Repost.

设计要点:
- weibo_id 用 BigInteger (微博 ID 可能很大)
- 关系字段惰性加载 (避免抓取场景过度 join)
- 关键查询字段加 index (uid / weibo_id / created_at)
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """微博用户 — 19 项原项目字段全保留 + 抓取元数据."""

    __tablename__ = "users"

    uid: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    screen_name: Mapped[str] = mapped_column(String(128), index=True)
    gender: Mapped[str | None] = mapped_column(String(8), default=None)
    location: Mapped[str | None] = mapped_column(String(128), default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    birthday: Mapped[str | None] = mapped_column(String(32), default=None)
    education: Mapped[str | None] = mapped_column(String(256), default=None)
    company: Mapped[str | None] = mapped_column(String(256), default=None)
    sunshine_credit: Mapped[str | None] = mapped_column(String(64), default=None)
    registration_time: Mapped[str | None] = mapped_column(String(32), default=None)
    verified: Mapped[bool] = mapped_column(default=False)
    verified_type: Mapped[int | None] = mapped_column(Integer, default=None)
    verified_reason: Mapped[str | None] = mapped_column(String(512), default=None)
    statuses_count: Mapped[int] = mapped_column(Integer, default=0)
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    follow_count: Mapped[int] = mapped_column(Integer, default=0)
    urank: Mapped[int | None] = mapped_column(Integer, default=None)
    mbrank: Mapped[int | None] = mapped_column(Integer, default=None)
    avatar_hd: Mapped[str | None] = mapped_column(String(512), default=None)
    profile_url: Mapped[str | None] = mapped_column(String(512), default=None)

    crawled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    weibos: Mapped[list[Weibo]] = relationship(back_populates="user", lazy="noload")


class Weibo(Base):
    __tablename__ = "weibos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    weibo_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    bid: Mapped[str | None] = mapped_column(String(32), default=None, index=True)
    uid: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.uid"), index=True)
    text: Mapped[str] = mapped_column(Text, default="")
    text_raw: Mapped[str | None] = mapped_column(Text, default=None)
    source: Mapped[str | None] = mapped_column(String(128), default=None)
    location: Mapped[str | None] = mapped_column(String(128), default=None)
    topics: Mapped[list | None] = mapped_column(JSON, default=list)
    at_users: Mapped[list | None] = mapped_column(JSON, default=list)
    pic_urls: Mapped[list | None] = mapped_column(JSON, default=list)
    video_url: Mapped[str | None] = mapped_column(String(1024), default=None)
    article_url: Mapped[str | None] = mapped_column(String(1024), default=None)
    is_retweet: Mapped[bool] = mapped_column(default=False)
    retweet_id: Mapped[str | None] = mapped_column(String(32), default=None, index=True)
    attitudes_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    reposts_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    crawled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped[User] = relationship(back_populates="weibos", lazy="noload")
    media: Mapped[list[Media]] = relationship(back_populates="weibo", lazy="noload")
    comments: Mapped[list[Comment]] = relationship(back_populates="weibo", lazy="noload")

    __table_args__ = (
        Index("ix_weibos_uid_created", "uid", "created_at"),
        Index("ix_weibos_is_retweet", "is_retweet"),
    )


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    weibo_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("weibos.weibo_id"), index=True
    )
    kind: Mapped[str] = mapped_column(String(16))  # pic / video / live_photo / article
    url: Mapped[str] = mapped_column(String(1024))
    local_path: Mapped[str | None] = mapped_column(String(1024), default=None)
    downloaded: Mapped[bool] = mapped_column(default=False)
    file_size: Mapped[int | None] = mapped_column(Integer, default=None)
    crawled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    weibo: Mapped[Weibo] = relationship(back_populates="media", lazy="noload")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    weibo_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("weibos.weibo_id"), index=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_screen_name: Mapped[str] = mapped_column(String(128))
    text: Mapped[str] = mapped_column(Text, default="")
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    crawled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    weibo: Mapped[Weibo] = relationship(back_populates="comments", lazy="noload")


class Repost(Base):
    __tablename__ = "reposts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repost_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    weibo_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("weibos.weibo_id"), index=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_screen_name: Mapped[str] = mapped_column(String(128))
    text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    crawled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class CrawlTask(Base):
    """采集任务记录 — 用于审计 / 进度 / 重试."""

    __tablename__ = "crawl_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256))
    uid: Mapped[int | None] = mapped_column(BigInteger, default=None, index=True)
    query: Mapped[str | None] = mapped_column(String(256), default=None)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, name="task_status"),
        default=TaskStatus.PENDING,
        index=True,
    )
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    total_fetched: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, default=None)
    config_snapshot: Mapped[dict | None] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
