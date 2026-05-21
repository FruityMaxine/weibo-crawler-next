"""FastAPI 主入口 — lifespan + 路由注册 + CORS."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.db.base import init_db
from backend.app.routers import health, tasks, users, weibo
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
    async with lifespan_scheduler():
        yield
    logger.info("backend 已优雅关闭")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="weibo-crawler-next",
        version="0.2.0.0",
        description="现代化微博数据采集与分析平台",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(weibo.router, prefix="/api/weibo", tags=["weibo"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
    return app


app = create_app()
