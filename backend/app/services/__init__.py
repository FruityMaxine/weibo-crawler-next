"""业务逻辑层 — 不直接与 HTTP / DB 耦合, 方便 CLI 与 API 复用."""

from backend.app.services.user_service import UserService
from backend.app.services.weibo_service import WeiboService
from backend.app.services.task_service import TaskService

__all__ = ["UserService", "WeiboService", "TaskService"]
