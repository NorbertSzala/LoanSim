"""Run engine and database work outside the Qt event thread."""

from collections.abc import Callable

from PySide6.QtCore import QObject, QRunnable, Signal


class TaskSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class Task(QRunnable):
    def __init__(self, operation: Callable[[], object]) -> None:
        super().__init__()
        self.operation = operation
        self.signals = TaskSignals()

    def run(self) -> None:
        try:
            self.signals.finished.emit(self.operation())
        except Exception as error:
            self.signals.failed.emit(str(error))
