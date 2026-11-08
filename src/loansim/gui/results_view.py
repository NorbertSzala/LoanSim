"""Auditable single-scenario totals, payment rows, and balance chart."""

from importlib.metadata import version

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGridLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from loansim.core.amortization import SimulationResult
from loansim.gui.chart import BalanceChart
from loansim.gui.strings import tr, tr_list


class ResultsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.notice = QLabel(tr("estimate_notice"))
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        summary = QGridLayout()
        self.total_interest = QLabel(tr("empty"))
        self.total_interest.setObjectName("total_interest")
        summary.addWidget(QLabel(tr("summary_interest")), 0, 0)
        summary.addWidget(self.total_interest, 0, 1)
        self.total_financing_charges = QLabel(tr("empty"))
        summary.addWidget(QLabel(tr("summary_charges")), 0, 2)
        summary.addWidget(self.total_financing_charges, 0, 3)
        self.financing_cost = QLabel(tr("empty"))
        summary.addWidget(QLabel(tr("summary_financing_cost")), 1, 0)
        summary.addWidget(self.financing_cost, 1, 1)
        self.lender_repayments = QLabel(tr("empty"))
        summary.addWidget(QLabel(tr("summary_lender")), 1, 2)
        summary.addWidget(self.lender_repayments, 1, 3)
        self.cash_outflow = QLabel(tr("empty"))
        summary.addWidget(QLabel(tr("summary_cash")), 2, 0)
        summary.addWidget(self.cash_outflow, 2, 1)
        self.lifetime_outflow = QLabel(tr("empty"))
        summary.addWidget(QLabel(tr("summary_lifetime")), 2, 2)
        summary.addWidget(self.lifetime_outflow, 2, 3)
        self.duration = QLabel(tr("empty"))
        summary.addWidget(QLabel(tr("summary_duration")), 3, 0)
        summary.addWidget(self.duration, 3, 1)
        self.ltv = QLabel(tr("empty"))
        summary.addWidget(QLabel(tr("summary_ltv")), 3, 2)
        summary.addWidget(self.ltv, 3, 3)
        self.acquisition_cost = QLabel(tr("empty"))
        summary.addWidget(QLabel(tr("summary_acquisition")), 4, 0)
        summary.addWidget(self.acquisition_cost, 4, 1)
        self.interest_savings = QLabel(tr("empty"))
        summary.addWidget(QLabel(tr("summary_savings")), 4, 2)
        summary.addWidget(self.interest_savings, 4, 3)
        self.nominal_cost = QLabel(tr("empty"))
        summary.addWidget(QLabel(tr("summary_nominal_cost")), 5, 0)
        summary.addWidget(self.nominal_cost, 5, 1)
        layout.addLayout(summary)
        self.rate_label = QLabel(tr("empty"))
        self.rate_heading = QLabel(tr("rate_heading"))
        layout.addWidget(self.rate_heading)
        layout.addWidget(self.rate_label)
        self.engine_info = QLabel(tr("empty"))
        self.engine_info.setObjectName("engine_info")
        layout.addWidget(self.engine_info)
        self.save_button = QPushButton(tr("save"))
        self.save_button.setObjectName("save_scenario")
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)
        self.chart = BalanceChart()
        layout.addWidget(self.chart)
        self.schedule = QTableWidget(0, 13)
        self.schedule.setObjectName("payment_schedule")
        self.schedule.setHorizontalHeaderLabels(tr_list("schedule_headers"))
        self.schedule.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.schedule.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.schedule)

    def set_result(
        self,
        result: SimulationResult,
        *,
        engine_version: str | None = None,
        scenario_color: str = "#3355AA",
    ) -> None:
        self.total_interest.setText(f"{result.total_interest:.2f} PLN")
        self.total_financing_charges.setText(f"{result.total_financing_charges:.2f} PLN")
        self.financing_cost.setText(f"{result.financing_cost:.2f} PLN")
        self.nominal_cost.setText(f"{result.total_nominal_loan_cost:.2f} PLN")
        self.cash_outflow.setText(f"{result.total_cash_outflow:.2f} PLN")
        self.lender_repayments.setText(f"{result.total_lender_repayments:.2f} PLN")
        self.lifetime_outflow.setText(
            f"{result.lifetime_buyer_cash_outflow:.2f} PLN"
            if result.lifetime_buyer_cash_outflow is not None
            else tr("empty")
        )
        self.duration.setText(
            tr(
                "duration_value",
                effective=result.effective_months,
                contractual=result.contractual_months,
            )
        )
        self.ltv.setText(f"{result.ltv * 100:.2f}%" if result.ltv is not None else tr("empty"))
        self.acquisition_cost.setText(
            f"{result.total_property_acquisition_cost:.2f} PLN"
            if result.total_property_acquisition_cost is not None
            else tr("empty")
        )
        self.interest_savings.setText(
            f"{result.interest_savings:.2f} PLN"
            if result.interest_savings is not None
            else tr("empty")
        )
        self.rate_label.setText(
            f"{result.initial_nominal_annual * 100:.2f}% / "
            f"{result.initial_effective_annual * 100:.2f}%"
        )
        saved_version = engine_version or version("loansim")
        if saved_version != version("loansim"):
            self.engine_info.setText(
                tr("engine_old", version=saved_version, convention=result.convention_id)
            )
        else:
            self.engine_info.setText(
                tr("engine_current", version=saved_version, convention=result.convention_id)
            )
        self.notice.setText(tr("estimate_notice"))
        self.notice.setToolTip(result.estimate_notice)
        self.chart.set_color(scenario_color)
        self.chart.set_result(result)
        self.schedule.setRowCount(len(result.rows))
        for row_index, row in enumerate(result.rows):
            values = (
                row.period,
                row.payment_date.isoformat(),
                f"{row.nominal_annual * 100:.2f}%",
                row.interest,
                row.mandatory_principal,
                row.mandatory_payment,
                row.requested_extra,
                row.applied_extra,
                row.charge_outflow,
                row.actual_cash_outflow,
                row.closing_balance,
                tr(f"rate_source_{row.rate_source_kind}"),
                row.rate_detail.source_name,
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.schedule.setItem(row_index, column, item)
        self.save_button.setEnabled(True)

    def invalidate(self) -> None:
        self.save_button.setEnabled(False)
