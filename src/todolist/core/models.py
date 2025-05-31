"""
Data model for one task row.
"""
from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
from typing import Dict

__all__ = ["TodoItem"]


@dataclasses.dataclass
class TodoItem:
    """
    @param description: Brief task text.
    @param priority: 'high' | 'medium' | 'low'.
    @param assignee: Optional person.
    @param created_at: ISO timestamp when first logged.
    @param start_time: ISO timestamp when watcher stamps first check.
    @param completed: Flag.
    """
    description: str
    priority: str = "medium"
    assignee: str | None = None
    created_at: str = dataclasses.field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    start_time: str | None = None
    completed: bool = False

    # ------------------------------------------------------------------ #
    def to_dict(self) -> Dict:
        """@return dict: JSON-ready."""
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(data: Dict) -> "TodoItem":
        """Factory from persisted JSON."""
        return TodoItem(**data)
