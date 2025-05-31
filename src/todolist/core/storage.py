"""
JSON persistence helpers.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .models import TodoItem

__all__ = ["DB_PATH", "load_tasks", "save_tasks", "append_tasks"]

DB_PATH = Path(__file__).resolve().parent.parent / "todos.json"


def load_tasks() -> List[TodoItem]:
    """Load all tasks from disk (empty list if none)."""
    if DB_PATH.exists():
        with DB_PATH.open(encoding="utf8") as fh:
            return [TodoItem.from_dict(d) for d in json.load(fh)]
    return []


def save_tasks(tasks: List[TodoItem]) -> None:
    """Overwrite DB with tasks."""
    with DB_PATH.open("w", encoding="utf8") as fh:
        json.dump([t.to_dict() for t in tasks], fh, indent=2)


def append_tasks(new_items: List[dict]) -> List[TodoItem]:
    """
    Append raw extractor dicts to DB.

    @param new_items: [{'description': str, 'priority': str, …}, …]
    @return list[TodoItem]: Updated full list.
    """
    tasks = load_tasks()
    tasks.extend(TodoItem(**d) for d in new_items)
    save_tasks(tasks)
    return tasks
