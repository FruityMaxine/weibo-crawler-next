"""Settings 核心 — pydantic-settings + 单例缓存."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="WCN_",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # === 运行环境 ===
    env: str = Field(default="dev", description="dev / staging / prod")
    host: str = Field(default="127.0.0.1", description="后端绑定地址 (铁律: 不绑 0.0.0.0)")
    port: int = Field(default=28800, description="后端 HTTP 端口")

    # === 数据存储 ===
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/wcn.db",
        description="SQLAlchemy 异步连接字符串 (敏感字段从 env 注入)",
    )
    data_dir: Path = Field(default=Path("./data"), description="本地数据文件根目录")
    output_dir: Path = Field(default=Path("./weibo_output"), description="导出文件根目录")

    # === 微博认证 ===
    weibo_cookie: str = Field(default="", description="微博 cookie, 空则匿名模式")

    # === 抓取参数 ===
    crawler_rate_limit: float = Field(default=1.0, description="请求频率上限 req/sec")
    crawler_timeout: int = Field(default=20, description="单次 HTTP 超时秒")
    crawler_retry_max: int = Field(default=3, description="最大重试次数")
    crawler_page_size: int = Field(default=10, description="每页微博数 (1-100)")
    crawler_max_page: int = Field(default=50, description="单用户最多翻页数, 防广告卡死循环")
    crawler_empty_page_threshold: int = Field(default=3, description="连续 N 空页强制终止")

    # === anti_ban 池配置 (v0.6.0.0 引入) ===
    cookie_pool: str = Field(default="", description="多 cookie 池, ; 分号分隔")
    proxy_pool: str = Field(default="", description="多 proxy 池, ; 分号分隔 (http:// 或 socks5://)")
    ua_pool_mobile_weight: float = Field(default=0.7, description="UA 池移动端权重")

    # === 调度器 ===
    scheduler_enabled: bool = Field(default=True, description="开机自启 APScheduler")

    # === 日志 ===
    log_level: str = Field(default="INFO", description="DEBUG/INFO/WARNING/ERROR")

    # === 导出 (Tick 3 新增) ===
    export_default_format: str = Field(default="csv", description="默认导出格式")
    export_csv_delimiter: str = Field(default=",", description="CSV 分隔符")
    export_remove_html: bool = Field(default=True, description="导出前剥离 HTML 标签")
    export_include_retweet: bool = Field(default=True, description="导出含转发")

    # === MySQL (可选) ===
    mysql_host: str = Field(default="localhost")
    mysql_port: int = Field(default=3306)
    mysql_user: str = Field(default="root")
    mysql_password: str = Field(default="", description="敏感, 从 env 注入")
    mysql_database: str = Field(default="weibo")
    mysql_charset: str = Field(default="utf8mb4")

    # === MongoDB (可选) ===
    mongodb_uri: str = Field(default="", description="MongoDB 连接 URI, 敏感从 env 注入")
    mongodb_database: str = Field(default="weibo")

    # === Webhook 导出 ===
    webhook_url: str = Field(default="", description="POST 数据到外部 webhook 的 URL")
    webhook_token: str = Field(default="", description="Webhook Authorization Bearer, 敏感")

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def adjust_for_container(self) -> None:
        """容器内自动调整: 若检测到 /.dockerenv 且 host 仍是 loopback,
        则切换到 IPv6 双栈通配 `::`, 让宿主 -p 映射生效.
        宿主层 ports 已限制 `127.0.0.1:28800:28800`, 不会泄露到公网.
        """
        if self.host in ("127.0.0.1", "localhost") and Path("/.dockerenv").exists():
            self.host = "::"


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.ensure_dirs()
    s.adjust_for_container()
    return s
