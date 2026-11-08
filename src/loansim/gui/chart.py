"""Qt-only balance chart with a complete numeric alternative."""

from decimal import Decimal

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from loansim.core.amortization import SimulationResult
from loansim.gui.strings import tr, tr_list


class _BalanceCanvas(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.values: tuple[Decimal, ...] = ()
        self.color = QColor("#3355AA")
        self.setMinimumHeight(160)
        self.setAccessibleName(tr("balance_chart_name"))

    def paintEvent(self, _event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("white"))
        if len(self.values) < 2:
            painter.end()
            return
        left, right, top, bottom = 52.0, 12.0, 12.0, 32.0
        width = max(1.0, self.width() - left - right)
        height = max(1.0, self.height() - top - bottom)
        painter.setPen(QPen(QColor("#555555"), 1))
        painter.drawLine(int(left), int(top), int(left), int(top + height))
        painter.drawLine(int(left), int(top + height), int(left + width), int(top + height))
        max_balance = max(self.values)
        scale = float(max_balance) if max_balance > 0 else 1.0
        points = QPolygonF(
            [
                QPointF(
                    left + width * i / (len(self.values) - 1),
                    top + height * (1 - float(value) / scale),
                )
                for i, value in enumerate(self.values)
            ]
        )
        painter.setPen(QPen(self.color, 2))
        painter.drawPolyline(points)
        painter.setPen(QColor("#333333"))
        painter.drawText(2, int(top + 10), f"{max_balance:.0f}")
        painter.drawText(8, int(top + height), "0")
        painter.drawText(int(left), self.height() - 8, "0")
        painter.drawText(int(left + width - 25), self.height() - 8, str(len(self.values) - 1))
        painter.end()


class BalanceChart(QWidget):
    """Plot principal after each period and show the same values in a table."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.canvas = _BalanceCanvas()
        layout.addWidget(self.canvas)
        self.table = QTableWidget(0, 3)
        self.table.setObjectName("balance_values")
        self.table.setHorizontalHeaderLabels(tr_list("balance_headers"))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAccessibleName(tr("balance_table_name"))
        layout.addWidget(self.table)

    def set_result(self, result: SimulationResult) -> None:
        first_date = result.rows[0].rate_detail.period_start.isoformat() if result.rows else ""
        points = [(0, result.initial_debt, first_date)] + [
            (row.period, row.closing_balance, row.payment_date.isoformat()) for row in result.rows
        ]
        self.canvas.values = tuple(balance for _, balance, _ in points)
        self.canvas.update()
        self.table.setRowCount(len(points))
        for row, values in enumerate(points):
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, column, item)

    def set_color(self, color: str) -> None:
        selected = QColor(color)
        if not selected.isValid():
            raise ValueError("scenario color is invalid")
        self.canvas.color = selected
        self.canvas.update()
