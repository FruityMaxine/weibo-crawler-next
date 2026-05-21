"""YAML 配置加载 / 落盘 — 给 TUI 配置中心实时编辑用.

使用流程:
    yaml_dict = load_yaml("config.yaml")
    merge_into_env(yaml_dict)             # 注入环境变量
    get_settings.cache_clear()
    settings = get_settings()             # 读到合并后的值
    save_yaml("config.yaml", changed)     # TUI 修改后回写
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{p} 顶层必须是 mapping, 实际 {type(data).__name__}")
    return data


def save_yaml(path: str | Path, data: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            data, f, allow_unicode=True, default_flow_style=False, sort_keys=True
        )


def merge_into_env(data: dict[str, Any], *, prefix: str = "WCN_") -> None:
    """把 YAML / dict 配置注入到 os.environ (pydantic-settings 会读)."""
    for k, v in data.items():
        env_key = f"{prefix}{k.upper()}"
        if v is None:
            continue
        if isinstance(v, bool):
            os.environ[env_key] = "true" if v else "false"
        elif isinstance(v, (int, float, str)):
            os.environ[env_key] = str(v)
        else:
            # list / dict 转 JSON 字符串
            import json
            os.environ[env_key] = json.dumps(v, ensure_ascii=False)


def settings_to_dict(settings) -> dict[str, Any]:
    """把 Settings 实例序列化为 dict, 用于 TUI 配置编辑回填."""
    return {
        k: (str(v) if isinstance(v, Path) else v)
        for k, v in settings.model_dump().items()
    }
