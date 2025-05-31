"""
Main window that glues extractor + storage + table widget.
"""
from __future__ import annotations

from PySide6 import QtWidgets

from todolist.ai.extractor import GPTTodoExtractor
from todolist.core import storage
from todolist.core.models import TodoItem
from todolist.gui.widgets import TodoTable

__all__ = ["TodoApp"]


class TodoApp(QtWidgets.QWidget):
    """
    @param tasks: Shared task list loaded on startup.
    """

    def __init__(self, tasks: list[TodoItem]):
        super().__init__()
        self.setWindowTitle("Todo-AI")
        self.resize(750, 420)

        self._tasks = tasks
        self._extractor = GPTTodoExtractor()          # needs OPENAI_API_KEY

        lay = QtWidgets.QVBoxLayout(self)

        self._table = TodoTable(self._tasks)
        lay.addWidget(self._table)

        self._input = QtWidgets.QTextEdit(
            placeholderText="Paste raw meeting notes…")
        lay.addWidget(self._input)

        btn = QtWidgets.QPushButton("Extract ➜ Append")
        btn.clicked.connect(self.on_append)
        lay.addWidget(btn)

    # ------------------------------------------------------------------ #
    def on_append(self) -> None:
        raw = self._input.toPlainText().strip()
        if not raw:
            return
        items = self._extractor.extract(raw)
        self._tasks[:] = storage.append_tasks(items)   # mutate in-place
        self._table.populate()
        self._input.clear()
