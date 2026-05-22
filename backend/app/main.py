"""FastAPI 主入口 — lifespan + 路由注册 + CORS + StaticFiles."""

from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import get_settings
from backend.app.db.base import init_db
from backend.app.db.fts import init_fts
from backend.app.routers import health, search, tasks, users, weibo, ws
from backend.app.tasks.scheduler import lifespan_scheduler

logger = logging.getLogger("wcn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    logger.info("启动 weibo-crawler-next backend (host=%s port=%s)", settings.host, settings.port)
    await init_db()
    await init_fts()
    async with lifespan_scheduler():
        yield
    logger.info("backend 已优雅关闭")


def _frontend_dist_path() -> Path | None:
    """寻找前端 dist 目录: dev/Docker/PyInstaller 三种场景都覆盖.

    优先级:
      1. 环境变量 WCN_FRONTEND_DIST 显式指定
      2. /app/frontend/dist  (Docker runtime)
      3. <项目根>/frontend/dist  (dev / pip / systemd)
      4. PyInstaller 打包后的 sys._MEIPASS/frontend/dist
    """
    candidates: list[Path] = []
    env_path = os.getenv("WCN_FRONTEND_DIST")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path("/app/frontend/dist"))
    repo_root = Path(__file__).resolve().parents[2]
    candidates.append(repo_root / "frontend" / "dist")
    try:
        import sys
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            candidates.append(Path(sys._MEIPASS) / "frontend" / "dist")  # type: ignore[attr-defined]
    except Exception:
        pass
    for c in candidates:
        if c.is_dir() and (c / "index.html").is_file():
            return c
    return None


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="weibo-crawler-next",
        version="0.4.2.0",
        description="现代化微博数据采集与分析平台",
        lifespan=lifespan,
    )

    # CORS — 默认含 Vite dev 端口, 生产可通过 WCN_CORS_ORIGINS env 扩展
    cors_origins = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        f"http://127.0.0.1:{settings.port}",
        f"http://localhost:{settings.port}",
    ]
    extra = os.getenv("WCN_CORS_ORIGINS", "").strip()
    if extra:
        cors_origins.extend([o.strip() for o in extra.split(",") if o.strip()])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(weibo.router, prefix="/api/weibo", tags=["weibo"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
    app.include_router(search.router, prefix="/api/search", tags=["search"])
    app.include_router(ws.router, tags=["ws"])

    # 挂载前端静态资源 — Docker / PyInstaller / 同进程服务都从这里出
    dist = _frontend_dist_path()
    if dist is not None:
        app.mount("/", StaticFiles(directory=str(dist), html=True), name="frontend")
        logger.info("挂载前端静态资源: %s", dist)
    else:
        logger.info("未发现前端 dist (frontend 未 build / dev 模式), 跳过 StaticFiles 挂载")

    return app


app = create_app()
