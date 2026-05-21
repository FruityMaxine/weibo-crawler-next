"""Exporter 注册中心 — 装饰器风格自注册 + 名称查询."""

from __future__ import annotations

from typing import Callable, Type

from backend.app.exporters.base import BaseExporter

_REGISTRY: dict[str, Type[BaseExporter]] = {}


def register_exporter(name: str) -> Callable[[Type[BaseExporter]], Type[BaseExporter]]:
    """装饰器: 把 exporter class 注册到全局 registry."""

    def _wrap(cls: Type[BaseExporter]) -> Type[BaseExporter]:
        cls.FORMAT_NAME = name
        if name in _REGISTRY:
            raise ValueError(f"exporter '{name}' 已注册")
        _REGISTRY[name] = cls
        return cls

    return _wrap


def get_exporter(name: str) -> BaseExporter:
    if name not in _REGISTRY:
        raise KeyError(f"未知 exporter '{name}', 可用: {sorted(_REGISTRY.keys())}")
    return _REGISTRY[name]()


def available_exporters() -> list[tuple[str, str]]:
    return [(name, cls.DESCRIPTION) for name, cls in sorted(_REGISTRY.items())]
