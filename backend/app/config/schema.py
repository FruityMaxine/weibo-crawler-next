"""配置项分组 + JSON Schema 导出 — 供 TUI / WebUI 渲染配置表单.

每个 group 含字段元信息: 标签, 类型, 描述, 默认, 取值范围.
"""

from __future__ import annotations

from typing import Any

from backend.app.config.settings import Settings

# 字段分组 — TUI/WebUI 按 group 渲染 sidebar
FIELD_GROUPS: dict[str, list[str]] = {
    "运行环境": ["env", "host", "port", "log_level"],
    "数据存储": ["database_url", "data_dir", "output_dir"],
    "微博认证": ["weibo_cookie"],
    "抓取参数": [
        "crawler_rate_limit", "crawler_timeout", "crawler_retry_max", "crawler_page_size"
    ],
    "调度器": ["scheduler_enabled"],
    "导出": [
        "export_default_format", "export_csv_delimiter",
        "export_remove_html", "export_include_retweet"
    ],
    "MySQL (可选)": [
        "mysql_host", "mysql_port", "mysql_user",
        "mysql_password", "mysql_database", "mysql_charset"
    ],
    "MongoDB (可选)": ["mongodb_uri", "mongodb_database"],
    "Webhook": ["webhook_url", "webhook_token"],
}

SECRET_FIELDS = {"weibo_cookie", "mysql_password", "webhook_token"}


def config_json_schema() -> dict[str, Any]:
    """pydantic v2 自动生成 JSON Schema, 注入 group 元信息."""
    schema = Settings.model_json_schema()
    schema["x-field-groups"] = FIELD_GROUPS
    schema["x-secret-fields"] = sorted(SECRET_FIELDS)
    return schema


def field_label(key: str) -> str:
    """key → 人类可读标签 (TUI 渲染用)."""
    return key.replace("_", " ").title()
