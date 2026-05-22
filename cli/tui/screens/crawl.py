"""抓取屏 — 输入 UID 或选用户列表, 启动后实时进度条 + 滚动日志.

v0.5.1.0 修复:
  - 状态机鲁棒化: on_screen_resume 每次重置 _running/_task
  - action_stop 真 await task 结束, 不再卡死
  - _notify 加 is_attached 守卫, 避免在已卸载 widget 上操作
  - Esc 强制返回, 不卡 _running 检查
  - 新增 [📋 加载列表] 按钮, 选用户列表批量顺序抓取
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
from cli.tui.user_list_store import UserListStore

logger = logging.getLogger("wcn.tui.crawl")


class CrawlScreen(Screen):
    """采集屏 — 输入 UID + 数量 → 启动 → 实时进度 + 日志."""

    BINDINGS = [
        ("escape", "force_back", "返回"),
        ("q", "app.exit", "退出"),
        ("ctrl+s", "submit", "开始"),
        ("ctrl+x", "stop", "停止"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._task: asyncio.Task | None = None
        self._running = False
        self._batch_uids: list[int] = []
        self._batch_name: str = ""

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
                    yield Button("▶ 开始", id="btn-start", variant="primary", classes="-primary")
                    yield Button("📋 加载列表", id="btn-load-list")
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
        log.write("[#8a8f98]提示: 输入 UID 或点 [📋 加载列表] 选已保存的批次, Ctrl+S 开始[/]")

    def on_screen_resume(self) -> None:
        """每次屏幕重新显示时安全重置 — Textual 复用 Screen instance."""
        if not self._running:
            self._task = None
            self._notify("", level="info")

    def action_force_back(self) -> None:
        """Esc 强制返回, 不被 _running 状态卡住."""
        if self._running and self._task is not None:
            self._task.cancel()
        self._running = False
        self._task = None
        self.app.pop_screen()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            # 防御性: 如果在运行就 cancel 再返回, 不阻塞用户
            if self._running and self._task is not None:
                self._notify("正在中断当前任务...", level="warning")
                self._task.cancel()
                try:
                    await asyncio.wait_for(self._task, timeout=3.0)
                except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
                    pass
                self._running = False
                self._task = None
            self.app.pop_screen()
            return
        if bid == "btn-stop":
            await self.action_stop()
            return
        if bid == "btn-start":
            await self.action_submit()
            return
        if bid == "btn-load-list":
            await self._load_list_dialog()

    async def action_submit(self) -> None:
        if self._running:
            self._notify("已在抓取中, 请先停止.", level="warning")
            return

        uid_text = self.query_one("#input-uid", Input).value.strip()
        max_text = self.query_one("#input-max", Input).value.strip()
        since_text = self.query_one("#input-since", Input).value.strip()
        cookie_text = self.query_one("#input-cookie", Input).value.strip() or None

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

        # 优先用单 UID, 没填则用批次列表
        uids: list[int] = []
        if uid_text:
            if not uid_text.isdigit():
                self._notify("UID 必须是纯数字", level="danger")
                return
            uids = [int(uid_text)]
        elif self._batch_uids:
            uids = list(self._batch_uids)
        else:
            self._notify("请输入 UID 或点 [📋 加载列表] 选已保存批次.", level="danger")
            return

        self._running = True
        self._task = asyncio.create_task(
            self._run_crawl_batch(uids, max_count, since_date, cookie_text)
        )

    async def _run_crawl_batch(
        self, uids: list[int], max_count: int, since_date, cookie_override: str | None
    ) -> None:
        """顺序抓取多个 UID, 单个失败不影响其他.

        v0.6.0.0: init_db 在 batch 开始一次, 不在每个 _run_crawl 内重复.
        """
        if not self.is_attached:
            return
        log = self.query_one("#crawl-log", RichLog)
        total_users = len(uids)
        log.write(
            f"[bold #5e6ad2]► 开始批次抓取 {total_users} 用户 "
            f"(每个 max={max_count})[/]"
        )

        # init_db 提到 batch 外, 多 uid 共享一次 schema 检查
        await init_db()

        try:
            for idx, uid in enumerate(uids, 1):
                log.write(f"\n[bold #4ec3ff]── [{idx}/{total_users}] uid={uid} ──[/]")
                self._notify(
                    f"批次进度 [{idx}/{total_users}]  当前 uid={uid}",
                    level="info",
                )
                try:
                    await self._run_crawl(uid, max_count, since_date, cookie_override)
                except asyncio.CancelledError:
                    log.write("[bold #d9a300]⚠ 批次中断[/]")
                    raise
                except Exception as e:
                    log.write(f"[#d65555]✗ uid={uid} 失败: {e}, 跳过下一个[/]")
            log.write(f"\n[bold #27a644]✓ 批次完成 — {total_users} 用户全部尝试[/]")
            self._notify(f"批次完成 ✓ {total_users} 用户", level="success")
        except asyncio.CancelledError:
            pass
        finally:
            self._running = False
            self._task = None

    async def action_stop(self) -> None:
        if not self._running or self._task is None:
            self._notify("没有正在进行的抓取任务.", level="info")
            return
        self._task.cancel()
        try:
            # 等 task 真正结束 (含 finally 跑完), 上限 5 秒避免死等
            await asyncio.wait_for(self._task, timeout=5.0)
        except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
            pass
        # finally 块已 reset _running/_task, 再保险一次
        self._running = False
        self._task = None
        self._notify("已停止.", level="warning")

    async def _load_list_dialog(self) -> None:
        """v0.8.0.0: 推 UserListPickerScreen 让用户真选, 不再固定第一个."""
        log = self.query_one("#crawl-log", RichLog)
        store = UserListStore()
        if not store.list_all():
            log.write("[#d9a300]⚠ 还没有保存的用户列表. 回主菜单选 [用户列表] 创建.[/]")
            self._notify("无已保存列表, 请先在 [用户列表] 屏创建.", level="warning")
            return

        from cli.tui.screens.user_list_picker import UserListPickerScreen

        def _on_picked(result):
            """Picker dismiss 回调: result = (name, uids) 或 None."""
            if result is None:
                self._notify("已取消列表选择", level="info")
                return
            name, uids = result
            self._batch_uids = uids
            self._batch_name = name
            try:
                log2 = self.query_one("#crawl-log", RichLog)
                log2.write(
                    f"[bold #5e6ad2]► 已加载列表 '{name}' — 共 {len(uids)} 个 UID:[/]"
                )
                for u in uids:
                    log2.write(f"  • {u}")
            except Exception:
                pass
            self._notify(
                f"已加载列表 [bold]{name}[/] ({len(uids)} 个 UID). "
                f"点 [开始] 顺序抓取每个 UID.",
                level="success",
            )

        await self.app.push_screen(UserListPickerScreen(), callback=_on_picked)

    async def _run_crawl(
        self, uid: int, max_count: int, since_date, cookie_override: str | None
    ) -> None:
        """抓单个用户. 由 action_submit (单 UID) 或 _run_crawl_batch (批次) 调用.

        v0.6.0.0:
          - is_attached 守卫: 屏幕已卸载时不 query_one 防崩
          - init_db 由 _run_crawl_batch 调一次, 此处不重复
          - 注入 anti_ban 三池
        """
        from backend.app.anti_ban import get_pools

        if not self.is_attached:
            return
        log = self.query_one("#crawl-log", RichLog)
        bar = self.query_one("#crawl-progress", ProgressBar)
        bar.update(total=max_count, progress=0)
        log.write(f"[#5e6ad2]► uid={uid} max={max_count} since={since_date}[/]")

        sm = get_sessionmaker()
        cookie_pool, proxy_pool, ua_pool = get_pools()
        async with sm() as session:
            us = UserService(session)
            ws = WeiboService(session)
            async with AsyncWeiboClient(
                cookie=cookie_override,
                cookie_pool=cookie_pool,
                proxy_pool=proxy_pool,
                ua_pool=ua_pool,
            ) as client:
                log.write(f"[#4ec3ff]→ 拉取用户 {uid} 资料...[/]")
                user = await us.fetch_and_upsert(uid, client=client)
                await session.commit()
                log.write(
                    f"[#27a644]✓ 用户:[/] [bold]{user.screen_name}[/] "
                    f"(微博 {user.statuses_count} / 粉丝 {user.followers_count})"
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
                log.write(f"[bold #27a644]✓ uid={uid} 完成 — {count} 条[/]")

    def _notify(self, msg: str, *, level: str = "info") -> None:
        # 防御: 屏幕已卸载时不操作
        if not self.is_attached:
            return
        try:
            status = self.query_one("#crawl-status", Static)
        except Exception:
            return
        cls = {
            "info": "info",
            "success": "success",
            "warning": "warning",
            "danger": "danger",
        }.get(level, "info")
        status.set_classes(f"card {cls}")
        status.update(msg)
