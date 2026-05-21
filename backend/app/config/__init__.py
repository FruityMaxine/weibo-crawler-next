"""配置中心 — pydantic-settings 三层合并 (env / YAML / CLI flag).

公开 API:
    from backend.app.config import Settings, get_settings, load_yaml, save_yaml
"""

from backend.app.config.settings import Settings, get_settings
from backend.app.config.loader import load_yaml, save_yaml, merge_into_env
from backend.app.config.schema import config_json_schema

__all__ = [
    "Settings",
    "get_settings",
    "load_yaml",
    "save_yaml",
    "merge_into_env",
    "config_json_schema",
]
