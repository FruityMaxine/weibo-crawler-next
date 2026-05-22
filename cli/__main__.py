"""CLI 主入口 — `wcn` / `python -m cli`.

v0.5.0.0 起:
  - `wcn`            (无参数)  →  自动启 Textual TUI 菜单界面 (TTY 环境)
                                 非 TTY 环境 → 显示 --help
  - `wcn tui`         显式启 TUI
  - `wcn run/serve/export/...`  专业 CLI 命令 (保留)
"""

from __future__ import annotations

import sys

from cli.commands import build_cli


def _is_no_args() -> bool:
    return len(sys.argv) == 1


def main() -> int:
    # 无参数 + TTY → 默认启 TUI 菜单 (Textual)
    if _is_no_args() and sys.stdout.isatty() and sys.stdin.isatty():
        try:
            from cli.tui import WCNApp
        except ImportError:
            # 没装 [tui] extras → 走默认 --help
            pass
        else:
            try:
                WCNApp().run()
                return 0
            except KeyboardInterrupt:
                return 130

    cli = build_cli()
    try:
        cli(standalone_mode=False)
    except SystemExit as e:  # click 正常退出
        return int(e.code or 0)
    except KeyboardInterrupt:
        print("\n已中断", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
