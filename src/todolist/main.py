#!/usr/bin/env python3
"""
Entry-point – run `python -m todo_list.src` or `python todo_list/src/main.py`.
"""
from __future__ import annotations

import sys

from PySide6 import QtWidgets

from todolist.core import storage, watcher
from todolist.gui.app import TodoApp


def main() -> None:
    tasks = storage.load_tasks()

    # 1-hour watcher (10 s when env TODO_DEBUG=1)
    interval = 10 if "TODO_DEBUG" in sys.argv else 3600
    watcher.TaskWatcher(tasks, interval).start()

    app = QtWidgets.QApplication(sys.argv)
    gui = TodoApp(tasks)
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
