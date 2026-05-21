"""initial schema — 6 tables (users / weibos / media / comments / reposts / crawl_tasks).

注: 开发期可直接用 backend.app.db.base.init_db() 的 create_all,
生产部署用 `alembic upgrade head`.

Revision ID: 0001
"""

from __future__ import annotations

revision: str = "0001"
down_revision: str | None = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 实际表结构由 SQLAlchemy DeclarativeBase 描述, 此处仅占位.
    # Tick 5 用 alembic autogenerate 重新生成精确的 DDL.
    pass


def downgrade() -> None:
    pass
