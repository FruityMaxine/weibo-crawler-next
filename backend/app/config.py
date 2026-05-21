"""全局配置 — pydantic-settings 三层合并（env / .env / CLI flag）."""

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

    # 运行环境
    env: str = Field(default="dev", description="dev / staging / prod")
    host: str = Field(default="127.0.0.1", description="后端绑定地址 (铁律: 不绑 0.0.0.0)")
    port: int = Field(default=28800, description="后端 HTTP 端口")

    # 数据存储
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/wcn.db",
        description="SQLAlchemy 异步连接字符串",
    )
    data_dir: Path = Field(default=Path("./data"), description="本地数据文件根目录")
    output_dir: Path = Field(default=Path("./weibo_output"), description="导出文件根目录")

    # 微博认证 (可选)
    weibo_cookie: str = Field(default="", description="微博 cookie, 空则匿名模式")

    # 抓取参数
    crawler_rate_limit: float = Field(default=1.0, description="请求频率上限 req/sec")
    crawler_timeout: int = Field(default=20, description="单次 HTTP 超时秒")
    crawler_retry_max: int = Field(default=3, description="最大重试次数")
    crawler_page_size: int = Field(default=10, description="每页微博数 (1-100)")

    # 调度器
    scheduler_enabled: bool = Field(default=True, description="开机自启 APScheduler")

    # 日志
    log_level: str = Field(default="INFO", description="DEBUG/INFO/WARNING/ERROR")

    def ensure_dirs(self) -> None:
        """启动时确保数据 / 输出目录存在."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """单例 settings, 避免重复读 .env."""
    s = Settings()
    s.ensure_dirs()
    return s
