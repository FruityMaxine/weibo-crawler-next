"""用户列表持久化存储 — JSON 文件存 ~/.config/wcn/user_lists/.

用户场景: 固定批次的微博用户, 第一次添加, 后续打开 TUI 直接加载即可批量抓取.
不放数据库的原因: 这是 UI 状态, 与抓取业务无关, 用文件存更轻量 + 用户可手动编辑.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def _store_dir() -> Path:
    """优先 $WCN_USER_LISTS_DIR, 否则 ~/.config/wcn/user_lists/."""
    env = os.getenv("WCN_USER_LISTS_DIR")
    if env:
        p = Path(env)
    else:
        # Linux/macOS: ~/.config/wcn, Windows: %APPDATA%\wcn
        appdata = os.getenv("APPDATA")
        if appdata:
            p = Path(appdata) / "wcn" / "user_lists"
        else:
            p = Path.home() / ".config" / "wcn" / "user_lists"
    p.mkdir(parents=True, exist_ok=True)
    return p


class UserListStore:
    """JSON 文件持久化的用户列表 CRUD.

    文件名 = 列表名 + .json. 文件内容 schema:
      {
        "name": "default",
        "uids": [1669879400, 1223178222, ...],
        "labels": {"1669879400": "迪丽热巴", ...}   # 可选
      }
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self._dir = Path(base_dir) if base_dir else _store_dir()

    def list_all(self) -> list[str]:
        """返回所有已保存列表名 (按修改时间倒序)."""
        files = list(self._dir.glob("*.json"))
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return [f.stem for f in files]

    def load(self, name: str) -> list[int]:
        """加载指定列表的 uid 列表. v0.6.0.0: 损坏文件给 logger.warning, 不再静默."""
        import logging
        p = self._dir / f"{self._safe_name(name)}.json"
        if not p.exists():
            return []
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            uids = data.get("uids", [])
            return [int(u) for u in uids if str(u).isdigit()]
        except (json.JSONDecodeError, ValueError, OSError) as e:
            logging.getLogger("wcn.user_list").warning(
                "用户列表文件损坏 %s: %s — 返回空列表", p, e,
            )
            return []

    def load_full(self, name: str) -> dict:
        """加载完整数据 (含 labels). v0.6.0.0: 损坏文件给 warning, 不静默."""
        import logging
        p = self._dir / f"{self._safe_name(name)}.json"
        if not p.exists():
            return {"name": name, "uids": [], "labels": {}}
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logging.getLogger("wcn.user_list").warning(
                "用户列表文件损坏 %s: %s — 返回空数据", p, e,
            )
            return {"name": name, "uids": [], "labels": {}}

    def save(self, name: str, uids: list[int], labels: dict[str, str] | None = None) -> Path:
        """保存列表到文件."""
        safe = self._safe_name(name)
        p = self._dir / f"{safe}.json"
        data = {
            "name": name,
            "uids": list(dict.fromkeys(int(u) for u in uids if int(u) > 0)),
            "labels": labels or {},
        }
        p.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return p

    def delete(self, name: str) -> bool:
        p = self._dir / f"{self._safe_name(name)}.json"
        if p.exists():
            p.unlink()
            return True
        return False

    def add_uid(self, name: str, uid: int, label: str = "") -> None:
        """往列表追加单 UID, 不重复."""
        data = self.load_full(name)
        uids = data.get("uids") or []
        if int(uid) not in uids:
            uids.append(int(uid))
        data["uids"] = uids
        if label:
            data.setdefault("labels", {})[str(uid)] = label
        self.save(name, uids, data.get("labels"))

    def remove_uid(self, name: str, uid: int) -> bool:
        data = self.load_full(name)
        uids = data.get("uids") or []
        if int(uid) in uids:
            uids.remove(int(uid))
            data["uids"] = uids
            data.setdefault("labels", {}).pop(str(uid), None)
            self.save(name, uids, data.get("labels"))
            return True
        return False

    @staticmethod
    def _safe_name(name: str) -> str:
        """文件名安全: 仅保留字母数字下划线连字符, 防止路径穿越."""
        import re
        safe = re.sub(r"[^\w\-]", "_", name.strip())[:64]
        return safe or "default"
