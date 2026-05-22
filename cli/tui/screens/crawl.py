"""抓取屏 — 输入 UID + 数量, 启动后实时进度条 + 滚动日志.

这是 TUI 的"核心交互界面": 用户上下键到主菜单"开始采集" 进来, 在这里
完成全部抓取动作, 无需记任何命令.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button, Footer, Header, Input, Label, ProgressBar, RichLog, Static,
)

from backend.app.crawler import AsyncWeiboClient
from backend.app.db.base import get_sessionmaker, init_db
from backend.app.services import UserService, WeiboService

logger = logging.getLogger("wcn.tui.crawl")


class CrawlScreen(Screen):
    """采集屏 — 输入 UID + 数量 → 启动 → 实时进度 + 日志."""

    BINDINGS = [
        ("escape", "app.pop_screen", "返回"),
        ("q", "app.exit", "退出"),
        ("ctrl+s", "submit", "开始"),
        ("ctrl+x", "stop", "停止"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._task: asyncio.Task | None = None
        self._running = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("[bold #27a644]● 开始采集[/]  输入 UID 与数量, 实时显示进度", classes="card-title")
        with Horizontal():
            with Vertical(id="crawl-form"):
                yield Label("微博用户 UID (必填)")
                yield Input(placeholder="例如: 1669879400", id="input-uid")

                yield Label("最大条数 (默认 20)")
                yield Input(value="20", id="input-max")

                yield Label("起始日期 (可空, 支持 yyyy-mm-dd 或整数 N 天)")
                yield Input(placeholder="例: 7 (最近 7 天) 或 2026-01-01", id="input-since")

                yield Label("Cookie (可空, 留空用 .env 默认)")
                yield Input(placeholder="可粘贴新 cookie 临时覆盖", id="input-cookie", password=True)

                with Horizontal():
                    yield Button("▶ 开始采集", id="btn-start", variant="primary", classes="-primary")
                    yield Button("■ 停止", id="btn-stop", variant="error", classes="-danger")
                    yield Button("← 返回", id="btn-back")

                yield Static("", id="crawl-status", classes="card")
                yield Static("[#8a8f98]说明: 进度条 + 日志在右侧. 抓取支持中途停止.[/]", classes="muted")

            with Vertical(id="crawl-output"):
                yield Static("[bold #5e6ad2]实时进度[/]", classes="card-title")
                yield ProgressBar(total=100, id="crawl-progress", show_eta=True)

                yield Static("[bold #5e6ad2]实时日志[/]", classes="card-title")
                yield RichLog(highlight=True, markup=True, id="crawl-log", wrap=False, max_lines=500)

        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#crawl-log", RichLog)
        log.write("[#8a8f98]等待输入...[/]")
        log.write("[#8a8f98]提示: 1) 输入 UID  2) (可选) 数量/日期/Cookie  3) Ctrl+S 或点 [开始采集][/]")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            if self._running:
                self._notify("正在抓取中, 请先按 [停止] 或 Ctrl+X.", level="warning")
                return
            self.app.pop_screen()
            return
        if bid == "btn-stop":
            await self.action_stop()
            return
        if bid == "btn-start":
            await self.action_submit()

    async def action_submit(self) -> None:
        if self._running:
            self._notify("已在抓取中, 请先停止.", level="warning")
            return

        uid_text = self.query_one("#input-uid", Input).value.strip()
        max_text = self.query_one("#input-max", Input).value.strip()
        since_text = self.query_one("#input-since", Input).value.strip()
        cookie_text = self.query_one("#input-cookie", Input).value.strip() or None

        if not uid_text.isdigit():
            self._notify("UID 必须是纯数字", level="danger")
            return

        try:
            max_count = int(max_text) if max_text else 20
            if max_count < 1 or max_count > 10000:
                raise ValueError
        except ValueError:
            self._notify("最大条数应是 1-10000 的整数", level="danger")
            return

        since_date = None
        if since_text:
            try:
                from cli.commands import _parse_since
                since_date = _parse_since(since_text)
            except Exception as e:
                self._notify(f"起始日期格式错: {e}", level="danger")
                return

        uid = int(uid_text)
        self._running = True
        self._task = asyncio.create_task(self._run_crawl(uid, max_count, since_date, cookie_text))

    async def action_stop(self) -> None:
        if not self._running or self._task is None:
            return
        self._task.cancel()
        self._notify("已请求停止 (等当前请求完成后退出).", level="warning")

    async def _run_crawl(
        self, uid: int, max_count: int, since_date, cookie_override: str | None
    ) -> None:
        log = self.query_one("#crawl-log", RichLog)
        bar = self.query_one("#crawl-progress", ProgressBar)
        bar.update(total=max_count, progress=0)
        self._notify("初始化数据库与 HTTP client...", level="info")
        log.write(f"[#5e6ad2]► 准备抓取 uid={uid} max={max_count} since={since_date}[/]")

        try:
            await init_db()
            sm = get_sessionmaker()
            async with sm() as session:
                us = UserService(session)
                ws = WeiboService(session)
                async with AsyncWeiboClient(cookie=cookie_override) as client:
                    log.write(f"[#4ec3ff]→ 拉取用户 {uid} 资料...[/]")
                    user = await us.fetch_and_upsert(uid, client=client)
                    await session.commit()
                    log.write(
                        f"[#27a644]✓ 用户:[/] [bold]{user.screen_name}[/] "
                        f"(微博 {user.statuses_count} / 粉丝 {user.followers_count})"
                    )
                    self._notify(
                        f"已锁定 [bold]{user.screen_name}[/], 开始翻页抓取...",
                        level="success",
                    )

                    count = 0
                    async for w in ws.crawl_user(
                        uid, client=client, max_count=max_count, since=since_date,
                    ):
                        count += 1
                        bar.update(progress=count)
                        ts = datetime.now().strftime("%H:%M:%S")
                        tag = "[#b88aff]🔁[/]" if w.is_retweet else "[#27a644]📝[/]"
                        preview = (w.text or "")[:60].replace("\n", " ")
                        log.write(
                            f"[#8a8f98]{ts}[/]  {tag}  "
                            f"[#5e6ad2]{w.weibo_id}[/]  {preview}"
                        )
                        if count % 10 == 0:
                            await session.commit()
                    await session.commit()
                    log.write(f"[bold #27a644]✓ 完成 — 共抓取 {count} 条[/]")
                    self._notify(f"全部完成 ✓ 共 {count} 条已落库", level="success")
                    bar.update(progress=max_count)
        except asyncio.CancelledError:
            log.write("[bold #d9a300]⚠ 用户中断[/]")
            self._notify("已中断", level="warning")
        except Exception as e:
            log.write(f"[bold #d65555]✗ 失败: {type(e).__name__}: {e}[/]")
            self._notify(f"失败: {e}", level="danger")
        finally:
            self._running = False
            self._task = None

    def _notify(self, msg: str, *, level: str = "info") -> None:
        status = self.query_one("#crawl-status", Static)
        cls = {
            "info": "info",
            "success": "success",
            "warning": "warning",
            "danger": "danger",
        }.get(level, "info")
        status.set_classes(f"card {cls}")
        status.update(msg)
