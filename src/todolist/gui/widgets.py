"""
PySide6 widgets – now with coloured rows + blink on stale items.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from PySide6 import QtCore, QtGui, QtWidgets

from todolist.core.models import TodoItem

__all__ = ["TodoTable"]


# --------------------------------------------------------------------------- #
# Colour constants                                                            #
# --------------------------------------------------------------------------- #
# darker palette
CLR_HIGH   = QtGui.QColor("#8b0000")   # dark-red
CLR_MEDIUM = QtGui.QColor("#b38f00")   # dark-mustard
CLR_LOW    = QtGui.QColor("#006400")   # dark-green
CLR_DONE   = QtGui.QColor("#6e6e6e")   # dark-grey
CLR_BLINK  = QtGui.QColor("#b30059")   # dark-magenta (blink)


BLINK_INTERVAL_MS = 500
STALE_AFTER       = timedelta(days=1)


class TodoTable(QtWidgets.QTableWidget):
    """Coloured rows, double-click toggles complete, blink if stale."""

    HEADERS = ("Description", "Assignee", "Priority",
               "Created", "Started", "Done")

    def __init__(self, tasks: list[TodoItem]):
        super().__init__(len(tasks), len(self.HEADERS))
        self._tasks = tasks
        self._blink_state = False
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.populate()

        # 0.5-sec timer for blink
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._toggle_blink)  # type: ignore[arg-type]
        self._timer.start(BLINK_INTERVAL_MS)

    # ------------------------------------------------------------------ #
    # painting                                                            #
    # ------------------------------------------------------------------ #
    def populate(self) -> None:
        """Refresh entire table."""
        self.setRowCount(len(self._tasks))
        for r, t in enumerate(self._tasks):
            self._set(r, 0, t.description)
            self._set(r, 1, t.assignee or "-")
            self._set(r, 2, t.priority)
            self._set(r, 3, t.created_at.split("T")[0])
            self._set(r, 4, (t.start_time or "-").split("T")[0])
            self._set(r, 5, "✓" if t.completed else "")
            self._apply_row_style(r, t)
        self.resizeColumnsToContents()

    def _set(self, row: int, col: int, text: str) -> None:
        self.setItem(row, col, QtWidgets.QTableWidgetItem(text))

    def _apply_row_style(self, row: int, task: TodoItem) -> None:
        """
        Colour row based on priority / completion.
        Blink handled separately by timer.
        """
        if task.completed:
            colour = CLR_DONE
        else:
            colour = {
                "high":   CLR_HIGH,
                "medium": CLR_MEDIUM,
                "low":    CLR_LOW,
            }.get(task.priority, CLR_LOW)

        for c in range(self.columnCount()):
            self.item(row, c).setBackground(colour)

    # ------------------------------------------------------------------ #
    # user interaction                                                   #
    # ------------------------------------------------------------------ #
    def mouseDoubleClickEvent(self, ev):  # noqa: N802
        idx = self.indexAt(ev.pos())
        if idx.isValid():
            task = self._tasks[idx.row()]
            task.completed = not task.completed
            from todolist.core.storage import save_tasks
            save_tasks(self._tasks)
            self.populate()
        super().mouseDoubleClickEvent(ev)

    # ------------------------------------------------------------------ #
    # blink logic                                                        #
    # ------------------------------------------------------------------ #
    def _toggle_blink(self) -> None:
        """
        Flip _blink_state, recolour stale rows accordingly.
        """
        self._blink_state = not self._blink_state
        now = datetime.now(timezone.utc)

        for row, task in enumerate(self._tasks):
            if task.completed:
                continue
            created = datetime.fromisoformat(task.created_at)
            if now - created < STALE_AFTER:
                continue

            # choose blink colour vs base
            colour = CLR_BLINK if self._blink_state else {
                "high": CLR_HIGH,
                "medium": CLR_MEDIUM,
                "low": CLR_LOW,
            }.get(task.priority, CLR_LOW)

            for col in range(self.columnCount()):
                self.item(row, col).setBackground(colour)
