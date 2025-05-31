"""
Reusable PySide6 widgets.
"""
from __future__ import annotations

from PySide6 import QtWidgets

from todolist.core.models import TodoItem

__all__ = ["TodoTable"]


class TodoTable(QtWidgets.QTableWidget):
    """Double-click to toggle completion."""

    HEADERS = ("Description", "Assignee", "Priority",
               "Created", "Started", "Done")

    def __init__(self, tasks: list[TodoItem]):
        super().__init__(len(tasks), len(self.HEADERS))
        self._tasks = tasks
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.populate()

    # ------------------------------------------------------------------ #
    def populate(self) -> None:
        """Refresh table from internal list."""
        self.setRowCount(len(self._tasks))
        for r, t in enumerate(self._tasks):
            self._set(r, 0, t.description)
            self._set(r, 1, t.assignee or "-")
            self._set(r, 2, t.priority)
            self._set(r, 3, t.created_at.split("T")[0])
            self._set(r, 4, (t.start_time or "-").split("T")[0])
            self._set(r, 5, "✓" if t.completed else "")
        self.resizeColumnsToContents()

    def _set(self, row: int, col: int, text: str) -> None:
        self.setItem(row, col, QtWidgets.QTableWidgetItem(text))

    # ------------------------------------------------------------------ #
    # toggle                                                               #
    # ------------------------------------------------------------------ #
    def mouseDoubleClickEvent(self, ev):  # noqa: N802,E501 (Qt sig style)
        idx = self.indexAt(ev.pos())
        if idx.isValid():
            task = self._tasks[idx.row()]
            task.completed = not task.completed
            from todolist.core.storage import save_tasks  # local import to avoid cycles
            save_tasks(self._tasks)
            self.populate()
        super().mouseDoubleClickEvent(ev)
