"""Explicit controls for opening, copying, and deleting saved scenarios."""

from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from loansim.data.repository import ScenarioSummary
from loansim.gui.strings import tr


class HistoryView(QWidget):
    open_requested = Signal(str)
    duplicate_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.scenarios = QListWidget()
        self.scenarios.setObjectName("scenario_history")
        layout.addWidget(self.scenarios)
        buttons = QHBoxLayout()
        self.open_button = QPushButton(tr("open"))
        self.duplicate_button = QPushButton(tr("duplicate"))
        self.delete_button = QPushButton(tr("delete"))
        buttons.addWidget(self.open_button)
        buttons.addWidget(self.duplicate_button)
        buttons.addWidget(self.delete_button)
        layout.addLayout(buttons)
        self.open_button.clicked.connect(lambda: self._request(self.open_requested))
        self.duplicate_button.clicked.connect(lambda: self._request(self.duplicate_requested))
        self.delete_button.clicked.connect(lambda: self._request(self.delete_requested))

    def _request(self, signal: SignalInstance) -> None:
        selected = self.scenarios.currentItem()
        if selected is not None:
            signal.emit(selected.data(Qt.ItemDataRole.UserRole))

    def set_scenarios(self, scenarios: tuple[ScenarioSummary, ...]) -> None:
        self.scenarios.clear()
        for scenario in scenarios:
            item = QListWidgetItem(
                tr("history_item", name=scenario.name, modified_at=scenario.modified_at)
            )
            item.setData(Qt.ItemDataRole.UserRole, scenario.id)
            item.setToolTip(tr("history_tooltip", id=scenario.id, created_at=scenario.created_at))
            self.scenarios.addItem(item)
