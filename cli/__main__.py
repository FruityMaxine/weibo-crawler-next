"""CLI 主入口 — `wcn` / `python -m cli`.

Tick 2 简版: argparse / click 风格命令组.
Tick 3 升级: 加入 `wcn tui` 子命令 (Textual 框架, 上下键菜单).
"""

from __future__ import annotations

import sys

from cli.commands import build_cli


def main() -> int:
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
