"""CLI 命令实现 — click + Rich 富终端输出.

子命令:
- wcn run --user <uid>     抓取单用户 (前台模式, 直接落 SQLite)
- wcn serve                启动 FastAPI 后端 (host/port 用 .env)
- wcn user <uid>           查询本地已抓用户
- wcn weibo --uid <uid>    查询本地已抓微博
- wcn tasks                列出最近任务
- wcn info                 显示当前配置摘要
- wcn version              打印版本号
- wcn tui                  (Tick 3 占位 — 未实现)
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date as date_type

import click
from rich.console import Console
from rich.table import Table

from backend import __version__
from backend.app.config import get_settings
from backend.app.crawler import AsyncWeiboClient
from backend.app.db.base import get_sessionmaker, init_db
from backend.app.services import TaskService, UserService, WeiboService

console = Console()


@click.group(name="wcn", help="weibo-crawler-next — 现代化微博数据采集 CLI")
@click.option("-v", "--verbose", is_flag=True, help="开启 DEBUG 日志")
def cli(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


@cli.command()
def version() -> None:
    """打印版本号."""
    console.print(f"[bold cyan]weibo-crawler-next[/bold cyan] v{__version__}")


@cli.command()
def info() -> None:
    """显示当前配置摘要."""
    s = get_settings()
    table = Table(title="weibo-crawler-next 配置", show_header=True, header_style="bold magenta")
    table.add_column("项", style="cyan", no_wrap=True)
    table.add_column("值", style="white")
    rows = [
        ("env", s.env),
        ("host:port", f"{s.host}:{s.port}"),
        ("database_url", s.database_url),
        ("data_dir", str(s.data_dir)),
        ("output_dir", str(s.output_dir)),
        ("cookie 已配置", "✓" if s.weibo_cookie else "未配置 (匿名模式)"),
        ("rate_limit", f"{s.crawler_rate_limit} req/sec"),
        ("page_size", str(s.crawler_page_size)),
        ("scheduler_enabled", str(s.scheduler_enabled)),
        ("log_level", s.log_level),
    ]
    for k, v in rows:
        table.add_row(k, v)
    console.print(table)


def _parse_since(since: str | None) -> date_type | None:
    """支持原项目 3 种 since_date 格式:
       - "yyyy-mm-dd" 绝对日期
       - "N" 整数: 抓取最近 N 天
       - None: 不限
    """
    if not since:
        return None
    s = since.strip()
    if s.isdigit():
        from datetime import datetime as _dt, timedelta as _td, timezone as _tz
        days = int(s)
        return (_dt.now(_tz.utc) - _td(days=days)).date()
    try:
        return date_type.fromisoformat(s)
    except ValueError:
        raise click.BadParameter(
            f"--since 必须是 'yyyy-mm-dd' 或正整数 (最近 N 天), 实际: {since!r}"
        )


@cli.command()
@click.option("-u", "--user", "uid", type=int, default=None, help="单个微博用户 ID")
@click.option(
    "-f", "--user-file", "user_file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default=None,
    help="批量模式: 从文本文件读 uid (每行一个 uid, # 注释跳过, 兼容原项目 user_id_list.txt)",
)
@click.option("-n", "--max", "max_count", type=int, default=20, help="每个用户最多抓取微博条数")
@click.option("--only-original", is_flag=True, help="仅原创 (跳过转发)")
@click.option(
    "--since", "since", type=str, default=None,
    help="只抓此日期之后. 支持 'yyyy-mm-dd' 或整数 N (最近 N 天)",
)
@click.option("--cookie", "cookie", default=None, help="覆盖 .env 中的 cookie")
def run(
    uid: int | None, user_file: str | None,
    max_count: int, only_original: bool,
    since: str | None, cookie: str | None,
) -> None:
    """前台抓取微博 → 落本地 SQLite. 支持单 uid 或批量文件."""
    if not uid and not user_file:
        raise click.BadParameter("必须指定 -u <uid> 或 -f <user-id-file>")
    since_date = _parse_since(since)

    uids: list[int] = []
    if uid is not None:
        uids.append(uid)
    if user_file:
        from pathlib import Path as _P
        for line in _P(user_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # 原项目格式: "uid [nickname] [since N] [topic]" — 仅取第 1 字段
            parts = line.split()
            try:
                uids.append(int(parts[0]))
            except (ValueError, IndexError):
                console.print(f"[yellow]跳过无效行: {line!r}[/yellow]")

    if not uids:
        console.print("[red]无任何有效 uid[/red]")
        return

    console.print(f"[cyan]>>> 批量抓取 {len(uids)} 个用户 (max={max_count}/user)[/cyan]")
    asyncio.run(_run_users(uids, max_count, only_original, since_date, cookie))


async def _run_users(
    uids: list[int], max_count: int, only_original: bool,
    since_date: date_type | None, cookie: str | None,
) -> None:
    await init_db()
    sm = get_sessionmaker()
    async with sm() as session:
        us = UserService(session)
        ws = WeiboService(session)
        async with AsyncWeiboClient(cookie=cookie) as client:
            for idx, uid in enumerate(uids, 1):
                console.print(
                    f"\n[yellow]>>> [{idx}/{len(uids)}] 抓取用户 {uid}...[/yellow]"
                )
                try:
                    user = await us.fetch_and_upsert(uid, client=client)
                    await session.commit()
                    console.print(
                        f"[green]✓[/green] [bold]{user.screen_name}[/bold] "
                        f"(微博 {user.statuses_count} / 粉丝 {user.followers_count})"
                    )
                    count = 0
                    async for w in ws.crawl_user(
                        uid, client=client, max_count=max_count,
                        only_original=only_original, since=since_date,
                    ):
                        count += 1
                        tag = "🔁" if w.is_retweet else "📝"
                        preview = (w.text or "")[:60].replace("\n", " ")
                        console.print(f"  {tag} [{count}] {w.weibo_id}  {preview}")
                        if count % 10 == 0:
                            await session.commit()
                    await session.commit()
                    console.print(f"[bold green]✓ uid={uid} 完成, 抓 {count} 条[/bold green]")
                except Exception as e:
                    console.print(f"[red]✗ uid={uid} 失败: {e}[/red]")
                    await session.rollback()


async def _run_user(
    uid: int,
    max_count: int,
    only_original: bool,
    since_date: date_type | None,
    cookie: str | None,
) -> None:
    """单用户抓取 (保留以兼容旧调用, 内部走 _run_users)."""
    await _run_users([uid], max_count, only_original, since_date, cookie)


@cli.command()
@click.argument("uid", type=int)
def user(uid: int) -> None:
    """查询本地已抓用户."""
    asyncio.run(_show_user(uid))


async def _show_user(uid: int) -> None:
    sm = get_sessionmaker()
    async with sm() as session:
        u = await UserService(session).get(uid)
        if u is None:
            console.print(f"[red]用户 {uid} 本地未抓取[/red]")
            return
        console.print(f"[bold cyan]{u.screen_name}[/bold cyan] (uid={u.uid})")
        console.print(f"  描述: {u.description or '无'}")
        console.print(f"  认证: {u.verified}  原因: {u.verified_reason or '无'}")
        console.print(
            f"  微博 {u.statuses_count} / 粉丝 {u.followers_count} / 关注 {u.follow_count}"
        )


@cli.command()
@click.option("--uid", type=int, default=None)
@click.option("-n", "--limit", type=int, default=20)
def weibo(uid: int | None, limit: int) -> None:
    """列出本地已抓微博."""
    asyncio.run(_list_weibo(uid, limit))


async def _list_weibo(uid: int | None, limit: int) -> None:
    sm = get_sessionmaker()
    async with sm() as session:
        items = await WeiboService(session).list_recent(limit=limit, uid=uid)
        if not items:
            console.print("[yellow]本地暂无微博数据, 先 `wcn run -u <uid>` 抓取[/yellow]")
            return
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("weibo_id", style="dim", no_wrap=True)
        table.add_column("uid", justify="right")
        table.add_column("时间", style="cyan")
        table.add_column("👍", justify="right")
        table.add_column("💬", justify="right")
        table.add_column("正文", overflow="fold")
        for w in items:
            ts = w.created_at.strftime("%Y-%m-%d %H:%M") if w.created_at else "-"
            text = (w.text or "")[:80].replace("\n", " ")
            table.add_row(
                w.weibo_id, str(w.uid), ts, str(w.attitudes_count),
                str(w.comments_count), text,
            )
        console.print(table)


@cli.command()
def tasks() -> None:
    """列出最近的采集任务."""
    asyncio.run(_list_tasks())


async def _list_tasks() -> None:
    sm = get_sessionmaker()
    async with sm() as session:
        items = await TaskService(session).list_all()
        if not items:
            console.print("[yellow]暂无任务[/yellow]")
            return
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", justify="right")
        table.add_column("名称")
        table.add_column("UID", justify="right")
        table.add_column("状态", style="cyan")
        table.add_column("进度", justify="right")
        table.add_column("已抓", justify="right")
        for t in items:
            table.add_row(
                str(t.id), t.name, str(t.uid or "-"),
                str(t.status.value), f"{t.progress}%", str(t.total_fetched),
            )
        console.print(table)


@cli.command()
@click.option("--host", default=None, help="覆盖 .env 中的 host")
@click.option("--port", type=int, default=None, help="覆盖 .env 中的 port")
@click.option("--reload", is_flag=True, help="开发模式 reload")
def serve(host: str | None, port: int | None, reload: bool) -> None:
    """启动 FastAPI 后端 (uvicorn)."""
    import uvicorn

    s = get_settings()
    uvicorn.run(
        "backend.app.main:app",
        host=host or s.host,
        port=port or s.port,
        reload=reload,
        log_level=s.log_level.lower(),
    )


@cli.command()
def tui() -> None:
    """启动 Textual TUI (上下键菜单 / 6 子屏)."""
    import sys
    if not sys.stdout.isatty():
        console.print(
            "[red]TUI 需要交互式终端 (TTY). 当前输出不是 TTY (可能是管道/重定向/CI).\n"
            "请直接在终端运行 `wcn tui`, 不要 pipe 或重定向 stdout.[/red]"
        )
        return
    try:
        from cli.tui import WCNApp
    except ImportError as e:
        console.print(
            f"[red]TUI 需要 [tui] extras: uv pip install -e '.[tui]'  ({e})[/red]"
        )
        return
    WCNApp().run()


@cli.command()
@click.option(
    "-f", "--format", "fmt",
    type=click.Choice(["csv", "json", "sqlite", "mysql", "mongodb", "webhook"]),
    default=None, help="导出格式 (留空用 .env WCN_EXPORT_DEFAULT_FORMAT)",
)
@click.option("--uid", type=int, default=None, help="只导出指定 uid")
@click.option("-n", "--limit", type=int, default=1000, help="最大条数")
@click.option("-o", "--output", default=None, help="自定义文件名 (CSV/JSON/SQLite 用)")
def export(fmt: str | None, uid: int | None, limit: int, output: str | None) -> None:
    """导出本地数据到 CSV / JSON / SQLite / MySQL / MongoDB / Webhook."""
    import asyncio as _asyncio
    from backend.app.config import get_settings as _gs
    from backend.app.db.base import get_sessionmaker as _gsm
    from backend.app.exporters import available_exporters, get_exporter
    from backend.app.exporters.base import ExportContext
    from backend.app.services import WeiboService as _WS

    fmt = fmt or _gs().export_default_format
    s = _gs()

    async def _run() -> None:
        sm = _gsm()
        async with sm() as session:
            items = await _WS(session).list_recent(limit=limit, uid=uid)
        if not items:
            console.print(
                "[yellow]本地无微博数据可导出, 先用 `wcn run -u <uid>` 抓取.[/yellow]"
            )
            return
        exporter = get_exporter(fmt)
        ctx = ExportContext(uid=uid, output_dir=s.output_dir, filename=output)
        with console.status(f"[#5e6ad2]导出 {len(items)} 条到 {fmt}...[/]"):
            result = await exporter.export(items, ctx)
        if result.success:
            console.print(
                f"[green]✓[/] 导出 [bold]{result.item_count}[/] 条到 "
                f"[cyan]{result.output_path}[/] ({result.duration_ms} ms)"
            )
        else:
            console.print(f"[red]✗ 导出失败:[/] {result.error}")
            console.print(
                "[#8a8f98]可用 exporter: "
                + ", ".join(k for k, _ in available_exporters())
                + "[/]"
            )

    _asyncio.run(_run())


@cli.command(name="exporters")
def list_exporters() -> None:
    """列出可用导出器."""
    from backend.app.exporters import available_exporters

    table = Table(title="可用导出器", show_header=True, header_style="bold magenta")
    table.add_column("格式", style="cyan", no_wrap=True)
    table.add_column("描述", style="white")
    for name, desc in available_exporters():
        table.add_row(name, desc)
    console.print(table)


def build_cli() -> click.Group:
    """显式返回根命令组 — 给 __main__.py 调用."""
    return cli
