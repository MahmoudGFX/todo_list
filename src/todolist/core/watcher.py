"""
Background thread that stamps `start_time` once per task.
"""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import List

from .models import TodoItem
from .storage import save_tasks

__all__ = ["TaskWatcher"]


class TaskWatcher(threading.Thread):
    """Runs every `interval_sec` (default 1 h)."""

    def __init__(self, tasks: List[TodoItem], interval_sec: int = 3600):
        super().__init__(daemon=True)
        self._tasks = tasks
        self._interval = interval_sec

    def run(self) -> None:
        while True:
            dirty = False
            now_iso = datetime.now(timezone.utc).isoformat()
            for t in self._tasks:
                if not t.completed and t.start_time is None:
                    t.start_time = now_iso
                    dirty = True
            if dirty:
                save_tasks(self._tasks)
            time.sleep(self._interval)
