"""Exporter 插件系统 — BaseExporter ABC + registry + 6 内置实现.

自定义扩展:
    from backend.app.exporters import BaseExporter, register_exporter
    @register_exporter("myformat")
    class MyExporter(BaseExporter):
        async def export(self, items, **opts): ...
"""

from backend.app.exporters.base import BaseExporter, ExportContext, ExportResult
from backend.app.exporters.registry import (
    available_exporters,
    get_exporter,
    register_exporter,
)

# 触发内置 6 个 exporter 自注册
from backend.app.exporters import (  # noqa: F401, E402
    csv_exporter,
    json_exporter,
    sqlite_exporter,
    mysql_exporter,
    mongodb_exporter,
    webhook_exporter,
)

__all__ = [
    "BaseExporter",
    "ExportContext",
    "ExportResult",
    "available_exporters",
    "get_exporter",
    "register_exporter",
]
