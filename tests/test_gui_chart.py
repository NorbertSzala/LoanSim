"""Balance chart keeps a numeric alternative for every plotted point."""

from datetime import date
from decimal import Decimal

from PySide6.QtWidgets import QApplication, QTableWidget

from loansim.core.amortization import simulate
from loansim.core.models import ExtraPayment, InstallmentType, LoanTerms, OverpaymentPlan
from loansim.core.rates import FixedRate, RateObservation, VariableRate
from loansim.gui.chart import BalanceChart
from loansim.gui.results_view import ResultsView
from test_data_codec import sample_snapshot


def test_chart_exposes_engine_balances_in_table() -> None:
    app = QApplication.instance() or QApplication([])
    chart = BalanceChart()
    chart.set_result(sample_snapshot().result)
    app.processEvents()
    table = chart.findChild(QTableWidget, "balance_values")
    assert table is not None
    assert table.rowCount() == 3
    values = [table.item(row, 1) for row in range(3)]
    assert all(item is not None for item in values)
    assert [item.text() for item in values if item is not None] == ["1000.00", "502.49", "0.00"]


def test_chart_uses_scenario_color() -> None:
    app = QApplication.instance() or QApplication([])
    chart = BalanceChart()
    chart.set_color("#12AB34")
    app.processEvents()
    assert chart.canvas.color.name() == "#12ab34"


def test_results_show_polish_estimate_notice() -> None:
    app = QApplication.instance() or QApplication([])
    view = ResultsView()
    view.set_result(sample_snapshot().result)
    app.processEvents()
    assert "szacun" in view.notice.text().lower()
    assert "bank" in view.notice.text().lower()


def test_reopened_result_discloses_saved_engine_version() -> None:
    app = QApplication.instance() or QApplication([])
    view = ResultsView()
    view.set_result(sample_snapshot().result, engine_version="0.0.1")
    app.processEvents()
    assert "0.0.1" in view.engine_info.text()
    assert "bez ponownego przeliczenia" in view.engine_info.text()


def test_results_disclose_constant_future_rate_assumption_and_not_rrso() -> None:
    app = QApplication.instance() or QApplication([])
    terms = LoanTerms(Decimal("1000.00"), 2, date(2026, 1, 1), InstallmentType.ANNUITY)
    rates = VariableRate(
        "Manual",
        Decimal("0.02"),
        (RateObservation(1, Decimal("0.05"), "hypothetical", "user input"),),
        date(2025, 12, 31),
    )
    result = simulate(terms, rates)
    view = ResultsView()
    view.set_result(result)
    app.processEvents()
    headers = _headers(view.schedule)
    future_source = view.schedule.item(1, headers.index("Źródło stopy"))
    assert future_source is not None
    assert future_source.text() == "Stała przyszła (założenie)"
    assert "nie RRSO" in view.rate_heading.text()


def test_results_show_principal_requested_and_applied_extra_and_nominal_cost() -> None:
    app = QApplication.instance() or QApplication([])
    terms = LoanTerms(Decimal("1000.00"), 2, date(2026, 1, 1), InstallmentType.ANNUITY)
    plan = OverpaymentPlan(one_time=(ExtraPayment(1, Decimal("1000.00")),))
    result = simulate(terms, FixedRate(Decimal("0.12")), plan)
    view = ResultsView()
    view.set_result(result)
    app.processEvents()
    headers = _headers(view.schedule)
    first = result.rows[0]
    for heading, expected in (
        ("Kapitał raty", first.mandatory_principal),
        ("Nadpłata żądana", first.requested_extra),
        ("Nadpłata zastosowana", first.applied_extra),
    ):
        item = view.schedule.item(0, headers.index(heading))
        assert item is not None
        assert item.text() == str(expected)
    assert first.requested_extra > first.applied_extra
    assert view.nominal_cost.text() == f"{result.total_nominal_loan_cost:.2f} PLN"


def _headers(table: QTableWidget) -> list[str]:
    items = [table.horizontalHeaderItem(index) for index in range(table.columnCount())]
    assert all(item is not None for item in items)
    return [item.text() for item in items if item is not None]
